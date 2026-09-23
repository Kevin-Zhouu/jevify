# Jev Conversion Plan

## Preflight

| Field | Value |
|---|---|
| Source revision | `6013ff5396ee175c76aa5feddd7e93d903e667a7` |
| Source branch | `main` |
| Output mode | `branch` |
| Output branch | `jev-convert/evaluation` |
| Output repository | `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/vercel_enum-claude-headless/original` |
| Provider | OpenRouter |
| Key env | `OPENROUTER_API_KEY` |
| Key present | Yes |
| Model pin | `typesafe/jev-1.13-20260917` |
| Risk posture | Conservative (fallback retained) |

## Audit

### Site 1: `workflow.ts:6`

| Field | Value |
|---|---|
| SDK / Provider / Model | Vercel AI SDK / `@ai-sdk/openai` / `gpt-4o-mini` |
| Input origin | Fixed trusted string literal (movie plot classification prompt) |
| Downstream | `result.object` logged (line 16), `result.usage` logged (line 18), `result.finishReason` logged (line 19) |
| Classification | **DECISION** — selects one label from a closed 5-element enum |
| Context size | Small (~30 tokens of state) |
| Untrusted input | None — hardcoded prompt |
| Fit | **FIT** — bounded semantic classification over trusted text |

### Wrapper relationships

No shared wrappers. Single direct SDK call site.

## Options

### `workflow.ts:6`

| # | Action | Primitive | Benefit | Risk |
|---|---|---|---|---|
| 1 | `fallback` | Choice | Likely cheaper accepted decisions; Jev input-only pricing ($0.042/Mtok) vs gpt-4o-mini ($0.15/$0.60/Mtok). Faster for accepted decisions. | Serial misses add Jev latency + cost before original inference on fallback path. |
| 2 | `leave` | none | No speculative savings; no integration risk. | None. |

## Approval

Config predicate: `actions: [fallback]`, scope: "Only pure DECISION sites with enumerated outputs."

**Resolved selections:**
- `workflow.ts:6` → Option 1 (`fallback` with Choice primitive)

## Conversion Plan

1. Create `jevDecisions.ts` — single decisions module owning model ID, question, criteria, threshold, confidence gate, and usage adapter.
2. Modify `workflow.ts` — try Jev classification first via `jevDecisions.ts`; on success with sufficient confidence, log the Jev result with adapted usage/finishReason. On low confidence, error, timeout, or missing key, fall back to original `generateObject` unchanged.
3. Create `.env.example` with `OPENROUTER_API_KEY=` placeholder.
4. Preserve: stdout contract (`console.log` of genre label, usage object, finish reason), async behavior, error propagation.
