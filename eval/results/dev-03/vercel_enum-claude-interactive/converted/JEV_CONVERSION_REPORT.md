# Jev Conversion Report

## Summary

| Field | Value |
|---|---|
| Source revision | `4bc5e23` on `main` |
| Output mode | Clone → `converted/` on branch `jev-convert/evaluation` |
| Provider | OpenRouter (`OPENROUTER_API_KEY`) |
| Jev model pin | `typesafe/jev-1.13-20260917` |
| Original model | `gpt-4o-mini` via `@ai-sdk/openai` |
| Risk posture | Conservative (fallback retained permanently) |
| Approvals | Option A (fallback) for `workflow.ts:6`; scope: pure DECISION sites with enumerated outputs only |

## Converted sites

### `workflow.ts:6` — `generateObject` enum classification

- **Classification:** DECISION
- **Primitive:** Choice (5 options: action, comedy, drama, horror, sci-fi)
- **Action:** fallback — Jev gate before original; on low confidence/error, original called once
- **Confidence threshold:** 0.7

### Files changed

| File | Change |
|---|---|
| `jevDecisions.ts` | New — decisions module: model pin, question, criteria, threshold, gate, response validation |
| `workflow.ts` | Modified — Jev gate before `generateObject`; on acceptance uses Jev answer with mapped diagnostics |
| `.env.example` | New — `OPENROUTER_API_KEY` placeholder |
| `validate_parity.py` | New — live parity validation script |

### Unchanged sites

None — there is only one LLM call site in this repository.

## Smoke test

```
$ node smoke.cjs converted vercel_enum
{"path":"original","reason":"error","jev_model":"typesafe/jev-1.13-20260917","model":"gpt-4o-mini"}
PASS: observable TypeScript behavior and original-path fallback smoke
```

The smoke test disables `fetch` (network unavailable). The Jev call fails, logs the error path to stderr, falls through to the original `generateObject` mock, which returns `'sci-fi'`. The genre is logged to stdout. `calls === 1` (exactly one original call).

## Live parity validation

### Input provenance

- 32 unique inputs total
- 1 from the repository (the hardcoded movie plot)
- 31 synthetic: 6 per genre (action, comedy, drama, horror, sci-fi) + 2 ambiguous/boundary cases
- Coverage: normal, genre-typical, boundary, and cross-genre cases

### Agreement

| Metric | Value |
|---|---|
| Total valid pairs | 32 |
| Accepted (confidence ≥ 0.7) | 30 |
| Fallback (confidence < 0.7) | 2 (6.2%) |
| Raw agreement (Jev vs original) | 31/32 (96.9%) |
| Selective agreement (accepted only) | 30/30 (100.0%) |

The 1 raw disagreement occurred on an ambiguous input that fell below the confidence threshold and would take the fallback path in production, so it does not affect the delivered answer.

### Latency

| Metric | Jev | Original (gpt-4o-mini) |
|---|---|---|
| p50 | 388.8 ms | 1371.6 ms |
| p95 | 741.9 ms | 1788.1 ms |

Jev is ~3.5x faster at p50 for this workload.

### Cost

- **Jev:** $0.042/M input tokens (output free). Estimated per-request cost for this ~40-token input: ~$0.000002
- **gpt-4o-mini:** $0.15/M input + $0.60/M output. Estimated per-request cost: ~$0.000005
- **Cascade cost:** For accepted decisions (93.8%), only Jev cost applies. For fallback (6.2%), both Jev + original costs apply.
- **Cost source:** Estimated from published pricing as of 2026-09-23. Not provider-reported.

### Threshold recommendation

**0.7** — validated on 32 inputs. At this threshold:
- 100% selective agreement (all accepted answers match the original)
- 6.2% fallback rate (low enough to realize latency/cost benefits)
- Conservative posture: fallback is retained permanently

Calibration and confirmation were performed on the same set (32 inputs is too small to split). This is noted as a limitation.

### Fault injection

All 8 fault injection tests executed and passed:

| Fault | Tested | Result |
|---|---|---|
| Below threshold | `shouldAccept(0.5)` returns false | PASS |
| Boolean confidence rejected | `shouldAccept(true)` returns false | PASS |
| NaN confidence rejected | `shouldAccept(NaN)` returns false | PASS |
| Infinity confidence rejected | `shouldAccept(Infinity)` returns false | PASS |
| Out-of-range rejected | `shouldAccept(-0.1)` and `shouldAccept(1.5)` return false | PASS |
| Generic error | Injected network error → null result, stderr logged | PASS |
| Timeout | Injected hanging fetch with 500ms timeout → null result, stderr logged | PASS |
| Rate limit (429) | Injected HTTP 429 response → null result, stderr logged | PASS |

## Diagnostics mapping

On the Jev-accepted path:
- `result.object` → `jevResult.genre` — identical genre string from Jev Choice answer
- `result.usage` → Jev `{input_tokens, output_tokens}` mapped to `{promptTokens, completionTokens, totalTokens}` — real Jev token counts
- `result.finishReason` → adapter-owned `"stop"` — documented in `jevDecisions.ts` as a completed decision status, not a native Jev field

On the original path: all fields unchanged from upstream.

## Limitations

1. **Small sample:** 32 inputs is the minimum required, not production assurance. Calibration and confirmation used the same set.
2. **Synthetic inputs:** 31 of 32 inputs are synthetic. Real-world distribution may differ.
3. **Single hardcoded prompt:** The original workflow has one hardcoded input. Parity on diverse inputs demonstrates the pattern but the actual production input never changes.
4. **Cost estimates:** Based on published pricing, not provider-reported `usage.cost`.

## Undo instructions

```bash
# Delete the clone entirely
rm -rf /Users/bigsoup/Downloads/Jev\ Converter/eval/runs/dev-03/vercel_enum-claude-interactive/converted

# Or if working on branches in the same repo:
git checkout main
git branch -D jev-convert/evaluation
```

## Reproduction

```bash
# Run smoke test (offline)
node /path/to/smoke.cjs /path/to/converted vercel_enum

# Run live parity (requires OPENROUTER_API_KEY)
cd converted
OPENROUTER_API_KEY=... python3 validate_parity.py
```
