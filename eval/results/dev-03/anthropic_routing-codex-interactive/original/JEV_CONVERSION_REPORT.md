# Jev conversion report

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

Validation: the upstream example has no project test command. The user-supplied independent smoke command was executed using Python 3.14:

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/bigsoup/Downloads/Jev\ Converter/eval/smoke.py /Users/bigsoup/Downloads/Jev\ Converter/eval/runs/dev-03/anthropic_routing-codex-interactive/original anthropic_routing
```

Exit status 0; output: `PASS: observable Python behavior and original-path fallback smoke`.
This is behavioral smoke evidence, not live model parity. No live requests, paired inputs, confidence curves, fallback-rate measurements, latency measurements, cost measurements or injected Jev fault tests were performed. Sample count: 0 live pairs. JEV_PARITY.json is intentionally absent. Threshold recommendation for each of workflow.py:24, workflow.py:34 and util.py:23: not applicable; leave unchanged. No cost or latency savings are claimed.

Artifact verification command:

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 .agents/skills/jevify/scripts/check_artifacts.py .
```

Artifact shape validation passed. Shape validation verifies required artifact fields, not semantic or live parity. Source preservation was verified against the source revision; only the three requested documentation artifacts were added. The smoke's coverage is limited to its observable behavior checks; it does not establish production model quality.

Undo after saving any later work:

```sh
git switch main
git branch -D jev-convert/evaluation
```

No push or pull request was performed.
