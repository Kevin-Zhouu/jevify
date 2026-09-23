# Jev conversion plan

No good Jev opportunities here.

Source revision: `6fa3fbbdfca247d087ec4a7454ae2990bb401330`; original branch: `main`.
Output mode: branch; output branch: `jev-convert/evaluation`.
Output repository: `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/anthropic_routing-codex-interactive/original`.
The supplied clone_path is inactive in branch mode; no clone is created.

## Approval and resolved scope

User approved only `fallback` for pure DECISION sites with enumerated outputs, explicitly leaving MIXED and GENERATION unchanged and preserving all externally observable fields. All other conversion options are declined. This predicate matches zero sites. No conversion, decomposition, extra router, dependency, environment, or production-provider changes are selected. Record the audit and validation only; `converted_sites: []`.

Risk: conservative. Selected access: OpenRouter via `OPENROUTER_API_KEY`; proposed pinned model `typesafe/jev-1.13-20260917` is unused. Authorization to route the SAME baseline model through OpenRouter applies only to isolated evaluation adapters; no adapter is needed or introduced.

## Preflight

Read-only preflight passed: clean main (including untracked files), git available, requested branch valid and unused, selected credential present. Only presence was checked; no credential values were printed or saved. Branch creation follows explicit approval. No applicable AGENTS.md was found within this repository.

## Audit and options

| Original site | Provider / model | Classification | Downstream | Fit and reason | Option, benefit and risk |
|---|---|---|---|---|---|
| `workflow.py:24` | Anthropic Messages API / claude-sonnet-4-6 | MIXED | XML reasoning is printed under Routing Analysis; selection is stripped/lowercased, printed and used to index routes and select the specialist prompt. | NOT A FIT: Choice cannot preserve the generated, observable routing explanation. | leave / none: Preserve selector prompt, XML parsing, reasoning and route diagnostics. Cost and latency unchanged because the original inference remains. Risk: Replacing the whole call loses reasoning; retaining it while adding Jev adds cost and potential route/explanation disagreement. |
| `workflow.py:34` | Anthropic Messages API / claude-sonnet-4-6 | GENERATION | Selected specialist prompt and original input produce the free-form response returned by route(). | NOT A FIT: Specialist prose is generation, not an enumerated decision. | leave / none: Preserve the substantive specialist response and its return contract. Cost and latency unchanged because the original inference remains. Risk: A typed label cannot replace the generated response. |
| `util.py:23` | Anthropic Messages API / claude-sonnet-4-6 | MIXED | llm_call at util.py:9 returns response.content[0].text to both workflow.py:24 and workflow.py:34. | NOT A FIT: Shared Anthropic transport serves both mixed routing and prose generation. | leave / none: Preserve provider, model default, request parameters, first-block text return and exceptions. Cost and latency unchanged because the original inference remains. Risk: Replacing the shared wrapper breaks both consumers and their output contracts. |

There are two logical inference sites sharing one transport, not three independent savings opportunities. `extract_xml` is deterministic parsing, not inference. Inputs originate in the three bundled benign support tickets or arbitrary caller-provided strings and route dictionaries. The public API has no length bound or effective adversarial-input mitigation; fixture suitability does not establish production suitability. No mitigation changes are approved.

Preserve route signature and synchronous string return, original prompts, strip/lowercase selection normalization, available-route/reasoning/selection diagnostics, dictionary lookup and original exceptions. Preserve Anthropic parameters: default claude-sonnet-4-6, max_tokens 4096, temperature 0.1, system prompt and first response text block.

## Validation plan

Run the user-supplied independent anthropic_routing smoke with Python 3.14 against this output repository. Verify all upstream tracked files are unchanged against the source revision. Run the installed artifact checker. No converted sites means no live parity calls, thresholds, confidence/fallback metrics or fault-injection gate tests are applicable. Do not create JEV_PARITY.json or claim measurements.

The prior supplied audit consulted current Jev documentation and recorded the building guide as inaccessible; this execution confirms source contracts and applies that audit without introducing an API integration.
