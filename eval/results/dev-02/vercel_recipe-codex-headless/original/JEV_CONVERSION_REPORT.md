# Jev conversion report

No good Jev opportunities here.

The only inference site is `workflow.ts:7`: `generateObject` using OpenAI `gpt-4o-mini` with `structuredOutputs: true`. It generates a recipe, rather than selecting a bounded answer. The Zod object constrains structure but leaves all substantive strings open-ended.

| Original site | Provider | Classification | Downstream | Fit | Option, primitive, economics and risk |
| --- | --- | --- | --- | --- | --- |
| workflow.ts:7 | Vercel AI SDK / OpenAI gpt-4o-mini | GENERATION | Recipe JSON at line 24; blank line at 25; usage and finish reason at 26–27; errors at 30 | NOT A FIT | leave; none; unchanged inference cost/latency, no savings; retains existing generation variability and provider failures |

Source revision: `3ba7263b681fee55022bb3bacee9e8df6dc334d7`, branch `main`.
Resolved output mode: `report`. Output directory: `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/vercel_recipe-codex-headless/original`.
The supplied config's branch and clone_path are inactive in report mode. No clone or conversion branch is requested by the active mode.
Preflight: git available, clean including untracked files, no errors, selected provider `openrouter`, `OPENROUTER_API_KEY` present (presence only). Configured Jev pin: `typesafe/jev-1.13-20260917`; no Jev model was called or installed.
Risk posture: conservative. Upfront approval permits fallback only for pure DECISION sites with enumerated outputs, leaving GENERATION and MIXED unchanged and preserving observable fields. This predicate resolves to zero approved conversions. The leave recommendation follows that scope and report-only mode; no additional approval is required for these report artifacts.

The full runtime source is workflow.ts. There are no shared inference wrappers or additional consumers, no project manifest/test command, and no repository AGENTS.md found. Installed skill code is excluded from the workflow inventory. main() executes once at module load and awaits the SDK result; its rejection handler remains console.error. No signatures, return types, prompts, schemas, diagnostics or error handling were changed.
Input is the short fixed English literal `Generate a lasagna recipe.` at line 21 plus the schema; token count was not measured. This example has no external untrusted input entry point and no input-sanitization layer. The verdict concerns this fixture; no adversarial robustness is claimed. There are no source spans or finite recipe candidates for extraction. Adding routing, guardrails or a recipe catalog would introduce new behavior outside the approved scope and would not remove the need for generation.

Documentation reviewed live on 2026-09-23: the index was available through web; individual Markdown pages failed in that tool and were successfully retrieved using Python HTTPS. The conclusions use the current documentation, not invented API behavior:

- [API](https://docs.typesafe.ai/api.md), [Models](https://docs.typesafe.ai/models.md), and [Confidence](https://docs.typesafe.ai/confidence.md).
- [Building guide](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md) and [Coding agents](https://docs.typesafe.ai/introduction/coding-agents.md).
- [Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md): generation is explicitly unsuitable.
- [Intent routing](https://docs.typesafe.ai/patterns/intent-routing.md), [Confidence routing](https://docs.typesafe.ai/patterns/confidence-routing.md), [Composite scoring](https://docs.typesafe.ai/patterns/composite-scoring.md), and [Fan-out](https://docs.typesafe.ai/patterns/fan-out.md).
- [Pre-parsed extraction](https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook.md): selecting existing candidates does not supply this workflow's generated recipe.

Changed: three report artifacts only. Unchanged: workflow.ts and all upstream tracked files. Converted sites: none.

Validation:

- Executed `node '/Users/bigsoup/Downloads/Jev Converter/eval/smoke.cjs' '/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/vercel_recipe-codex-headless/original' vercel_recipe`: exit 0, `PASS: observable TypeScript behavior and original-path fallback smoke`.
- The smoke transpiles the actual entrypoint, supplies original-SDK doubles, disables network, and asserts one original call and recipe output containing lasagna. It does not establish live model parity or exhaustively assert diagnostics.
- Compared workflow.ts bytes against `git show HEAD:workflow.ts`: identical. This verifies preservation of the original diagnostics and error path in source, beyond the smoke's narrower assertions.
- Artifact shape verification command: `/opt/homebrew/opt/python@3.14/bin/python3.14 .agents/skills/jevify/scripts/check_artifacts.py '/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/vercel_recipe-codex-headless/original'`. Result recorded after execution below.

Live validation skipped: no converted sites, so the skill's no-conversion exception applies despite the selected key being present. No live inference requests or paired comparisons were performed, no request IDs or metric values were invented, and no JEV_PARITY.json was created. The isolated same-model baseline routing authorization was not needed or used.

Per-site threshold recommendation for workflow.ts:7: not applicable; leave generation unchanged. Sample count: no live pairs. Agreement, confidence curve, fallback rate, p50/p95 latency, cost and calibration/confirmation split: not measured, not applicable to this report-only outcome. No Jev wrapper exists, so Jev fault-injection tests were not performed. Smoke data comes from the supplied original-SDK fixture, not live inference.

Undo: from `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/vercel_recipe-codex-headless/original`, remove only `JEV_CONVERSION_PLAN.md`, `JEV_AUDIT.json` and `JEV_CONVERSION_REPORT.md`. The branch and source revision remain unchanged; no branch or clone deletion is needed.

Artifact checker result: exit 0, shape_valid=true, errors=[]. This validates artifact shape only. Final git diff was empty; git status listed only the three new report artifacts.
