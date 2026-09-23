"""Single decisions module for all Jev model IDs, questions, criteria, thresholds and gate policy."""

import logging
import os
import time

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model pin
# ---------------------------------------------------------------------------
JEV_MODEL = "jev-1.13.0"

# ---------------------------------------------------------------------------
# Confidence threshold (conservative)
# ---------------------------------------------------------------------------
CONFIDENCE_THRESHOLD = 0.7

# ---------------------------------------------------------------------------
# Question: ticket classification
# ---------------------------------------------------------------------------
CATEGORY_CRITERIA = {
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
}

VALID_LABELS = frozenset(CATEGORY_CRITERIA.keys())

CLASSIFICATION_INSTRUCTIONS = "Which insurance support category best matches this customer support ticket?"

# ---------------------------------------------------------------------------
# Jev timeout (seconds)
# ---------------------------------------------------------------------------
JEV_TIMEOUT = 10.0


def classify_ticket(ticket_text, original_fn):
    """Try Jev classification; fall back to original_fn(ticket_text) on rejection/error/missing key.

    Returns the category label string (same contract as the original).
    """
    accepted = None

    try:
        api_key = os.environ.get("TYPESAFE_API_KEY")
        if not api_key:
            logger.info(
                "jev_decisions: path=original, reason=missing_key, model=%s",
                "claude-haiku-4-5",
            )
            return original_fn(ticket_text)

        from typesafe_sdk import Choice, TypeSafeClient  # noqa: E402

        start = time.monotonic()
        with TypeSafeClient(
            api_key=api_key,
            timeout=JEV_TIMEOUT,
            max_retries=0,
        ) as client:
            response = client.system_one(
                state=ticket_text,
                questions={
                    "category": Choice(
                        instructions=CLASSIFICATION_INSTRUCTIONS,
                        criteria=CATEGORY_CRITERIA,
                    ),
                },
                model=JEV_MODEL,
            )
        elapsed_ms = (time.monotonic() - start) * 1000

        answer = response.choices["category"]

        # Validate confidence
        conf = answer.confidence
        if not isinstance(conf, (int, float)) or isinstance(conf, bool):
            logger.info(
                "jev_decisions: path=original, reason=invalid_confidence, jev_model=%s, model=%s",
                JEV_MODEL,
                "claude-haiku-4-5",
            )
            return original_fn(ticket_text)

        if not (0.0 <= conf <= 1.0):
            logger.info(
                "jev_decisions: path=original, reason=confidence_out_of_range, jev_model=%s, model=%s",
                JEV_MODEL,
                "claude-haiku-4-5",
            )
            return original_fn(ticket_text)

        # Validate label
        label = answer.choice
        if label not in VALID_LABELS:
            logger.info(
                "jev_decisions: path=original, reason=unknown_label, jev_model=%s, model=%s",
                JEV_MODEL,
                "claude-haiku-4-5",
            )
            return original_fn(ticket_text)

        # Validate model
        if response.model != JEV_MODEL:
            logger.info(
                "jev_decisions: path=original, reason=model_mismatch, jev_model=%s, model=%s",
                JEV_MODEL,
                "claude-haiku-4-5",
            )
            return original_fn(ticket_text)

        # Validate usage
        usage = response.usage
        if usage is not None:
            inp = getattr(usage, "input_tokens", None)
            out = getattr(usage, "output_tokens", None)
            if inp is not None and (not isinstance(inp, (int, float)) or isinstance(inp, bool) or inp < 0 or not _isfinite(inp)):
                logger.info(
                    "jev_decisions: path=original, reason=invalid_usage, jev_model=%s, model=%s",
                    JEV_MODEL,
                    "claude-haiku-4-5",
                )
                return original_fn(ticket_text)
            if out is not None and (not isinstance(out, (int, float)) or isinstance(out, bool) or out < 0 or not _isfinite(out)):
                logger.info(
                    "jev_decisions: path=original, reason=invalid_usage, jev_model=%s, model=%s",
                    JEV_MODEL,
                    "claude-haiku-4-5",
                )
                return original_fn(ticket_text)

        # Confidence gate
        if conf < CONFIDENCE_THRESHOLD:
            logger.info(
                "jev_decisions: path=original, reason=low_confidence, confidence=%.4f, threshold=%.2f, jev_model=%s, model=%s",
                conf,
                CONFIDENCE_THRESHOLD,
                JEV_MODEL,
                "claude-haiku-4-5",
            )
            return original_fn(ticket_text)

        # Accept
        accepted = label
        logger.info(
            "jev_decisions: path=jev, reason=accepted, label=%s, confidence=%.4f, latency_ms=%.1f, jev_model=%s",
            label,
            conf,
            elapsed_ms,
            JEV_MODEL,
        )

    except Exception as exc:
        reason = "timeout" if "timeout" in type(exc).__name__.lower() or "timed out" in str(exc).lower() else "error"
        logger.info(
            "jev_decisions: path=original, reason=%s, jev_model=%s, model=%s",
            reason,
            JEV_MODEL,
            "claude-haiku-4-5",
        )

    if accepted is not None:
        return accepted

    return original_fn(ticket_text)


def _isfinite(v):
    """Check if a numeric value is finite."""
    import math
    return math.isfinite(v)
