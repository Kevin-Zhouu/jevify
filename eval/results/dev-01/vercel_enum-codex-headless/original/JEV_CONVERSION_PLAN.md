# Jev conversion plan

No good Jev opportunities here under the approved preservation contract.

## Setup and preflight

- Source: `709e2e2a68c8c389ace54287a676237fe8b561f2`, original branch `main`.
- Repository: `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-01/vercel_enum-codex-headless/original`. Inspection stayed inside this repository except the explicitly supplied config, permitted smoke file, and public vendor documentation. No eval labels, graders, other runs, or corpus files inspected.
- Git available; tracked and untracked status clean before audit; no applicable AGENTS.md found inside repository. Requested branch name valid and unused.
- Config output mode is `branch`: `jev-convert/evaluation`. The additional clone_path is inactive in branch mode; no clone created.
- Provider selection: OpenRouter, credential variable `OPENROUTER_API_KEY`, configured pin `typesafe/jev-1.13-20260917`. Conservative risk. No credential values read, printed or saved; no credential needed for this negative audit.
- Upfront approval permits fallback conversion only for pure enumerated DECISION sites, preserving every observable field. Isolated same-model OpenRouter baseline evaluation is authorized, but unnecessary with no converted sites.

## Inventory and options

| Original ID | Provider | Classification | Downstream | Fit | Option / primitive | Benefit | Risk |
|---|---|---|---|---|---|---|---|
| workflow.ts:6 | Vercel AI SDK / OpenAI gpt-4o-mini | DECISION | Genre stdout plus usage and finish reason; errors to console.error | NOT A FIT for full contract | leave / none | Preserve semantics and diagnostics; no claimed savings | Retains baseline costs and latency |

Exactly one inference call exists; there are no local inference wrappers or other consumers to double-count. `main()` executes on module load, is async, and returns no substantive value. The five possible labels are action, comedy, drama, horror and sci-fi. The literal movie plot is short English text (17 whitespace-delimited words), not a runtime untrusted input; no math, date comparison, non-text input or multi-hop computation is requested. No production adversarial-input mitigation exists, so semantic suitability is limited to this benign fixed fixture.

The result is DECISION, not MIXED: usage and finish reason are envelope diagnostics, not generated prose. Choice could represent the label. However, full integration suitability is blocked by the public diagnostic contract: The genre is a closed-set semantic decision over a benign fixed plot, but result.usage and result.finishReason are printed. System One documents real token usage but no equivalent generation finish reason. A faithful full diagnostic mapping is not established; synthesizing stop, dropping the field, or borrowing baseline metadata would violate the approved preservation scope.

Real input/output token counts could in principle be renamed and summed in code to match the usage fields. That does not establish a faithful finish-reason mapping. Successful HTTP completion is not evidence of the original generation stop condition. Always calling OpenAI just to obtain its diagnostics would add Jev cost/latency and couple another model's metadata to the label; it is not a useful replacement. A generic fallback option cannot cure missing metadata on accepted Jev responses.

## Approval resolution and implementation

The upfront predicate resolves to zero safe conversions. Leave `workflow.ts:6` unchanged; do not add an adapter, decisions module, dependencies or environment files. Write only this plan, the JSON audit and final report on the configured branch. No further permission is needed to retain the original code and produce the requested assessment. No push or PR.

## Documentation basis

Live docs read on 2026-09-23; the web tool could read the index and OpenRouter guide but failed on TypeSafe Markdown pages. Python 3.14 urllib fetched those live pages successfully. Embedded UI component code and lengthy cookbook examples were omitted from some displayed reads.

- [Index](https://docs.typesafe.ai/llms.txt)
- [API](https://docs.typesafe.ai/api.md), [Models](https://docs.typesafe.ai/models.md), [Confidence](https://docs.typesafe.ai/confidence.md), [Choice](https://docs.typesafe.ai/primitives/choice.md)
- [Building guide](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md), [Coding agents](https://docs.typesafe.ai/introduction/coding-agents.md), [Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md)
- [Intent routing](https://docs.typesafe.ai/patterns/intent-routing.md), [Confidence routing](https://docs.typesafe.ai/patterns/confidence-routing.md), [Composite scoring](https://docs.typesafe.ai/patterns/composite-scoring.md), [Fan-out](https://docs.typesafe.ai/patterns/fan-out.md)
- [Hierarchical classification cookbook](https://docs.typesafe.ai/cookbooks/hierarchical_classification.md)
- [OpenRouter TypeSafe SDK guide](https://openrouter.ai/docs/guides/community/typesafe-sdk): documents model, answers, usage and extra request/provider/cost metadata, without a finish reason.

The installed skill's conversion rules explicitly say: "If a faithful mapping is impossible, leave the site unchanged and explain why; do not delete the diagnostics to get a passing test."
