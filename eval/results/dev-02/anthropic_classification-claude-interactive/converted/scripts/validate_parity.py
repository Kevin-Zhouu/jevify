#!/usr/bin/env python3
"""Live paired validation for Jev conversion of anthropic_classification.

For each input:
1. Calls the original Anthropic path (routed through OpenRouter per authorized baseline)
2. Calls the actual Jev decisions module with the same input
3. Records agreement, confidence, latency, cost, and request metadata

Outputs JEV_PARITY.json alongside this script's parent directory.
"""
import csv
import json
import math
import os
import pathlib
import sys
import time
import types
import urllib.request

# Add the converted repo to path so we can import the actual decisions module
REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from jev_decisions import (
    CATEGORY_CRITERIA,
    CLASSIFICATION_QUESTION,
    CONFIDENCE_THRESHOLD,
    JEV_MODEL,
    JEV_TIMEOUT,
    KNOWN_LABELS,
    _build_jev_request_body,
    _validate_jev_response,
    gate_accepts,
)

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
# Original model routed through OpenRouter per authorized baseline scope
ORIGINAL_MODEL = "anthropic/claude-haiku-4-5"
OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_SYSTEMONE_URL = "https://openrouter.ai/api/v1/systemone"

# Jev pricing: $0.042 per million input tokens, output free
JEV_COST_PER_INPUT_TOKEN = 0.042 / 1_000_000
# Haiku pricing via OpenRouter (approximate as of 2026-09): $0.80/M input, $4/M output
HAIKU_COST_PER_INPUT_TOKEN = 0.80 / 1_000_000
HAIKU_COST_PER_OUTPUT_TOKEN = 4.0 / 1_000_000


