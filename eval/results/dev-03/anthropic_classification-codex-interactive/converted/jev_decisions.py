"""Conservative Choice policy for benign insurance support tickets (Python 3.10+)."""
import http.client
import json
import logging
import math
import os
import time

MODEL = "typesafe/jev-1.13-20260917"
KEY_ENV = "OPENROUTER_API_KEY"
THRESHOLD = 0.95  # Provisional, frozen before confirmation.
TIMEOUT_SECONDS = 15
MAX_REQUEST_BYTES = 16000  # Conservative byte bound below 32k state+question tokens.
MAX_RESPONSE_BYTES = 1024 * 1024
LOGGER = logging.getLogger(__name__)
CRITERIA = {'Account Management': 'Requests for login credentials or password resets Questions about online '
                       'account features and functionality Inquiries about updating contact or '
                       'personal information',
 'Billing Disputes': 'Complaints about unexpected or incorrect charges Requests for refunds or '
                     'premium adjustments Inquiries about late fees or collection notices',
 'Billing Inquiries': 'Questions about invoices, charges, fees, and premiums Requests for '
                      'clarification on billing statements Inquiries about payment methods and due '
                      'dates',
 'Claims Assistance': 'Questions about the claims process and filing procedures Requests for help '
                      'with submitting claim documentation Inquiries about claim status and payout '
                      'timelines',
 'Claims Disputes': 'Complaints about denied or underpaid claims Requests for reconsideration of '
                    'claim decisions Inquiries about appealing a claim outcome',
 'Coverage Explanations': 'Questions about what is covered under specific policy types Requests '
                          'for clarification on coverage limits and exclusions Inquiries about '
                          'deductibles and out-of-pocket expenses',
 'General Inquiries': 'Questions about company contact information or hours of operation Requests '
                      "for general information about products or services Inquiries that don't fit "
                      'neatly into other categories',
 'Policy Administration': 'Requests for policy changes, updates, or cancellations Questions about '
                          'policy renewals and reinstatements Inquiries about adding or removing '
                          'coverage options',
 'Policy Comparisons': 'Questions about the differences between policy options Requests for help '
                       'deciding between coverage levels Inquiries about how policies compare to '
                       "competitors' offerings",
 'Quotes and Proposals': 'Requests for new policy quotes and price comparisons Questions about '
                         'available discounts and bundling options Inquiries about switching from '
                         'another insurer'}
QUESTIONS = {"category": {
    "type": "choice",
    "instructions": "Classify the customer support ticket in `ticket` into one category.",
    "criteria": CRITERIA,
}}


def _post(payload, key):
    """No retries; socket and total read deadlines; no credential-bearing diagnostics."""
    deadline = time.monotonic() + TIMEOUT_SECONDS
    connection = http.client.HTTPSConnection("openrouter.ai", timeout=TIMEOUT_SECONDS)
    try:
        connection.connect()
        sock = connection.sock
        sock.settimeout(max(0.001, deadline - time.monotonic()))
        connection.request("POST", "/api/v1/systemone", body=payload,
                           headers={"Authorization": "Bearer " + key,
                                    "Content-Type": "application/json"})
        sock.settimeout(max(0.001, deadline - time.monotonic()))
        response = connection.getresponse()
        if response.status != 200:
            raise HTTPFailure(response.status)
        body = bytearray()
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError()
            sock.settimeout(remaining)
            chunk = response.read1(min(65536, MAX_RESPONSE_BYTES + 1 - len(body)))
            if not chunk:
                break
            body.extend(chunk)
            if len(body) > MAX_RESPONSE_BYTES:
                raise ValueError("response_size")
        result = json.loads(body)
        if time.monotonic() > deadline:
            raise TimeoutError()
        return result
    finally:
        connection.close()


class HTTPFailure(Exception):
    def __init__(self, status):
        self.status = status
        super().__init__("http_failure")


def finite_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def accepts(confidence):
    return finite_number(confidence) and THRESHOLD <= confidence <= 1


def parse_response(response):
    if not isinstance(response, dict) or response.get("model") != MODEL:
        raise ValueError("model")
    answers = response.get("answers")
    if not isinstance(answers, dict):
        raise ValueError("answers")
    answer = answers.get("category")
    if not isinstance(answer, dict) or answer.get("type") != "choice":
        raise ValueError("primitive")
    label, confidence = answer.get("choice"), answer.get("confidence")
    if not isinstance(label, str) or label not in CRITERIA:
        raise ValueError("label")
    if not finite_number(confidence) or not 0 <= confidence <= 1:
        raise ValueError("confidence")
    probabilities = answer.get("probabilities")
    if not isinstance(probabilities, dict) or set(probabilities) != set(CRITERIA):
        raise ValueError("probabilities")
    if any(not finite_number(v) or not 0 <= v <= 1 for v in probabilities.values()):
        raise ValueError("probabilities")
    if not math.isclose(sum(probabilities.values()), 1, abs_tol=0.001):
        raise ValueError("probability_sum")
    if probabilities[label] < max(probabilities.values()):
        raise ValueError("choice_probability")
    usage = response.get("usage")
    if not isinstance(usage, dict):
        raise ValueError("usage")
    for field in ("input_tokens", "output_tokens"):
        value = usage.get(field)
        if not finite_number(value) or value < 0:
            raise ValueError("usage")
    return label, confidence


def evaluate(ticket):
    if not isinstance(ticket, str):
        raise ValueError("input_type")
    payload = json.dumps({"model": MODEL, "state": {"ticket": ticket},
                          "questions": QUESTIONS}, ensure_ascii=False).encode("utf-8")
    if len(payload) > MAX_REQUEST_BYTES:
        raise ValueError("input_size")
    key = os.environ.get(KEY_ENV)
    if not key:
        raise MissingKey()
    response = _post(payload, key)
    parse_response(response)
    return response


class MissingKey(Exception):
    pass


def classify_with_fallback(ticket, original, original_model):
    accepted = None
    reason = "invalid_response"
    try:
        response = evaluate(ticket)
        label, confidence = parse_response(response)
        if accepts(confidence):
            accepted = label
        else:
            reason = "low_confidence"
    except MissingKey:
        reason = "missing_key"
    except TimeoutError:
        reason = "timeout"
    except HTTPFailure as error:
        reason = "rate_limit" if error.status == 429 else "http_error"
    except Exception:
        reason = "invalid_or_error"
    if accepted is not None:
        LOGGER.info("path=jev model=%s reason=accepted", MODEL)
        return accepted
    LOGGER.info("path=original model=%s jev_model=%s reason=%s", original_model, MODEL, reason)
    # Outside the protected Jev block: preserve original exceptions and never retry it.
    return original(ticket)
