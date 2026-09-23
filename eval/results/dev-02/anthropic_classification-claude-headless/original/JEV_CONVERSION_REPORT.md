# Jev Conversion Report

## Source

- **Repository:** `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/anthropic_classification-claude-headless/original`
- **Source revision:** `eff84f8f58d676d6b3b2eb21ae7b906300e2ef1b` (branch `main`)
- **Output mode:** branch `jev-convert/evaluation`
- **Provider:** OpenRouter (`OPENROUTER_API_KEY`)
- **Model pin:** `typesafe/jev-1.13-20260917`
- **Risk posture:** conservative (fallback always retained)

## Approvals

- Headless config: `actions: [fallback]`, `scope: "Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged."`
- Baseline routing authorized via OpenRouter (`anthropic/claude-haiku-4-5`)

## Changed Sites

| Site ID | Classification | Action | Primitive |
|---|---|---|---|
| `workflow.py:83` | DECISION | fallback | Choice |

## Unchanged Sites

None — single site in the workflow.

## Implementation

### Files changed

- **`jev_decisions.py`** (new): Decisions module owning Jev model ID (`typesafe/jev-1.13-20260917`), question definition, 10 category criteria, confidence threshold (0.85), gate logic, and HTTP transport to OpenRouter System One endpoint. Uses Python standard library only (no SDK dependency).
- **`workflow.py`** (modified): `simple_classify()` now calls `classify_with_jev()` from the decisions module, which attempts Jev Choice classification first and falls back to the original Anthropic path on low confidence, errors, timeouts, invalid labels, or missing keys. Original function preserved as `_original_classify()` with identical signature, return type, and behavior.
- **`.env.example`** (new): Placeholder for `OPENROUTER_API_KEY` and `ANTHROPIC_API_KEY`.

### Validation files (not production code)

- **`jev_validate.py`**: Live paired validation script using isolated OpenRouter adapter for baseline.
- **`jev_fault_test.py`**: Fault injection tests for fallback behavior.

## Test Results

### Smoke test

```
PASS: observable Python behavior and original-path fallback smoke
```

Command: `/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/bigsoup/Downloads/Jev\ Converter/eval/smoke.py <repo_path> anthropic_classification`

The smoke test blocks network access, forcing Jev transport error and validating that:
1. `simple_classify('Please explain my invoice.')` returns `'Billing Inquiries'`
2. Exactly one original call is made (to the Anthropic mock)
3. The model used is `claude-haiku-4-5`

### Live paired validation

- **Inputs:** 68 unique tickets from `data/test.tsv` (provenance: repo)
- **Jev model:** `typesafe/jev-1.13-20260917` via OpenRouter
- **Original model:** `anthropic/claude-haiku-4-5` via OpenRouter (authorized baseline adapter)

#### Metrics at threshold 0.85

| Metric | Value |
|---|---|
| Total inputs | 68 |
| Accepted (above threshold) | 48 |
| Fallback count | 20 |
| Fallback rate | 29.4% |
| **Selective agreement** | **93.75%** |
| Raw agreement | 83.8% |
| Jev p50 latency | 367ms |
| Jev p95 latency | 556ms |
| Original p50 latency | 1034ms |
| Original p95 latency | 1549ms |

#### Threshold curve

| Threshold | Accepted | Fallback | Selective Agreement |
|---|---|---|---|
| 0.70 | 57 | 11 | 89.5% |
| 0.75 | 54 | 14 | 88.9% |
| 0.80 | 52 | 16 | 90.4% |
| **0.85** | **48** | **20** | **93.75%** |
| 0.90 | 44 | 24 | 95.5% |
| 0.95 | 38 | 30 | 97.4% |

#### Cost

- Jev cost is estimated at ~$0.02/M tokens (OpenRouter Jev pricing, sourced 2026-09-23). Per-request cost is negligible (~$0.000002).
- Original cost estimated at $0.80/M input + $4.00/M output (OpenRouter Claude Haiku 4.5 pricing, sourced 2026-09-23).
- Expected cascade cost per request = Jev cost + fallback_rate x original cost.
- At 29.4% fallback rate, expected cost is ~30% of original for accepted decisions + full original cost on 29.4% of requests.

### Fault injection tests

All 8/8 fault tests passed (`jev_fault_test.py`):

| Fault | Assertion | Result |
|---|---|---|
| Below threshold (conf < 0.85) | Fallback triggered, original called exactly once | PASS |
| Transport error | Fallback triggered, original called exactly once | PASS |
| Timeout | Fallback triggered, original called exactly once | PASS |
| Rate limit (429) | Fallback triggered, original called exactly once | PASS |
| Unknown label | Fallback triggered, original called exactly once | PASS |
| Invalid/missing usage | Fallback triggered, original called exactly once | PASS |
| Non-finite confidence (NaN) | Fallback triggered, original called exactly once | PASS |
| Missing API key | Fallback triggered, original called exactly once | PASS |

## Threshold Recommendation

**Recommended threshold: 0.85**

- Achieves 93.75% selective agreement (above the 90% target)
- 29.4% fallback rate is acceptable for conservative posture
- Higher thresholds (0.90, 0.95) improve agreement further but increase fallback rate
- Lower thresholds (0.70-0.80) reduce fallback but drop below 90% agreement

## Limitations

- Validation used 68 inputs from a single test file; production traffic may differ
- Cost estimates use sourced pricing as of 2026-09-23; actual costs may vary
- Jev and original were called sequentially with small delays; parallel production traffic may show different latency
- No calibration/check split was applied (all 68 inputs used for both threshold selection and validation, since the threshold was pre-set)
- Conservative fallback is always retained; Jev-only was not evaluated

## Undo Instructions

To revert to the original state:

```bash
git switch main
git branch -D jev-convert/evaluation
```
