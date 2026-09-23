# Jev Conversion Report

## Summary

**No good Jev opportunities here.**

The workflow generates a lasagna recipe using `generateObject` with OpenAI gpt-4o-mini. This is a pure GENERATION task — all output fields are free-form strings, not enumerated decisions. Jev does not generate prose or arbitrary text content.

## Details

| Item | Value |
|---|---|
| Source revision | `3abedb3` (main) |
| Output mode | Report only (no code changes) |
| Risk posture | Conservative |
| Jev provider | OpenRouter `typesafe/jev-1.13-20260917` |
| Jev model pin | `jev-1.13.0` |
| Sites audited | 1 |
| Sites converted | 0 |
| Approval scope | "Only pure DECISION sites with enumerated outputs" |

## Audited sites

### workflow.ts:7 — GENERATION — NOT A FIT

- **SDK:** Vercel AI SDK `generateObject`
- **Model:** `openai('gpt-4o-mini', { structuredOutputs: true })`
- **Prompt:** `"Generate a lasagna recipe."`
- **Schema:** `z.object({ recipe: z.object({ name: z.string(), ingredients: z.array(z.object({ name: z.string(), amount: z.string() })), steps: z.array(z.string()) }) })`
- **Downstream:** `result.object.recipe` is JSON-stringified and logged to stdout. `result.usage` and `result.finishReason` are logged separately.
- **Classification:** GENERATION — the model produces creative content (recipe name, ingredient names/amounts, cooking steps) as open-ended strings. Structured JSON does not make it a decision.
- **Fit:** NOT A FIT — Jev returns typed judgments over defined option sets. It cannot generate recipes, ingredient lists, or cooking instructions. No subcomponent of this call is a closed-set selection.
- **Action:** Leave unchanged.

## Test / smoke results

No conversion was performed, so no converted-code smoke test is applicable.

The original workflow smoke test can be run with:
```
node /Users/bigsoup/Downloads/Jev\ Converter/eval/smoke.cjs <OUTPUT_DIR> vercel_recipe
```

## Live validation

Live validation skipped — no sites were converted. No parity claim is made.

## Limitations

- Only one source file (`workflow.ts`) exists in this repository.
- The workflow is a single generation call with no decision component to convert.

## Undo instructions

No changes were made. Report-only mode produced artifacts in the output directory only. To discard: delete the converted output directory.

## Artifacts

| File | Purpose |
|---|---|
| `JEV_AUDIT.json` | Machine-readable audit with site classification, fit, and options |
| `JEV_CONVERSION_PLAN.md` | Audit table, approval resolution, and selected options |
| `JEV_CONVERSION_REPORT.md` | This report |
