# Jev Conversion Plan

## Preflight

| Field | Value |
|---|---|
| Repository | `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/langchain_completion-claude-headless/original` |
| Source revision | `2ac85615cc36a346736e33ef460bfb5341950211` |
| Branch | `main` |
| Clean | Yes |
| Output mode | report |
| Provider | openrouter |
| Key env | `OPENROUTER_API_KEY` |
| Key present | Yes |
| Risk posture | conservative |

## Setup Answers

- **Output**: Report only (no code changes)
- **Access**: OpenRouter, `typesafe/jev-1.13-20260917`
- **Risk**: Conservative

## Audit Summary

| Site ID | Provider | Downstream | Classification | Fit | Selected Option |
|---|---|---|---|---|---|
| `workflow.ts:13` | LangChain ChatOpenAI / OpenAI / gpt-3.5-turbo-0125 | Streamed text returned to client | GENERATION | NOT A FIT | leave |

### Site: `workflow.ts:13` — `model.stream(prompt)`

**Classification: GENERATION**

This is a Next.js API route that accepts an arbitrary user prompt, sends it to GPT-3.5-turbo via LangChain's `ChatOpenAI`, and streams the generated text back to the client via `LangChainAdapter.toDataStreamResponse()`. The entire purpose is open-ended text generation — there is no label, boolean, route, enum selection, or structured decision anywhere in the pipeline.

**Fit: NOT A FIT**

- Jev supplies typed decisions (Choice, Score, Noul); it does not generate prose, code, or free-form content.
- The input is an arbitrary, untrusted user prompt with no adversarial mitigation.
- The output is streamed text with no parsing or decision extraction.
- There are no enumerated outputs or closed-set selections.

**Options:**

| # | Action | Primitive | Benefit | Risk |
|---|---|---|---|---|
| 1 | leave | none | No speculative savings; the call is free-form text generation which Jev cannot perform | None — preserves current behavior unchanged |

## Approval Resolution

The headless approval scope specifies: "Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged."

The single site (`workflow.ts:13`) is classified as GENERATION. Per the approval predicate, it is left unchanged. No sites qualify for conversion.

## Conclusion

**No good Jev opportunities here.** The workflow contains a single LLM call that performs streaming text generation from arbitrary user prompts. This is fundamentally incompatible with Jev's typed decision primitives. No code changes, dependencies, or environment modifications are warranted.
