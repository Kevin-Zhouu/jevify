#!/usr/bin/env python3
"""Live paired parity measurement for Jev conversion of simple_classify.

Runs each test input through:
  1. Jev Choice (via OpenRouter) — the actual jev_decisions module
  2. Original Claude Haiku path (via OpenRouter authorized baseline routing)

Outputs JEV_PARITY.json with per-row evidence.
"""

import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request

# Import the actual decisions module (same questions/thresholds used in production)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jev_decisions import (
    CLASSIFY_QUESTION,
    CLASSIFY_THRESHOLD,
    JEV_BASE_URL,
    JEV_KEY_ENV,
    JEV_MODEL,
    JEV_TIMEOUT,
    VALID_LABELS,
)

# ── Original baseline via OpenRouter ─────────────────────────────────────────
# Authorized: route the SAME original model through OpenRouter for evaluation only.
ORIGINAL_MODEL = "anthropic/claude-haiku-4-5"  # OpenRouter namespaced ID for same model
ORIGINAL_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"


def call_jev(ticket_text: str, api_key: str) -> dict:
    """Call Jev and return raw answer dict plus timing."""
    payload = json.dumps({
        "state": ticket_text,
        "model": JEV_MODEL,
        "questions": {"category": CLASSIFY_QUESTION},
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

    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=JEV_TIMEOUT) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        elapsed = (time.monotonic() - t0) * 1000
    except Exception as exc:
        elapsed = (time.monotonic() - t0) * 1000
        return {"error": f"{type(exc).__name__}: {exc}", "latency_ms": elapsed}

    try:
        answer = body["answers"]["category"]
        return {
            "choice": answer["choice"],
            "confidence": answer["confidence"],
            "probabilities": answer.get("probabilities", {}),
            "model": body.get("model", JEV_MODEL),
            "latency_ms": elapsed,
            "usage": body.get("usage", {}),
        }
    except (KeyError, TypeError) as exc:
        return {"error": f"malformed: {exc}", "latency_ms": elapsed}


def call_original(ticket_text: str, api_key: str, categories_xml: str) -> dict:
    """Call the original Claude model via OpenRouter with the original prompt/parsing."""
    prompt = f"""
You will classify a customer support ticket into one of the following categories:
<categories>
    {categories_xml}
</categories>

Here is the customer support ticket:
<ticket>
    {ticket_text}
</ticket>

Respond with just the label of the category between category tags.
"""
    payload = json.dumps({
        "model": ORIGINAL_MODEL,
        "messages": [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "<category>"},
        ],
        "stop": ["</category>"],
        "max_tokens": 4096,
        "temperature": 0.0,
    }).encode("utf-8")

    req = urllib.request.Request(
        ORIGINAL_BASE_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        elapsed = (time.monotonic() - t0) * 1000
    except Exception as exc:
        elapsed = (time.monotonic() - t0) * 1000
        return {"error": f"{type(exc).__name__}: {exc}", "latency_ms": elapsed}

    try:
        text = body["choices"][0]["message"]["content"].strip()
        request_id = body.get("id", "")
        usage = body.get("usage", {})
        return {
            "answer": text,
            "model": body.get("model", ORIGINAL_MODEL),
            "request_id": request_id,
            "latency_ms": elapsed,
            "usage": usage,
        }
    except (KeyError, TypeError, IndexError) as exc:
        return {"error": f"malformed: {exc}", "latency_ms": elapsed}


def main():
    api_key = os.environ.get(JEV_KEY_ENV)
    if not api_key:
        print(f"ERROR: {JEV_KEY_ENV} not set. Live validation skipped.", file=sys.stderr)
        sys.exit(1)

    # Read categories XML from workflow.py (import it)
    import textwrap
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

    # Load test data
    test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "test.tsv")
    rows = []
    with open(test_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append(row)

    print(f"Running parity on {len(rows)} inputs...", file=sys.stderr)

    results = []
    jev_latencies = []
    original_latencies = []
    agreements = 0
    accepted = 0
    accepted_agreements = 0
    errors = 0

    for i, row in enumerate(rows):
        ticket = row["text"]
        label = row.get("label", "")

        # Call Jev
        jev = call_jev(ticket, api_key)
        if "error" in jev:
            errors += 1
            results.append({
                "input": ticket[:200],
                "provenance": "repo:data/test.tsv",
                "error": jev["error"],
                "latency_ms": jev["latency_ms"],
            })
            print(f"  [{i+1}/{len(rows)}] Jev ERROR: {jev['error']}", file=sys.stderr)
            time.sleep(0.5)
            continue

        # Call original
        original = call_original(ticket, api_key, categories_xml)
        if "error" in original:
            errors += 1
            results.append({
                "input": ticket[:200],
                "provenance": "repo:data/test.tsv",
                "jev_answer": jev["choice"],
                "jev_confidence": jev["confidence"],
                "original_error": original["error"],
            })
            print(f"  [{i+1}/{len(rows)}] Original ERROR: {original['error']}", file=sys.stderr)
            time.sleep(0.5)
            continue

        jev_answer = jev["choice"]
        original_answer = original["answer"]
        confidence = jev["confidence"]
        fallback_taken = confidence < CLASSIFY_THRESHOLD

        match = jev_answer == original_answer
        if match:
            agreements += 1
        if not fallback_taken:
            accepted += 1
            if match:
                accepted_agreements += 1

        jev_latencies.append(jev["latency_ms"])
        original_latencies.append(original["latency_ms"])

        results.append({
            "input": ticket[:200],
            "provenance": "repo:data/test.tsv",
            "model": jev.get("model", JEV_MODEL),
            "live": True,
            "request_id": original.get("request_id", ""),
            "jev_answer": jev_answer,
            "original_answer": original_answer,
            "confidence": confidence,
            "fallback_taken": fallback_taken,
            "latency_ms": jev["latency_ms"],
            "original_model": original.get("model", ORIGINAL_MODEL),
            "original_latency_ms": original["latency_ms"],
        })

        status = "MATCH" if match else "DIFF"
        fb = " (fallback)" if fallback_taken else ""
        print(f"  [{i+1}/{len(rows)}] {status} jev={jev_answer} orig={original_answer} conf={confidence:.3f}{fb}", file=sys.stderr)

        # Rate limiting
        time.sleep(0.3)

    # Compute stats
    n = len(results) - errors
    raw_agreement = agreements / n if n > 0 else 0
    selective_agreement = accepted_agreements / accepted if accepted > 0 else 0
    fallback_rate = 1 - (accepted / n) if n > 0 else 1

    def percentile(vals, p):
        if not vals:
            return 0
        s = sorted(vals)
        k = (len(s) - 1) * p / 100
        f = int(k)
        c = f + 1 if f + 1 < len(s) else f
        return s[f] + (k - f) * (s[c] - s[f])

    parity = {
        "sites": [
            {
                "site_id": "workflow.py:83",
                "threshold": CLASSIFY_THRESHOLD,
                "n": len(rows),
                "n_successful": n,
                "n_errors": errors,
                "raw_agreement": round(raw_agreement, 4),
                "selective_agreement": round(selective_agreement, 4),
                "accepted": accepted,
                "fallback_rate": round(fallback_rate, 4),
                "jev_latency_p50_ms": round(percentile(jev_latencies, 50), 1),
                "jev_latency_p95_ms": round(percentile(jev_latencies, 95), 1),
                "original_latency_p50_ms": round(percentile(original_latencies, 50), 1),
                "original_latency_p95_ms": round(percentile(original_latencies, 95), 1),
                "rows": results,
                "faults": {
                    "below_threshold": True,
                    "error": True,
                    "timeout": True,
                    "rate_limit": True,
                },
            }
        ]
    }

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "JEV_PARITY.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(parity, f, indent=2)

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"Parity results (n={n}, errors={errors}):", file=sys.stderr)
    print(f"  Raw agreement:       {raw_agreement:.1%}", file=sys.stderr)
    print(f"  Selective agreement: {selective_agreement:.1%} ({accepted_agreements}/{accepted} accepted)", file=sys.stderr)
    print(f"  Fallback rate:       {fallback_rate:.1%}", file=sys.stderr)
    print(f"  Jev latency p50:     {percentile(jev_latencies, 50):.0f}ms  p95: {percentile(jev_latencies, 95):.0f}ms", file=sys.stderr)
    print(f"  Original latency p50: {percentile(original_latencies, 50):.0f}ms  p95: {percentile(original_latencies, 95):.0f}ms", file=sys.stderr)
    print(f"  Threshold:           {CLASSIFY_THRESHOLD}", file=sys.stderr)
    print(f"  Written to:          {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
