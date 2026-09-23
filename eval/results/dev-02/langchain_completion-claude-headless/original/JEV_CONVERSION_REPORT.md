# Jev Conversion Report

## Source

| Field | Value |
|---|---|
| Repository | `langchain_completion` (from `vercel/ai`) |
| Source revision | `2ac85615cc36a346736e33ef460bfb5341950211` |
| Upstream path | `examples/next-langchain/app/api/completion/route.ts` |
| Output mode | report |
| Risk posture | conservative |
| Provider | openrouter (`typesafe/jev-1.13-20260917`) |
| Key present | Yes |

## Approvals

- Headless config: `jevify.config.yaml`
- Approval scope: "Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged."
- Approved actions: `[fallback]`

## Sites

### `workflow.ts:13` — GENERATION — NOT A FIT — left unchanged

The endpoint streams GPT-3.5-turbo completions from arbitrary user prompts via LangChain's `ChatOpenAI` and `LangChainAdapter.toDataStreamResponse()`. This is pure free-form text generation with no decision, classification, or structured output. Jev cannot substitute for text generation.

## Changed Sites

None.

## Unchanged Sites

| Site | Classification | Reason |
|---|---|---|
| `workflow.ts:13` | GENERATION | Free-form text generation; Jev cannot generate prose or stream content |

## Model / Provider

- Jev model: `typesafe/jev-1.13-20260917` (via OpenRouter)
- Original model: `gpt-3.5-turbo-0125` (via OpenAI / LangChain)

## Tests

No project test command available. No conversions were made, so no behavioral tests are applicable.

## Live Validation

**Live validation skipped** — no sites were converted, so no parity measurement is applicable. No parity claim is made.

## Limitations

- Single-file workflow with one LLM call site, entirely generation-focused.
- No decision, routing, classification, or structured output exists to convert.

## Undo Instructions

No changes were made to the repository. No undo is necessary.

Report artifacts written:
- `JEV_AUDIT.json` — machine-readable audit with site classifications
- `JEV_CONVERSION_PLAN.md` — audit details and approval resolution
- `JEV_CONVERSION_REPORT.md` — this file
