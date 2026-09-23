# Jev Conversion Report

## Source

- Repository: `anthropic_classification` (Anthropic Cookbook — classification guide)
- Source revision: `9ad0ba53546ba42a9b50165c3fe51ec275a58d68`
- Output mode: clone
- Clone path: `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-01/anthropic_classification-claude-headless/converted`
- Branch: `jev-convert/evaluation`
- Date: 2026-09-23

## Provider and model

- Jev provider: OpenRouter
- Jev model pin: `typesafe/jev-1.13-20260917`
- Key variable: `OPENROUTER_API_KEY`
- Original model: `claude-haiku-4-5` (Anthropic SDK)
- Baseline routing: Original routed through OpenRouter as `anthropic/claude-haiku-4-5` (authorized by config `validation.baseline_routing_authorized: true`)

## Approval

- Risk posture: conservative (fallback retained everywhere)
- Approval predicate: "Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged. Preserve all externally observable fields."
- Resolved: `workflow.py:83` approved for `fallback` action with Choice primitive

## Converted sites

| Site | Classification | Action | Primitive |
|---|---|---|---|
| `workflow.py:83` | DECISION | fallback | Choice |

## Unchanged sites

None — single call site in the workflow.

## Changes

| File | Change |
|---|---|
| `jev_decisions.py` | New — Jev decisions module with all questions, criteria, thresholds, model pin, and fallback gate logic |
| `workflow.py` | Modified — `simple_classify()` now calls `classify_with_jev()` which tries Jev first with confidence-gated fallback to original `_original_classify()` |
| `.env.example` | New — placeholder for `OPENROUTER_API_KEY` alongside existing `ANTHROPIC_API_KEY` |
| `scripts/run_parity.py` | New — paired live parity measurement script |
| `scripts/test_faults.py` | New — fault injection tests for fallback behavior |

## Test commands and results

### Smoke test (evaluator-supplied)

```
/opt/homebrew/opt/python@3.14/bin/python3.14 eval/smoke.py OUTPUT_DIR anthropic_classification
```

Result: **PASS** — observable Python behavior and original-path fallback smoke. Smoke test injects mock Anthropic SDK with network blocked; Jev times out and falls back to original path. Verified `simple_classify('Please explain my invoice.')` returns `'Billing Inquiries'` with exactly 1 original call to `claude-haiku-4-5`.

### Fault injection tests

```
/opt/homebrew/opt/python@3.14/bin/python3.14 scripts/test_faults.py
```

Result: **All 10 tests passed.** Exercised:
- Low confidence at gate boundary (just below 0.80) → fallback, exactly 1 original call
- Confidence exactly at threshold (0.80) → Jev answer used, 0 original calls
- Timeout → fallback
- HTTP 429 rate limit → fallback
- Generic network error → fallback
- Missing `OPENROUTER_API_KEY` → fallback
- Malformed Jev response → fallback
- Unknown category label → fallback
- Nonfinite (NaN) confidence → fallback
- High confidence → Jev answer used

## Live paired validation

### Input provenance

68 inputs from `data/test.tsv` (repo fixture). All unique realistic insurance support tickets. No cherry-picking. 5 inputs experienced Jev timeout errors and were excluded from paired results.

### Limitations

- Calibration and confirmation use the same 63-input set (no separate hold-out). The threshold was chosen after observing all results. Sample size is small; production should validate on a larger, independent set.
- Cost is estimated from documented pricing, not provider-reported usage amounts.
- Pricing sourced from TypeSafe docs (Jev: $0.042/Mtok input, output free) and Anthropic pricing (Haiku 4.5: $0.80/Mtok input, $4/Mtok output) as of 2026-09-23.

### Agreement curve

| Threshold | Accepted | Selective agreement | Fallback fraction |
|---|---|---|---|
| 0.50 | 58/63 | 86.2% | 7.9% |
| 0.60 | 55/63 | 89.1% | 12.7% |
| **0.70** | 51/63 | 92.2% | 19.0% |
| **0.80 (selected)** | **45/63** | **97.8%** | **28.6%** |
| 0.90 | 38/63 | 100.0% | 39.7% |
| 0.95 | 34/63 | 100.0% | 46.0% |

Raw agreement (all pairs, no threshold): 53/63 = 84.1%

### Recommended threshold

**0.80** — achieves 97.8% selective agreement (above 90% target) with 28.6% fallback rate. At this threshold, only 1 out of 45 accepted decisions disagreed with the original baseline.

### Latency

| Path | p50 (ms) | p95 (ms) |
|---|---|---|
| Jev | 349.7 | 553.4 |
| Original (Haiku via OpenRouter) | 1051.9 | 1996.2 |

Jev is ~3x faster at p50. Fallback cascade (Jev miss + original) adds Jev latency to original latency.

### Expected cost per decision

- Jev: ~$0.042/Mtok × ~300 input tokens = ~$0.0000126
- Original (Haiku): ~$0.80/Mtok input × ~800 tokens + $4/Mtok output × ~5 tokens = ~$0.00066
- Expected cascade at 0.80 threshold: $0.0000126 + 28.6% × $0.00066 ≈ $0.00020 per decision (~70% cost reduction vs original-only)

Cost is estimated from documented pricing, not provider-reported per-request usage.

### Fallback rate and error rate

- Confidence-gated fallback (below 0.80): 18/63 = 28.6%
- Jev transport errors (timeout): 5/68 = 7.4%
- Total fallback rate in production: confidence fallback + error fallback

## Undo instructions

To revert the conversion:
1. Switch to the original branch: the source repository at the original path is unchanged.
2. Delete the clone directory: `rm -rf "/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-01/anthropic_classification-claude-headless/converted"`
