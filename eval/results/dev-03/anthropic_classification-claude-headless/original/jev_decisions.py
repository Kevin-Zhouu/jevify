"""Jev decisions module — all model pins, questions, criteria, thresholds and gate logic."""

import json
import logging
import math
import os
import sys
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model and provider configuration
# ---------------------------------------------------------------------------
JEV_MODEL = "typesafe/jev-1.13-20260917"
JEV_ENDPOINT = "https://openrouter.ai/api/v1/systemone"
JEV_KEY_ENV = "OPENROUTER_API_KEY"
JEV_TIMEOUT_SECONDS = 15

# ---------------------------------------------------------------------------
# Confidence threshold (conservative)
# ---------------------------------------------------------------------------
CONFIDENCE_THRESHOLD = 0.95

# ---------------------------------------------------------------------------
# Category question — mirrors the 10 insurance categories from workflow.py
# ---------------------------------------------------------------------------
CATEGORY_CRITERIA = {
    "billing_inquiries": "Questions about invoices, charges, fees, and premiums. Requests for clarification on billing statements. Inquiries about payment methods and due dates.",
    "policy_administration": "Requests for policy changes, updates, or cancellations. Questions about policy renewals and reinstatements. Inquiries about adding or removing coverage options.",
    "claims_assistance": "Questions about the claims process and filing procedures. Requests for help with submitting claim documentation. Inquiries about claim status and payout timelines.",
    "coverage_explanations": "Questions about what is covered under specific policy types. Requests for clarification on coverage limits and exclusions. Inquiries about deductibles and out-of-pocket expenses.",
    "quotes_and_proposals": "Requests for new policy quotes and price comparisons. Questions about available discounts and bundling options. Inquiries about switching from another insurer.",
    "account_management": "Requests for login credentials or password resets. Questions about online account features and functionality. Inquiries about updating contact or personal information.",
    "billing_disputes": "Complaints about unexpected or incorrect charges. Requests for refunds or premium adjustments. Inquiries about late fees or collection notices.",
    "claims_disputes": "Complaints about denied or underpaid claims. Requests for reconsideration of claim decisions. Inquiries about appealing a claim outcome.",
    "policy_comparisons": "Questions about the differences between policy options. Requests for help deciding between coverage levels. Inquiries about how policies compare to competitors' offerings.",
    "general_inquiries": "Questions about company contact information or hours of operation. Requests for general information about products or services. Inquiries that don't fit neatly into other categories.",
}

# Map Jev option keys back to the original label strings returned by the workflow
JEV_KEY_TO_LABEL = {
    "billing_inquiries": "Billing Inquiries",
    "policy_administration": "Policy Administration",
    "claims_assistance": "Claims Assistance",
    "coverage_explanations": "Coverage Explanations",
    "quotes_and_proposals": "Quotes and Proposals",
    "account_management": "Account Management",
    "billing_disputes": "Billing Disputes",
    "claims_disputes": "Claims Disputes",
    "policy_comparisons": "Policy Comparisons",
    "general_inquiries": "General Inquiries",
}

CATEGORY_QUESTION = {
    "category": {
        "type": "choice",
        "instructions": "Which insurance customer support category does this ticket belong to?",
        "criteria": CATEGORY_CRITERIA,
    }
}

# All valid Jev option keys
VALID_OPTIONS = set(CATEGORY_CRITERIA.keys())


def _get_key():
    """Return the API key or None if not set."""
    return os.environ.get(JEV_KEY_ENV)


def evaluate_category(ticket_text: str):
    """Call Jev via OpenRouter and return (label, confidence, raw_response_body) or raise."""
    key = _get_key()
    if not key:
        raise RuntimeError("missing_key")

    payload = json.dumps({
        "state": ticket_text,
        "model": JEV_MODEL,
        "questions": CATEGORY_QUESTION,
    }).encode()

    req = urllib.request.Request(
        JEV_ENDPOINT,
        data=payload,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=JEV_TIMEOUT_SECONDS) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            raise RuntimeError("rate_limit") from exc
        raise

    # Validate response structure
    if not isinstance(body, dict):
        raise RuntimeError("malformed_response")

    # Validate model matches pin (accept both direct and OpenRouter IDs)
    resp_model = body.get("model")
    accepted_models = {"jev-1.13.0", JEV_MODEL}
    if not isinstance(resp_model, str) or resp_model not in accepted_models:
        raise RuntimeError("model_mismatch")

    answers = body.get("answers")
    if not isinstance(answers, dict):
        raise RuntimeError("malformed_response")

    cat_answer = answers.get("category")
    if not isinstance(cat_answer, dict):
        raise RuntimeError("malformed_response")

    choice = cat_answer.get("choice")
    if not isinstance(choice, str) or choice not in VALID_OPTIONS:
        raise RuntimeError("unknown_label")

    confidence = cat_answer.get("confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        raise RuntimeError("invalid_confidence")
    if not math.isfinite(confidence) or not (0.0 <= confidence <= 1.0):
        raise RuntimeError("invalid_confidence")

    # Validate usage if present
    usage = body.get("usage")
    if isinstance(usage, dict):
        for tok_field in ("input_tokens", "output_tokens"):
            tok_val = usage.get(tok_field)
            if tok_val is not None:
                if not isinstance(tok_val, (int, float)) or isinstance(tok_val, bool):
                    raise RuntimeError("invalid_usage")
                if not math.isfinite(tok_val) or tok_val < 0:
                    raise RuntimeError("invalid_usage")
    elif usage is not None and not isinstance(usage, dict):
        raise RuntimeError("malformed_response")

    label = JEV_KEY_TO_LABEL[choice]
    return label, confidence, body


def gate(confidence: float) -> bool:
    """Return True if confidence meets the threshold for acceptance."""
    return confidence >= CONFIDENCE_THRESHOLD
