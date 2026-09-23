# Jev conversion plan

No good Jev opportunities here under the requirement to preserve upstream semantics and diagnostics.

## Setup and preflight

Source branch: `main`. Source revision: `444c1aad9442a670679de44a5ab786edb9e11cce`.
Output mode: branch, `jev-convert/evaluation`, in the original repository. The supplied clone path is inapplicable to branch mode.
Preflight: clean tracked/untracked status; valid, unused branch name. No applicable repository AGENTS.md was found. Setup answers in the user message were authoritative; the external config was not needed or read.
Selected access: OpenRouter, credential variable `OPENROUTER_API_KEY`, model `typesafe/jev-1.13-20260917`; conservative risk. No credentials were inspected and no provider requests made.

## Audit and options

| Original site | Provider/model | Classification and downstream | Fit/reason | Option, primitive, benefit and risk |
|---|---|---|---|---|
| workflow.py:24 | Anthropic / claude-sonnet-4-6 | MIXED: XML reasoning is printed; selection is stripped/lowercased, printed and used to index routes. | NOT A FIT: a typed answer cannot supply generated reasoning. | A: leave; none. Preserves diagnostics, unchanged cost/latency, retains existing dependency. |
| workflow.py:34 | Anthropic / claude-sonnet-4-6 | GENERATION: specialist free-form response is returned. | NOT A FIT: requires prose/instructions. | B: leave; none. Preserves response, unchanged cost/latency, retains existing dependency. |
| util.py:23 | Anthropic / claude-sonnet-4-6 | MIXED transport through llm_call at util.py:9, returning first response text block to both workflow sites. | NOT A FIT: shared generation and mixed consumers. | C: leave; none. Preserves provider, parameters, return behavior and exceptions, unchanged cost/latency. |

The transport row represents the same two calls, not a third savings opportunity. Inputs originate from route(input, routes), including three supplied benign ticket fixtures. The public function accepts arbitrary text and route dictionaries, with no context bound or adversarial-input mitigation. The selector appends input to its prompt; the specialist receives the selected prompt plus the same input. No mitigation or new routing behavior is introduced.

## Approval resolution

Approved action: `fallback`, only for pure DECISION sites with enumerated outputs, preserving all externally observable fields. All other conversion options declined. Matching sites: **none**. Converted sites: **none**. MIXED and GENERATION remain unchanged as expressly instructed. The approval does not authorize decomposition of the selector or an extra Jev call.

Write only this plan, JEV_AUDIT.json and JEV_CONVERSION_REPORT.md; run the authorized independent behavior smoke. Preserve source, prompts, provider, model, diagnostics, exceptions, dependencies and environment configuration. No decisions module, threshold, or parity adapter is needed.
