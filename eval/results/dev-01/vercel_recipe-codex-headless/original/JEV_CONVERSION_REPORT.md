# Jev conversion report

No good Jev opportunities here.

The sole site, `workflow.ts:7`, is GENERATION and NOT A FIT. It produces arbitrary recipe names, ingredient amounts and cooking instructions. A schema constrains shape, not the set of possible content. Leave the OpenAI call unchanged. See `JEV_CONVERSION_PLAN.md` for the full audit, options, documentation sources and approval resolution; `JEV_AUDIT.json` records the site and an empty `converted_sites` list.

## Scope and preservation

Source revision: `5403b2818cf05879a0f0750fd84750cfc91ee03b` on `main`. Output mode: report, in `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-01/vercel_recipe-codex-headless/original`. The approval predicate matches zero pure DECISION sites. No source, dependencies, environment files, prompts, provider routes, schema, logging, error semantics or git refs were changed. Only the three report artifacts were created. No commit, push, PR or clone was made.

Original behavior remains: async `main()` awaits `generateObject`, prints two-space-indented recipe JSON, a blank line, real provider usage and finish reason, and forwards rejections to `console.error`. No fabricated diagnostics or recipe catalog were introduced.

Configured potential Jev provider/model: OpenRouter / `typesafe/jev-1.13-20260917`; unused. Original provider/model remains OpenAI / `gpt-4o-mini`. The permission for isolated same-model baseline routing was not exercised.

## Validation actually performed

The supplied independent smoke was read, not edited, and executed against the actual output repository:

```sh
node /Users/bigsoup/Downloads/Jev\ Converter/eval/smoke.cjs "/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-01/vercel_recipe-codex-headless/original" vercel_recipe
```

Exit code: **0**. Output: `PASS: observable TypeScript behavior and original-path fallback smoke`.

This command transpiles and executes the actual TypeScript entrypoint with an ORIGINAL-provider SDK double and network access forced to fail. Its assertions verify no transpilation errors, exactly one original-provider call and recipe output containing lasagna. It does not independently assert the exact usage/finish log values or exercise the original provider's rejection path. Those source statements remain unchanged; source-diff verification establishes preservation, not live provider behavior. The smoke produced no repository artifacts. No upstream project test command exists and no dependency installation was performed.

**Live validation skipped**: no converted sites require live paired inference. No credential values were read, printed or saved. Live pair count: 0; input provenance, agreement curve, fallback rate, latency, cost, calibration/confirmation splits and request IDs: not measured / not applicable. No `JEV_PARITY.json` was created. No successful Jev inference, parity, or fallback fault coverage is claimed. Forced Jev low-confidence, timeout, rate-limit and malformed-answer tests are inapplicable because no Jev wrapper was added.

Threshold recommendation for `workflow.ts:7`: **none; leave unchanged**. No acceptance threshold can make typed decisions generate this free-form content. No cost savings or performance gains were measured or claimed.

## Undo

Delete only `JEV_CONVERSION_PLAN.md`, `JEV_AUDIT.json`, and `JEV_CONVERSION_REPORT.md` from this repository to remove this assessment. There is no conversion branch or clone to remove. Upstream tracked files and source revision remain unchanged.
