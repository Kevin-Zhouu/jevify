# Jev Conversion Report

## Summary

| Field | Value |
|---|---|
| Source revision | `709e2e2` (branch `main`) |
| Output mode | Clone to `converted/` on branch `jev-convert/evaluation` |
| Provider | OpenRouter |
| Model pin | `typesafe/jev-1.13-20260917` |
| Risk posture | Conservative (fallback retained) |
| Credential env var | `OPENROUTER_API_KEY` |

## Approvals

- **`workflow.ts:6`**: Option A (fallback) approved. Scope: pure DECISION sites with enumerated outputs only. Preserve all externally observable fields.

## Changed Sites

### `workflow.ts:6` — genre classification (fallback)

- **Primitive:** Choice
- **Question:** "What is the genre of this movie based on its plot?" with options `action`, `comedy`, `drama`, `horror`, `sci-fi` (null descriptions — option names are self-descriptive).
- **Confidence threshold:** 0.7
- **Fallback triggers:** confidence < 0.7, missing `OPENROUTER_API_KEY`, HTTP errors, network errors, timeout (5s), malformed response, unknown label.
- **Diagnostics:** Answer path (`jev` or `original`) and model version logged to stderr. Token usage uses real Jev `input_tokens`/`output_tokens` on the Jev path; original `usage` object on the fallback path. `finishReason` is `'stop'` on the Jev path (System One always completes); original value on the fallback path.

### Files added/modified

| File | Change |
|---|---|
| `jevDecisions.ts` | **New** — decisions module owning model ID, endpoint, timeout, confidence threshold, genre question definition, and HTTP adapter with fallback logic |
| `workflow.ts` | **Modified** — imports from `jevDecisions`; tries Jev first, falls back to original `generateObject` on failure |
| `JEV_CONVERSION_PLAN.md` | **New** — conversion plan |
| `JEV_AUDIT.json` | **New** — machine-readable audit evidence |
| `JEV_CONVERSION_REPORT.md` | **New** — this report |

## Unchanged Sites

None — only one LLM call site exists.

## Test Results

### Smoke test (offline fallback)

```
$ node smoke.cjs converted/ vercel_enum
[jev] error, taking original path
[jev] answered: path=original model=gpt-4o-mini
PASS: observable TypeScript behavior and original-path fallback smoke
```

The smoke test stubs `fetch` to throw errors and `generateObject` to return a canned response. The converted code:
1. Attempts Jev via fetch → catches the error
2. Falls back to original `generateObject` → returns `'sci-fi'`
3. Logs `'sci-fi'` to console (asserted by smoke)
4. Exactly 1 call to original provider (asserted by smoke)

### Live validation

**Live validation skipped.** No `OPENROUTER_API_KEY` was available in the test environment. Conservative fallback is retained; no parity claim is made.

## Cost and Latency Expectations

- **Jev path (when accepted):** ~$0.042/Mtok input-only pricing (Jev 1.13). This request has minimal state (~30 tokens). Expected latency: low single-digit milliseconds per the System One model profile. Cost per request: negligible.
- **Fallback path:** Original `gpt-4o-mini` cost and latency, unchanged.
- **Cascade cost (miss):** Jev latency + original latency. Conservative posture means fallback is always available.

## Threshold Recommendations

- **0.7** is a reasonable starting threshold for a 5-option genre classification with clear, non-overlapping categories. Adjust after observing live confidence distributions on production inputs.
- With conservative fallback retained, a lower threshold (e.g. 0.5) would reduce fallback rate but accept more uncertain answers. A higher threshold (e.g. 0.9) prioritizes precision at the cost of more fallback traffic.

## Limitations

- Live parity was not measured; no `OPENROUTER_API_KEY` was available.
- The project has no test suite beyond the provided smoke test.
- Only one input (the hardcoded movie plot) was exercised.

## Undo Instructions

To revert to the original code:

```bash
# If using the clone:
rm -rf converted/

# If on the conversion branch in the same repo:
git checkout main
git branch -D jev-convert/evaluation
```
