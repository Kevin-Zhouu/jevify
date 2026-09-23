# Jev conversion plan

No good Jev opportunities here.

## Setup and preflight

- Source/output repository: `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/langchain_completion-codex-headless/original`. Report mode keeps this output directory; the inactive clone_path and branch settings do not authorize a clone or branch.
- Original branch: `main`; source SHA: `81b7cce7b483eebc6ab39e6317c3759192561e6d`.
- Read-only preflight passed: git available, repository initially clean including untracked files, no errors. Python: `/opt/homebrew/opt/python@3.14/bin/python3.14`.
- Selected access: OpenRouter, `OPENROUTER_API_KEY`; presence checked and true. No credential values read into artifacts or printed. Configured Jev pin: `typesafe/jev-1.13-20260917`; not invoked.
- Conservative risk; headless approval allows only `fallback` for pure DECISION sites with enumerated outputs, preserving observable fields. Matches: **zero**. No conversion selected or performed. GENERATION remains unchanged.
- Isolated baseline routing through OpenRouter is authorized for the same original model only; not used because no site is converted.

## Inventory and selectable recommendation

| Original site | Provider/model | Classification | Downstream | Fit | Option / primitive | Benefit and economics | Risk and scope |
| --- | --- | --- | --- | --- | --- | --- | --- |
| workflow.ts:15 | LangChain ChatOpenAI / OpenAI / gpt-3.5-turbo-0125 | GENERATION | Stream → LangChainAdapter.toDataStreamResponse at line 17 → HTTP caller | NOT A FIT | leave / none | Preserve stream and original behavior; cost and latency unchanged, no savings claimed | No migration risk; retain existing provider limitations; leave workflow.ts intact |

`POST(req: Request)` at line 7 is the only local wrapper. It awaits JSON, extracts `prompt`, constructs ChatOpenAI with temperature 0 and the original model, then awaits `model.stream(prompt)`. The adapter is a response consumer, not a second model call. Count: one inference site, zero DECISION, one GENERATION, zero MIXED, zero EXTRACTION. Repository search found no other workflow calls, manifests, lockfiles, notebooks, tests, or AGENTS.md; installed skills were excluded from workflow inventory.

The response content is arbitrary generated text, not a closed enum. The request input has no local length bound, schema check or adversarial mitigation. Actual context size depends on the caller. Jev cannot replace this text stream with a typed answer while retaining semantics. A new router/guardrail would introduce policy and behavior beyond approval and would still require generation; it is not selected.

Preserve `maxDuration = 30`, the async signature, prompt forwarding, model/temperature, adapter response, stream chunks and adapter-owned metadata/diagnostics. There are no explicit application logs or catches; errors remain governed by the original SDK, adapter and caller. No metadata is synthesized.

## Documentation basis

Live Markdown pages were fetched successfully with Python urllib after the web tool could read the index but failed on individual pages. Reviewed 2026-09-23:

- [Index](https://docs.typesafe.ai/llms.txt), [API](https://docs.typesafe.ai/api.md), [Models](https://docs.typesafe.ai/models.md), [Confidence](https://docs.typesafe.ai/confidence.md).
- [Building guide](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md), [Coding agents](https://docs.typesafe.ai/introduction/coding-agents.md), [Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md).
- [Intent routing](https://docs.typesafe.ai/patterns/intent-routing.md), [Confidence routing](https://docs.typesafe.ai/patterns/confidence-routing.md), [Composite scoring](https://docs.typesafe.ai/patterns/composite-scoring.md), [Fan-out](https://docs.typesafe.ai/patterns/fan-out.md).
- [Function calling cookbook](https://docs.typesafe.ai/cookbooks/function_calling.md): closed-set function selection does not match this unrestricted completion endpoint.

The coding-agents and jaggedness pages explicitly distinguish typed judgments from text generation. Patterns require decisions that are absent here. Cookbook thresholds provide no applicable gate for this site.

## Authorized execution

Write only this plan, JEV_AUDIT.json and JEV_CONVERSION_REPORT.md in the original repository. Run the user-provided independent smoke and artifact shape checker. No code, dependencies, env files, branch, clone, commits, push or PR. No paired live measurements are needed for zero conversions; no JEV_PARITY.json will be created.
