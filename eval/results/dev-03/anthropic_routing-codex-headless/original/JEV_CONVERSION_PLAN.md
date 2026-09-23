# Jev conversion plan

Output mode: **report**. Exact output directory: `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/anthropic_routing-codex-headless/original`. Remain on `main` at source revision `800f561f5ab9d455d349560f1adcab352d83723d`. Inactive branch and clone-path config fields do not authorize either operation.

Read-only preflight passed: git available, repository clean including untracked files, no errors. Selected provider: OpenRouter; environment variable `OPENROUTER_API_KEY` was present (value never printed or saved). Configured Jev pin: `typesafe/jev-1.13-20260917`; not invoked or installed. Risk: conservative.

Config approval permits fallback only for pure DECISION sites with enumerated outputs, preserves all observable fields, and leaves MIXED/GENERATION unchanged. Resolved qualifying selections: **none**. Report-only mode independently excludes code changes. The authorized same-model OpenRouter baseline adapter is unnecessary because no site is converted.

## Recommendation and options

**No good Jev opportunities here** within the existing behavior and approved scope. `workflow.py:24` is MIXED because the generated reasoning is printed, even though selection is a closed route. `workflow.py:34` requires free-form support prose. `util.py:23` serves both and inherits MIXED usage. Replacing routing with Choice would drop or fabricate an externally visible explanation. Retaining the original selector to generate that explanation adds Jev work without eliminating that original call; decomposition is outside approval.

There are two consumer sites and one shared transport, not three independent runtime calls. A successful `route()` invokes the shared transport twice. `extract_xml` is deterministic parsing, not an LLM extraction site. The Anthropic constructors at util.py:6 and :21 are client setup, not inference calls. No other inference sites or local AGENTS.md guidance were found. This small repository has no manifest or project test command.

Preserve synchronous signatures, first content-block text return, original model, max_tokens=4096, temperature=0.1, empty default system prompt, XML parsing and route-key normalization, route dictionary lookup (including existing KeyError behavior), stdout diagnostics, and provider exception behavior. Source files remain byte-for-byte unchanged.

Inputs are text; bundled tickets are short, but the public callable has no size bound or demonstrated prompt-injection mitigation. Confidence cannot substitute for such mitigation. No broader production suitability is inferred from the fixtures.

| Original site | Provider/model | Classification | Downstream | Fit | Option |
|---|---|---|---|---|---|
| `workflow.py:24` | Anthropic SDK / claude-sonnet-4-6 | MIXED | route_response -> extract_xml(reasoning) -> stdout at lines 28–29; extract_xml(selection).strip().lower() -> routes[route_key] -> specialist prompt -> line 34 -> returned str. | NOT A FIT | leave; primitive `none`; entire site unchanged. Preserves behavior; latency/cost unchanged; retains existing model/provider risks. |
| `workflow.py:34` | Anthropic SDK / claude-sonnet-4-6 | GENERATION | Selected specialist instructions plus original input -> llm_call -> route() returns generated support response str. | NOT A FIT | leave; primitive `none`; entire site unchanged. Preserves behavior; latency/cost unchanged; retains existing model/provider risks. |
| `util.py:23` | Anthropic SDK / claude-sonnet-4-6 | MIXED | llm_call returns response.content[0].text to both workflow.py:24 and workflow.py:34; those consumers print routing reasoning, select a route, and return specialist prose. | NOT A FIT | leave; primitive `none`; entire site unchanged. Preserves behavior; latency/cost unchanged; retains existing model/provider risks. |

## Approved work

Write only this plan, JEV_AUDIT.json and JEV_CONVERSION_REPORT.md. Run the supplied smoke and artifact checker. No production conversion, dependencies, environment files, branches, clone, commits, push or PR.

## Validation plan

```sh
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/opt/python@3.14/bin/python3.14 '/Users/bigsoup/Downloads/Jev Converter/eval/smoke.py' '/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/anthropic_routing-codex-headless/original' anthropic_routing
```

Executed successfully, exit 0: `PASS: observable Python behavior and original-path fallback smoke`. This is behavior smoke evidence, not live model parity. The supplied smoke file was not edited. No project test command exists upstream.

No converted callable/evaluator/gate exists, so validation wiring and live paired tests are not applicable. Per-site thresholds: N/A for all three sites.

## References

Documentation reviewed on 2026-09-23: installed jevify entrypoint and configuration/audit/conversion/validation/validation-wiring references, plus vendored official TypeSafe skill. The live [index](https://docs.typesafe.ai/llms.txt) was accessible via web; page reads failed through that tool but succeeded using Python HTTPS reads. Consulted [API](https://docs.typesafe.ai/api.md), [Models](https://docs.typesafe.ai/models.md), [Confidence](https://docs.typesafe.ai/confidence.md), [building guide](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md), [coding agents](https://docs.typesafe.ai/introduction/coding-agents.md), [Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md), the [intent-routing](https://docs.typesafe.ai/patterns/intent-routing.md), [confidence-routing](https://docs.typesafe.ai/patterns/confidence-routing.md), [composite-scoring](https://docs.typesafe.ai/patterns/composite-scoring.md) and [fan-out](https://docs.typesafe.ai/patterns/fan-out.md) patterns, and [function calling](https://docs.typesafe.ai/cookbooks/function_calling.md) and [guardrails](https://docs.typesafe.ai/cookbooks/llm_guardrails.md) cookbooks. Jev supplies typed judgments rather than generated explanations; that mismatch controls this audit.
