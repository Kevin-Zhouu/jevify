# Jev Conversion Report — openai_demo

## Summary

**Outcome: No conversion performed.** All 3 LLM call sites are pure text generation. Zero sites qualify under the approved scope ("only pure DECISION sites with enumerated outputs").

## Audit

| Site | Line | Classification | Fit | Action |
|------|------|---------------|-----|--------|
| `workflow.py:10` | 10 | GENERATION | NOT A FIT | Leave |
| `workflow.py:23` | 23 | GENERATION | NOT A FIT | Leave |
| `workflow.py:42` | 42 | GENERATION | NOT A FIT | Leave |

## Reasoning

This workflow is a demo of the OpenAI Python SDK. Every call site asks the model to produce free-form prose ("Say this is a test", "How do I output all files in a directory using Python?") and prints the result. None select from a closed set, evaluate a condition, or score content.

Jev is a System One decision model returning typed primitives (Choice, Score, Noul) with calibrated probabilities. It is not a text generator. Converting any site would change the workflow's fundamental semantics.

Additional blockers at specific sites:
- **Site 2 (line 23):** Uses SSE streaming, which Jev's `/v1/systemone` endpoint does not support.
- **Site 3 (line 42):** Accesses `response.request_id` (raw HTTP envelope metadata), an SDK transport concern outside Jev's API contract.

## Approval & Scope

- **Approved actions:** fallback
- **Approved scope:** Only pure DECISION sites with enumerated outputs
- **Sites matching scope:** 0 of 3

## Parity

No parity measurement was performed — there are no converted sites to validate.

## Files

- `JEV_AUDIT.json` — structured audit with per-site classification and options
- `JEV_PARITY.json` — parity stub (no measurements taken)
- `workflow.py` — unchanged (no modifications made)
