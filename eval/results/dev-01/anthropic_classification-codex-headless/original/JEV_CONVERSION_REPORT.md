# Jev conversion report

Converted the sole eligible call, original ID `workflow.py:83`, on branch
`jev-convert/evaluation` in the original repository directory. Source `main` remains
at `9ad0ba53546ba42a9b50165c3fe51ec275a58d68`. The user-supplied headless config
explicitly approved conservative fallback for pure enumerated DECISION sites.
Its branch mode takes precedence over the inactive clone_path field. No push or PR.

## Delivered behavior

`simple_classify(X)` first tries one Choice with the same ten category definitions
via OpenRouter, pinned to `typesafe/jev-1.13-20260917`. At confidence >= 0.90 and a
valid response it returns the category string. Otherwise it runs the unchanged
Anthropic implementation exactly once. The fallback still uses `claude-haiku-4-5`;
its body is AST-identical to upstream apart from its private function name.
Client initialization, original prompt, assistant prefill, stop sequence, token
limit, temperature, first-text-block parser, stripping, and exception behavior
are preserved. The source exposes no usage/finish diagnostics. No runtime package
was added. Existing Anthropic credentials/SDK remain necessary as upstream requires.

`jev_decisions.py` owns questions, criteria, pin, threshold, bounds and gate.
A changed taxonomy, non-string or >12,000-byte ticket bypasses Jev. Missing key,
malformed/unknown/nonfinite answer, low confidence, network errors, HTTP 429 and
timeout retain the original path. Jev requests have a ten-second timeout and no
retries. INFO logs contain only path, model and bounded reason; stdout is unchanged.
Configure the host logger at INFO to see them. Environment placeholders are in
`.env.example`; no credential values were stored. The hidden-input launcher is
`.agents/skills/jevify/scripts/with_jev_key.py` (run with `--help` for usage).

## Validation executed

Python: `/opt/homebrew/opt/python@3.14/bin/python3.14`.

- PASS: supplied independent behavior smoke:
  `/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/bigsoup/Downloads/Jev\ Converter/eval/smoke.py "$PWD" anthropic_classification`
- PASS: `python3.14 scripts/validate_jev.py --live`: 14 injected control-flow checks,
  followed by 44 real paired comparisons, zero live errors.
- PASS: AST comparison of upstream original function against retained fallback.
- Fault checks: timeout, rate limit, generic error, malformed JSON, missing key,
  below-threshold gate, nonfinite/out-of-range confidence, unknown option,
  missing schema, oversize/non-string inputs, changed categories and original
  exception identity/exactly-once propagation. These are control-flow tests,
  not live model evidence. No successful Jev inference was mocked.

Live measurement used the original function with an isolated SDK transport adapter,
forwarding the SAME prompt/messages, `<category>` assistant prefill, max_tokens,
temperature and stop sequence to `anthropic/claude-haiku-4.5` through OpenRouter.
The adapter maps `stop_sequences` to `stop`, restricts routing to Anthropic, and
requires supported parameters. This route was explicitly authorized by config;
production fallback routing is unchanged. Returned text goes through the original
parser. Jev calls use the actual production decisions module. Each captured live
response was replayed through the actual classification wrapper with the measured
original output to verify return value and fallback call count without rebilling.

Inputs: ten unique train.tsv examples (calibration), thirty unique test.tsv examples,
and four clearly labeled synthetic empty/ambiguous/out-of-domain cases
(34 confirmation inputs). Category round-robin sampling covers all ten labels.
The 0.90 threshold was fixed before measurements; no tuning on the confirmation
set occurred. All 44 unique inputs and disagreements are saved, not cherry-picked.

## Measured results (2026-09-23)

| Measure | All 44 | Calibration (10) | Confirmation (34) |
| --- | ---: | ---: | ---: |
| Raw Jev/original agreement | 39/44 (88.6%) | 10/10 | 29/34 (85.3%) |
| Accepted at 0.90 | 30 | 8 | 22 |
| Accepted agreement | 29/30 (96.7%) | 8/8 | 21/22 (95.5%) |
| Fallback rate | 31.8% | 20.0% | 35.3% |

| Confidence threshold | Accepted (all) | Accepted agreement | Fallback fraction |
| --- | ---: | ---: | ---: |
| 0.00 | 44 | 88.6% | 0.0% |
| 0.50 | 43 | 90.7% | 2.3% |
| 0.70 | 38 | 94.7% | 13.6% |
| 0.80 | 34 | 97.1% | 22.7% |
| 0.90 | 30 | 96.7% | 31.8% |
| 0.95 | 25 | 100.0% | 43.2% |
| 0.99 | 23 | 100.0% | 47.7% |

| Latency | p50 | p95 |
| --- | ---: | ---: |
| Jev actual request | 375 ms | 662 ms |
| Original through authorized gateway | 783 ms | 1,253 ms |
| Estimated sequential cascade | 444 ms | 1,570 ms |

Mean provider-reported Jev cost: $0.0000316804 per request. Mean original gateway
cost: $0.000720182. Estimated cascade cost: $0.000260862, about 63.8% lower.
Costs use actual OpenRouter `usage.cost` responses, not assumed list prices;
IDs, usage and per-row costs are in `JEV_PARITY.json`. Cascade figures sum measured
Jev cost/latency plus original cost/latency only on fallback rows. They are estimates
from paired calls, not direct end-to-end production timing. Concurrent evaluation
used three workers. Original direct-Anthropic deployment latency/cost can differ.
The higher cascade p95 demonstrates the serial fallback penalty.

Recommendation for `workflow.py:83`: retain 0.90 with conservative fallback.
Accepted agreement exceeds the skill's 90% target on this small confirmation set,
but does not prove identical behavior or production assurance. One accepted
0.92-confidence disagreement classified a forthcoming policy-change explanation
as Coverage Explanations while the original returned Policy Administration.
Four additional disagreements were below threshold and fell back. A 0.95 gate
looks promising here but needs a fresh confirmation set before claiming its
100% observed agreement generalizes. No Jev-only removal is authorized or done.

The fit and measurements cover benign example tickets only. No adversarial safety
claim is made; prompt wording and confidence are not proven injection defenses.
No deployment hardening, new router/decomposition, provider switch or other site
conversion was performed. No generative sites existed. All provider output
comparisons use raw Jev answers before fallback; fallback output was not counted
as Jev agreement.

## Artifacts and undo

- `JEV_CONVERSION_PLAN.md`: audit table, scope, choices, preflight and live doc links.
- `JEV_AUDIT.json`: requested site inventory and actual converted original IDs.
- `JEV_PARITY.json`: real pairs, split curves, timing/cost, IDs and executed faults.
- `scripts/validate_jev.py`: reproducible offline faults and opt-in live validation.

Re-run offline checks with `python3.14 scripts/validate_jev.py`. `--live` incurs
provider usage and overwrites the parity artifact with the new measurements.

To undo after preserving any desired artifacts, from a clean checkout:
`git switch main`, then `git branch -D jev-convert/evaluation`.
