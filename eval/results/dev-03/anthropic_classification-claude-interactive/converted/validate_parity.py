#!/usr/bin/env python3
"""Live paired parity validation for workflow.py:83 (simple_classify).

Imports the ACTUAL jev_decisions module and invokes evaluate_classify once per input.
Captures the raw response via a recording adapter around urlopen.
Baseline routes claude-haiku-4-5 through OpenRouter (authorized in config).

Usage:
    python validate_parity.py [--threshold 0.6]
"""
import argparse
import json
import math
import os
import sys
import textwrap
import time
import unittest.mock
import urllib.error
import urllib.request

# ── Import the actual decisions module (same one production uses) ────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jev_decisions import (
    CLASSIFY_CONFIDENCE_THRESHOLD,
    CLASSIFY_QUESTION,
    JEV_BASE_URL,
    JEV_KEY_ENV,
    JEV_MODEL,
    JEV_TIMEOUT_S,
    VALID_CATEGORIES,
    evaluate_classify,
)

# ── Original baseline via OpenRouter (authorized adapter) ───────────────────
ORIGINAL_MODEL = "anthropic/claude-haiku-4-5"
OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"

# ── Read categories from the original workflow source ───────────────────────
_workflow_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workflow.py")
with open(_workflow_path) as _f:
    _src = _f.read()
_ns = {}
exec(
    "import textwrap\n" + _src[_src.index('categories = textwrap.dedent'):_src.index('\ndef simple_classify')],
    _ns,
)
_categories = _ns["categories"]


def _build_original_prompt(ticket_text):
    """Build the exact same prompt the original simple_classify uses."""
    return (
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
        .replace("{{categories}}", _categories)
        .replace("{{ticket}}", ticket_text)
    )


def call_original_via_openrouter(ticket_text, api_key):
    """Route the original prompt through OpenRouter to anthropic/claude-haiku-4-5."""
    prompt = _build_original_prompt(ticket_text)
    body = json.dumps({
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
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/jevify-eval",
        },
        method="POST",
    )

    start = time.monotonic()
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
    elapsed_ms = (time.monotonic() - start) * 1000

    data = json.loads(raw)
    request_id = data.get("id", "")
    content = data["choices"][0]["message"]["content"]
    result = content.strip()

    usage = data.get("usage", {})
    cost = None
    if "total_cost" in usage:
        cost = usage["total_cost"]

    return result, elapsed_ms, request_id, cost


# ── Recording adapter: captures raw Jev response while evaluate_classify runs ─
_real_urlopen = urllib.request.urlopen  # Save before any patching

class _RecordingResponse:
    """Wraps a real urllib response to capture its body."""
    def __init__(self, real_resp):
        self._real = real_resp
        self._body = None
    def read(self):
        self._body = self._real.read()
        return self._body
    def __enter__(self):
        self._real.__enter__()
        return self
    def __exit__(self, *a):
        return self._real.__exit__(*a)
    def __getattr__(self, name):
        return getattr(self._real, name)


_last_captured = None

def _recording_urlopen(req, **kwargs):
    """Wraps urlopen to capture the raw response body."""
    global _last_captured
    real = _real_urlopen(req, **kwargs)
    recorder = _RecordingResponse(real)
    _last_captured = recorder
    return recorder


