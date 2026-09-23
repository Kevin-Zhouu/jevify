# Jev Conversion Report

## Source

| Field | Value |
|---|---|
| Source revision | `6013ff5396ee175c76aa5feddd7e93d903e667a7` |
| Source branch | `main` |
| Output mode | `branch` |
| Output branch | `jev-convert/evaluation` |
| Provider | OpenRouter |
| Model pin | `typesafe/jev-1.13-20260917` |
| Risk posture | Conservative (fallback always retained) |

## Approvals

Config predicate approval: `actions: [fallback]`, scope: "Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged. Preserve all externally observable fields."

Resolved: `workflow.ts:6` approved for `fallback` with Choice primitive.

## Changed Sites

### `workflow.ts:6` — Genre Classification (DECISION, FIT)

**Original:** `generateObject({ model: openai('gpt-4o-mini'), output: 'enum', enum: [...], prompt: ... })`

**Converted:** Jev Choice via OpenRouter → fallback to original `generateObject` on low confidence / error / timeout / missing key.

**Files changed:**
- `workflow.ts` — added Jev-first path with fallback to original
- `jevDecisions.ts` — new decisions module with model ID, question, criteria, threshold, gate, and usage adapter
- `.env.example` — `OPENROUTER_API_KEY=` placeholder

**Preserved contracts:**
- stdout: genre label, blank line, `Token usage:` with usage object, `Finish reason:` with finish reason
- Async behavior unchanged
- Error propagation via `main().catch(console.error)` unchanged
- All 5 enum values preserved as Choice criteria

## Unchanged Sites

None. Single-site repository.

## Test Commands and Results

### Smoke test (offline, original-path fallback)

```
node smoke.cjs OUTPUT_DIR vercel_enum
```

**Result:** PASS. Network is disabled (fault injection), Jev call fails gracefully, original `generateObject` answers once, `sci-fi` is logged.

### Live parity measurement

```
/opt/homebrew/opt/python@3.14/bin/python3.14 validate_parity.py
```

**Result:** 30 unique synthetic movie plots measured.

## Parity Results

### Agreement

| Metric | Value |
|---|---|
| Total inputs | 30 |
| Accepted (confidence >= 0.7) | 29 |
| Fallback taken | 1 (3.3%) |
| Selective agreement | 100.0% (29/29 accepted pairs match) |
| Overall agreement | 96.7% (29/30 total) |

### Latency (ms)

| Metric | Jev | Original (gpt-4o-mini) |
|---|---|---|
| Min | 314 | 688 |
| Max | 891 | 2133 |
| Mean | 446 | 1235 |
| Median | 409 | 1170 |

Jev is approximately 2.8x faster on average.

### Cost

- Jev: $0.042/Mtok input only (output free). Source: docs.typesafe.ai/models, dated 2026-09-23.
- gpt-4o-mini via OpenRouter: $0.15/Mtok input, $0.60/Mtok output. Source: openrouter.ai, dated 2026-09-23.
- Expected cascade cost = Jev cost + (fallback fraction × original cost) = ~$0.018/Ktok + (3.3% × ~$0.021/Ktok) ≈ ~$0.019/Ktok per request.

### Fault Injection

| Fault | Executed | Pass |
|---|---|---|
| below_threshold | Yes — gate function tested with confidence 0.3, 0.69, None, 0.7 | PASS |
| error | Yes — real request to invalid endpoint | PASS |
| timeout | Yes — real request with 1ms timeout | PASS |
| rate_limit | Yes — real request with invalid auth | PASS |

### Input Provenance

All 30 inputs are synthetic movie plot descriptions. Provenance: `synthetic`. Covers clear single-genre (action, comedy, drama, horror, sci-fi), genre-blending (ambiguous), boundary (documentaries, experimental), and out-of-domain cases.

### Calibration / Check Split

All 30 inputs used for both calibration and measurement. The threshold of 0.7 was pre-set from the decisions module, not tuned on this data. At this threshold: 29/30 accepted, 100% selective agreement.

### Threshold Recommendation

**0.7** — At this threshold, 96.7% of inputs are accepted with 100% agreement with the original model. The single fallback case was an ambiguous genre-blending plot. Conservative posture retains fallback permanently.

## Limitations

1. **Small sample size:** 30 inputs is a minimum estimate, not production assurance.
2. **Synthetic inputs only:** No real user data tested. Results are scoped to this distribution.
3. **Conservative posture:** Fallback is always retained; Jev-only path not authorized.
4. **Fixed trusted input:** The original workflow uses a hardcoded prompt. Real-world deployment with user-supplied input would need adversarial robustness testing.
5. **Cost estimates are approximations:** Based on published pricing as of 2026-09-23; actual costs may vary.

## Undo Instructions

To revert to the original workflow:

```sh
git switch main
git branch -D jev-convert/evaluation
```

This restores the original branch. The conversion branch can be safely deleted as the original `main` branch is unchanged.
