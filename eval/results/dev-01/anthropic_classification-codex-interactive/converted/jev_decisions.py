"""Bounded insurance-ticket Choice; all Jev policy lives here."""
import json
import logging
import math
import os
import urllib.request

MODEL = "typesafe/jev-1.13-20260917"
ENDPOINT = "https://openrouter.ai/api/v1/systemone"
KEY_ENV = "OPENROUTER_API_KEY"
THRESHOLD = 0.95
MAX_INPUT_BYTES = 2000
TIMEOUT_SECONDS = 10
CRITERIA = {'Billing Inquiries': 'Questions about invoices, charges, fees, and premiums Requests for '
                      'clarification on billing statements Inquiries about payment methods and due '
                      'dates',
 'Policy Administration': 'Requests for policy changes, updates, or cancellations Questions about '
                          'policy renewals and reinstatements Inquiries about adding or removing '
                          'coverage options',
 'Claims Assistance': 'Questions about the claims process and filing procedures Requests for help '
                      'with submitting claim documentation Inquiries about claim status and payout '
                      'timelines',
 'Coverage Explanations': 'Questions about what is covered under specific policy types Requests '
                          'for clarification on coverage limits and exclusions Inquiries about '
                          'deductibles and out-of-pocket expenses',
 'Quotes and Proposals': 'Requests for new policy quotes and price comparisons Questions about '
                         'available discounts and bundling options Inquiries about switching from '
                         'another insurer',
 'Account Management': 'Requests for login credentials or password resets Questions about online '
                       'account features and functionality Inquiries about updating contact or '
                       'personal information',
 'Billing Disputes': 'Complaints about unexpected or incorrect charges Requests for refunds or '
                     'premium adjustments Inquiries about late fees or collection notices',
 'Claims Disputes': 'Complaints about denied or underpaid claims Requests for reconsideration of '
                    'claim decisions Inquiries about appealing a claim outcome',
 'Policy Comparisons': 'Questions about the differences between policy options Requests for help '
                       'deciding between coverage levels Inquiries about how policies compare to '
                       "competitors' offerings",
 'General Inquiries': 'Questions about company contact information or hours of operation Requests '
                      "for general information about products or services Inquiries that don't fit "
                      'neatly into other categories'}
QUESTIONS = {"category": {
    "type": "choice",
    "instructions": "Classify the customer support ticket into one of the categories.",
    "criteria": CRITERIA,
}}
logger = logging.getLogger(__name__)


def evaluate(ticket):
    """Real HTTP call; callers must enforce supported state and handle failures."""
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps({"model": MODEL, "state": ticket, "questions": QUESTIONS}).encode(),
        headers={"Authorization": "Bearer " + os.environ[KEY_ENV],
                 "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return json.load(response)


def gate(choice, confidence):
    return (isinstance(choice, str) and choice in CRITERIA
            and type(confidence) in (float, int) and math.isfinite(confidence)
            and THRESHOLD <= confidence <= 1)


def accepted_label(response):
    if not isinstance(response, dict) or response.get("model") != MODEL:
        return None
    answer = response.get("answers", {}).get("category", {})
    if not isinstance(answer, dict) or answer.get("type") != "choice":
        return None
    choice, confidence = answer.get("choice"), answer.get("confidence")
    probabilities = answer.get("probabilities")
    if not isinstance(probabilities, dict) or set(probabilities) != set(CRITERIA):
        return None
    if not all(type(v) in (int, float) and math.isfinite(v) and 0 <= v <= 1
               for v in probabilities.values()):
        return None
    if not math.isclose(sum(probabilities.values()), 1, abs_tol=0.001):
        return None
    if not gate(choice, confidence) or probabilities[choice] != max(probabilities.values()):
        return None
    return choice


def classify(ticket, original, original_model):
    label = None
    reason = "unsupported_state"
    try:
        if isinstance(ticket, str) and len(ticket.encode("utf-8")) <= MAX_INPUT_BYTES:
            reason = "missing_key"
            if os.environ.get(KEY_ENV):
                reason = "rejected_answer"
                label = accepted_label(evaluate(ticket))
    except Exception:
        # Do not expose response bodies, credentials, input text or headers.
        reason = "jev_error"
    if label is not None:
        logger.info("path=jev model=%s reason=accepted", MODEL)
        return label
    logger.info("path=original model=%s reason=%s", original_model, reason)
    # Outside the try: preserve the original exception, with no second attempt.
    return original(ticket)
