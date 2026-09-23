# Jev conversion plan

Source: `6013ff5396ee175c76aa5feddd7e93d903e667a7`, original branch `main`.
Output mode: branch `jev-convert/evaluation`, in `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/vercel_enum-codex-headless/original`.
The inactive config clone_path is ignored. Preflight: clean including untracked files, branch unused, git available, OPENROUTER_API_KEY present (value never read into artifacts).

## Audit and resolved approval

| Original site | Class / fit | Provider / consumers | Options |
|---|---|---|---|
| workflow.ts:6 | DECISION / FIT for benign fixed plot | generateObject, OpenAI gpt-4o-mini; prints enum, usage and generic finish status | **Selected fallback / Choice:** likely lower accepted-call cost/latency; serial misses add cost/latency. Preserve truthful metadata. Risk: ambiguous genres, confidence calibration. **leave / none:** unchanged behavior, no savings, existing ambiguity remains. |

One transport site, no shared wrappers or other consumers. Input is a fixed short English movie plot. Five genres are exhaustive only relative to the original forced-choice task; do not add an unknown label. Metadata does not make this MIXED. No user-input surface or existing prompt-injection mitigation; verdict is scoped to benign fixtures. Context is far below documented 32k state-plus-question and 64k total limits. Impose an 8000-byte bound as an extra conservative guard, not an injection defense.

Explicit config approval permits fallback at pure enumerated DECISION sites, with all observable fields preserved; resolved selection is `fallback:workflow.ts:6`. Conservative risk excludes fallback removal. No further confirmation needed. No push or PR authorized.

## Implementation contract

One TypeScript decisions module owns model pin `typesafe/jev-1.13-20260917`, Choice question, criteria, provisional 0.9 confidence threshold, 5-second timeout and bounds. Use OpenRouter System One HTTP endpoint; no dependency additions. Retain original OpenAI model, structured output setting, prompt bytes, enum and error handling. Every failed gate calls original exactly once. Path/model diagnostics go to stderr, without input or error-body contents.

Validate response model, enum, confidence, probabilities and token usage before accepting. Map real `input_tokens`/`output_tokens` to `promptTokens`/`completionTokens`; total is their sum. `finishReason: stop` is adapter-owned generic completion, not a claim of native token termination. All original stdout labels/order remain.

## Validation plan

Run the user-provided independent smoke, plus full diagnostic and forced-failure assertions. Attempt live pairs with the present key. Use the SAME original gpt-4o-mini through OpenRouter only in an isolated evaluation adapter, as explicitly authorized. Invoke real AI SDK prompt construction/parsing; assert original request equivalence. At least 30 unique benign plots, including ambiguous/out-of-domain cases; label synthetic provenance. Preserve all disagreements, real request IDs, costs/usage and monotonic latency. Import actual Jev evaluator/gate. Threshold remains provisional absent representative confirmation. Use a fixed predeclared calibration/check split if measurements complete.

Live documentation read on 2026-09-23: [index](https://docs.typesafe.ai/llms.txt), [API](https://docs.typesafe.ai/api.md), [Models](https://docs.typesafe.ai/models.md), [Confidence](https://docs.typesafe.ai/confidence.md), [building](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md), [coding agents](https://docs.typesafe.ai/introduction/coding-agents.md), [jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md), all four [Patterns](https://docs.typesafe.ai/patterns.md), [Choice](https://docs.typesafe.ai/primitives/choice.md), [classification cookbook](https://docs.typesafe.ai/cookbooks/classification_using_confidence.md), and [OpenRouter transport](https://openrouter.ai/docs/guides/community/typesafe-sdk). Direct HTTPS reads succeeded when browser Markdown opens failed. Cookbook thresholds are examples, not parity evidence.

## Validation environment adjustment

The inherited AI SDK installation failed to load because its Zod dependency lacked the required `zod/v3` export. Validation therefore uses an isolated, locked `validation/package.json`: AI SDK 4.3.19, OpenAI provider 1.3.24, Zod 3.25.76 and TypeScript 5.9.3. This matches the upstream example's `structuredOutputs` and `promptTokens` contract; upstream has no manifest/lockfile to reproduce exact historical dependency versions. Production dependencies and provider remain unchanged. Validation adds only `maxRetries: 0` to bound attempts, which does not change the model prompt or parsing. All 36 input fixtures and the alternating 18/18 calibration/confirmation split are declared before measurement; the provisional threshold stays fixed during both halves.
