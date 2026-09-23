# Jev conversion plan

No good Jev opportunities here.

## Setup and preflight

- Source/output repository: `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-01/vercel_recipe-codex-headless/original`.
- Original branch: `main`; revision: `5403b2818cf05879a0f0750fd84750cfc91ee03b`.
- Git preflight succeeded; tracked and untracked status was clean. Reads used `GIT_OPTIONAL_LOCKS=0`.
- Config selects `output.mode: report`, conservative risk, OpenRouter and `OPENROUTER_API_KEY`, with configured version `typesafe/jev-1.13-20260917`. No credentials were read or used.
- The config's branch and clone_path are inactive in report mode. No branch or clone is required or created; ref/path availability checks are inapplicable. Reports belong in this original repository.
- No application AGENTS.md, manifest, lockfile, tests or project test command exists in this checkout. Installed skill assets were excluded from application call-site discovery.
- Upfront approval permits fallback only for pure DECISION sites with enumerated outputs, leaves MIXED/GENERATION unchanged, and preserves observable fields. Report mode independently prohibits source changes.

## Audit and selectable options

| Original site | Provider/model | Class | Downstream | Fit | Option / primitive | Benefit and economics | Risk and scope |
| --- | --- | --- | --- | --- | --- | --- | --- |
| workflow.ts:7 | Vercel AI SDK generateObject → OpenAI gpt-4o-mini, structuredOutputs enabled | GENERATION | Recipe JSON to stdout, blank line, token usage and finish reason; rejection to console.error | NOT A FIT | leave / none | Preserve generation and diagnostics; unchanged latency/cost, no claimed savings | Existing model variability remains. Leave whole call and consumers intact. |

The fixed prompt is `Generate a lasagna recipe.` (25 characters); the request adds a small Zod schema. Exact wire tokens were not measured. `recipe.name`, each ingredient's `name`/`amount`, and every step are open strings, and arrays are variable length. This is neither extraction nor a closed-set decision. There is no runtime untrusted input in this fixture; no broader public-input robustness is inferred.

`main()` at line 6 wraps the single call at line 7; its invocation at line 30 is not another inference site. The provider factory at line 8 configures that same call. All local consumers are lines 24–27 and the rejection handler at line 30. SDK internals are external dependencies, not additional repository sites.

Jev cannot supply the generated recipe. Candidate extraction has no source recipe to copy from. Introducing a catalog, guardrail or router adds or changes behavior and is outside the bounded approval. Confidence thresholds cannot fix this output mismatch.

## Resolved selections and work

Approved conversion sites: **none**. Recommended selection: `leave` for `workflow.ts:7`, consistent with the explicit instruction to leave GENERATION unchanged. Actually converted sites: **none**.

Write only this plan, `JEV_AUDIT.json`, and `JEV_CONVERSION_REPORT.md`. Preserve workflow source, dependencies, environment files, diagnostics and git refs. Run the user-supplied independent smoke on the actual report-mode repository. No live parity calls are necessary with no conversions, and no parity artifact or measurements will be fabricated. Do not commit, push or open a PR in report mode.

## Documentation reviewed

The installed jevify entrypoint, configuration, audit, conversion, validation and vendored official TypeSafe skill were read. The live index was retrieved with the web tool; individual Markdown requests failed through that tool but succeeded using Python 3.14 urllib. Live pages retrieved on 2026-09-23:

- [api](https://docs.typesafe.ai/api.md)
- [models](https://docs.typesafe.ai/models.md)
- [confidence](https://docs.typesafe.ai/confidence.md)
- [concepts/how-to-build-with-system-one](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md)
- [introduction/coding-agents](https://docs.typesafe.ai/introduction/coding-agents.md)
- [model-jaggedness/jev-1.13](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md)
- [patterns/intent-routing](https://docs.typesafe.ai/patterns/intent-routing.md)
- [patterns/confidence-routing](https://docs.typesafe.ai/patterns/confidence-routing.md)
- [patterns/composite-scoring](https://docs.typesafe.ai/patterns/composite-scoring.md)
- [patterns/fan-out](https://docs.typesafe.ai/patterns/fan-out.md)
- [cookbooks/pre_parsed_value_extraction_cookbook](https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook.md)

The generation limitation is decisive. The extraction cookbook requires pre-existing candidates, which this workflow does not provide. No cookbook thresholds or timing claims were adopted as measurements.
