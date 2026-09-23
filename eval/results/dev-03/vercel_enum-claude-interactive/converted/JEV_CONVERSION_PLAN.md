# Jev Conversion Plan

## Preflight

| Check | Result |
|---|---|
| Git clean | Yes |
| Original SHA | `4bc5e23` on `main` |
| Output mode | Clone → `converted/` on branch `jev-convert/evaluation` |
| Provider | OpenRouter (`OPENROUTER_API_KEY`) |
| Key present | Yes (verified by preflight) |
| Risk posture | Conservative (fallback retained permanently) |

## Audit summary

### Site inventory

| Site ID | File | Line | Provider | Classification | Fit | Downstream |
|---|---|---|---|---|---|---|
| `workflow.ts:6` | workflow.ts | 6 | `@ai-sdk/openai` / `gpt-4o-mini` | DECISION | FIT | `result.object` → console.log (genre); `result.usage` → logged; `result.finishReason` → logged |

### Classification rationale

The call selects one label from a closed enum of 5 genres over a hardcoded, trusted movie-plot string. This is a pure DECISION — no generation, no multi-hop reasoning, no adversarial input. Token usage and finish reason are envelope metadata.

## Approved options

| Site | Option | Action | Primitive |
|---|---|---|---|
| `workflow.ts:6` | A | `fallback` | Choice |

Approval scope: "Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged. Preserve all externally observable fields."

## Conversion design

### Wiring record

| Component | Symbol / path | Role |
|---|---|---|
| Original callable | `generateObject` from `ai` | Original LLM inference; unchanged |
| Converted public callable | `main()` in `workflow.ts` | Entry point with Jev gate |
| Decisions evaluator | `evaluateGenre()` in `jevDecisions.ts` | Jev HTTP call + validation + gate |
| Gate predicate | `shouldAccept()` in `jevDecisions.ts` | Pure confidence threshold check |
| Transport adaptation | OpenRouter System One endpoint via `fetch` | Authorized evaluation route |
| Authorization | User authorized OpenRouter for both Jev and baseline routing |

### Fallback structure

1. `evaluateGenre(moviePlot)` is called inside a try block
2. On acceptance (high confidence, valid response): use Jev answer, log Jev diagnostics
3. On rejection (low confidence, invalid response, error, timeout, missing key, rate limit): `jevResult` stays null
4. After the try block: if null, call original `generateObject` exactly once

### Diagnostics mapping

On the Jev-accepted path:
- `result.object` → `jevResult.genre` (identical genre string)
- `result.usage` → mapped from Jev `{input_tokens, output_tokens}` to Vercel SDK shape `{promptTokens, completionTokens, totalTokens}` using real Jev usage
- `result.finishReason` → adapter-owned `"stop"` status for a completed decision (documented in decisions module)

On the original path: all fields unchanged.

### Model pin

- Jev: `typesafe/jev-1.13-20260917` (OpenRouter dated pin, verified)
- Original: `gpt-4o-mini` via `@ai-sdk/openai` (unchanged)

### Confidence threshold

- Initial: 0.7
- Rationale: Conservative starting point for a low-stakes genre classification. Below this, fall through to original.
- To be calibrated during validation.

## Files changed

| File | Change |
|---|---|
| `jevDecisions.ts` | New — decisions module with model pin, question, criteria, threshold, gate, validation |
| `workflow.ts` | Modified — import decisions module, add Jev gate before original call |
| `.env.example` | New — placeholder for `OPENROUTER_API_KEY` |

## Undo instructions

```bash
# Delete the clone
rm -rf converted/
# Or if working in the same repo on a branch:
git checkout main
git branch -D jev-convert/evaluation
```
