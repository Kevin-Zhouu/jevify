"""Conservative typed ticket decisions; the original callable owns fallback."""
import http.client
import json
import logging
import math
import os
import time
import xml.etree.ElementTree as ET

MODEL = "typesafe/jev-1.13-20260917"
KEY_ENV = "OPENROUTER_API_KEY"
THRESHOLD = 0.90
TIMEOUT_SECONDS = 8.0
MAX_STATE_BYTES = 8000
MAX_RESPONSE_BYTES = 65536
INSTRUCTIONS = "Classify the customer support ticket in `ticket` into exactly one of the insurance support categories."
LOG = logging.getLogger(__name__)


class TransportError(Exception):
    def __init__(self, status):
        self.status = status
        super().__init__("Jev HTTP error")


def questions(categories):
    root = ET.fromstring("<categories>" + categories + "</categories>")
    criteria = {c.findtext("label").strip(): c.findtext("content").strip() for c in root}
    if len(criteria) != 10:
        raise ValueError("Unexpected taxonomy")
    return {"category": {"type": "choice", "instructions": INSTRUCTIONS, "criteria": criteria}}


def _post(payload, key):
    # A deadline remains active through headers and each body read. No retries.
    deadline = time.monotonic() + TIMEOUT_SECONDS
    conn = http.client.HTTPSConnection("openrouter.ai", timeout=TIMEOUT_SECONDS)
    try:
        conn.connect()
        sock = conn.sock
        sock.settimeout(max(0.001, deadline - time.monotonic()))
        conn.request("POST", "/api/v1/systemone", body=json.dumps(payload).encode(),
                     headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
        sock.settimeout(max(0.001, deadline - time.monotonic()))
        response = conn.getresponse()
        if response.status != 200:
            raise TransportError(response.status)
        chunks, size = [], 0
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError()
            sock.settimeout(remaining)
            part = response.read1(8192)
            if not part:
                break
            size += len(part)
            if size > MAX_RESPONSE_BYTES:
                raise ValueError("Oversize response")
            chunks.append(part)
        result = json.loads(b"".join(chunks))
        if time.monotonic() > deadline:
            raise TimeoutError()
        return result
    finally:
        conn.close()


def evaluate(ticket, categories):
    return _post({"model": MODEL, "state": {"ticket": ticket},
                  "questions": questions(categories)}, os.environ[KEY_ENV])


def probability(value):
    return type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1


def accepted(confidence):
    return probability(confidence) and confidence >= THRESHOLD


def parse_answer(response, categories):
    if not isinstance(response, dict) or response.get("model") != MODEL:
        raise ValueError("Invalid model")
    answers = response.get("answers")
    if not isinstance(answers, dict):
        raise ValueError("Invalid answers")
    answer = answers.get("category")
    if not isinstance(answer, dict) or answer.get("type") != "choice":
        raise ValueError("Invalid primitive")
    labels = questions(categories)["category"]["criteria"]
    choice, confidence = answer.get("choice"), answer.get("confidence")
    if not isinstance(choice, str) or choice not in labels or not probability(confidence):
        raise ValueError("Invalid choice or confidence")
    probabilities = answer.get("probabilities")
    if (not isinstance(probabilities, dict) or set(probabilities) != set(labels)
            or not all(probability(v) for v in probabilities.values())
            or not math.isclose(sum(probabilities.values()), 1, abs_tol=0.01)
            or probabilities[choice] < max(probabilities.values())):
        raise ValueError("Invalid probabilities")
    return choice, confidence


def classify(ticket, categories, original, original_model):
    value, reason = None, "unsupported_input"
    if isinstance(ticket, str) and len(ticket.encode("utf-8", errors="surrogatepass")) <= MAX_STATE_BYTES:
        reason = "missing_key"
        if os.environ.get(KEY_ENV):
            try:
                response = evaluate(ticket, categories)
                choice, confidence = parse_answer(response, categories)
                reason = "low_confidence"
                if accepted(confidence):
                    value = choice
            except TimeoutError:
                reason = "timeout"
            except TransportError as error:
                reason = "rate_limit" if error.status == 429 else "http_error"
            except Exception:
                reason = "invalid_or_error"
    if value is not None:
        LOG.info("path=jev model=%s reason=accepted", MODEL)
        return value
    LOG.info("path=original model=%s jev_model=%s reason=%s", original_model, MODEL, reason)
    return original(ticket)
