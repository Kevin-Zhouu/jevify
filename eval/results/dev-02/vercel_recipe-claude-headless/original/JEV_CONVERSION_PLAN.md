# Jev Conversion Plan

## Preflight

| Field | Value |
|---|---|
| Repository | `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/vercel_recipe-claude-headless/original` |
| Source SHA | `46b66f0338e60ab0d233244ca2cbf0d6e8faaa0a` |
| Branch | `main` |
| Clean | Yes |
| Output mode | report |
| Provider | openrouter |
| Key env | `OPENROUTER_API_KEY` |
| Key present | Yes |
| Risk posture | conservative |

## Audit

### Site 1: `workflow.ts:7`

| Field | Value |
|---|---|
| SDK / Provider / Model | Vercel AI SDK (`ai`) / OpenAI (`@ai-sdk/openai`) / `gpt-4o-mini` |
| Call | `generateObject()` with structured Zod schema |
| Input | Fixed hardcoded prompt: `"Generate a lasagna recipe."` |
| Schema fields | `recipe.name` (string), `recipe.ingredients[]` ({name, amount} — both strings), `recipe.steps[]` (string) |
| Downstream | `.object.recipe` → JSON-stringified to stdout; `.usage` and `.finishReason` printed as diagnostics |
| Context size | Minimal — single fixed string |
| Untrusted input | None |
| Classification | **GENERATION** |
| Fit | **NOT A FIT** |

**Reasoning:** Every value field in the schema is an open-ended string that requires the model to generate free-form content — a recipe name, ingredient names, amounts expressed as prose ("2 cups"), and multi-sentence cooking step descriptions. The Zod schema enforces structure but does not constrain the content to a closed set. Per Jev 1.13 jaggedness documentation: "Text generation is not supported; the model cannot reliably produce original content." Jev's primitives (Choice, Score, Noul) select from defined options or evaluate along described dimensions; they cannot produce novel prose, ingredient lists, or procedural instructions.

### Options

| # | Action | Primitive | Benefit | Risk |
|---|---|---|---|---|
| 1 | **leave** | none | No change. Avoids forcing a decision model onto a generation task. Zero integration risk. | None. The site is fundamentally generative and cannot be served by a System One model. |

## Conclusion

**No good Jev opportunities here.**

This workflow consists of a single LLM call site whose entire purpose is content generation — producing a structured recipe with free-form text fields. Jev is a decision model that returns typed judgments from closed option sets; it does not generate prose, creative content, or open-ended structured data. There are no decision, routing, classification, or extraction components in this workflow that could benefit from Jev integration.

## Selections

No conversions selected. The only available option is to leave the site unchanged. No code, dependency, or environment changes are required.
