# Jev Conversion Plan — langchain_completion

## Preflight

| Check | Result |
|---|---|
| Source revision | `34f59ab` on `main` |
| Repository status | Clean |
| Output mode | Branch `jev-convert/evaluation` → clone path `converted/` |
| Provider | OpenRouter (`OPENROUTER_API_KEY`) |
| Model pin | `typesafe/jev-1.13-20260917` |
| Risk posture | Conservative |
| Key present | Yes (verified by preflight) |

## Audit Summary

One LLM call site found:

| Site ID | Classification | Fit | Selected Option |
|---|---|---|---|
| `workflow.ts:15` | GENERATION | Not a fit | **leave** |

## Approval

- **Approved actions**: `fallback`
- **Approved scope**: Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged. Preserve all externally observable fields.
- **Matching sites**: None. Zero DECISION sites exist in this repository.

## Selections

No sites selected for conversion. The single site (`workflow.ts:15`) is classified as GENERATION and is explicitly excluded by the approval scope.

## Conversion Work

None. No code changes, no dependencies added, no environment variables introduced.

## Validation Plan

- No live parity measurement required (no converted sites).
- Smoke test: `node smoke.cjs OUTPUT_DIRECTORY langchain_completion` to confirm original behavior is preserved.
