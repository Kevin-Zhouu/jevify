"""Centralised Jev decision definitions for the insurance ticket classifier.

All Jev model IDs, question definitions, criteria, thresholds and gate
policy live here.  Call sites supply runtime state and the original
callable.
"""

import logging
import math
import os
import time

logger = logging.getLogger(__name__)

# ── Model pin ────────────────────────────────────────────────────────
JEV_MODEL = "jev-1.13.0"

# ── Confidence gate ──────────────────────────────────────────────────
CONFIDENCE_THRESHOLD = 0.7

# ── Jev timeout (seconds) ───────────────────────────────────────────
JEV_TIMEOUT_S = 10

# ── Category labels and criteria ─────────────────────────────────────
CATEGORY_CRITERIA = {
    "Billing Inquiries": (
        "Questions about invoices, charges, fees, and premiums; "
        "requests for clarification on billing statements; "
        "inquiries about payment methods and due dates"
    ),
    "Policy Administration": (
        "Requests for policy changes, updates, or cancellations; "
        "questions about policy renewals and reinstatements; "
        "inquiries about adding or removing coverage options"
    ),
    "Claims Assistance": (
        "Questions about the claims process and filing procedures; "
        "requests for help with submitting claim documentation; "
        "inquiries about claim status and payout timelines"
    ),
    "Coverage Explanations": (
        "Questions about what is covered under specific policy types; "
        "requests for clarification on coverage limits and exclusions; "
        "inquiries about deductibles and out-of-pocket expenses"
    ),
    "Quotes and Proposals": (
        "Requests for new policy quotes and price comparisons; "
        "questions about available discounts and bundling options; "
        "inquiries about switching from another insurer"
    ),
    "Account Management": (
        "Requests for login credentials or password resets; "
        "questions about online account features and functionality; "
        "inquiries about updating contact or personal information"
    ),
    "Billing Disputes": (
        "Complaints about unexpected or incorrect charges; "
        "requests for refunds or premium adjustments; "
        "inquiries about late fees or collection notices"
    ),
    "Claims Disputes": (
        "Complaints about denied or underpaid claims; "
        "requests for reconsideration of claim decisions; "
        "inquiries about appealing a claim outcome"
    ),
    "Policy Comparisons": (
        "Questions about the differences between policy options; "
        "requests for help deciding between coverage levels; "
        "inquiries about how policies compare to competitors' offerings"
    ),
    "General Inquiries": (
        "Questions about company contact information or hours of operation; "
        "requests for general information about products or services; "
        "inquiries that don't fit neatly into other categories"
    ),
}

VALID_LABELS = frozenset(CATEGORY_CRITERIA)


def _make_question():
    """Return the Choice question dict for the ticket classification."""
    return {
        "category": {
            "type": "choice",
            "instructions": (
                "Which customer-support category does this ticket belong to?"
            ),
            "criteria": CATEGORY_CRITERIA,
        }
    }


def _validate_jev_response(body):
    """Validate essential fields of a parsed Jev JSON response.

    Returns (label, confidence, usage) on success, raises ValueError on
    any contract violation.
    """
    answers = body.get("answers", {})
    cat_answer = answers.get("category")
    if cat_answer is None:
        raise ValueError("missing 'category' answer")
    label = cat_answer.get("choice")
    if label not in VALID_LABELS:
        raise ValueError(f"unknown label: {label!r}")
    confidence = cat_answer.get("confidence")
    if not isinstance(confidence, (int, float)) or not math.isfinite(confidence):
        raise ValueError(f"confidence not finite: {confidence!r}")
    if not (0 <= confidence <= 1):
        raise ValueError(f"confidence out of range: {confidence}")
    usage = body.get("usage", {})
    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    if input_tokens is not None:
        if not isinstance(input_tokens, (int, float)) or not math.isfinite(input_tokens) or input_tokens < 0:
            raise ValueError(f"invalid input_tokens: {input_tokens!r}")
    if output_tokens is not None:
        if not isinstance(output_tokens, (int, float)) or not math.isfinite(output_tokens) or output_tokens < 0:
            raise ValueError(f"invalid output_tokens: {output_tokens!r}")
    model = body.get("model", "")
    return label, confidence, model


def classify_with_jev(ticket_text, original_fn):
    """Classify a ticket using Jev Choice, falling back to the original.

    Parameters
    ----------
    ticket_text : str
        The customer support ticket to classify.
    original_fn : callable
        The original classification function ``simple_classify`` to call
        when Jev is unavailable, low-confidence, or returns an error.

    Returns
    -------
    str
        The chosen category label.
    """
    api_key = os.getenv("TYPESAFE_API_KEY", "")
    if not api_key:
        logger.info("jev path=original reason=missing_key")
        return original_fn(ticket_text)

    try:
        import urllib.request
        import json

        payload = json.dumps({
            "model": JEV_MODEL,
            "state": ticket_text,
            "questions": _make_question(),
        }).encode()

        req = urllib.request.Request(
            "https://api.typesafe.ai/v1/systemone",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        start = time.monotonic()
        with urllib.request.urlopen(req, timeout=JEV_TIMEOUT_S) as resp:
            body = json.loads(resp.read())
        elapsed_ms = (time.monotonic() - start) * 1000

        label, confidence, model_id = _validate_jev_response(body)

        if confidence < CONFIDENCE_THRESHOLD:
            logger.info(
                "jev path=original reason=low_confidence "
                "confidence=%.4f threshold=%.2f model=%s",
                confidence, CONFIDENCE_THRESHOLD, model_id,
            )
            return original_fn(ticket_text)

        logger.info(
            "jev path=jev reason=accepted confidence=%.4f model=%s latency_ms=%.1f",
            confidence, model_id, elapsed_ms,
        )
        return label

    except Exception as exc:
        logger.info("jev path=original reason=error error=%s", exc)
        return original_fn(ticket_text)
