# Jev Conversion Plan

## Preflight

- **Source revision:** `709e2e2` (branch `main`)
- **Repo status:** Clean, no untracked files
- **Output mode:** Clone to `converted/` on branch `jev-convert/evaluation`
- **Provider:** OpenRouter (`OPENROUTER_API_KEY`)
- **Model pin:** `typesafe/jev-1.13-20260917`
- **Risk posture:** Conservative (fallback retained)

## Audit Summary

### Site: `workflow.ts:6`

| Field | Value |
|---|---|
| Provider | OpenAI via Vercel AI SDK (`gpt-4o-mini`) |
| Call | `generateObject({ output: 'enum', enum: [...], prompt })` |
| Classification | DECISION |
| Fit | FIT — closed 5-label genre classification, fixed trusted prompt |
| Downstream | `result.object` (genre label), `result.usage` (token counts), `result.finishReason` (diagnostic) |

## Approved Options

| Site | Option | Action |
|---|---|---|
| `workflow.ts:6` | A | **fallback** — Jev Choice with confidence gate; original `generateObject` retained as fallback |

## Conversion Steps

1. Create `jevDecisions.ts` — single decisions module owning model ID, question definition, confidence threshold, and fallback wrapper.
2. Modify `workflow.ts` — import fallback wrapper from decisions module; replace direct `generateObject` call with Jev-first logic that falls back to original on low confidence, errors, timeouts, or missing credentials.
3. Preserve all observable fields: `result.object` (genre label), `result.usage`, `result.finishReason` — using real Jev values on the Jev path and original values on the fallback path.
4. Log answer path (`jev` or `original`) and model version to stderr for diagnostics.
5. Run smoke test to verify fallback path works offline.

## Declined / Unchanged

- No other sites exist. Option B (leave) was declined.
