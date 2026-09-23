# Jev conversion plan

No good Jev opportunities here. The observable routing explanation makes the selector MIXED, and the specialist generates prose. No conversion is selected.

## Setup and preflight

- Source revision: `6ad2f63dc4cf74cd89f71028115f855f528a2a83`; branch: `main`.
- Git repository present; initial tracked and untracked status clean. No applicable AGENTS.md found within this repository. No manifest, lockfile, or project test command is present.
- Config explicitly chooses `output.mode: report`. Reports are written in the original repository. The config's branch and clone_path fields are inactive in this mode; no branch or clone is created. The named branch did not exist; clone destination checks are not applicable.
- Conservative risk posture; selected prospective provider OpenRouter, credential variable `OPENROUTER_API_KEY`, pinned model `typesafe/jev-1.13-20260917`. No credential values inspected or saved; no inference provider contacted.
- Approval permits fallback only for pure DECISION sites with enumerated outputs, preserving all observable fields. Resolved eligible/selected conversion IDs: `[]`. MIXED and GENERATION remain unchanged. Report mode independently excludes source/dependency/env changes and commits.
- Isolated baseline routing through OpenRouter for the same original model was authorized, but is unnecessary because no sites are converted.

## Audit and options

| Original ID | Provider/model | Classification | Downstream use | Fit and reason | Option |
|---|---|---|---|---|---|
| workflow.py:24 | Anthropic SDK / claude-sonnet-4-6 | MIXED | extract_xml(reasoning) -> stdout; extract_xml(selection).strip().lower() -> routes[route_key] -> specialist prompt -> workflow.py:34 -> returned prose | NOT A FIT: The same call generates observable routing reasoning and a route. Choice cannot preserve the printed explanation; retaining the original call for reasoning avoids no original inference. | leave; primitive: none. Preserve behavior; latency/cost unchanged; existing model risks remain. |
| workflow.py:34 | Anthropic SDK / claude-sonnet-4-6 | GENERATION | Selected support prompt plus original input -> llm_call -> response.content[0].text -> route() return value | NOT A FIT: Open-ended specialist advice, steps, explanations and documentation references require generated text. | leave; primitive: none. Preserve behavior; latency/cost unchanged; existing model risks remain. |
| util.py:23 | Anthropic SDK / claude-sonnet-4-6 | MIXED | Shared llm_call wrapper (util.py:9) -> response.content[0].text -> workflow.py:24 and workflow.py:34 | NOT A FIT: Shared transport serves both routing-with-reasoning and specialist generation; a blanket typed-decision replacement breaks both consumers. | leave; primitive: none. Preserve behavior; latency/cost unchanged; existing model risks remain. |

There are two logical inference sites and one shared transport, not three independent inference opportunities. Both workflow calls use util.llm_call, defined at util.py:9, with its default model. The SDK request is at util.py:23. XML parsing at util.py:44 is deterministic regex work, not another LLM/extraction site. Client construction at util.py:6 and :21 is not inference. No additional runnable call sites were found outside installed skill assets.

## Inputs, context and behavior contract

`route(input: str, routes: dict[str, str]) -> str` is synchronous. Input and route definitions come from callers; this repository provides four support prompts and three short English ticket fixtures, but no top-level route execution. Runtime inputs and route counts are unbounded. The selector sees the input and available route keys; the specialist sees the selected prompt and the same input. No tokenizer measurement was performed. The fixtures are small text inputs; arbitrary callers could exceed Jev's documented limits (64k request, 32k state plus longest question). No existing filtering or effective adversarial-input mitigation is present. The fixtures are benign examples, not evidence of robustness to public user traffic. Confidence alone is not a prompt-injection defense.

Preserve available-routes output, Routing Analysis and original reasoning, normalized selected-route output, the exact selected prompt plus input, and returned specialist text. Missing XML returns an empty string; missing/unknown route raises KeyError at lookup. Provider errors and missing ANTHROPIC_API_KEY errors currently propagate. The wrapper returns only the first response content block's text; usage/finish metadata are not exposed. Original request parameters are max_tokens=4096, temperature=0.1, system default empty, one user message, model claude-sonnet-4-6.

A Choice might classify intent in a redesigned workflow, but dropping or fabricating the printed reasoning would violate this contract. Keeping the complete original call to supply reasoning would not remove its cost, and could produce disagreement between explanation and route. Decomposition or a new guardrail requires separate scope approval and input validation. It is not recommended as an approved fallback conversion here. Specialist generation stays with its original model.

## Planned work and validation

Write only this plan, JEV_AUDIT.json and JEV_CONVERSION_REPORT.md. Run the user-provided offline behavior smoke against this original/output repository, with Python 3.14 and bytecode writes disabled. No Jev module, dependency, env file, branch, commit, push or PR is needed. Live validation skipped: zero converted sites. No threshold, parity curve, cost or latency measurement is warranted. Do not produce JEV_PARITY.json without measured live evidence.

## Documentation reviewed

The live index was available through the web tool. Individual Markdown reads failed there; public HTTPS reads via Python urllib succeeded. The installed official TypeSafe skill and jevify configuration, audit, conversion and validation references were read. The following live pages informed the assessment (2026-09-23). Generation and adversarial-state limitations are explicit in the jaggedness page; the pattern examples do not override the existing observable contract.

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
- [cookbooks/llm_guardrails](https://docs.typesafe.ai/cookbooks/llm_guardrails.md)
