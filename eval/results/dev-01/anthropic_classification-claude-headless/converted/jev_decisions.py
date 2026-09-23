"""Jev decisions module — all model IDs, questions, criteria, thresholds and gate policy.

Call sites supply runtime state and the original callable.
Validation imports this same module; no duplicated question definitions.
"""

import json
import logging
import os
import time
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

# ── Model and provider pin ──────────────────────────────────────────────────

JEV_MODEL = "typesafe/jev-1.13-20260917"
JEV_BASE_URL = "https://openrouter.ai/api/v1/systemone"
JEV_TIMEOUT_S = 10

# ── Confidence threshold (calibrate during validation) ──────────────────────

CLASSIFY_CONFIDENCE_THRESHOLD = 0.80

# ── Question definition ─────────────────────────────────────────────────────

CLASSIFY_QUESTION = {
    "type": "choice",
    "instructions": "Which insurance support category does this customer ticket belong to?",
    "criteria": {
        "Billing Inquiries": "Questions about invoices, charges, fees, and premiums; requests for clarification on billing statements; inquiries about payment methods and due dates",
        "Policy Administration": "Requests for policy changes, updates, or cancellations; questions about policy renewals and reinstatements; inquiries about adding or removing coverage options",
        "Claims Assistance": "Questions about the claims process and filing procedures; requests for help with submitting claim documentation; inquiries about claim status and payout timelines",
        "Coverage Explanations": "Questions about what is covered under specific policy types; requests for clarification on coverage limits and exclusions; inquiries about deductibles and out-of-pocket expenses",
        "Quotes and Proposals": "Requests for new policy quotes and price comparisons; questions about available discounts and bundling options; inquiries about switching from another insurer",
        "Account Management": "Requests for login credentials or password resets; questions about online account features and functionality; inquiries about updating contact or personal information",
        "Billing Disputes": "Complaints about unexpected or incorrect charges; requests for refunds or premium adjustments; inquiries about late fees or collection notices",
        "Claims Disputes": "Complaints about denied or underpaid claims; requests for reconsideration of claim decisions; inquiries about appealing a claim outcome",
        "Policy Comparisons": "Questions about the differences between policy options; requests for help deciding between coverage levels; inquiries about how policies compare to competitors' offerings",
        "General Inquiries": "Questions about company contact information or hours of operation; requests for general information about products or services; inquiries that don't fit neatly into other categories",
    },
}

# ── Category label set (for unknown-label validation) ───────────────────────

VALID_CATEGORIES = set(CLASSIFY_QUESTION["criteria"].keys())


def _call_jev(state: str) -> dict | None:
    """Call Jev via OpenRouter System One endpoint. Returns parsed response or None on failure."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        logger.info("jev path=original reason=missing_credentials")
        return None

    payload = json.dumps({
        "model": JEV_MODEL,
        "state": state,
        "questions": {
            "category": CLASSIFY_QUESTION,
        },
    }).encode()

    req = urllib.request.Request(
        JEV_BASE_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=JEV_TIMEOUT_S) as resp:
            return json.loads(resp.read())
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        logger.info("jev path=original reason=jev_error error_type=%s", type(exc).__name__)
        return None


def classify_with_jev(ticket: str, original_fn) -> str:
    """Attempt Jev classification with confidence-gated fallback to original_fn.

    Args:
        ticket: The customer support ticket text.
        original_fn: Callable that takes the ticket text and returns the category label
                     using the original Anthropic path.

    Returns:
        The category label string.
    """
    start = time.monotonic()
    response = _call_jev(ticket)
    jev_elapsed_ms = (time.monotonic() - start) * 1000

    if response is None:
        return original_fn(ticket)

    try:
        answer = response["answers"]["category"]
        choice = answer["choice"]
        confidence = answer["confidence"]
        model = response.get("model", JEV_MODEL)
    except (KeyError, TypeError):
        logger.info("jev path=original reason=malformed_response")
        return original_fn(ticket)

    # Validate: confidence must be finite and in range
    if not isinstance(confidence, (int, float)) or confidence != confidence:  # NaN check
        logger.info("jev path=original reason=nonfinite_confidence")
        return original_fn(ticket)

    # Validate: choice must be a known category
    if choice not in VALID_CATEGORIES:
        logger.info("jev path=original reason=unknown_label label=%s model=%s", choice, model)
        return original_fn(ticket)

    # Confidence gate
    if confidence < CLASSIFY_CONFIDENCE_THRESHOLD:
        logger.info(
            "jev path=original reason=low_confidence confidence=%.3f threshold=%.2f model=%s latency_ms=%.1f",
            confidence, CLASSIFY_CONFIDENCE_THRESHOLD, model, jev_elapsed_ms,
        )
        return original_fn(ticket)

    logger.info(
        "jev path=jev confidence=%.3f model=%s latency_ms=%.1f",
        confidence, model, jev_elapsed_ms,
    )
    return choice
