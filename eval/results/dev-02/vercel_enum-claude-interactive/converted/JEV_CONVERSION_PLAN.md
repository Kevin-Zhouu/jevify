# Jev Conversion Plan

## Source revision

- Repository: `vercel_enum`
- Original SHA: `6013ff5396ee175c76aa5feddd7e93d903e667a7`
- Original branch: `main`

## Output mode

- Mode: **clone** to `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/vercel_enum-claude-interactive/converted`
- Branch: `jev-convert/evaluation`

## Preflight

- Clean: yes
- Provider: OpenRouter
- Key env: `OPENROUTER_API_KEY`
- Key present: yes

## Audit

| Site | File:Line | Provider | Downstream | Classification | Fit |
|------|-----------|----------|------------|----------------|-----|
| S1 | `workflow.ts:6` | Vercel AI SDK `generateObject` / OpenAI / `gpt-4o-mini` | `result.object` (genre label) printed to stdout; `result.usage` and `result.finishReason` also printed | DECISION | FIT |

## Approvals

- User approved: **fallback** for pure DECISION sites with enumerated outputs
- Scope: Only `workflow.ts:6` (the single DECISION site)
- Risk posture: **conservative** (retain original fallback permanently)

## Selected options

| Site | Action | Primitive |
|------|--------|-----------|
| `workflow.ts:6` | `fallback` | Choice |

## Conversion design

### New file: `jevDecisions.ts`

Single decisions module containing:
- **Model pin**: `typesafe/jev-1.13-20260917` (OpenRouter dated pin)
- **Endpoint**: `https://openrouter.ai/api/v1/systemone`
- **Question**: Choice — "What genre is this movie plot?" with 5 criteria: `{action: null, comedy: null, drama: null, horror: null, "sci-fi": null}`
- **Confidence threshold**: 0.7
- **Timeout**: 5000ms
- **Usage mapping**: Jev `input_tokens`/`output_tokens` → Vercel SDK `promptTokens`/`completionTokens`/`totalTokens`
- **finishReason mapping**: Adapter-owned `"stop"` for successful Jev decisions
- **Logging**: Path (`jev`/`original`), model, confidence, reason on every call via `process.stderr.write`

### Modified file: `workflow.ts`

- Extracts prompt to a variable
- Calls `classifyGenre(prompt, () => generateObject(...))` from `jevDecisions.ts`
- All `console.log` output preserved unchanged: `result.object`, `result.usage`, `result.finishReason`

### Fallback conditions

On any of: missing key, network error, timeout (AbortError), HTTP 429/5xx, non-200, invalid response shape, non-finite confidence, unknown label, invalid usage, confidence below threshold — calls original `generateObject` exactly once and returns its result.

### New file: `.env.example`

Documents `OPENROUTER_API_KEY` and `OPENAI_API_KEY` placeholders.
