# Jev Conversion Report

## Source

- Repository: `anthropic_classification` (Anthropic cookbook — customer support ticket classification)
- Source SHA: `eff84f8f58d676d6b3b2eb21ae7b906300e2ef1b`
- Source branch: `main`
- Output mode: **clone** to `converted/`
- Output branch: `jev-convert/evaluation`

## Approvals

- Risk posture: **conservative** (fallback retained)
- Approved action: **fallback** for `workflow.py:83`
- Declined: jev_only, leave
- Scope: Only pure DECISION sites with enumerated outputs; preserve all externally observable fields
- Baseline routing: authorized via OpenRouter (same original model `anthropic/claude-haiku-4-5` routed as `anthropic/claude-haiku-4-5` through OpenRouter chat completions endpoint)

## Converted Sites

| Site | Classification | Primitive | Action | Model Pin |
|---|---|---|---|---|
| `workflow.py:83` | DECISION | Choice | fallback | `typesafe/jev-1.13-20260917` |

## Unchanged Sites

None — single-site workflow.

## Changed Files

| File | Change |
|---|---|
| `jev_decisions.py` | **New** — decisions module: model pin, 10 category criteria with `what`/`not_for`, confidence threshold (0.80), gate logic, response validation, `classify_with_jev()` wrapper |
| `workflow.py` | **Modified** — original `simple_classify` renamed to `_original_classify`; new `simple_classify` delegates through `classify_with_jev()` |
| `.env.example` | **New** — credential placeholders for `OPENROUTER_API_KEY` and `ANTHROPIC_API_KEY` |
| `scripts/validate_parity.py` | **New** — live paired validation script |
| `JEV_CONVERSION_PLAN.md` | **New** — audit, options, and selected plan |
| `JEV_AUDIT.json` | **New** — machine-readable audit |
| `JEV_PARITY.json` | **New** — live parity evidence |
| `JEV_CONVERSION_REPORT.md` | **New** — this file |

## Model and Provider

- Jev model: `typesafe/jev-1.13-20260917` (OpenRouter dated pin)
- Jev endpoint: `https://openrouter.ai/api/v1/systemone`
- Original model: `claude-haiku-4-5` (Anthropic SDK direct; OpenRouter `anthropic/claude-haiku-4-5` for evaluation baseline)
- Credential: `OPENROUTER_API_KEY` (present during validation)

## Test Commands and Results

### Smoke Test (offline, original-path fallback)

```
/opt/homebrew/opt/python@3.14/bin/python3.14 /path/to/eval/smoke.py OUTPUT_DIR anthropic_classification
```

**Result: PASS** — `simple_classify('Please explain my invoice.')` returns `'Billing Inquiries'` via the original Anthropic path when Jev network is unavailable. Original callable invoked exactly once.

### Live Paired Validation

```
cd converted && /opt/homebrew/opt/python@3.14/bin/python3.14 scripts/validate_parity.py
```

**Input provenance**: 68 unique inputs from `data/test.tsv` (repo fixtures). 20 calibration, 48 confirmation.

## Agreement Curve

| Threshold | Accepted | Selective Agreement | Fallback Rate |
|---|---|---|---|
| 0.50 | 66/68 | 81.82% | 2.94% |
| 0.60 | 62/68 | 85.48% | 8.82% |
| 0.70 | 58/68 | 87.93% | 14.71% |
| 0.75 | 57/68 | 89.47% | 16.18% |
| **0.80** | **55/68** | **90.91%** | **19.12%** |
| 0.85 | 52/68 | 90.38% | 23.53% |
| 0.90 | 48/68 | 89.58% | 29.41% |
| 0.95 | 39/68 | 94.87% | 42.65% |

### Selected Threshold: 0.80

- **Calibration** (n=20): 93.33% selective agreement, 25.0% fallback rate, 15 accepted
- **Confirmation** (n=48): 90.00% selective agreement, 16.67% fallback rate, 40 accepted
- **Combined** (n=68): 90.91% selective agreement, 19.12% fallback rate, 55 accepted
- **Raw agreement** (all inputs): 80.88%

## Latency

| Metric | Jev | Original (Haiku via OpenRouter) |
|---|---|---|
| p50 | 399.6 ms | 1076.6 ms |
| p95 | 697.1 ms | 1466.9 ms |

Jev is ~2.7x faster at p50.

## Cost

- **Jev pricing**: $0.042/M input tokens (output free). Source: TypeSafe docs, dated 2026-09-23.
- **Haiku pricing**: ~$0.80/M input, ~$4.00/M output (OpenRouter, approximate). Estimated from provider-reported usage.
- **Cost is estimated**, not provider-reported billing. Model pricing may change.

| Metric | Jev (68 inputs) | Original (68 inputs) |
|---|---|---|
| Total cost | $0.002902 | $0.039932 |
| Per-input avg | $0.0000427 | $0.000587 |

Expected cascade cost per input = Jev cost + (fallback_rate × original cost) = $0.0000427 + (0.19 × $0.000587) = ~$0.000154. ~3.8x cheaper than original-only.

## Fault Injection Tests

All four fault paths verified with executed assertions:

| Fault | Tested | Method |
|---|---|---|
| Below threshold | **Pass** | `gate_accepts()` with values at, below, and edge cases (NaN, inf, negative, >1, string) |
| Error (missing key) | **Pass** | Removed `OPENROUTER_API_KEY`; verified original called exactly once, correct result returned |
| Timeout | **Pass** | Set `JEV_TIMEOUT=0.001`; verified original called exactly once on timeout |
| Rate limit / HTTP error | **Pass** | Set invalid key; verified original called exactly once on auth error |

## Disagreement Analysis

13 of 68 inputs disagree between Jev and original. Patterns:

1. **Billing Inquiries vs Billing Disputes** (5 cases): Jev classifies tickets mentioning unexpected/incorrect charges as "Billing Disputes" where Haiku calls them "Billing Inquiries." Jev's structured `what`/`not_for` criteria make it more sensitive to complaint language. At threshold 0.80, 2 of these are accepted (high-confidence Jev disagreements); 3 fall back.

2. **Coverage/Policy category confusion** (4 cases): Ambiguous tickets about policy changes that also ask coverage questions. Split between Coverage Explanations, Policy Administration, and Policy Comparisons.

3. **Account Management vs Billing Inquiries** (3 cases): Paperless billing requests — arguably both categories apply.

4. **Claims Assistance boundary** (1 case): Jev routes to Coverage Explanations where original routes to Claims Assistance.

These are genuinely ambiguous categorizations. The conservative fallback ensures the original path handles disputed cases when confidence is low.

## Limitations

1. **68 test inputs is small** — sufficient to calibrate a threshold and observe patterns, but not production assurance. The distribution is the repo's test fixture set (synthetic insurance support tickets), not real production traffic.
2. **Cost estimates are approximate** — based on published pricing as of 2026-09-23; actual billing may differ.
3. **Baseline routing through OpenRouter** — the original Anthropic path was routed through OpenRouter for this evaluation. Minor behavioral differences between direct Anthropic SDK and OpenRouter routing are possible but unlikely for this simple classification task.
4. **Conservative fallback retained** — per risk posture, fallback to the original Anthropic path remains even though parity target (90%) is met. Jev-only mode was not approved.

## Undo Instructions

To revert to the original workflow:

```bash
# If using the clone:
rm -rf /path/to/converted

# The original repository at /path/to/original is unchanged.
```

The original repository was never modified. The clone at `converted/` contains all conversion artifacts. Deleting the clone directory fully reverts the conversion.
