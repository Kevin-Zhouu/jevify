# Jev conversion plan

Source revision: `ad8a0b622db326ffd047b3f25c62cf66d2f09e6b` on original branch `main`.
Output mode: branch, `jev-convert/evaluation`, in the original repository. The inactive clone path is unused.

Approval permits only `fallback` for pure DECISION sites with enumerated outputs, while preserving all externally observable fields. This predicate matches zero sites. All other conversion options are declined. No source, dependency, environment, prompt, parsing, provider, diagnostic or fallback changes are authorized or made.

No good Jev opportunities here. The router's printed reasoning makes its call MIXED; the specialist requires GENERATION; the shared wrapper is MIXED infrastructure rather than a third independent savings opportunity.

| Original site | Provider | Classification | Downstream / fit | Recorded option (not a conversion selection) |
|---|---|---|---|---|
| workflow.py:24 | Anthropic / claude-sonnet-4-6 | MIXED | XML selection chooses specialist; reasoning is printed. Not a fit. | leave; primitive none. Preserves both outputs, unchanged cost/latency. Substituting a route risks inconsistent reasoning. |
| workflow.py:34 | Anthropic / claude-sonnet-4-6 | GENERATION | Free-form specialist text returned to caller. Not a fit. | leave; primitive none. Preserves response, unchanged cost/latency. A label cannot replace prose. |
| util.py:23 | Anthropic SDK / claude-sonnet-4-6 default | MIXED | Returns response.content[0].text to both consumers above. Not a fit. | leave; primitive none. Preserves parameters, errors and return shape, unchanged cost/latency. Blanket conversion breaks consumers. |

The three bundled tickets in workflow.py:79–95 are short benign fixtures. Public route() accepts unrestricted input and route dictionaries, without an explicit context bound or effective adversarial-input mitigation. Fixture suitability does not establish production suitability. There is no approved decomposition or route substitution.

Preflight: clean repository including untracked files, requested branch available, git available, OPENROUTER_API_KEY present (presence only; no credential values read into artifacts). Setup arguments supplied in the request were used; the external config was not read.
Selected Jev access would be OpenRouter, model `typesafe/jev-1.13-20260917`, with conservative original fallback. No Jev integration was introduced. Authorization to route the SAME original model through OpenRouter applies only to isolated evaluation adapters; none was needed or created.

Resolved plan: create the requested branch, save the complete negative audit and report, run the supplied independent behavior smoke, check artifact shape, and commit only the three documentation artifacts. Converted sites: none. No threshold is applicable to any site. No live parity is required because no sites are converted.
