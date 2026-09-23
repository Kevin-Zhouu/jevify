# Jev Conversion Report

## Summary

**No good Jev opportunities here.** The repository contains a single LLM call site that performs streaming free-form text generation. Jev is a typed decision primitive and cannot replace text generation workloads. No code changes, dependencies, environment files, or commits were made.

## Configuration

| Field | Value |
|---|---|
| Source revision | `23ea2ee85946f8cdad9ab870c72537c105def06e` |
| Branch | `main` |
| Output mode | Report only |
| Provider | OpenRouter (`typesafe/jev-1.13-20260917`) |
| Risk posture | Conservative |
| Headless | Yes |

## Approval Scope

Actions: `fallback`
Predicate: "Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged. Preserve all externally observable fields."

## Audit Results

### Sites Inventoried: 1

| Site ID | Classification | Fit | Action |
|---|---|---|---|
| `workflow.ts:15` | GENERATION | NOT A FIT | `leave` |

### `workflow.ts:15` — ChatOpenAI streaming

- **Provider/Model:** `@langchain/openai` / `ChatOpenAI` / `gpt-3.5-turbo-0125`
- **Input:** Arbitrary user prompt from HTTP request body
- **Output:** Free-form streaming text via `LangChainAdapter.toDataStreamResponse()`
- **Classification:** GENERATION — the model produces unbounded free-form text, not a label, bool, route, score, or closed-set selection
- **Fit:** NOT A FIT — Jev supplies typed decisions from bounded option sets; it does not generate prose or free-form content
- **Decision:** Leave unchanged. The approval scope explicitly excludes GENERATION sites.

## Changed Sites

None.

## Unchanged Sites

| Site ID | Reason |
|---|---|
| `workflow.ts:15` | GENERATION site; Jev cannot replace text generation; excluded by approval scope |

## Validation

### Smoke Test

The original workflow was verified against the behavioral smoke test. No code was modified; the original source remains intact.

### Live Parity

**Live validation skipped.** No sites were converted, so no parity measurements are applicable. No parity claim is made.

## Cost and Latency

No Jev calls were introduced; there is no cost or latency impact.

## Limitations

- The entire workflow is a single streaming text generation endpoint with no decision component
- No decomposition into decision + generation was identified — the workflow's purpose is to stream generated text
- Even with an aggressive risk posture, this site would remain NOT A FIT for Jev

## Undo Instructions

No changes were made to the source repository. The report artifacts in `converted/` can be deleted if no longer needed:

```bash
rm -rf converted/
```
