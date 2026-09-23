"""Jev decisions module — single source of truth for all Jev questions, model pins, and thresholds.

Uses the TypeSafe System One HTTP API via OpenRouter. No SDK dependency required.
"""

import json
import os
import sys
import urllib.request
import urllib.error

# ── Model pin ────────────────────────────────────────────────────────────────
JEV_MODEL = "typesafe/jev-1.13-20260917"

# ── Provider ─────────────────────────────────────────────────────────────────
JEV_BASE_URL = "https://openrouter.ai/api/v1/systemone"
JEV_KEY_ENV = "OPENROUTER_API_KEY"

# ── Confidence threshold for site S1 (workflow.py:83) ────────────────────────
# Initial conservative value; calibrate on representative data during parity.
CLASSIFY_THRESHOLD = 0.85

# ── Timeout (seconds) ────────────────────────────────────────────────────────
JEV_TIMEOUT = 10

# ── Choice question: insurance ticket classification ─────────────────────────
CLASSIFY_QUESTION = {
    "type": "choice",
    "instructions": "Which insurance support category does this customer ticket belong to?",
    "criteria": {
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
    },
}

# ── Valid labels (for response validation) ───────────────────────────────────
VALID_LABELS = set(CLASSIFY_QUESTION["criteria"].keys())


def classify_with_jev(ticket_text: str) -> str | None:
    """Attempt to classify a ticket using Jev Choice.

    Returns the label string on high confidence, or None on low confidence,
    missing credentials, network errors, timeouts, malformed responses,
    or unknown labels. Caller should fall back to the original path on None.
    """
    api_key = os.environ.get(JEV_KEY_ENV)
    if not api_key:
        _log("original", reason="missing_key")
        return None

    payload = json.dumps({
        "state": ticket_text,
        "model": JEV_MODEL,
        "questions": {
            "category": CLASSIFY_QUESTION,
        },
    }).encode("utf-8")

    req = urllib.request.Request(
        JEV_BASE_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=JEV_TIMEOUT) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        _log("original", reason=f"jev_error:{type(exc).__name__}")
        return None

    # Parse answer
    try:
        answer = body["answers"]["category"]
        label = answer["choice"]
        confidence = answer["confidence"]
        model_version = body.get("model", JEV_MODEL)
    except (KeyError, TypeError):
        _log("original", reason="malformed_response")
        return None

    # Validate confidence is a finite number
    if not isinstance(confidence, (int, float)) or confidence != confidence:  # NaN check
        _log("original", reason="nonfinite_confidence")
        return None

    # Validate label
    if label not in VALID_LABELS:
        _log("original", reason=f"unknown_label:{label}")
        return None

    # Gate on confidence
    if confidence < CLASSIFY_THRESHOLD:
        _log("original", reason=f"low_confidence:{confidence:.3f}", model=model_version)
        return None

    _log("jev", model=model_version, confidence=f"{confidence:.3f}")
    return label


def _log(path: str, *, model: str = "", reason: str = "", confidence: str = "") -> None:
    """Log decision path to stderr. Never logs keys, headers, or input content."""
    parts = [f"jev_decision_path={path}"]
    if model:
        parts.append(f"model={model}")
    if confidence:
        parts.append(f"confidence={confidence}")
    if reason:
        parts.append(f"reason={reason}")
    print(" ".join(parts), file=sys.stderr)