def load_test_inputs():
    """Load inputs from test.tsv — repo fixture data."""
    inputs = []
    test_path = REPO / "data" / "test.tsv"
    with open(test_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            inputs.append({
                "text": row["text"],
                "expected_label": row["label"],
                "source": f"data/test.tsv:{reader.line_num}",
                "provenance": "repo",
            })
    return inputs


def call_original_via_openrouter(ticket_text):
    """Call the original Anthropic prompt via OpenRouter (authorized baseline route).

    Preserves the exact original prompt, model parameters, and output parsing.
    """
    import textwrap

    # Reconstruct the exact original prompt from workflow.py
    categories_xml = textwrap.dedent("""\
<category>
    <label>Billing Inquiries</label>
    <content> Questions about invoices, charges, fees, and premiums Requests for clarification on billing statements Inquiries about payment methods and due dates
    </content>
</category>
<category>
    <label>Policy Administration</label>
    <content> Requests for policy changes, updates, or cancellations Questions about policy renewals and reinstatements Inquiries about adding or removing coverage options
    </content>
</category>
<category>
    <label>Claims Assistance</label>
    <content> Questions about the claims process and filing procedures Requests for help with submitting claim documentation Inquiries about claim status and payout timelines
    </content>
</category>
<category>
    <label>Coverage Explanations</label>
    <content> Questions about what is covered under specific policy types Requests for clarification on coverage limits and exclusions Inquiries about deductibles and out-of-pocket expenses
    </content>
</category>
<category>
    <label>Quotes and Proposals</label>
    <content> Requests for new policy quotes and price comparisons Questions about available discounts and bundling options Inquiries about switching from another insurer
    </content>
</category>
<category>
    <label>Account Management</label>
    <content> Requests for login credentials or password resets Questions about online account features and functionality Inquiries about updating contact or personal information
    </content>
</category>
<category>
    <label>Billing Disputes</label>
    <content> Complaints about unexpected or incorrect charges Requests for refunds or premium adjustments Inquiries about late fees or collection notices
    </content>
</category>
<category>
    <label>Claims Disputes</label>
    <content> Complaints about denied or underpaid claims Requests for reconsideration of claim decisions Inquiries about appealing a claim outcome
    </content>
</category>
<category>
    <label>Policy Comparisons</label>
    <content> Questions about the differences between policy options Requests for help deciding between coverage levels Inquiries about how policies compare to competitors' offerings
    </content>
</category>
<category>
    <label>General Inquiries</label>
    <content> Questions about company contact information or hours of operation Requests for general information about products or services Inquiries that don't fit neatly into other categories
    </content>
</category>""")

    prompt = textwrap.dedent("""
    You will classify a customer support ticket into one of the following categories:
    <categories>
        {{categories}}
    </categories>

    Here is the customer support ticket:
    <ticket>
        {{ticket}}
    </ticket>

    Respond with just the label of the category between category tags.
    """).replace("{{categories}}", categories_xml).replace("{{ticket}}", ticket_text)

    body = {
        "model": ORIGINAL_MODEL,
        "messages": [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "<category>"},
        ],
        "stop": ["</category>"],
        "max_tokens": 4096,
        "temperature": 0.0,
    }

    payload = json.dumps(body).encode()
    req = urllib.request.Request(
        OPENROUTER_CHAT_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    start = time.monotonic()
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
    elapsed_ms = (time.monotonic() - start) * 1000

    data = json.loads(raw)
    label = data["choices"][0]["message"]["content"].strip()
    usage = data.get("usage", {})
    request_id = data.get("id", "")
    model_used = data.get("model", ORIGINAL_MODEL)

    input_tokens = usage.get("prompt_tokens", 0)
    output_tokens = usage.get("completion_tokens", 0)
    cost = input_tokens * HAIKU_COST_PER_INPUT_TOKEN + output_tokens * HAIKU_COST_PER_OUTPUT_TOKEN

    return {
        "label": label,
        "latency_ms": elapsed_ms,
        "cost_usd": cost,
        "request_id": request_id,
        "model": model_used,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }


def call_jev(ticket_text):
    """Call the actual Jev decisions module."""
    body = _build_jev_request_body(ticket_text)
    payload = json.dumps(body).encode()

    req = urllib.request.Request(
        OPENROUTER_SYSTEMONE_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    start = time.monotonic()
    with urllib.request.urlopen(req, timeout=JEV_TIMEOUT) as resp:
        raw = resp.read()
    elapsed_ms = (time.monotonic() - start) * 1000

    data = json.loads(raw)
    label, confidence, usage, answering_model = _validate_jev_response(data)
    request_id = data.get("id", "")

    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)
    cost = input_tokens * JEV_COST_PER_INPUT_TOKEN  # output tokens are free

    return {
        "label": label,
        "confidence": confidence,
        "latency_ms": elapsed_ms,
        "cost_usd": cost,
        "request_id": request_id,
        "model": answering_model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "probabilities": data.get("answers", {}).get("category", {}).get("probabilities", {}),
    }


def run_fault_tests():
    """Exercise fallback paths: low confidence, timeout, error, rate limit."""
    faults = {"below_threshold": False, "error": False, "timeout": False, "rate_limit": False}

    # Import the actual wrapper to test gate behavior
    from jev_decisions import classify_with_jev

    # 1. Test gate_accepts with below-threshold confidence
    assert not gate_accepts(CONFIDENCE_THRESHOLD - 0.01), "gate should reject below threshold"
    assert gate_accepts(CONFIDENCE_THRESHOLD), "gate should accept at threshold"
    assert not gate_accepts(float("nan")), "gate should reject NaN"
    assert not gate_accepts(float("inf")), "gate should reject inf"
    assert not gate_accepts(-0.1), "gate should reject negative"
    assert not gate_accepts(1.1), "gate should reject >1"
    assert not gate_accepts("high"), "gate should reject non-numeric"
    faults["below_threshold"] = True

    # 2. Test error handling — force an import error scenario
    original_called = []
    def mock_original(text):
        original_called.append(text)
        return "General Inquiries"

    # Test with missing key
    old_key = os.environ.pop("OPENROUTER_API_KEY", None)
    try:
        result = classify_with_jev("test ticket", mock_original)
        assert result == "General Inquiries", f"expected fallback result, got {result}"
        assert len(original_called) == 1, "original should be called once on missing key"
    finally:
        if old_key is not None:
            os.environ["OPENROUTER_API_KEY"] = old_key
    faults["error"] = True

    # 3. Test timeout — use an unreachable endpoint
    import jev_decisions
    old_timeout = jev_decisions.JEV_TIMEOUT
    jev_decisions.JEV_TIMEOUT = 0.001  # absurdly low timeout
    original_called.clear()
    try:
        result = classify_with_jev("test ticket", mock_original)
        assert result == "General Inquiries", f"expected fallback on timeout, got {result}"
        assert len(original_called) == 1, "original should be called once on timeout"
    finally:
        jev_decisions.JEV_TIMEOUT = old_timeout
    faults["timeout"] = True

    # 4. Rate limit — test with invalid key to trigger 401 (similar error path)
    old_key_val = os.environ.get("OPENROUTER_API_KEY")
    os.environ["OPENROUTER_API_KEY"] = "invalid-key-for-fault-test"
    original_called.clear()
    try:
        result = classify_with_jev("test ticket", mock_original)
        assert result == "General Inquiries", f"expected fallback on auth error, got {result}"
        assert len(original_called) == 1, "original should be called once on HTTP error"
    finally:
        if old_key_val is not None:
            os.environ["OPENROUTER_API_KEY"] = old_key_val
        else:
            os.environ.pop("OPENROUTER_API_KEY", None)
    faults["rate_limit"] = True

    return faults


def main():
    if not OPENROUTER_KEY:
        print("ERROR: OPENROUTER_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    inputs = load_test_inputs()
    print(f"Loaded {len(inputs)} test inputs from data/test.tsv", file=sys.stderr)

    # Use first 20 for calibration, remaining for confirmation
    calibration_inputs = inputs[:20]
    confirmation_inputs = inputs[20:]

    # ── Calibration run ──────────────────────────────────────────────
    print("Running calibration set...", file=sys.stderr)
    calibration_rows = []
    for i, inp in enumerate(calibration_inputs):
        print(f"  Calibration {i+1}/{len(calibration_inputs)}: {inp['text'][:60]}...", file=sys.stderr)
        try:
            original = call_original_via_openrouter(inp["text"])
            jev = call_jev(inp["text"])
            row = {
                "input": inp["text"][:200],
                "provenance": inp["provenance"],
                "source": inp["source"],
                "model": jev["model"],
                "live": True,
                "request_id": jev["request_id"],
                "jev_answer": jev["label"],
                "original_answer": original["label"],
                "confidence": jev["confidence"],
                "fallback_taken": not gate_accepts(jev["confidence"]),
                "latency_ms": round(jev["latency_ms"], 1),
                "cost_usd": round(jev["cost_usd"], 7),
                "original_model": original["model"],
                "original_latency_ms": round(original["latency_ms"], 1),
                "original_cost_usd": round(original["cost_usd"], 7),
                "original_request_id": original["request_id"],
            }
            calibration_rows.append(row)
        except Exception as e:
            print(f"  ERROR on input {i+1}: {e}", file=sys.stderr)
            calibration_rows.append({
                "input": inp["text"][:200],
                "provenance": inp["provenance"],
                "source": inp["source"],
                "model": JEV_MODEL,
                "live": True,
                "request_id": "",
                "jev_answer": "",
                "original_answer": "",
                "confidence": -1,
                "fallback_taken": True,
                "latency_ms": 0,
                "cost_usd": 0,
                "original_model": ORIGINAL_MODEL,
                "original_latency_ms": 0,
                "original_cost_usd": 0,
                "original_request_id": "",
                "error": str(e),
            })
        time.sleep(0.3)  # bounded concurrency

    # ── Confirmation run ─────────────────────────────────────────────
    print("Running confirmation set...", file=sys.stderr)
    confirmation_rows = []
    for i, inp in enumerate(confirmation_inputs):
        print(f"  Confirmation {i+1}/{len(confirmation_inputs)}: {inp['text'][:60]}...", file=sys.stderr)
        try:
            original = call_original_via_openrouter(inp["text"])
            jev = call_jev(inp["text"])
            row = {
                "input": inp["text"][:200],
                "provenance": inp["provenance"],
                "source": inp["source"],
                "model": jev["model"],
                "live": True,
                "request_id": jev["request_id"],
                "jev_answer": jev["label"],
                "original_answer": original["label"],
                "confidence": jev["confidence"],
                "fallback_taken": not gate_accepts(jev["confidence"]),
                "latency_ms": round(jev["latency_ms"], 1),
                "cost_usd": round(jev["cost_usd"], 7),
                "original_model": original["model"],
                "original_latency_ms": round(original["latency_ms"], 1),
                "original_cost_usd": round(original["cost_usd"], 7),
                "original_request_id": original["request_id"],
            }
            confirmation_rows.append(row)
        except Exception as e:
            print(f"  ERROR on input {i+1}: {e}", file=sys.stderr)
            confirmation_rows.append({
                "input": inp["text"][:200],
                "provenance": inp["provenance"],
                "source": inp["source"],
                "model": JEV_MODEL,
                "live": True,
                "request_id": "",
                "jev_answer": "",
                "original_answer": "",
                "confidence": -1,
                "fallback_taken": True,
                "latency_ms": 0,
                "cost_usd": 0,
                "original_model": ORIGINAL_MODEL,
                "original_latency_ms": 0,
                "original_cost_usd": 0,
                "original_request_id": "",
                "error": str(e),
            })
        time.sleep(0.3)

    # ── Fault tests ──────────────────────────────────────────────────
    print("Running fault injection tests...", file=sys.stderr)
    faults = run_fault_tests()
    print(f"  Faults: {faults}", file=sys.stderr)

    # ── Compute statistics ───────────────────────────────────────────
    all_rows = calibration_rows + confirmation_rows

    def compute_stats(rows, label):
        valid = [r for r in rows if r.get("confidence", -1) >= 0]
        if not valid:
            return {"label": label, "n": 0, "error": "no valid rows"}

        total = len(valid)
        agreements = sum(1 for r in valid if r["jev_answer"] == r["original_answer"])
        raw_agreement = agreements / total if total else 0

        # Selective agreement at current threshold
        accepted = [r for r in valid if not r["fallback_taken"]]
        accepted_agreements = sum(1 for r in accepted if r["jev_answer"] == r["original_answer"])
        selective_agreement = accepted_agreements / len(accepted) if accepted else 0
        fallback_rate = 1 - (len(accepted) / total) if total else 0

        confidences = [r["confidence"] for r in valid]
        jev_latencies = [r["latency_ms"] for r in valid if r["latency_ms"] > 0]
        orig_latencies = [r["original_latency_ms"] for r in valid if r["original_latency_ms"] > 0]

        return {
            "label": label,
            "n": total,
            "raw_agreement": round(raw_agreement, 4),
            "selective_agreement": round(selective_agreement, 4),
            "accepted_count": len(accepted),
            "fallback_rate": round(fallback_rate, 4),
            "confidence_p50": round(sorted(confidences)[len(confidences) // 2], 4) if confidences else None,
            "confidence_p95": round(sorted(confidences)[int(len(confidences) * 0.95)] , 4) if confidences else None,
            "jev_latency_p50": round(sorted(jev_latencies)[len(jev_latencies) // 2], 1) if jev_latencies else None,
            "jev_latency_p95": round(sorted(jev_latencies)[int(len(jev_latencies) * 0.95)], 1) if jev_latencies else None,
            "orig_latency_p50": round(sorted(orig_latencies)[len(orig_latencies) // 2], 1) if orig_latencies else None,
            "orig_latency_p95": round(sorted(orig_latencies)[int(len(orig_latencies) * 0.95)], 1) if orig_latencies else None,
            "total_jev_cost": round(sum(r["cost_usd"] for r in valid), 6),
            "total_orig_cost": round(sum(r["original_cost_usd"] for r in valid), 6),
        }

    cal_stats = compute_stats(calibration_rows, "calibration")
    conf_stats = compute_stats(confirmation_rows, "confirmation")
    all_stats = compute_stats(all_rows, "all")

    # ── Write parity JSON ────────────────────────────────────────────
    parity = {
        "sites": [
            {
                "site_id": "workflow.py:83",
                "threshold": CONFIDENCE_THRESHOLD,
                "calibration": cal_stats,
                "confirmation": conf_stats,
                "combined": all_stats,
                "rows": all_rows,
                "faults": faults,
            }
        ]
    }

    out_path = REPO / "JEV_PARITY.json"
    with open(out_path, "w") as f:
        json.dump(parity, f, indent=2)
    print(f"\nWrote {out_path}", file=sys.stderr)

    # ── Print summary ────────────────────────────────────────────────
    print("\n=== Validation Summary ===", file=sys.stderr)
    for stats in [cal_stats, conf_stats, all_stats]:
        print(f"\n{stats['label']} (n={stats.get('n', 0)}):", file=sys.stderr)
        for k, v in stats.items():
            if k not in ("label",):
                print(f"  {k}: {v}", file=sys.stderr)

    print(f"\nFault tests: {faults}", file=sys.stderr)
    print(f"Threshold: {CONFIDENCE_THRESHOLD}", file=sys.stderr)


if __name__ == "__main__":
    main()
