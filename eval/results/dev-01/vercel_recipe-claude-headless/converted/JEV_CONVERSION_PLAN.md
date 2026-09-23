# Jev Conversion Plan

## Preflight

| Item | Value |
|---|---|
| Source revision | `3abedb3` (main) |
| Output mode | Report only |
| Risk posture | Conservative |
| Provider | OpenRouter (`typesafe/jev-1.13-20260917`) |
| Repository status | Clean, no untracked files |

## Audit summary

**No good Jev opportunities here.**

The repository contains a single LLM call site. It is a pure generation task with no decision component.

## Site inventory

| ID | Provider | Downstream | Classification | Fit | Options |
|---|---|---|---|---|---|
| `workflow.ts:7` | Vercel AI SDK / OpenAI gpt-4o-mini | Recipe printed to stdout; usage and finish reason logged | GENERATION | NOT A FIT | Leave unchanged |

### workflow.ts:7 — `generateObject`

**What it does:** Calls `generateObject` with a Zod schema to generate a complete lasagna recipe. The schema defines `recipe.name` (string), `recipe.ingredients` (array of `{name: string, amount: string}`), and `recipe.steps` (array of string). All fields are open-ended `z.string()` — none are enumerations or closed sets.

**Why NOT A FIT:**

1. **Generation, not decision.** The prompt "Generate a lasagna recipe" asks the model to produce creative prose content in structured form. The audit rules state: "Structured JSON does not make it a decision." Recipe names, ingredient lists, and cooking steps are arbitrary free-form text.
2. **No enumerated outputs.** Every schema field accepts unbounded string values. There is no closed set of options for Jev to select among.
3. **Jev cannot generate text.** Jev returns typed judgments (Choice, Score, Noul) over defined options. It does not produce recipes, descriptions, or any open-ended content.

**Option: Leave unchanged.**
- Primitive: None
- Benefit: None — no Jev opportunity exists
- Risk: None — original behavior preserved
- Economics: Original gpt-4o-mini cost only

## Approval resolution

The headless config approves actions on "Only pure DECISION sites with enumerated outputs." No sites match this predicate. Zero sites selected for conversion.

## Selections

None. No code changes, dependencies, environment files, or git commits are produced in report mode with a negative audit.
