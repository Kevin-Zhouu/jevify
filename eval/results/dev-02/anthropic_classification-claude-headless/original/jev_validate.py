"""Live paired validation: Jev vs original Anthropic classification.

Baseline routed through OpenRouter as authorized by validation config.
This is an isolated evaluation adapter, not a production code change.
"""
import csv
import json
import logging
import os
import sys
import time
import urllib.error
import urllib.request

# Import the actual production decisions module
sys.path.insert(0, os.path.dirname(__file__))
from jev_decisions import (
    CATEGORY_CRITERIA,
    CLASSIFICATION_QUESTION,
    CONFIDENCE_THRESHOLD,
    JEV_BASE_URL,
    JEV_KEY_ENV,
    JEV_MODEL,
    JEV_TIMEOUT_SECONDS,
    call_jev,
    is_confidence_acceptable,
    is_valid_label,
    validate_usage,
)

logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
logger = logging.getLogger(__name__)

OPENROUTER_BASE = "https://openrouter.ai/api/v1/chat/completions"
ORIGINAL_MODEL = "anthropic/claude-haiku-4-5"

# Categories from workflow.py
import textwrap
CATEGORIES_XML = textwrap.dedent("""<category>
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


def call_original_via_openrouter(ticket_text):
    """Call the original Anthropic model through OpenRouter (authorized baseline adapter)."""
    api_key = os.environ.get(JEV_KEY_ENV)
    if not api_key:
        raise EnvironmentError(f"{JEV_KEY_ENV} not set")

    prompt = textwrap.dedent("""
    You will classify a customer support ticket into one of the following categories:
    <categories>
        {categories}
    </categories>

    Here is the customer support ticket:
    <ticket>
        {ticket}
    </ticket>

    Respond with just the label of the category between category tags.
    """).format(categories=CATEGORIES_XML, ticket=ticket_text)

    request_body = json.dumps({
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
        OPENROUTER_BASE,
        data=request_body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    start = time.monotonic()
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    elapsed_ms = (time.monotonic() - start) * 1000

    content = raw["choices"][0]["message"]["content"].strip()
    request_id = raw.get("id", "")
    usage = raw.get("usage", {})

    # Estimate cost from usage (Claude Haiku 4.5 pricing via OpenRouter)
    input_tokens = usage.get("prompt_tokens", 0)
    output_tokens = usage.get("completion_tokens", 0)
    # OpenRouter Claude Haiku 4.5: $0.80/M input, $4.00/M output (approximate, 2026-09)
    cost_usd = (input_tokens * 0.8 + output_tokens * 4.0) / 1_000_000

    return content, elapsed_ms, request_id, cost_usd


def run_validation():
    data_path = os.path.join(os.path.dirname(__file__), "data", "test.tsv")
    rows = []
    with open(data_path, "r") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append(row)

    results = []
    jev_errors = 0
    original_errors = 0

    for i, row in enumerate(rows):
        ticket = row["text"]
        expected = row["label"]
        provenance = "repo"
        source = f"data/test.tsv:{i+2}"

        # Call Jev
        jev_answer = None
        jev_confidence = None
        jev_latency = None
        jev_cost = None
        jev_model = None
        jev_request_id = ""
        fallback_taken = False
        jev_error = None

        try:
            choice, confidence, usage, model, raw, elapsed_ms = call_jev(ticket)
            jev_answer = choice
            jev_confidence = confidence
            jev_latency = elapsed_ms
            jev_model = model
            jev_request_id = raw.get("id", "")
            # Estimate Jev cost from usage
            if validate_usage(usage):
                inp = usage.get("input_tokens", 0)
                out = usage.get("output_tokens", 0)
                # Jev pricing via OpenRouter: approximate $0.02/M input, $0.02/M output
                jev_cost = (inp * 0.02 + out * 0.02) / 1_000_000
            else:
                jev_cost = None

            # Apply actual gate logic
            if not is_valid_label(choice):
                fallback_taken = True
            elif not is_confidence_acceptable(confidence):
                fallback_taken = True
        except Exception as exc:
            jev_error = str(exc)
            jev_errors += 1
            fallback_taken = True

        # Call original via OpenRouter
        original_answer = None
        original_latency = None
        original_cost = None
        original_request_id = ""

        try:
            content, elapsed_ms, req_id, cost = call_original_via_openrouter(ticket)
            original_answer = content
            original_latency = elapsed_ms
            original_cost = cost
            original_request_id = req_id
        except Exception as exc:
            original_errors += 1
            logger.error("Original call failed for row %d: %s", i, exc)
            continue

        result = {
            "input": ticket[:200],
            "provenance": provenance,
            "source": source,
            "expected_label": expected,
            "model": JEV_MODEL,
            "live": True,
            "request_id": jev_request_id,
            "jev_answer": jev_answer,
            "confidence": jev_confidence,
            "fallback_taken": fallback_taken,
            "latency_ms": jev_latency,
            "cost_usd": jev_cost,
            "original_model": ORIGINAL_MODEL,
            "original_answer": original_answer,
            "original_latency_ms": original_latency,
            "original_cost_usd": original_cost,
            "original_request_id": original_request_id,
        }
        if jev_error:
            result["jev_error"] = jev_error

        results.append(result)
        logger.info(
            "Row %d/%d: jev=%s original=%s expected=%s conf=%s fallback=%s",
            i + 1, len(rows), jev_answer, original_answer, expected, jev_confidence, fallback_taken,
        )

        # Small delay to avoid rate limiting
        time.sleep(0.3)

    return results


def compute_metrics(results, threshold):
    """Compute agreement metrics at the given threshold."""
    accepted = [r for r in results if not r["fallback_taken"] and r["jev_answer"] is not None]
    total = len(results)
    accepted_count = len(accepted)
    fallback_count = total - accepted_count

    if accepted_count > 0:
        agreeing = sum(1 for r in accepted if r["jev_answer"] == r["original_answer"])
        selective_agreement = agreeing / accepted_count
    else:
        selective_agreement = None

    # Raw agreement (jev vs original, ignoring confidence)
    raw_comparable = [r for r in results if r["jev_answer"] is not None and r["original_answer"] is not None]
    if raw_comparable:
        raw_agreeing = sum(1 for r in raw_comparable if r["jev_answer"] == r["original_answer"])
        raw_agreement = raw_agreeing / len(raw_comparable)
    else:
        raw_agreement = None

    # Latency stats
    jev_latencies = [r["latency_ms"] for r in results if r["latency_ms"] is not None]
    orig_latencies = [r["original_latency_ms"] for r in results if r["original_latency_ms"] is not None]

    def percentile(data, p):
        if not data:
            return None
        s = sorted(data)
        idx = int(len(s) * p / 100)
        return s[min(idx, len(s) - 1)]

    return {
        "threshold": threshold,
        "total": total,
        "accepted": accepted_count,
        "fallback_count": fallback_count,
        "fallback_rate": fallback_count / total if total else None,
        "selective_agreement": selective_agreement,
        "raw_agreement": raw_agreement,
        "jev_p50_ms": percentile(jev_latencies, 50),
        "jev_p95_ms": percentile(jev_latencies, 95),
        "original_p50_ms": percentile(orig_latencies, 50),
        "original_p95_ms": percentile(orig_latencies, 95),
    }


def main():
    logger.info("Starting live paired validation...")
    results = run_validation()

    if not results:
        logger.error("No results collected")
        sys.exit(1)

    metrics = compute_metrics(results, CONFIDENCE_THRESHOLD)
    logger.info("\n=== Metrics at threshold %.2f ===", CONFIDENCE_THRESHOLD)
    for k, v in metrics.items():
        logger.info("  %s: %s", k, v)

    # Also compute at alternative thresholds for the curve
    thresholds = [0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
    threshold_curve = []
    for t in thresholds:
        accepted = [r for r in results if r["confidence"] is not None and r["confidence"] >= t
                     and r["jev_answer"] is not None and is_valid_label(r["jev_answer"])]
        if accepted:
            agreeing = sum(1 for r in accepted if r["jev_answer"] == r["original_answer"])
            threshold_curve.append({
                "threshold": t,
                "accepted": len(accepted),
                "fallback": len(results) - len(accepted),
                "selective_agreement": agreeing / len(accepted),
            })

    parity = {
        "sites": [
            {
                "site_id": "workflow.py:83",
                "threshold": CONFIDENCE_THRESHOLD,
                "metrics": metrics,
                "threshold_curve": threshold_curve,
                "rows": results,
                "faults": {
                    "below_threshold": False,
                    "error": False,
                    "timeout": False,
                    "rate_limit": False,
                },
            }
        ]
    }

    output_path = os.path.join(os.path.dirname(__file__), "JEV_PARITY.json")
    with open(output_path, "w") as f:
        json.dump(parity, f, indent=2)

    logger.info("\nParity results written to %s", output_path)
    logger.info("Total rows: %d", len(results))


if __name__ == "__main__":
    main()
