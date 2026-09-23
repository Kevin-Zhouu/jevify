# Jev Conversion Plan

## Source
- Repository: vercel/ai example `examples/ai-core/src/generate-object/openai-enum.ts`
- Source revision: `4bc5e23750b6af7d32147d2480a5bde33bb935cb` (main)
- Entrypoint: `workflow.ts`

## Preflight
- Mode: branch (`jev-convert/evaluation`)
- Provider: OpenRouter (`OPENROUTER_API_KEY`)
- Key present: yes
- Risk: conservative
- Repository clean: yes

## Audit

| Site | Provider | Downstream | Classification | Fit | Selected |
|------|----------|------------|----------------|-----|----------|
| `workflow.ts:6` | Vercel AI SDK / gpt-4o-mini | `result.object` logged as genre; `result.usage` logged; `result.finishReason` logged | DECISION | FIT | fallback (Choice) |

### Site: `workflow.ts:6` — `generateObject` enum classification

**Input**: Hardcoded movie plot string (trusted, no adversarial risk).
**Output**: One of `['action', 'comedy', 'drama', 'horror', 'sci-fi']`.
**Observable fields**: `object` (genre string), `usage` (`{promptTokens, completionTokens, totalTokens}`), `finishReason` (string).

**Classification**: DECISION — the model's substantive answer is one label from a closed set of 5 options.

**Fit**: FIT — bounded semantic routing over trusted text. No math, date comparison, multi-hop reasoning, generation, non-text input, or adversarial content.

### Selected option: `fallback` with Choice primitive

- Jev Choice classifies the movie plot into one of 5 genres
- Confidence threshold: 0.85 (conservative, calibrated during validation)
- On accepted: return Jev genre with real Jev usage adapted to Vercel format, `finishReason: 'stop'`
- On rejection/error/timeout/missing key: call original `generateObject` once, return its result unchanged
- All Jev config in single `jevDecisions.ts` module

## Wiring Record

| Component | Symbol | Location |
|-----------|--------|----------|
| Original callable | `generateObject({...})` | `workflow.ts:12-18` (passed as lambda) |
| Converted public callable | `classifyGenre()` | `jevDecisions.ts:classifyGenre` |
| Decisions evaluator/gate | `isAcceptedGenre()` | `jevDecisions.ts:isAcceptedGenre` |
| Question definition | `genreQuestion()` | `jevDecisions.ts:genreQuestion` |
| Model pin | `JEV_MODEL` | `jevDecisions.ts:JEV_MODEL` |
| Threshold | `GENRE_CONFIDENCE_THRESHOLD` | `jevDecisions.ts:GENRE_CONFIDENCE_THRESHOLD` |

### Transport adaptation
- Jev path: direct HTTP fetch to OpenRouter System One endpoint (`https://openrouter.ai/api/v1/systemone`)
- Original fallback: unchanged Vercel AI SDK `generateObject` call
- Baseline validation: original model `openai/gpt-4o-mini` routed through OpenRouter chat completions (authorized)

## Behavior Preservation

- **Signature**: `main()` remains async void, called at module level
- **Return type**: `{ object, usage, finishReason }` shape preserved on both paths
- **Usage**: Jev path maps real `input_tokens`/`output_tokens` to `promptTokens`/`completionTokens`/`totalTokens`; fallback returns original usage unchanged
- **finishReason**: Jev accepted path returns adapter-owned `'stop'` for completed decision; fallback returns original value
- **Logging**: `console.log` calls unchanged; decision path logged to stderr via `process.stderr.write`
- **Error propagation**: original path exceptions propagate unchanged; Jev errors trigger fallback
- **Diagnostics**: path, model, confidence logged on every decision (jev or original)

## Approvals
- Headless config approval: `fallback` action for pure DECISION sites with enumerated outputs
- Risk posture: conservative (fallback always retained)
- Baseline routing: authorized (`openai/gpt-4o-mini` via OpenRouter)
