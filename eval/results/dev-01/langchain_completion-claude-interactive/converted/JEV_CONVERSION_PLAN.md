# Jev Conversion Plan

## Source revision

- Commit: `e721efbb5530b5ab771b674fb843055696d8b1c0`
- Branch: `main`
- Repository status: clean

## Setup

- **Output mode:** Clone to sibling directory, branch `jev-convert/evaluation`
- **Access:** OpenRouter, env `OPENROUTER_API_KEY`, model `typesafe/jev-1.13-20260917`
- **Risk posture:** Conservative (retain original fallback everywhere)

## Audit summary

Single-file workflow (`workflow.ts`): a Next.js API route that accepts a free-form `prompt`, streams a GPT-3.5-turbo completion via LangChain's `ChatOpenAI`, and returns it through `LangChainAdapter.toDataStreamResponse`.

### LLM call inventory

| Site ID | File | Line | Provider | Downstream | Classification | Fit |
|---|---|---|---|---|---|---|
| S1 | `workflow.ts` | 15 | LangChain ChatOpenAI / OpenAI / gpt-3.5-turbo-0125 | Raw token stream to client | GENERATION | NOT A FIT |

### Classification rationale (S1)

- Unconstrained user prompt in, free-form streaming text out.
- No structured output, enum selection, routing, scoring, or extraction.
- Output consumed as raw token stream with no post-processing.
- Textbook GENERATION: Jev is unable to serve this category.

## Options presented

| Site | Option | Action | Primitive | Benefit | Risk |
|---|---|---|---|---|---|
| `workflow.ts:15` | 1 | leave | none | No action needed; no decision component exists | None |

## Approval received

- **Scope:** "Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged."
- **Actions authorized:** `fallback`
- **Result:** Zero sites match approval predicate. No DECISION sites exist.

## Conversion plan

**No conversions.** The approval scope restricts changes to pure DECISION sites, and the audit found none. The sole LLM call is GENERATION and is excluded by both the audit classification and the explicit approval scope.

No code changes, dependencies, environment variables, or git commits are produced.
