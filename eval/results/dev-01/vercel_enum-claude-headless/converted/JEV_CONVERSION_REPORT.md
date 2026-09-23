# Jev Conversion Report

## Source
- **Source revision**: `709e2e2a68c8c389ace54287a676237fe8b561f2` (main)
- **Output mode**: branch `jev-convert/evaluation`, cloned to `converted/`
- **Risk posture**: conservative (fallback always retained)
- **Provider**: OpenRouter
- **Model pin**: `typesafe/jev-1.13-20260917`

## Approvals
- Headless config approval: `fallback` action for pure DECISION sites with enumerated outputs.
- Resolved: `workflow.ts:6` approved for fallback conversion.

## Changed Sites

### workflow.ts:6 — generateObject (enum)
- **Classification**: DECISION
- **Primitive**: Choice
- **Action**: fallback (conservative)
- **Changes**:
  - Created `jevDecisions.ts`: single decisions module owning model pin (`typesafe/jev-1.13-20260917`), question definition (genre classification Choice with 5 options), confidence threshold (0.7), and a dependency-free HTTP adapter using Node fetch against the OpenRouter System One endpoint.
  - Modified `workflow.ts`: tries Jev Choice first; accepts on confidence ≥ 0.7; maps Jev usage (`input_tokens`/`output_tokens`) to Vercel AI SDK shape (`promptTokens`/`completionTokens`/`totalTokens`); preserves `finishReason` as `'stop'`; falls back to original `generateObject` on any failure, low confidence, or missing API key.
  - Diagnostic logging via `process.stderr.write` (does not alter stdout contract).
  - Unknown labels, non-finite confidence, malformed responses, timeouts, and missing credentials all trigger fallback.

## Unchanged Sites
None — only one LLM call site in the project.

## Test Commands and Results

### Smoke test
```
node smoke.cjs converted/ vercel_enum
```
**Result**: PASS
- Jev path correctly detected unavailable fetch (network mocked to fail), logged `[jev] path=original reason=jev-unavailable` to stderr.
- Fell back to original `generateObject` which returned `'sci-fi'`.
- Original provider called exactly once.
- `'sci-fi'` appeared in stdout output.
- Token usage and finish reason preserved from original path.

## Live Validation
**Live validation skipped** — no `OPENROUTER_API_KEY` was available during this conversion run. Conservative fallback is retained at all times. No parity claim is made.

## Recommended Thresholds
- `workflow.ts:6` (genre classification): 0.7 initial threshold. Should be calibrated with live paired measurements (≥30 unique inputs) when credentials are available. For a 5-option classification on clear movie plots, high agreement is expected.

## Fault Coverage (smoke)
- **Network unavailable**: ✓ (fetch mocked to throw; fallback triggered)
- **Missing key**: ✓ (classifyGenre returns null when `OPENROUTER_API_KEY` unset)
- **Unknown label**: ✓ (validated in code; returns null)
- **Non-finite confidence**: ✓ (validated in code; returns null)
- **Malformed response**: ✓ (null checks on answer shape)

## Limitations
- No live Jev inference was performed; parity is not established.
- Threshold (0.7) is an initial conservative value, not calibrated on domain data.
- The project has no package.json or dependency management; `jevDecisions.ts` uses a dependency-free HTTP adapter.
- Token usage on the Jev path maps Jev's `input_tokens`/`output_tokens` to the Vercel SDK's `promptTokens`/`completionTokens`/`totalTokens` shape. These are real Jev usage numbers, not original-model numbers.

## Cost Assumptions
- No cost data collected (live validation skipped).
- Expected: Jev Choice requests are typically cheaper than gpt-4o-mini generateObject for single-label classification. Conservative fallback adds Jev cost on every request (successful or not on the Jev path, original cost on fallback).

## Undo Instructions
To revert to the original state:
1. Delete the `converted/` directory, or
2. Within the clone: `git switch main` then `git branch -D jev-convert/evaluation`

The original repository at `original/` is unchanged on branch `main`.
