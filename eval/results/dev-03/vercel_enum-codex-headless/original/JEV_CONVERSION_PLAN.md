# Jev conversion plan

## Setup and authorization

Source: `4bc5e23750b6af7d32147d2480a5bde33bb935cb`, branch `main`.
Read-only preflight: clean including untracked files, git available, requested branch unused,
OpenRouter key present (presence only). No applicable AGENTS.md found in this repository.
Output mode: branch `jev-convert/evaluation` in
`/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/vercel_enum-codex-headless/original`.
The inactive clone_path is ignored. All writes and commits target this directory.
The explicitly supplied `../jevify.config.yaml` authorizes fallback only for pure enumerated
DECISION sites, conservative risk, and isolated evaluation of the same baseline model via
OpenRouter. Production fallback remains OpenAI. No push or PR.

## Complete audit and selectable options

| Original site | Provider | Class | Downstream | Fit | Options |
|---|---|---|---|---|---|
| workflow.ts:6 | Vercel AI SDK generateObject / OpenAI gpt-4o-mini | DECISION | main prints object, blank line, usage, finishReason at original lines 16–19 | FIT for fixed trusted fixture | fallback / Choice: selected; leave / none: available |

One provider call; no shared local wrappers or additional consumers exist in the baseline.
The input is a fixed short English movie plot (one sentence, well below documented context
limits). It needs semantic genre selection, not generation, arithmetic, date ordering,
extraction, non-text processing, or multi-hop reasoning. Usage and finishReason are
observable envelope metadata, not generated reasoning; classification remains DECISION.
There is no public input entrypoint or existing prompt-injection defense. Eligibility is
limited to this benign fixture distribution, not adversarial user input. Confidence is
not an injection defense. A byte bound routes oversized future inputs to the original.

**fallback / Choice (selected by the config predicate):** one genre question with the
same five labels; provisional confidence >=0.9, versioned OpenRouter Jev. Accepted
decisions may be faster and cheaper because they avoid generative inference. Serial
misses cost and take longer: expected cost = Jev cost + fallback fraction × original
cost. No savings are measured yet. Risks: overlapping genres, confident disagreement,
provider availability, and metadata mapping. Scope includes validation of response model,
primitive, label, confidence, distribution and real token counts before any stdout.
Missing key, bad responses, errors, timeouts, rate limits and low confidence retain
the unchanged original path exactly once.

**leave / none:** preserve original call and diagnostics; unchanged cost and latency,
no speculative savings, but no Jev decision benefit. Not selected.

## Integration contract

Only original site `workflow.ts:6` is selected. Keep original generateObject options,
prompt, structuredOutputs, enum, model, diagnostics and main().catch(console.error).
`jevDecisions.ts` owns questions, criteria, model pin, thresholds, size bound, timeout,
gate and adapter. Real input/output token counts map to promptTokens/completionTokens;
totalTokens is their sum. `finishReason: stop` means adapter-completed decision and
does not assert native token termination. Actual path/model go to stderr, no secrets
or input text. No dependency is needed for the production fetch adapter.

## Validation wiring (before validation script)

Original callable: baseline `main` and its generateObject request, loaded from the
source revision via git. Converted callable: current `main`, invoking
`withGenreDecision`; evaluator `evaluateGenre`, parser `parseDecision`, gate
`confidenceAccepted`, all imported from the actual decisions module using TypeScript
transpilation. Assert baseline generateObject expression is unchanged in current source.
For cases beyond the single fixture, replace only the plot string literal in both
source versions. Capture the actual baseline SDK options by executing its entrypoint.
Evaluation invokes real ai generateObject with those options and the same gpt-4o-mini
through an isolated OpenRouter transport/provider adapter; preserve SDK schema/parsing.
No hand-reconstructed prompt and no production provider switch.

Run one actual Jev evaluator per case; capture sanitized response and replay that same
body through the converted main, asserting original calls 0/1, object, usage and
finishReason plus printed blank line. Fault tests use the actual wrapper, transport
exceptions/429, and a real response mutated only for an explicitly injected gate fault.
Use >=30 unique synthetic/fixture inputs if service access succeeds; freeze 0.9 before
confirmation. Report raw/selective agreement, fallback fraction, p50/p95 latency and
provider-reported costs. Failed access is incomplete validation, never parity.

Run supplied independent smoke and artifact checker with --require-live. There is no
upstream package manifest or project test command. Validation dependencies, if needed,
are isolated and ignored; dependency versions must be reported as a baseline limitation.

## Documentation reviewed

Live docs read 2026-09-23 (Markdown fetched over HTTPS after browser tool errors):
[index](https://docs.typesafe.ai/llms.txt), [API](https://docs.typesafe.ai/api.md),
[Models](https://docs.typesafe.ai/models.md), [Confidence](https://docs.typesafe.ai/confidence.md),
[building](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md),
[coding agents](https://docs.typesafe.ai/introduction/coding-agents.md),
[jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md),
[intent routing](https://docs.typesafe.ai/patterns/intent-routing.md),
[confidence routing](https://docs.typesafe.ai/patterns/confidence-routing.md),
[composite scoring](https://docs.typesafe.ai/patterns/composite-scoring.md),
[fan-out](https://docs.typesafe.ai/patterns/fan-out.md),
[classification cookbook](https://docs.typesafe.ai/cookbooks/classification_using_confidence.md),
[Choice](https://docs.typesafe.ai/primitives/choice.md),
[OpenRouter](https://openrouter.ai/docs/guides/community/typesafe-sdk).
Jev's documented text and context constraints support this narrow fit. Cookbook thresholds
and performance numbers are not measurements for this workflow.
