# Jev conversion plan

**No good Jev opportunities here.** The sole inference site generates free-form text
for a streaming HTTP response. Leave it unchanged.

Source revision: `f16140e0900995cd09ae48d9ec833b9866309f56`; original branch: `main`.
Output mode: **report**. Output directory: `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/langchain_completion-codex-headless/original`.
The config's inactive branch and clone_path fields do not authorize either operation.
Preflight passed: git available, repository clean (including untracked files), no errors.
`OPENROUTER_API_KEY` was present; only presence was checked. Configured Jev provider/model:
OpenRouter / `typesafe/jev-1.13-20260917`; neither was invoked or added to production.
Risk posture: conservative. Upfront approval permits fallback only for pure DECISION sites
with enumerated outputs. It matches **zero sites**. GENERATION remains unchanged.
The isolated same-model OpenRouter baseline authorization was not needed.

## Audit and recommendation

| Original site | Provider/model | Classification | Downstream | Fit | Option, primitive, benefit and risk |
| --- | --- | --- | --- | --- | --- |
| workflow.ts:15 | LangChain ChatOpenAI / OpenAI gpt-3.5-turbo-0125, temperature 0 | GENERATION | Stream → LangChainAdapter.toDataStreamResponse → HTTP caller | NOT A FIT | leave; none; preserve complete streaming generation, unchanged latency/cost; no migration-induced risk, existing provider/input risks remain |

`workflow.ts` is the only application source found. There is no package manifest,
lockfile, project test command, local SDK wrapper, notebook, or local AGENTS.md guidance.
Installed skill directories were excluded from application call searches.
`ChatOpenAI` construction at lines 10–13 configures the single inference call at line 15;
it is not an additional inference site. The imported SDK contains the provider transport,
but there is no local wrapper/provider implementation to inventory separately.
`LangChainAdapter` at line 17 consumes the stream; it is not another model call.

Input flows from `req.json().prompt` (line 8), unchanged into `model.stream(prompt)`.
There is no local prompt template, extraction parser, finite candidate list, branching
classification, or generated decision consumed by code. The entire generated stream is
public output. Its SDK/adapter semantics, errors, metadata and diagnostics must remain
intact; upstream has no explicit logging or catch/retry logic here. `POST` remains async,
and the exported `maxDuration` stays 30. Context is request-dependent, with no local
size bound or effective untrusted-input mitigation demonstrated. No robustness is inferred.

A new router or guardrail would require new policy and change behavior; it is neither an
existing decision to replace nor covered by the fallback-only approval. Jev cannot supply
the arbitrary generated text required by this endpoint.

## Resolved scope and execution

No sites selected for conversion; `converted_sites` is empty. In report mode, write only
`JEV_CONVERSION_PLAN.md`, `JEV_AUDIT.json`, and `JEV_CONVERSION_REPORT.md` in the current
repository. No code, dependency, environment, branch, clone, commit, push or PR changes.
Run the supplied independent smoke and the skill artifact checker. No live parity calls
are required for zero conversions; no threshold, savings or parity will be claimed.

## Documentation basis

The live index and listed pages were fetched on 2026-09-23. The web tool could fetch the
index but returned access errors for individual pages; direct HTTPS retrieval succeeded.
The generation limitation in Jev 1.13 jaggedness directly rules out this replacement.
The function-calling cookbook concerns closed candidate sets absent from this workflow.

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
- [cookbooks/function_calling](https://docs.typesafe.ai/cookbooks/function_calling.md)