# ── Test inputs (30+ unique, covering all 10 categories + boundary) ─────────
INPUTS = [
    # Billing Inquiries
    {"text": "I need to understand the charges on my latest invoice. Can you break down each line item?", "provenance": "synthetic"},
    {"text": "When is my next premium payment due and what payment methods do you accept?", "provenance": "synthetic"},
    {"text": "Can you explain why my monthly premium increased this quarter?", "provenance": "synthetic"},
    # Policy Administration
    {"text": "I'd like to add my teenage driver to my auto insurance policy. What do I need to do?", "provenance": "synthetic"},
    {"text": "I need to cancel my renters insurance policy effective next month.", "provenance": "synthetic"},
    {"text": "My policy is up for renewal next week. Can you walk me through the renewal process?", "provenance": "synthetic"},
    # Claims Assistance
    {"text": "I was in a car accident yesterday. How do I file an auto insurance claim?", "provenance": "synthetic"},
    {"text": "What documents do I need to submit for my homeowner's insurance claim?", "provenance": "synthetic"},
    {"text": "Can you give me an update on the status of claim number 12345? When can I expect a payout?", "provenance": "synthetic"},
    # Coverage Explanations
    {"text": "Does my homeowner's policy cover flood damage or do I need separate flood insurance?", "provenance": "synthetic"},
    {"text": "What is my deductible for my auto insurance policy and what are my out-of-pocket limits?", "provenance": "synthetic"},
    {"text": "Can you explain what's excluded from my standard health insurance coverage?", "provenance": "synthetic"},
    # Quotes and Proposals
    {"text": "I'm looking for a quote on bundling my home and auto insurance. What discounts are available?", "provenance": "synthetic"},
    {"text": "How do your rates compare to State Farm for comprehensive auto coverage?", "provenance": "synthetic"},
    {"text": "I want to switch from my current insurer. What do I need to get started with a new policy?", "provenance": "synthetic"},
    # Account Management
    {"text": "I forgot my password and can't log into my online account. How do I reset it?", "provenance": "synthetic"},
    {"text": "I recently moved and need to update my address on file.", "provenance": "synthetic"},
    {"text": "What features are available in the online portal? Can I view my policy documents there?", "provenance": "synthetic"},
    # Billing Disputes
    {"text": "I was charged twice for the same premium last month. I need a refund for the duplicate charge.", "provenance": "synthetic"},
    {"text": "I received a late fee but I paid on time. Can you investigate and remove the fee?", "provenance": "synthetic"},
    {"text": "My premium went up without any explanation. I want to dispute this unexpected increase.", "provenance": "synthetic"},
    # Claims Disputes
    {"text": "My claim was denied but I believe the damage should be covered. How do I appeal this decision?", "provenance": "synthetic"},
    {"text": "The settlement amount for my claim is far lower than the actual repair costs. I want to dispute this.", "provenance": "synthetic"},
    {"text": "I disagree with the adjuster's assessment of my property damage claim. What are my options?", "provenance": "synthetic"},
    # Policy Comparisons
    {"text": "What's the difference between your basic and premium homeowner's insurance plans?", "provenance": "synthetic"},
    {"text": "Can you help me compare the coverage levels between your gold and platinum auto policies?", "provenance": "synthetic"},
    {"text": "How does your term life insurance compare to your competitor's whole life option?", "provenance": "synthetic"},
    # General Inquiries
    {"text": "What are your office hours and is there a branch near downtown?", "provenance": "synthetic"},
    {"text": "Do you offer any insurance products for small businesses?", "provenance": "synthetic"},
    {"text": "I'm just looking for general information about what types of insurance you offer.", "provenance": "synthetic"},
    # Boundary / ambiguous cases
    {"text": "Please explain my invoice.", "provenance": "repo", "source": "smoke.py:54"},
    {"text": "I got a bill I don't understand and my claim was denied at the same time. What should I do?", "provenance": "synthetic"},
    {"text": "hello", "provenance": "synthetic"},
    {"text": "", "provenance": "synthetic"},
    {"text": "Can you help me? I'm not sure what I need but something feels wrong with my account.", "provenance": "synthetic"},
]


