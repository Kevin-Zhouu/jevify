# Approved conversion plan

Source: `1c953f75ebe1580de909072ce9a73b8ab8f11d05`, original branch `main`.
Output: sibling clone `converted`, branch `jev-convert/evaluation`; original untouched.
Preflight: clean including untracked files; git present; clone path and branch available;
`OPENROUTER_API_KEY` present (value never read into artifacts).
Approval: fallback only for pure DECISION sites with enumerated outputs, preserving all
externally observable fields. All other actions declined. Conservative fallback remains.

| Original site | Provider | Class | Downstream | Fit | Options | Selection |
| --- | --- | --- | --- | --- | --- | --- |
| workflow.py:83 | Anthropic / claude-haiku-4-5 | DECISION | text, strip, string return | Conditional: benign ticket distribution | A: fallback / Choice; B: leave / none | A |

A uses the same ten labels and definitions. Confident decisions avoid generative inference,
so cost and latency are expected to decrease on accepted decisions. Serial fallback adds
Jev cost and latency. Expected cost = Jev cost + fallback fraction * original cost.
Confident misclassification remains possible, particularly inquiry/dispute distinctions.
B leaves behavior and cost unchanged. Full machine-readable options: JEV_AUDIT.json.
No GENERATION, MIXED, EXTRACTION, other provider sites, local wrappers or consumers found.
The two TSVs each contain 68 unique tickets; no original project test command exists.

## Implementation and proof wiring (before validation)

Original callable: workflow.simple_classify, preserved as workflow._original_simple_classify
with an AST identity assertion allowing only that rename, compared to git source revision.
Public converted callable: workflow.simple_classify(X).
Policy: jev_decisions.evaluate, parse_response, accepts, classify_with_fallback.
Validation imports these exact production symbols; no copied Jev question or inference client.
It executes evaluate once per input, captures its response, then replays that response through
simple_classify while counting zero/one original calls. Raw Jev answers stay separate from
fallback results. Original prompt, assistant prefill, stop, temperature, max_tokens and strip
remain unchanged. An isolated SDK-shaped evaluation transport sends the unchanged request
to OpenRouter chat completions, translating only stop_sequences to stop and the same
Claude model namespace. Authorization is explicit in the supplied setup; production Anthropic
fallback is not rerouted. Source identity and request equality must pass.

Provisional threshold: 0.95, frozen before live confirmation; no calibration/retuning.
Use at least 30 unique repository tickets across ten labels, plus ambiguous/boundary/out-of-domain
synthetics as a separately identified diagnostic set. Record request IDs, usage, provider cost,
latency and raw agreement/selective curves. Unknown metrics remain null, not fabricated zero.
Exercise transport errors, timeout, HTTP 429, and low-confidence rejection through actual wrapper.
Accepted replay requires a real capture. Run supplied behavior smoke and artifact checker.

All policy, model pin typesafe/jev-1.13-20260917, criteria, threshold and state limits live
in one module. Standard-library HTTP adds no runtime dependency. Preserve original exceptions;
Jev failure handling never catches or retries an original exception. Bound HTTP and body size.
Add environment placeholders only. Log bounded path/model/reason via logging (no input/secrets).

Docs read live on 2026-09-23 via HTTPS (web markdown fetch failed; urllib succeeded):
https://docs.typesafe.ai/llms.txt, api.md, models.md, confidence.md,
concepts/how-to-build-with-system-one.md, introduction/coding-agents.md,
model-jaggedness/jev-1.13.md, patterns/{intent-routing,confidence-routing,composite-scoring,fan-out}.md,
primitives/choice.md, cookbooks/hierarchical_classification.md.
OpenRouter contract: https://openrouter.ai/docs/guides/community/typesafe-sdk.

Fit does not extend to hostile public inputs: no existing effective injection mitigation.
Do not claim confidence fixes this. Oversize/unsupported inputs use original unchanged.
Commit plan, implementation, and validation locally; never push or create PR.
