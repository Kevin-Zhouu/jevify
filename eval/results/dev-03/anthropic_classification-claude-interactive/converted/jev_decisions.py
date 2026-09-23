"""Jev decisions module — all model IDs, questions, thresholds and gate policy.

Converted site: workflow.py:83 (simple_classify)
Primitive: Choice (10 insurance categories)
Provider: OpenRouter
Risk posture: Conservative (fallback always retained)
"""
import json
import logging
import math
import os
import sys
import time
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

# ── Model and provider ──────────────────────────────────────────────────────
JEV_MODEL = "typesafe/jev-1.13-20260917"
JEV_BASE_URL = "https://openrouter.ai/api/v1/systemone"
JEV_KEY_ENV = "OPENROUTER_API_KEY"
JEV_TIMEOUT_S = 10

# ── Confidence threshold ────────────────────────────────────────────────────
# Conservative starting point; tune on representative data.
CLASSIFY_CONFIDENCE_THRESHOLD = 0.6

# ── Category definitions (shared with workflow.py) ──────────────────────────
CATEGORY_CRITERIA = {
    "Billing Inquiries": "Questions about invoices, charges, fees, and premiums. Requests for clarification on billing statements. Inquiries about payment methods and due dates.",
    "Policy Administration": "Requests for policy changes, updates, or cancellations. Questions about policy renewals and reinstatements. Inquiries about adding or removing coverage options.",
    "Claims Assistance": "Questions about the claims process and filing procedures. Requests for help with submitting claim documentation. Inquiries about claim status and payout timelines.",
    "Coverage Explanations": "Questions about what is covered under specific policy types. Requests for clarification on coverage limits and exclusions. Inquiries about deductibles and out-of-pocket expenses.",
    "Quotes and Proposals": "Requests for new policy quotes and price comparisons. Questions about available discounts and bundling options. Inquiries about switching from another insurer.",
    "Account Management": "Requests for login credentials or password resets. Questions about online account features and functionality. Inquiries about updating contact or personal information.",
    "Billing Disputes": "Complaints about unexpected or incorrect charges. Requests for refunds or premium adjustments. Inquiries about late fees or collection notices.",
    "Claims Disputes": "Complaints about denied or underpaid claims. Requests for reconsideration of claim decisions. Inquiries about appealing a claim outcome.",
    "Policy Comparisons": "Questions about the differences between policy options. Requests for help deciding between coverage levels. Inquiries about how policies compare to competitors' offerings.",
    "General Inquiries": "Questions about company contact information or hours of operation. Requests for general information about products or services. Inquiries that don't fit neatly into other categories.",
}

VALID_CATEGORIES = set(CATEGORY_CRITERIA.keys())

# ── Choice question ─────────────────────────────────────────────────────────
CLASSIFY_QUESTION = {
    "category": {
        "type": "choice",
        "instructions": "Which insurance support category does this customer ticket belong to?",
        "criteria": CATEGORY_CRITERIA,
    }
}


def _log(*, path, model, reason):
    """Log answer path on every call. Never logs keys or raw input."""
    print(
        json.dumps({"jev_decision": path, "model": model, "reason": reason}),
        file=sys.stderr,
    )


def evaluate_classify(ticket_text):
    """Try Jev Choice for classification. Returns (label, accepted) or (None, False).

    On acceptance, returns the category label string and True.
    On rejection or error, returns None and False — caller must invoke original.
    """
    api_key = os.environ.get(JEV_KEY_ENV)
    if not api_key:
        _log(path="original", model="claude-haiku-4-5", reason="missing_key")
        return None, False

    request_body = json.dumps({
        "state": ticket_text,
        "model": JEV_MODEL,
        "questions": CLASSIFY_QUESTION,
    }).encode()

    req = urllib.request.Request(
        JEV_BASE_URL,
        data=request_body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/jevify-eval",
        },
        method="POST",
    )

    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=JEV_TIMEOUT_S) as resp:
            raw = resp.read()
        elapsed_ms = (time.monotonic() - start) * 1000
    except urllib.error.HTTPError as exc:
        elapsed_ms = (time.monotonic() - start) * 1000
        if exc.code == 429:
            _log(path="original", model="claude-haiku-4-5", reason="rate_limit")
        else:
            _log(path="original", model="claude-haiku-4-5", reason=f"http_{exc.code}")
        return None, False
    except (urllib.error.URLError, TimeoutError, OSError):
        _log(path="original", model="claude-haiku-4-5", reason="timeout_or_network")
        return None, False

    # Parse and validate response
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        _log(path="original", model="claude-haiku-4-5", reason="malformed_response")
        return None, False

    if not isinstance(data, dict):
        _log(path="original", model="claude-haiku-4-5", reason="malformed_response")
        return None, False

    # Validate model matches pin
    resp_model = data.get("model")
    if not isinstance(resp_model, str) or "jev" not in resp_model.lower():
        _log(path="original", model="claude-haiku-4-5", reason="model_mismatch")
        return None, False

    # Validate answers structure
    answers = data.get("answers")
    if not isinstance(answers, dict):
        _log(path="original", model="claude-haiku-4-5", reason="malformed_response")
        return None, False

    cat_answer = answers.get("category")
    if not isinstance(cat_answer, dict):
        _log(path="original", model="claude-haiku-4-5", reason="malformed_response")
        return None, False

    # Validate primitive type
    if cat_answer.get("type") != "choice":
        _log(path="original", model="claude-haiku-4-5", reason="wrong_primitive")
        return None, False

    # Validate label
    label = cat_answer.get("choice")
    if not isinstance(label, str) or label not in VALID_CATEGORIES:
        _log(path="original", model="claude-haiku-4-5", reason="unknown_label")
        return None, False

    # Validate confidence: must be finite float in [0,1], not bool
    confidence = cat_answer.get("confidence")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        _log(path="original", model="claude-haiku-4-5", reason="invalid_confidence")
        return None, False
    if not math.isfinite(confidence) or confidence < 0 or confidence > 1:
        _log(path="original", model="claude-haiku-4-5", reason="invalid_confidence")
        return None, False

    # Validate usage
    usage = data.get("usage")
    if isinstance(usage, dict):
        for tok_key in ("input_tokens", "output_tokens"):
            tok_val = usage.get(tok_key)
            if tok_val is not None:
                if isinstance(tok_val, bool) or not isinstance(tok_val, (int, float)):
                    _log(path="original", model="claude-haiku-4-5", reason="invalid_usage")
                    return None, False
                if not math.isfinite(tok_val) or tok_val < 0:
                    _log(path="original", model="claude-haiku-4-5", reason="invalid_usage")
                    return None, False
    elif usage is not None:
        # usage is present but not a dict — fall back
        _log(path="original", model="claude-haiku-4-5", reason="invalid_usage")
        return None, False

    # Confidence gate
    if confidence < CLASSIFY_CONFIDENCE_THRESHOLD:
        _log(
            path="original",
            model="claude-haiku-4-5",
            reason="low_confidence",
            )
        return None, False

    # Accepted
    _log(path="jev", model=resp_model, reason="accepted")
    return label, True
