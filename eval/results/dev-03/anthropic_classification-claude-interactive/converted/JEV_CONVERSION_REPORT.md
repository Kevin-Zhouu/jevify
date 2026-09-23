# Jev Conversion Report

## Summary

| Field | Value |
|---|---|
| Source revision | `1c953f75ebe1580de909072ce9a73b8ab8f11d05` |
| Output mode | Clone → `converted/` on branch `jev-convert/evaluation` |
| Risk posture | Conservative (fallback always retained) |
| Provider | OpenRouter (`OPENROUTER_API_KEY`) |
| Model pin | `typesafe/jev-1.13-20260917` |
| Approval | Option `fallback` for `workflow.py:83` |

## Changed Sites

### `workflow.py:83` — `simple_classify()` → Jev Choice with fallback

- **Primitive:** Choice (10 insurance categories)
- **Module:** `jev_decisions.py` (new) — model ID, question, criteria, threshold, gate
- **Integration:** `workflow.py` modified to try `evaluate_classify()` first; on rejection/error falls through to unchanged original Anthropic call
- **Confidence threshold:** 0.6

## Unchanged Sites

None — this is the only LLM call site in the project.

## Test Commands and Results

### Smoke test (offline, evaluator-provided)

```
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/bigsoup/Downloads/Jev\ Converter/eval/smoke.py \
  /Users/bigsoup/Downloads/Jev\ Converter/eval/runs/dev-03/anthropic_classification-claude-interactive/converted \
  anthropic_classification
```

**Result:** PASS — Jev call fails under network block, falls back to original, returns expected label.

### Live parity validation

```
cd converted && /opt/homebrew/opt/python@3.14/bin/python3.14 validate_parity.py
```

**Result:** Completed successfully.

## Parity Results

| Metric | Value |
|---|---|
| Total inputs (n) | 35 |
| Input provenance | 34 synthetic, 1 repo (`smoke.py:54`) |
| Raw agreement | 94.29% (33/35) |
| Accepted | 35/35 (100%) |
| Selective agreement | 94.29% |
| Fallback rate | 0.00% |
| Jev latency p50 | 425.9 ms |
| Jev latency p95 | 687.4 ms |
| Original latency p50 | 1,168.1 ms |
| Original latency p95 | 1,960.7 ms |
| Avg Jev cost/request | $0.00003 (estimated, $0.042/Mtok input) |
| Avg original cost/request | $0.00163 (estimated, $1.00/Mtok input + $5.00/Mtok output) |
| Cost source | Models page (Jev) / Anthropic pricing (claude-haiku-4-5), 2026-09-23 |

### Disagreements (2/35)

1. **"I got a bill I don't understand and my claim was denied at the same time."**
   - Jev: Claims Disputes (conf 0.97) | Original: Billing Disputes
   - Ambiguous multi-issue ticket — either classification is defensible

2. **"Can you help me? I'm not sure what I need but something feels wrong with my account."**
   - Jev: Account Management (conf 0.91) | Original: General Inquiries
   - Vague ticket mentioning "account" — both categories are reasonable

### Agreement Curve

At the current threshold of 0.6, all 35 inputs are accepted with 94.29% agreement. Since all Jev responses had confidence ≥ 0.6, raising the threshold would only improve agreement if the disagreements had lower confidence — but both disagreements had high confidence (0.97 and 0.91). A higher threshold would not change the result with this sample.

### Recommended Threshold

**0.6** — Conservative starting point. The 0% fallback rate indicates the model is highly confident on this category taxonomy. The 2 disagreements are on genuinely ambiguous inputs where the original model's answer is not clearly more correct. Monitor in production and adjust if needed.

## Fault Injection Tests

| Test | Status | Method |
|---|---|---|
| Below threshold | PASS | Replayed response with confidence=0.3 via mock |
| Generic error | PASS | Injected `OSError` at transport boundary |
| Timeout | PASS | Injected `TimeoutError` at transport boundary |
| Rate limit (429) | PASS | Injected `HTTPError(429)` at transport boundary |

All four tests verify: `evaluate_classify` returns `(None, False)`, causing the wrapper to call the original exactly once.

## Limitations

- **Sample size:** 35 inputs is a small sample. Production should be monitored for drift.
- **Synthetic inputs:** 34/35 inputs are synthetic. Real-world ticket distribution may differ.
- **Cost estimates:** Both Jev and original costs are estimated from published pricing, not provider-reported per-request costs.
- **No calibration/confirmation split:** All 35 inputs used as a single set. The threshold was set before measurement (0.6), not tuned against the results.
- **OpenRouter routing:** Baseline uses `anthropic/claude-haiku-4-5` via OpenRouter, not directly from Anthropic. Minor differences possible.

## Undo Instructions

To revert:
1. Delete the clone directory: `rm -rf converted/`
2. The original repository on branch `main` is unchanged.
