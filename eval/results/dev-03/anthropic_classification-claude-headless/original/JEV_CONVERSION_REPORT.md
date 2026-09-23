# Jev Conversion Report

## Source

- **Repository:** `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/anthropic_classification-claude-headless/original`
- **Source revision:** `1c953f75ebe1580de909072ce9a73b8ab8f11d05` (main)
- **Output mode:** branch (`jev-convert/evaluation`)
- **Provider:** OpenRouter (`OPENROUTER_API_KEY`)
- **Model pin:** `typesafe/jev-1.13-20260917` (resolves to `jev-1.13.0`)
- **Risk posture:** conservative (fallback retained)

## Approvals

- **Headless config:** `actions: [fallback]`, scope: "Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged."
- **Baseline routing authorized:** yes — route `anthropic/claude-haiku-4-5` through OpenRouter for isolated evaluation adapters only.

## Converted Sites

### `workflow.py:83` — DECISION (FIT)

- **Original:** `client.messages.create()` via Anthropic SDK, model `claude-haiku-4-5`
- **Function:** `simple_classify(X)` — classifies customer support tickets into 10 insurance categories
- **Conversion:** Jev Choice with confidence-gated fallback
- **Primitive:** Choice (10 options matching the original categories)
- **Threshold:** 0.95 (calibrated on 35-case split, confirmed on 33-case split)

**Changes:**
1. `jev_decisions.py` (new) — decisions module with model pin, question, criteria, threshold, gate, and all validation
2. `workflow.py` — original `simple_classify` renamed to `_original_classify`; new `simple_classify` tries Jev first, falls back on low confidence/error/missing key
3. `.env.example` (new) — placeholder env vars

## Unchanged Sites

None. Only one LLM call site exists in this codebase.

## Test Commands and Results

### Smoke test (offline, original-SDK doubles)
```
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/bigsoup/Downloads/Jev\ Converter/eval/smoke.py \
  /Users/bigsoup/Downloads/Jev\ Converter/eval/runs/dev-03/anthropic_classification-claude-headless/original \
  anthropic_classification
```
**Result:** PASS

### Live paired validation
```
/opt/homebrew/opt/python@3.14/bin/python3.14 validate_jev.py
```
**Result:** 68 pairs, 0 errors

## Input Provenance

- 68 test cases from `data/test.tsv` (repository fixture, tab-separated, labeled)
- All inputs are curated insurance customer support tickets

## Agreement Curve

| Threshold | Selective Agreement | Accepted | Fallback Rate |
|---|---|---|---|
| 0.50 | 79.4% (27/34)* | 34/35 | 2.9% |
| 0.60 | 89.7% (26/29)* | 29/35 | 17.1% |
| 0.70 | 96.2% (25/26)* | 26/35 | 25.7% |
| 0.80 | 95.5% (21/22)* | 22/35 | 37.1% |
| 0.85 | 95.2% (20/21)* | 21/35 | 40.0% |
| 0.90 | 100.0% (16/16)* | 16/35 | 54.3% |
| **0.95** | **100.0% (15/15)*** | **15/35** | **57.1%** |

*Calibration set (n=35). Confirmation set at threshold 0.95: 100.0% (23/23), fallback rate 30.3%.

### Overall at selected threshold (0.95)

- **Raw agreement:** 80.9% (55/68)
- **Selective agreement:** 100.0% (38/38 accepted)
- **Fallback rate:** 44.1% (30/68 fall back to original)
- **Target (>=90%):** MET

## Latency

| Metric | Jev | Original (via OpenRouter) |
|---|---|---|
| p50 | 398 ms | 1204 ms |
| p95 | 582 ms | 1772 ms |

Jev is approximately 3x faster per request.

## Cost

- **Jev:** $0.042/Mtok input, output free (models.md, 2026-09-23)
- **Haiku 4.5:** estimated $0.80/Mtok input, $4.00/Mtok output (Anthropic public pricing, 2026-09-23)
- **Cost type:** estimated (not provider-reported)
- **Expected cascade cost:** Jev cost + 44.1% x original cost per call at threshold 0.95

## Fault Injection

| Fault | Passed |
|---|---|
| Below threshold | Yes |
| Generic error | Yes |
| Timeout | Yes |
| Rate limit (HTTP 429) | Yes |

All four faults exercise the actual `simple_classify` wrapper with a counting fallback sentinel, asserting exactly one original call and correct return value.

## Recommended Threshold

**0.95** — achieves 100% selective agreement on both calibration and confirmation sets. Higher fallback rate (44.1%) is acceptable under conservative posture since fallback preserves original behavior exactly.

Alternative: threshold 0.70 achieves 96.2% selective agreement with 25.7% fallback rate if a slightly lower accuracy tradeoff is acceptable.

## Limitations

- Cost figures are estimated from public pricing, not provider-reported per-request cost
- Baseline used OpenRouter transport adapter for `anthropic/claude-haiku-4-5` (authorized), not direct Anthropic API
- 68 test cases is a small sample; production workloads should validate on a larger, independently drawn set
- The 0.95 threshold causes ~44% of requests to still use the original model, limiting cost savings
- Jev request IDs come from OpenRouter response body `id` field

## Skipped Work

None. All planned work was completed.

## Undo Instructions

To revert to the original state:
```bash
git switch main
git branch -D jev-convert/evaluation
```
