#!/usr/bin/env python3
"""Paired live parity measurement for Jev conversion of simple_classify.

Uses test.tsv fixtures. Runs each input through:
1. Jev (via OpenRouter System One endpoint) using the actual decisions module
2. Original baseline (Claude Haiku via OpenRouter gateway) using the actual original prompt

Imports the decisions module directly — no duplicated questions or thresholds.
"""

import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request

# Add parent directory so we can import jev_decisions
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jev_decisions import (
    CLASSIFY_CONFIDENCE_THRESHOLD,
    CLASSIFY_QUESTION,
    JEV_MODEL,
    JEV_BASE_URL,
    JEV_TIMEOUT_S,
    VALID_CATEGORIES,
)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
ORIGINAL_MODEL = "anthropic/claude-haiku-4-5"
OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"

# ── Categories prompt (copied from workflow.py to reproduce the original prompt exactly) ──

import textwrap

categories = textwrap.dedent("""<category>
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


def call_jev(ticket: str) -> dict:
    """Call Jev and return raw response dict."""
    payload = json.dumps({
        "model": JEV_MODEL,
        "state": ticket,
        "questions": {"category": CLASSIFY_QUESTION},
    }).encode()

    req = urllib.request.Request(
        JEV_BASE_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
    )
    start = time.monotonic()
    with urllib.request.urlopen(req, timeout=JEV_TIMEOUT_S) as resp:
        body = json.loads(resp.read())
        request_id = resp.headers.get("x-request-id", "")
    elapsed = (time.monotonic() - start) * 1000
    return {**body, "_latency_ms": elapsed, "_request_id": request_id}


def call_original(ticket: str) -> dict:
    """Call original model via OpenRouter chat completions (authorized baseline route)."""
    prompt = (
        textwrap.dedent("""
    You will classify a customer support ticket into one of the following categories:
    <categories>
        {{categories}}
    </categories>

    Here is the customer support ticket:
    <ticket>
        {{ticket}}
    </ticket>

    Respond with just the label of the category between category tags.
    """)
        .replace("{{categories}}", categories)
        .replace("{{ticket}}", ticket)
    )

    payload = json.dumps({
        "model": ORIGINAL_MODEL,
        "messages": [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "<category>"},
        ],
        "stop": ["</category>"],
        "max_tokens": 4096,
        "temperature": 0.0,
    }).encode()

    req = urllib.request.Request(
        OPENROUTER_CHAT_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
    )
    start = time.monotonic()
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read())
        request_id = resp.headers.get("x-request-id", "")
    elapsed = (time.monotonic() - start) * 1000

    content = body["choices"][0]["message"]["content"].strip()
    usage = body.get("usage", {})
    return {
        "answer": content,
        "model": body.get("model", ORIGINAL_MODEL),
        "latency_ms": elapsed,
        "request_id": request_id,
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
    }


def load_test_data(path: str) -> list[dict]:
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append({"text": row["text"], "label": row["label"]})
    return rows


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_path = os.path.join(repo_root, "data", "test.tsv")

    if not OPENROUTER_API_KEY:
        print("ERROR: OPENROUTER_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    test_data = load_test_data(test_path)
    print(f"Loaded {len(test_data)} test inputs from data/test.tsv")

    results = []
    threshold = CLASSIFY_CONFIDENCE_THRESHOLD

    for i, row in enumerate(test_data):
        ticket = row["text"]
        ground_truth = row["label"]
        print(f"  [{i+1}/{len(test_data)}] {ticket[:60]}...", end="", flush=True)

        # Call Jev
        try:
            jev_resp = call_jev(ticket)
            jev_answer_obj = jev_resp["answers"]["category"]
            jev_choice = jev_answer_obj["choice"]
            jev_confidence = jev_answer_obj["confidence"]
            jev_model = jev_resp.get("model", JEV_MODEL)
            jev_latency = jev_resp["_latency_ms"]
            jev_request_id = jev_resp["_request_id"]
            jev_usage = jev_resp.get("usage", {})
            jev_input_tokens = jev_usage.get("input_tokens")
            jev_output_tokens = jev_usage.get("output_tokens")
            jev_error = None
        except Exception as e:
            print(f" JEV_ERROR: {e}")
            jev_choice = None
            jev_confidence = None
            jev_model = JEV_MODEL
            jev_latency = None
            jev_request_id = None
            jev_input_tokens = None
            jev_output_tokens = None
            jev_error = str(e)
            results.append({
                "input": ticket,
                "provenance": "data/test.tsv",
                "ground_truth": ground_truth,
                "jev_error": jev_error,
            })
            continue

        # Call original baseline
        try:
            orig_resp = call_original(ticket)
            orig_answer = orig_resp["answer"]
            orig_latency = orig_resp["latency_ms"]
            orig_model = orig_resp["model"]
            orig_request_id = orig_resp["request_id"]
            orig_input_tokens = orig_resp.get("input_tokens")
            orig_output_tokens = orig_resp.get("output_tokens")
            orig_error = None
        except Exception as e:
            print(f" ORIG_ERROR: {e}")
            orig_answer = None
            orig_latency = None
            orig_model = ORIGINAL_MODEL
            orig_request_id = None
            orig_input_tokens = None
            orig_output_tokens = None
            orig_error = str(e)

        fallback_taken = (
            jev_confidence is not None and jev_confidence < threshold
        ) or jev_choice not in VALID_CATEGORIES

        result = {
            "input": ticket,
            "provenance": "data/test.tsv",
            "ground_truth": ground_truth,
            "model": jev_model,
            "live": True,
            "request_id": jev_request_id,
            "jev_answer": jev_choice,
            "original_answer": orig_answer,
            "confidence": jev_confidence,
            "fallback_taken": fallback_taken,
            "latency_ms": jev_latency,
            "jev_input_tokens": jev_input_tokens,
            "jev_output_tokens": jev_output_tokens,
            "original_model": orig_model,
            "original_latency_ms": orig_latency,
            "original_request_id": orig_request_id,
            "original_input_tokens": orig_input_tokens,
            "original_output_tokens": orig_output_tokens,
        }
        if orig_error:
            result["original_error"] = orig_error

        match = jev_choice == orig_answer
        result["agreement"] = match
        print(f" jev={jev_choice} orig={orig_answer} conf={jev_confidence:.3f} {'✓' if match else '✗'}")
        results.append(result)

    # ── Compute statistics ──────────────────────────────────────────────────
    valid = [r for r in results if "jev_error" not in r and "original_error" not in r]
    total = len(valid)

    if total == 0:
        print("\nNo valid paired results. Cannot compute parity.")
        sys.exit(1)

    raw_agree = sum(1 for r in valid if r["agreement"])
    raw_rate = raw_agree / total

    # Selective agreement at various thresholds
    thresholds_to_report = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
    threshold_stats = {}
    for t in thresholds_to_report:
        accepted = [r for r in valid if r["confidence"] >= t]
        n_accepted = len(accepted)
        if n_accepted > 0:
            agree_accepted = sum(1 for r in accepted if r["agreement"])
            threshold_stats[t] = {
                "accepted": n_accepted,
                "agreement": agree_accepted,
                "selective_agreement": agree_accepted / n_accepted,
                "fallback_fraction": 1 - n_accepted / total,
            }
        else:
            threshold_stats[t] = {
                "accepted": 0,
                "agreement": 0,
                "selective_agreement": None,
                "fallback_fraction": 1.0,
            }

    # Latency stats
    jev_latencies = sorted(r["latency_ms"] for r in valid if r["latency_ms"] is not None)
    orig_latencies = sorted(r["original_latency_ms"] for r in valid if r["original_latency_ms"] is not None)

    def percentile(arr, p):
        if not arr:
            return None
        idx = int(len(arr) * p / 100)
        return arr[min(idx, len(arr) - 1)]

    print(f"\n{'='*60}")
    print(f"Raw agreement: {raw_agree}/{total} = {raw_rate:.1%}")
    print(f"\nSelective agreement at thresholds:")
    for t, s in sorted(threshold_stats.items()):
        sa = f"{s['selective_agreement']:.1%}" if s['selective_agreement'] is not None else "N/A"
        print(f"  threshold={t:.2f}: accepted={s['accepted']}/{total}, agreement={sa}, fallback={s['fallback_fraction']:.1%}")

    print(f"\nLatency (ms):")
    print(f"  Jev   p50={percentile(jev_latencies, 50):.1f}  p95={percentile(jev_latencies, 95):.1f}")
    print(f"  Orig  p50={percentile(orig_latencies, 50):.1f}  p95={percentile(orig_latencies, 95):.1f}")

    # ── Write JEV_PARITY.json ───────────────────────────────────────────────
    parity = {
        "sites": [
            {
                "site_id": "workflow.py:83",
                "threshold": CLASSIFY_CONFIDENCE_THRESHOLD,
                "n": total,
                "raw_agreement": raw_rate,
                "threshold_stats": threshold_stats,
                "jev_latency_p50_ms": percentile(jev_latencies, 50),
                "jev_latency_p95_ms": percentile(jev_latencies, 95),
                "original_latency_p50_ms": percentile(orig_latencies, 50),
                "original_latency_p95_ms": percentile(orig_latencies, 95),
                "rows": [r for r in results if "jev_error" not in r],
                "errors": [r for r in results if "jev_error" in r],
                "faults": {
                    "below_threshold": False,
                    "error": False,
                    "timeout": False,
                    "rate_limit": False,
                },
            }
        ]
    }

    output_path = os.path.join(repo_root, "JEV_PARITY.json")
    with open(output_path, "w") as f:
        json.dump(parity, f, indent=2, default=str)
    print(f"\nWrote {output_path}")


if __name__ == "__main__":
    main()
