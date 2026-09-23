"""Jev decisions module for customer support ticket classification.

All Jev model IDs, question definitions, criteria, thresholds,
and gate logic live here. Call sites supply runtime state and the
original callable.
"""
import logging
import math
import os
import sys
import time

logger = logging.getLogger(__name__)

# ── Model pin ────────────────────────────────────────────────────────
JEV_MODEL = "typesafe/jev-1.13-20260917"  # OpenRouter dated pin

# ── Confidence threshold ─────────────────────────────────────────────
# Calibrated during validation; inputs below this fall back to original.
CONFIDENCE_THRESHOLD = 0.80

# ── Jev timeout (seconds) ───────────────────────────────────────────
JEV_TIMEOUT = 10.0

# ── Category criteria ────────────────────────────────────────────────
# Structured what/not_for to disambiguate overlapping categories.
CATEGORY_CRITERIA = {
    "Billing Inquiries": {
        "what": "Questions about invoices, charges, fees, and premiums; requests for clarification on billing statements; inquiries about payment methods and due dates",
        "not_for": "Complaints about unexpected or incorrect charges (use Billing Disputes)",
    },
    "Policy Administration": {
        "what": "Requests for policy changes, updates, or cancellations; questions about policy renewals and reinstatements; inquiries about adding or removing coverage options",
        "not_for": "Questions about what is covered (use Coverage Explanations) or comparing policies (use Policy Comparisons)",
    },
    "Claims Assistance": {
        "what": "Questions about the claims process and filing procedures; requests for help with submitting claim documentation; inquiries about claim status and payout timelines",
        "not_for": "Complaints about denied or underpaid claims (use Claims Disputes)",
    },
    "Coverage Explanations": {
        "what": "Questions about what is covered under specific policy types; requests for clarification on coverage limits and exclusions; inquiries about deductibles and out-of-pocket expenses",
        "not_for": "Requests for policy changes (use Policy Administration) or price comparisons (use Quotes and Proposals)",
    },
    "Quotes and Proposals": {
        "what": "Requests for new policy quotes and price comparisons; questions about available discounts and bundling options; inquiries about switching from another insurer",
        "not_for": "Questions about existing coverage details (use Coverage Explanations)",
    },
    "Account Management": {
        "what": "Requests for login credentials or password resets; questions about online account features and functionality; inquiries about updating contact or personal information",
        "not_for": "Billing or policy questions (use the relevant specific category)",
    },
    "Billing Disputes": {
        "what": "Complaints about unexpected or incorrect charges; requests for refunds or premium adjustments; inquiries about late fees or collection notices",
        "not_for": "General billing questions without a complaint (use Billing Inquiries)",
    },
    "Claims Disputes": {
        "what": "Complaints about denied or underpaid claims; requests for reconsideration of claim decisions; inquiries about appealing a claim outcome",
        "not_for": "Questions about how to file a claim (use Claims Assistance)",
    },
    "Policy Comparisons": {
        "what": "Questions about the differences between policy options; requests for help deciding between coverage levels; inquiries about how policies compare to competitors' offerings",
        "not_for": "Requests for new quotes (use Quotes and Proposals)",
    },
    "General Inquiries": {
        "what": "Questions about company contact information or hours of operation; requests for general information about products or services; inquiries that don't fit neatly into other categories",
        "not_for": "Any ticket that clearly belongs to a specific category above",
    },
}

# Known labels for validation
KNOWN_LABELS = frozenset(CATEGORY_CRITERIA.keys())

# ── Question definition ─────────────────────────────────────────────
CLASSIFICATION_QUESTION = {
    "category": {
        "type": "choice",
        "instructions": "Which customer support category does this ticket belong to?",
        "criteria": CATEGORY_CRITERIA,
    }
}


def _build_jev_request_body(ticket_text: str) -> dict:
    """Build the System One API request body."""
    return {
        "state": {"ticket": ticket_text},
        "model": JEV_MODEL,
        "questions": CLASSIFICATION_QUESTION,
    }


def gate_accepts(confidence: float) -> bool:
    """Pure confidence gate predicate."""
    if not isinstance(confidence, (int, float)):
        return False
    if not math.isfinite(confidence):
        return False
    if not (0 <= confidence <= 1):
        return False
    return confidence >= CONFIDENCE_THRESHOLD


def _validate_jev_response(data: dict) -> tuple:
    """Validate Jev response fields. Returns (label, confidence, usage, model) or raises ValueError."""
    if not isinstance(data, dict):
        raise ValueError("response is not a dict")

    model = data.get("model")
    answers = data.get("answers")
    if not isinstance(answers, dict):
        raise ValueError("missing answers")

    category = answers.get("category")
    if not isinstance(category, dict):
        raise ValueError("missing category answer")

    label = category.get("choice")
    if not isinstance(label, str) or label not in KNOWN_LABELS:
        raise ValueError(f"unknown label: {label!r}")

    confidence = category.get("confidence")
    if not isinstance(confidence, (int, float)) or not math.isfinite(confidence):
        raise ValueError(f"invalid confidence: {confidence!r}")
    if not (0 <= confidence <= 1):
        raise ValueError(f"confidence out of range: {confidence}")

    usage = data.get("usage", {})
    if isinstance(usage, dict):
        for field in ("input_tokens", "output_tokens"):
            val = usage.get(field)
            if val is not None and (not isinstance(val, (int, float)) or not math.isfinite(val) or val < 0):
                raise ValueError(f"invalid usage.{field}: {val!r}")
    else:
        usage = {}

    return label, confidence, usage, model


def classify_with_jev(ticket_text: str, original_fn) -> str:
    """Try Jev Choice classification; fall back to original_fn on any issue.

    Args:
        ticket_text: The customer support ticket text.
        original_fn: The original classification callable (takes ticket text, returns label str).

    Returns:
        The classification label string.
    """
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        logger.info("jev path=original reason=missing_key")
        return original_fn(ticket_text)

    try:
        # Lazy import to avoid blocking fallback when package is missing
        import urllib.request
        import json as _json

        body = _build_jev_request_body(ticket_text)
        payload = _json.dumps(body).encode()

        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/systemone",
            data=payload,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        start = time.monotonic()
        with urllib.request.urlopen(req, timeout=JEV_TIMEOUT) as resp:
            raw = resp.read()
        elapsed_ms = (time.monotonic() - start) * 1000

        data = _json.loads(raw)
        label, confidence, usage, answering_model = _validate_jev_response(data)

        if gate_accepts(confidence):
            logger.info(
                "jev path=jev model=%s confidence=%.3f latency_ms=%.1f",
                answering_model, confidence, elapsed_ms,
            )
            return label
        else:
            logger.info(
                "jev path=original reason=low_confidence confidence=%.3f model=%s",
                confidence, answering_model,
            )
            return original_fn(ticket_text)

    except Exception as e:
        reason = type(e).__name__
        logger.info("jev path=original reason=%s", reason)
        return original_fn(ticket_text)
