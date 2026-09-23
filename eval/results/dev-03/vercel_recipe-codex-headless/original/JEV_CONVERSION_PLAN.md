# Jev conversion plan

**No good Jev opportunities here**. The sole inference asks for a lasagna recipe. Its Zod schema defines open-ended strings for recipe name, ingredient names, ingredient amounts and steps. No substantive closed decision exists to convert. Replacing recipe generation with a Choice over canned recipes would alter behavior. Adding a router or guardrail would introduce new behavior and would not remove the necessary generation call.

The call at line 7 is the only local inference site. The provider factory at line 8 configures that same call; it is not a second inference. main() is invoked at line 30 and has no other consumers. No shared local SDK wrapper, other entrypoint, manifest, lockfile, tests or AGENTS.md was found in this repository. Dependencies and installed skills were excluded from application-site counting. External SDK internals are outside this repository audit.

The prompt is a short fixed source literal, not external input. Exact request token size was not measured. There is no existing adversarial-input mitigation to generalize to a public service; the fit verdict applies to this fixed example. Generated values, actual provider usage, finish reason, blank-line formatting and error handling must all remain intact.

## Setup and approval

Source revision: `df9cf64b2eb36e4e5bd3f1b428191d06d8366cbf`, branch `main`.
Output mode: **report**. Output directory: `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/vercel_recipe-codex-headless/original`.
The inactive branch and clone_path config fields do not authorize a branch or clone.
Preflight: git available; repository clean including untracked files; no errors.
Selected access: OpenRouter; `OPENROUTER_API_KEY` presence checked and true (value never read into output or saved).
Configured Jev pin: `typesafe/jev-1.13-20260917`; not invoked or integrated.
Risk: conservative. Upfront approval allows fallback only at pure DECISION sites with enumerated outputs, preserving every observable field; GENERATION and MIXED remain unchanged.
Approval resolves to zero conversion sites. Report mode independently prohibits code changes.
The authorized equivalent OpenRouter baseline route was not needed or used.

## Site options and selections

| Original site | Provider/model | Classification | Downstream | Fit | Option and scope | Benefit/economics | Risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| workflow.ts:7 | Vercel AI SDK / OpenAI gpt-4o-mini, structuredOutputs true | GENERATION | Recipe JSON to stdout at line 24, blank line 25, usage and finish reason at 26–27; rejection to console.error at 30 | NOT A FIT | leave; primitive none; entire call and consumers unchanged | Preserves behavior; no added cost/latency and no speculative savings | Existing generation correctness and provider risks remain |

Selection: leave workflow.ts:7 unchanged, consistent with the config's express exclusion of GENERATION. No fallback, decomposition, router or Jev-only implementation is selected.

## Execution plan

1. Stay on main in the original repository and write only the three report artifacts.
2. Run the supplied independent behavior smoke; no upstream project test command exists.
3. Verify source identity and artifact shape, then hand back the reports without a commit, push or PR.

Validation command:

```sh
node '/Users/bigsoup/Downloads/Jev Converter/eval/smoke.cjs' '/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/vercel_recipe-codex-headless/original' vercel_recipe
```

## Documentation basis

Live documentation reviewed on 2026-09-23. The web reader obtained the index but failed to retrieve individual pages; direct HTTPS retrieval using Python succeeded. Sources:

- [Index](https://docs.typesafe.ai/llms.txt)
- [API](https://docs.typesafe.ai/api.md), [Models](https://docs.typesafe.ai/models.md), [Confidence](https://docs.typesafe.ai/confidence.md)
- [Building guide](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md), [Coding agents](https://docs.typesafe.ai/introduction/coding-agents.md)
- [Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md), specifically the generation limitation
- [Intent routing](https://docs.typesafe.ai/patterns/intent-routing.md), [Confidence routing](https://docs.typesafe.ai/patterns/confidence-routing.md), [Composite scoring](https://docs.typesafe.ai/patterns/composite-scoring.md), [Fan-out](https://docs.typesafe.ai/patterns/fan-out.md)
- [Function calling cookbook](https://docs.typesafe.ai/cookbooks/function_calling.md): closed argument sets do not cover arbitrary recipe text.

Jev provides bounded typed judgments, not free-form recipe text. Confidence gating cannot repair that output mismatch. No price or performance measurement is inferred from documentation examples.
