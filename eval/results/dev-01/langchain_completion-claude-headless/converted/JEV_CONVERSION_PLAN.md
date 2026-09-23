# Jev Conversion Plan

## Preflight

- **Source revision:** `23ea2ee85946f8cdad9ab870c72537c105def06e` (branch: `main`)
- **Repository status:** Clean (no untracked or modified files)
- **Output mode:** Report only (no code changes, no branch, no clone)
- **Report destination:** `converted/`
- **Provider:** OpenRouter (`typesafe/jev-1.13-20260917`)
- **Risk posture:** Conservative
- **Headless:** Yes

## Setup Answers (from config)

| Question | Answer |
|---|---|
| Output | Report only |
| Access | OpenRouter, env `OPENROUTER_API_KEY`, model `typesafe/jev-1.13-20260917` |
| Risk | Conservative |

## Approval Scope

Actions: `fallback`
Scope: "Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged. Preserve all externally observable fields."

## Audit Summary

### Site Inventory

| ID | Provider | Downstream | Classification | Fit | Options |
|---|---|---|---|---|---|
| `workflow.ts:15` | LangChain / ChatOpenAI / gpt-3.5-turbo-0125 | Streamed text returned via `LangChainAdapter.toDataStreamResponse()` to HTTP client | GENERATION | NOT A FIT | `leave` |

### Site Detail: `workflow.ts:15`

- **SDK:** `@langchain/openai` — `ChatOpenAI`
- **Model:** `gpt-3.5-turbo-0125`, temperature 0
- **Input origin:** `prompt` field from request body JSON (`req.json()`)
- **Output:** Free-form streaming text, returned as HTTP streaming response
- **Context size:** Single user prompt string (unbounded user input)
- **Untrusted-input mitigation:** None (raw user prompt passed directly to model)
- **Classification rationale:** The model generates arbitrary prose/text. The output is not a label, bool, route, score, or closed-set selection. It is unbounded free-form generation streamed to the client.
- **Fit rationale:** Jev supplies typed decisions; it does not generate prose, code, or free-form content. This site has no decision component. NOT A FIT.

### Options for `workflow.ts:15`

| # | Action | Primitive | Benefit | Risk |
|---|---|---|---|---|
| 1 | `leave` | None | No speculative savings. Site is pure text generation with no decision component. | None. Preserves correct behavior. |

## Conclusion

**No good Jev opportunities here.**

This workflow is a single streaming text generation endpoint. The LangChain `ChatOpenAI` model receives an arbitrary user prompt and streams free-form text back to the client. There is no decision, classification, routing, or closed-set selection anywhere in the workflow. Jev is designed for typed decisions from bounded option sets, not open-ended text generation.

The approval scope explicitly excludes GENERATION sites: "leave MIXED and GENERATION unchanged." This site is correctly classified as GENERATION and is left unchanged.

## Selected Conversions

None. No sites qualify for conversion.
