# Jev Conversion Plan — vercel_recipe

## Source revision

Baseline commit: `6008b62` (branch `main`)

## Output mode

Branch `jev-convert/evaluation` in cloned directory.

## Preflight

- Repository clean: yes
- Branch available: yes
- `OPENROUTER_API_KEY`: present (value not inspected)
- Risk posture: conservative

## Audit summary

| ID | Location | Provider | Downstream | Classification | Fit |
|---|---|---|---|---|---|
| S1 | `workflow.ts:7` | Vercel AI SDK `generateObject` / OpenAI `gpt-4o-mini` | Full structured recipe object JSON-printed to stdout; usage and finishReason logged | GENERATION | NOT A FIT |

### Classification rationale

S1 uses `generateObject` with a Zod schema to produce a recipe. Every substantive field — `recipe.name`, `ingredients[].name`, `ingredients[].amount`, `steps[]` — is open-ended creative prose. Structured JSON does not change the nature of the output. The entire generated object is the product; nothing selects from it, routes on it, or uses it as a typed decision.

### Fit rationale

Jev is a System One model returning typed judgments (Choice, Score, Noul). It does not generate prose, recipes, code, or arbitrary strings. No decomposition rescues this site: the recipe name is generated (not selected), ingredients and amounts are creative content, and steps are instructional prose. No upstream candidates exist to select from.

## Options presented

| Site | Option | Action | Primitive | Benefit | Risk |
|---|---|---|---|---|---|
| S1 | A | leave | none | No speculative savings; preserves correctness | None |

**No good Jev opportunities here.**

## User approval

- Actions: `["fallback"]`
- Scope: "Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged. Preserve all externally observable fields."

## Selections applied

Zero sites match the approval predicate (no DECISION sites exist). No code changes made. No dependencies added. No environment variables required.

## Converted sites

None.
