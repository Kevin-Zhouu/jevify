# Jev conversion plan

Source revision: `709e2e2a68c8c389ace54287a676237fe8b561f2`, branch `main`.
Output: sibling clone at `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-01/vercel_enum-codex-interactive/converted`, branch `jev-convert/evaluation`.
Preflight: source clean including untracked files; branch name valid and unused; output path absent. No repository AGENTS.md, dependency manifest or project test command found. Original repository remains untouched.

## Scope and approval

The user selected only `fallback` for pure DECISION sites with enumerated outputs, conditional on preserving all externally observable fields. Conservative fallback must retain the exact original provider, model, prompt and parsing. Other options were declined. This predicate selects `workflow.ts:6` for conditional conversion assessment; it does not waive the diagnostic requirement. Setup answers in the conversation were used; the config was not read.

Selected access: OpenRouter, credential variable `OPENROUTER_API_KEY`, versioned model `typesafe/jev-1.13-20260917`. Baseline routing authorization is limited to isolated evaluation adapters using the same original model and original prompts/parsing. No production provider switch is authorized.

## Audit and options

| Original site | Classification | Provider | Downstream | Fit |
| --- | --- | --- | --- | --- |
| workflow.ts:6 | DECISION | Vercel AI SDK / OpenAI gpt-4o-mini, structured outputs | Prints enum, blank line, usage object and finishReason; rejection reaches console.error | Semantic fit for Choice; blocked by diagnostic contract |

One inference site, no shared wrappers. Input is a short hardcoded English movie plot; options are action, comedy, drama, horror and sci-fi. There is no adversarial-input mitigation; semantic suitability only covers the benign fixed fixture. Metadata does not make this MIXED. No GENERATION or EXTRACTION sites were found.

| Option | Primitive | Benefit | Risk | Selection |
| --- | --- | --- | --- | --- |
| fallback | Choice | Accepted decisions could avoid original inference; expected cost = Jev cost + fallback fraction × original cost | Disagreement; serial fallback overhead; must preserve truthful diagnostics | Approved conditionally, blocked |
| leave | none | Existing observable contract retained | No migration benefit | Declined as an elective option; unchanged source is required by failed conversion condition |

## Compatibility decision

No good Jev opportunities here under the approved requirement to preserve diagnostics. The [TypeSafe API](https://docs.typesafe.ai/api) documents model, answers and token usage. The [OpenRouter System One contract](https://openrouter.ai/docs/guides/community/typesafe-sdk) additionally documents id, provider and usage.cost, but no finish reason or documented adapter mapping. Reviewed live during this task. The Markdown API URL failed; the HTML API page succeeded.

A synthetic stop reason would invent provider semantics; omitting the printed diagnostic would alter public behavior. Running the original model merely to supply metadata would not establish Jev diagnostic compatibility. The skill conversion rules require leaving the site unchanged if a faithful mapping cannot be established. Therefore do not add a Jev adapter, dependencies, environment files or a threshold. Record converted_sites as empty.

## Validation plan

Run the user-supplied independent behavior smoke on the clone and verify source bytes match. Since there are no converted sites, no live paired requests or conversion fault-injection tests are applicable. Commit only audit, plan and report. Never push or create a PR.
