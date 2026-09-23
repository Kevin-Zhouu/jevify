"""Jev decisions module — all Jev model IDs, questions, criteria, thresholds and gate logic.

Single source of truth for the insurance ticket classification conversion.
"""
import json
import logging
import math
import os
import time
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

# --- Model and provider configuration ---

JEV_MODEL = "typesafe/jev-1.13-20260917"
JEV_BASE_URL = "https://openrouter.ai/api/v1/systemone"
JEV_KEY_ENV = "OPENROUTER_API_KEY"
JEV_TIMEOUT_SECONDS = 15

# --- Confidence threshold ---

CONFIDENCE_THRESHOLD = 0.85

# --- Category options and criteria for Choice ---

CATEGORY_CRITERIA = {
    "Billing Inquiries": "Questions about invoices, charges, fees, premiums, billing statements, payment methods and due dates",
    "Policy Administration": "Requests for policy changes, updates, cancellations, renewals, reinstatements, adding or removing coverage options",
    "Claims Assistance": "Questions about the claims process, filing procedures, submitting claim documentation, claim status and payout timelines",
    "Coverage Explanations": "Questions about what is covered under specific policy types, coverage limits, exclusions, deductibles and out-of-pocket expenses",
    "Quotes and Proposals": "Requests for new policy quotes, price comparisons, available discounts, bundling options, switching from another insurer",
    "Account Management": "Requests for login credentials, password resets, online account features, updating contact or personal information",
    "Billing Disputes": "Complaints about unexpected or incorrect charges, requests for refunds or premium adjustments, late fees or collection notices",
    "Claims Disputes": "Complaints about denied or underpaid claims, requests for reconsideration, appealing a claim outcome",
    "Policy Comparisons": "Questions about differences between policy options, help deciding between coverage levels, comparisons to competitors",
    "General Inquiries": "Questions about company contact information, hours of operation, general product or service information, inquiries that don't fit other categories",
}

CLASSIFICATION_QUESTION = {
    "type": "choice",
    "instructions": "Which insurance support category best matches this customer ticket?",
    "criteria": CATEGORY_CRITERIA,
}

# --- Gate logic ---


def is_confidence_acceptable(confidence):
    """Check if confidence meets threshold. Returns False for non-finite or out-of-range values."""
    if not isinstance(confidence, (int, float)):
        return False
    if not math.isfinite(confidence):
        return False
    if confidence < 0 or confidence > 1:
        return False
    return confidence >= CONFIDENCE_THRESHOLD


def is_valid_label(label):
    """Check if the returned label is one of the known categories."""
    return isinstance(label, str) and label in CATEGORY_CRITERIA


def validate_usage(usage):
    """Validate that usage fields are finite non-negative numbers. Returns False if invalid."""
    if usage is None:
        return False
    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    for val in (input_tokens, output_tokens):
        if not isinstance(val, (int, float)):
            return False
        if not math.isfinite(val) or val < 0:
            return False
    return True


def call_jev(ticket_text):
    """Call Jev via OpenRouter HTTP API. Returns (choice, confidence, usage, model, raw_response) or raises."""
    api_key = os.environ.get(JEV_KEY_ENV)
    if not api_key:
        raise EnvironmentError(f"{JEV_KEY_ENV} not set")

    request_body = json.dumps({
        "model": JEV_MODEL,
        "state": {"ticket": ticket_text},
        "questions": {
            "category": CLASSIFICATION_QUESTION,
        },
    }).encode("utf-8")

    req = urllib.request.Request(
        JEV_BASE_URL,
        data=request_body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=JEV_TIMEOUT_SECONDS) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        elapsed = time.monotonic() - start
        raise RuntimeError(f"Jev transport error after {elapsed:.1f}s: {exc}") from exc

    elapsed_ms = (time.monotonic() - start) * 1000

    answer = raw.get("answers", {}).get("category", {})
    choice = answer.get("choice")
    confidence = answer.get("confidence")
    usage = raw.get("usage")
    model = raw.get("model")

    return choice, confidence, usage, model, raw, elapsed_ms


def classify_with_jev(ticket_text, original_fn):
    """Attempt Jev classification with confidence-gated fallback to original.

    Args:
        ticket_text: The customer support ticket text.
        original_fn: Callable that performs the original Anthropic classification.

    Returns:
        The classification label string (same contract as original).
    """
    try:
        choice, confidence, usage, model, raw, elapsed_ms = call_jev(ticket_text)
    except Exception as exc:
        logger.info("path=original reason=jev_error error=%s", exc)
        return original_fn(ticket_text)

    # Validate usage before accepting
    if not validate_usage(usage):
        logger.info("path=original reason=invalid_usage model=%s", model)
        return original_fn(ticket_text)

    # Validate label
    if not is_valid_label(choice):
        logger.info("path=original reason=unknown_label label=%s model=%s", choice, model)
        return original_fn(ticket_text)

    # Validate confidence
    if not is_confidence_acceptable(confidence):
        logger.info(
            "path=original reason=low_confidence confidence=%s model=%s",
            confidence, model,
        )
        return original_fn(ticket_text)

    logger.info(
        "path=jev model=%s confidence=%.4f latency_ms=%.1f",
        model, confidence, elapsed_ms,
    )
    return choice
