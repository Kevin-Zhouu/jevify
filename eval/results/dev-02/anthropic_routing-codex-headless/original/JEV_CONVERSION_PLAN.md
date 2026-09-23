# Jev conversion plan

No good Jev opportunities here within the approved scope and unchanged observable contract.

## Setup and preflight

- Output mode: report; output directory: `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/anthropic_routing-codex-headless/original`.
- Original branch: `main`; revision: `6d194f3d9298d11d74499307d7db36848493d0d8`.
- Read-only preflight passed: git available, repository clean including untracked files, no errors.
- Selected access: OpenRouter; `OPENROUTER_API_KEY` presence checked and true. No credential values read into artifacts.
- Configured model: `typesafe/jev-1.13-20260917`; not invoked or installed.
- Conservative risk. The inactive branch and clone path do not authorize creating either.
- Approval: fallback only for pure DECISION sites with enumerated outputs; MIXED and GENERATION remain unchanged; all observable fields preserved.
- Resolved conversion selections: none. Recommended disposition for every site: leave.
- Same-model OpenRouter baseline routing is authorized for isolated evaluation only, but unnecessary with zero conversions.

## Audit and options

| Original site | Provider | Class | Downstream | Fit | Option / primitive | Benefit and economics | Risk |
|---|---|---|---|---|---|---|---|
| workflow.py:24 | Anthropic SDK / claude-sonnet-4-6 (default) | MIXED | XML reasoning is printed at lines 28–29; selection is stripped/lowercased and printed at line 30, indexes routes at line 33, then drives the specialist call at line 34. | NOT A FIT | leave / none | Preserves upstream output, diagnostics and exception behavior. Latency and cost remain unchanged because no calls are added or removed. | Retains existing model cost, parsing failures and input-injection exposure; introduces no conversion risk. |
| workflow.py:34 | Anthropic SDK / claude-sonnet-4-6 (default) | GENERATION | Selected specialist prompt plus original input produces the string returned by route(). | NOT A FIT | leave / none | Preserves upstream output, diagnostics and exception behavior. Latency and cost remain unchanged because no calls are added or removed. | Retains existing model cost, parsing failures and input-injection exposure; introduces no conversion risk. |
| util.py:23 | Anthropic SDK / claude-sonnet-4-6 (default) | MIXED | llm_call returns response.content[0].text at line 30 to both workflow.py:24 and workflow.py:34; route consumes XML reasoning/selection and returns specialist prose. | NOT A FIT | leave / none | Preserves upstream output, diagnostics and exception behavior. Latency and cost remain unchanged because no calls are added or removed. | Retains existing model cost, parsing failures and input-injection exposure; introduces no conversion risk. |

The two workflow calls both use `util.llm_call`, whose transport is `util.py:23`. These are two logical inference uses and one shared transport, not three independent savings opportunities. No other application LLM calls, notebooks, manifests, test commands, or repository AGENTS.md were found; installed skill code is excluded from application inventory.

`route(input: str, routes: dict[str, str]) -> str` is synchronous. It prints available routes, routing analysis, the generated reasoning, and the normalized selected route. It then looks up the caller's dictionary and returns generated specialist text. Missing XML returns an empty string through `extract_xml`; an invalid route can raise KeyError. Provider exceptions propagate. `llm_call` preserves the optional system prompt/model, max_tokens=4096, temperature=0.1 and first text block extraction. Import-time Anthropic key access also remains intact. Usage/finish metadata are not exposed by this wrapper.

Runtime route keys are enumerable, but the selector's complete answer is MIXED because reasoning is printed. Replacing it with Choice or canned reasoning would change diagnostics. Keeping the original reasoning call would retain its inference cost and add Jev cost; no savings are established. Decomposition is outside the approval predicate. The specialist answer is unbounded prose, and the shared wrapper cannot be classified solely by its routing consumer.

Fixtures contain three short support tickets; exact token lengths were not measured. Public inputs and custom route dictionaries are unbounded. There is no effective injection mitigation: user text is interpolated directly. Any future isolated routing proposal would need input bounds, defined route criteria, adversarial testing and separate approval to address the generated reasoning contract. Confidence alone does not mitigate injection.

## Documentation basis

Live documentation checked on 2026-09-23. Markdown endpoints failed through the web tool; normal pages were available, and the building guide Markdown was retrieved with Python urllib. Vendored API, Models, Confidence and official skill were also read. Jev returns typed judgments rather than prose; its documented generation and adversarial-content limits support the no-fit conclusion. The model documentation states 64k total tokens and 32k state plus longest question; unbounded application inputs have no demonstrated coverage. Pattern/cookbook thresholds are examples, not validated thresholds for this workflow.

- [api](https://docs.typesafe.ai/api)
- [models](https://docs.typesafe.ai/models)
- [confidence](https://docs.typesafe.ai/confidence)
- [concepts/how-to-build-with-system-one](https://docs.typesafe.ai/concepts/how-to-build-with-system-one)
- [introduction/coding-agents](https://docs.typesafe.ai/introduction/coding-agents)
- [model-jaggedness/jev-1.13](https://docs.typesafe.ai/model-jaggedness/jev-1.13)
- [patterns/intent-routing](https://docs.typesafe.ai/patterns/intent-routing)
- [patterns/confidence-routing](https://docs.typesafe.ai/patterns/confidence-routing)
- [patterns/composite-scoring](https://docs.typesafe.ai/patterns/composite-scoring)
- [patterns/fan-out](https://docs.typesafe.ai/patterns/fan-out)
- [cookbooks/function_calling](https://docs.typesafe.ai/cookbooks/function_calling)
- [cookbooks/llm_guardrails](https://docs.typesafe.ai/cookbooks/llm_guardrails)

## Execution and validation plan

Write only JEV_CONVERSION_PLAN.md, JEV_AUDIT.json and JEV_CONVERSION_REPORT.md in the original repository. No source, dependency, environment, branch, clone or commit changes. Run the user-supplied independent smoke and skill artifact checker. With no conversions, paired live calls and a parity artifact are unnecessary; do not claim agreement, confidence, latency, cost or fallback measurements. Undo consists only of deleting these three new artifacts.