def run_fault_tests(api_key):
    """Exercise the four required failure branches through the actual wrapper."""
    results = {}
    ticket = "Test ticket for fault injection."

    # Ensure key is set for evaluate_classify
    os.environ[JEV_KEY_ENV] = api_key

    # 1. Low confidence: replay a captured response with below-threshold confidence
    low_conf_response = json.dumps({
        "model": "jev-1.13.0",
        "answers": {
            "category": {
                "type": "choice",
                "choice": "General Inquiries",
                "confidence": 0.3,
                "probabilities": {
                    "Billing Inquiries": 0.15,
                    "Policy Administration": 0.1,
                    "Claims Assistance": 0.05,
                    "Coverage Explanations": 0.05,
                    "Quotes and Proposals": 0.05,
                    "Account Management": 0.1,
                    "Billing Disputes": 0.1,
                    "Claims Disputes": 0.05,
                    "Policy Comparisons": 0.05,
                    "General Inquiries": 0.3,
                }
            }
        },
        "usage": {"input_tokens": 300, "output_tokens": 30}
    }).encode()

    class FakeResp:
        def __init__(self, data):
            self._data = data
        def read(self):
            return self._data
        def __enter__(self):
            return self
        def __exit__(self, *a):
            pass

    with unittest.mock.patch("jev_decisions.urllib.request.urlopen", return_value=FakeResp(low_conf_response)):
        label, accepted = evaluate_classify(ticket)
        results["below_threshold"] = (not accepted and label is None)

    # 2. Generic error: inject a transport exception
    with unittest.mock.patch("jev_decisions.urllib.request.urlopen", side_effect=OSError("injected error")):
        label, accepted = evaluate_classify(ticket)
        results["error"] = (not accepted and label is None)

    # 3. Timeout: inject timeout exception
    with unittest.mock.patch("jev_decisions.urllib.request.urlopen", side_effect=TimeoutError("injected timeout")):
        label, accepted = evaluate_classify(ticket)
        results["timeout"] = (not accepted and label is None)

    # 4. Rate limit: inject HTTP 429
    exc_429 = urllib.error.HTTPError(
        url=JEV_BASE_URL, code=429, msg="Too Many Requests",
        hdrs=None, fp=None,  # type: ignore[arg-type]
    )
    with unittest.mock.patch("jev_decisions.urllib.request.urlopen", side_effect=exc_429):
        label, accepted = evaluate_classify(ticket)
        results["rate_limit"] = (not accepted and label is None)

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=None)
    args = parser.parse_args()

    api_key = os.environ.get(JEV_KEY_ENV)
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY not set. Live validation cannot proceed.", file=sys.stderr)
        sys.exit(1)

    threshold = args.threshold if args.threshold is not None else CLASSIFY_CONFIDENCE_THRESHOLD

    print(f"Running parity validation with threshold={threshold}", file=sys.stderr)
    print(f"Jev model: {JEV_MODEL}", file=sys.stderr)
    print(f"Original model (via OpenRouter): {ORIGINAL_MODEL}", file=sys.stderr)
    print(f"Inputs: {len(INPUTS)}", file=sys.stderr)

    global _last_captured
    rows = []
    errors = []

    for i, inp in enumerate(INPUTS):
        ticket = inp["text"]
        print(f"  [{i+1}/{len(INPUTS)}] {ticket[:60]}...", file=sys.stderr)

        # 1. Call Jev via the actual decisions module with recording adapter
        _last_captured = None
        jev_start = time.monotonic()
        try:
            with unittest.mock.patch("jev_decisions.urllib.request.urlopen", side_effect=_recording_urlopen):
                jev_label, jev_accepted = evaluate_classify(ticket)
            jev_elapsed = (time.monotonic() - jev_start) * 1000
        except Exception as exc:
            jev_label, jev_accepted = None, False
            jev_elapsed = (time.monotonic() - jev_start) * 1000
            errors.append({"input_index": i, "phase": "jev", "error": str(exc)})
            continue

        # Extract evidence from captured response
        jev_confidence = None
        jev_request_id = ""
        jev_cost = None
        jev_raw_label = jev_label
        if _last_captured is not None and _last_captured._body is not None:
            try:
                jev_data = json.loads(_last_captured._body)
                cat_ans = jev_data.get("answers", {}).get("category", {})
                jev_confidence = cat_ans.get("confidence")
                jev_raw_label = cat_ans.get("choice")
                jev_request_id = jev_data.get("id", "")
                jev_usage = jev_data.get("usage", {})
                if isinstance(jev_usage.get("input_tokens"), (int, float)):
                    jev_cost = round(jev_usage["input_tokens"] * 0.042 / 1_000_000, 8)
            except (json.JSONDecodeError, ValueError):
                pass

        # 2. Call original via OpenRouter
        try:
            orig_label, orig_elapsed, orig_request_id, orig_cost = call_original_via_openrouter(ticket, api_key)
        except Exception as exc:
            errors.append({"input_index": i, "phase": "original", "error": str(exc)})
            continue

        row = {
            "input": ticket,
            "provenance": inp["provenance"],
            "model": JEV_MODEL,
            "live": True,
            "request_id": jev_request_id,
            "jev_answer": jev_raw_label,
            "original_answer": orig_label,
            "confidence": jev_confidence,
            "fallback_taken": not jev_accepted,
            "latency_ms": round(jev_elapsed, 1),
            "cost_usd": jev_cost,
            "original_model": ORIGINAL_MODEL,
            "original_latency_ms": round(orig_elapsed, 1),
            "original_cost_usd": orig_cost,
            "original_request_id": orig_request_id,
        }
        if "source" in inp:
            row["source"] = inp["source"]
        rows.append(row)

        # Rate-limit courtesy
        time.sleep(0.3)

    # Run fault tests
    print("\nRunning fault injection tests...", file=sys.stderr)
    faults = run_fault_tests(api_key)
    for k, v in faults.items():
        status = "PASS" if v else "FAIL"
        print(f"  Fault test {k}: {status}", file=sys.stderr)

    # Compute metrics
    total = len(rows)
    if total == 0:
        print("ERROR: No successful rows collected.", file=sys.stderr)
        sys.exit(1)

    agreements = sum(1 for r in rows if r["jev_answer"] == r["original_answer"])
    raw_agreement = agreements / total

    accepted_rows = [r for r in rows if not r["fallback_taken"]]
    accepted_count = len(accepted_rows)
    accepted_agreements = sum(1 for r in accepted_rows if r["jev_answer"] == r["original_answer"])
    selective_agreement = accepted_agreements / accepted_count if accepted_count > 0 else 0
    fallback_rate = 1 - (accepted_count / total)

    jev_latencies = [r["latency_ms"] for r in rows if r["latency_ms"] is not None]
    orig_latencies = [r["original_latency_ms"] for r in rows if r["original_latency_ms"] is not None]

    def percentile(data, p):
        if not data:
            return None
        s = sorted(data)
        k = (len(s) - 1) * p / 100
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return s[int(k)]
        return s[f] * (c - k) + s[c] * (k - f)

    parity = {
        "sites": [
            {
                "site_id": "workflow.py:83",
                "threshold": threshold,
                "n": total,
                "raw_agreement": round(raw_agreement, 4),
                "accepted_count": accepted_count,
                "selective_agreement": round(selective_agreement, 4),
                "fallback_rate": round(fallback_rate, 4),
                "jev_latency_p50_ms": round(percentile(jev_latencies, 50), 1) if jev_latencies else None,
                "jev_latency_p95_ms": round(percentile(jev_latencies, 95), 1) if jev_latencies else None,
                "original_latency_p50_ms": round(percentile(orig_latencies, 50), 1) if orig_latencies else None,
                "original_latency_p95_ms": round(percentile(orig_latencies, 95), 1) if orig_latencies else None,
                "cost_source": "estimated at $0.042/Mtok input for Jev (models page, 2026-09-23); OpenRouter-reported for original where available",
                "cost_date": "2026-09-23",
                "rows": rows,
                "faults": faults,
                "errors": errors,
            }
        ]
    }

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "JEV_PARITY.json")
    with open(out_path, "w") as f:
        json.dump(parity, f, indent=2)

    print(f"\nResults written to {out_path}", file=sys.stderr)
    print(f"Total inputs: {total}", file=sys.stderr)
    print(f"Raw agreement: {raw_agreement:.2%}", file=sys.stderr)
    print(f"Accepted: {accepted_count}/{total} ({1-fallback_rate:.1%})", file=sys.stderr)
    print(f"Selective agreement: {selective_agreement:.2%}", file=sys.stderr)
    print(f"Fallback rate: {fallback_rate:.2%}", file=sys.stderr)


if __name__ == "__main__":
    main()
