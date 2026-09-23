# Jev conversion report

Converted `workflow.py:83` under config approval for enumerated DECISION fallback
sites. Source revision: `eff84f8f58d676d6b3b2eb21ae7b906300e2ef1b` (`main`).
Output is branch `jev-convert/evaluation` in the original repository; no clone,
push or PR. Preflight was clean and OPENROUTER_API_KEY was present.

## Behavior and scope

`simple_classify(X)` remains synchronous and returns a string. The original
Anthropic `claude-haiku-4-5` body was only renamed; an AST assertion confirms its
prompt, prefill, parameters, stop sequence, parsing and exceptions are unchanged.
Production fallback remains Anthropic. Category descriptions and ten labels are
preserved. No original token or finish diagnostics existed to adapt or remove.
Jev path/model/reason logs use the module logger at INFO; enable that logger to
observe them. Logs contain no inputs, headers or secrets and add no stdout.

`jev_decisions.py` owns the Choice, model pin
`typesafe/jev-1.13-20260917`, threshold 0.9, 16,000-byte input bound,
and 10-second transport timeout. It uses OpenRouter System One over stdlib HTTP,
without retries or new dependencies. Unsupported input, missing key, unavailable
transport, invalid model/answer/confidence or low confidence calls original once;
original errors propagate. Usage is neither consumed nor synthesized for the
production string contract. No other model sites were found or converted.

## Executed validation

Python: `/opt/homebrew/opt/python@3.14/bin/python3.14`.

- `python validate_jev.py`: 38 unique live pairs completed, 0 failed pairs.
- Supplied independent command: `/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/bigsoup/Downloads/Jev\ Converter/eval/smoke.py "/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/anthropic_classification-codex-headless/original" anthropic_classification`: PASS, observable Python behavior and original fallback.
- Actual public wrapper replayed all 38 real captured Jev responses; string result
  and exact fallback call count asserted. This is integration replay, not additional
  live inference. No successful Jev responses were fabricated.
- Executed fault assertions: transport timeout, HTTP 429, generic transport error,
  original exception identity/one-call propagation, missing credentials, malformed
  response, unknown option, unsupported/oversize input, and finite confidence gate.
  Low-confidence wrapper test forced the gate to reject a captured live response.
- Artifact checker with `--require-live`: PASS (`shape_valid: true`, no errors).
  This verifies artifact shape, not the truth of measurements.

Baseline evaluation uses the original callable loaded from its git revision, with
an isolated Anthropic transport adapter to the authorized OpenRouter route
`anthropic/claude-haiku-4.5`. Only model namespace and `stop_sequences` → `stop`
transport naming change. Prompt, assistant prefill, temperature, max_tokens and
parsing are original. Response models confirm the same Haiku model. This is
agreement against Haiku through OpenRouter, not a measurement of direct Anthropic
latency or proof of ground-truth accuracy.

Inputs: first three tickets from each of ten groups in `data/test.tsv` (30), plus
8 explicitly synthetic ambiguous, short, empty and out-of-domain cases. All are
unique. Fixture line references, raw answers, request IDs, real Jev responses,
provider usage/cost and baseline metadata are in `JEV_PARITY.json`.
Threshold 0.9 was selected before measurement; no tuning occurred. All 38 are
confirmation samples; there is no calibration subset. Repeated paraphrases limit
diversity and this small sample does not establish production reliability.

## Measured results

Raw agreement: 31/38 (81.6%). At 0.9: 25 accepted, 24/25 agreement (96%),
13/38 fallback (34.2%). The accepted mismatch is `data/test.tsv:28`: Jev chose
Coverage Explanations at 0.91, Haiku chose Policy Administration. Six other raw
mismatches fell back; none were omitted.

| Threshold | Accepted | Accepted agreement | Fallback |
| --- | --- | --- | --- |
| 0 | 38 | 81.6% | 0.0% |
| 0.5 | 35 | 88.6% | 7.9% |
| 0.7 | 31 | 90.3% | 18.4% |
| 0.8 | 28 | 96.4% | 26.3% |
| 0.9 | 25 | 96.0% | 34.2% |
| 0.95 | 20 | 100.0% | 47.4% |
| 1 | 19 | 100.0% | 50.0% |

Jev latency p50/p95: 405.7/713.5 ms. Original via OpenRouter: 1122.3/1867.5 ms.
Mean original latency: 1170.7 ms. Expected serial cascade mean: 849.2 ms, computed
from each real Jev latency plus original latency only on fallback rows. This is
an estimate from paired component timings, not an end-to-end cascade benchmark.
Bounded concurrency was four pairs; timing includes network overhead.

Provider-reported cost (`usage.cost`, USD, measured 2026-09-23): mean baseline
$0.000718737; expected cascade $0.000276521 per ticket (about 61.5% lower in this
sample). No price table assumptions or fabricated zero costs. The serial fallback
path adds both inference costs and latencies. Validation itself called both paths
for every sample and therefore did not realize cascade savings.

## Recommendation and limitations

Keep the conservative original fallback and provisional threshold 0.9 for
`workflow.py:83`. Accepted agreement exceeded the skill's 90% check on this small
sample, but parity is not exact. Do not lower the threshold from this result.
The observed 0.95 curve is exploratory; adopting it requires new independent
confirmation. No Jev-only removal is approved or recommended.

Fit is limited to benign English insurance-ticket examples. There is no proven
adversarial-input mitigation; separating ticket data and instructions, limiting
size, and confidence gating do not establish injection resistance. This is not
validation for a hostile public service. No live validation was skipped; direct
Anthropic latency was not measured because the config explicitly authorized the
same-model OpenRouter evaluation adapter.

## Artifacts and setup

`JEV_CONVERSION_PLAN.md`, `JEV_AUDIT.json`, `JEV_PARITY.json`, this report,
`jev_decisions.py`, `validate_jev.py`, `.env.example`, and the small workflow edit.
Runtime variable names: OPENROUTER_API_KEY for Jev; ANTHROPIC_API_KEY for the
unchanged production client/fallback. The original module still initializes its
Anthropic client at import, as upstream did. No environment loader was added.
For hidden credential entry, use `.agents/skills/jevify/scripts/with_jev_key.py`.
No credential values have been printed or saved.

After saving any subsequent work, undo with `git switch main` then
`git branch -D jev-convert/evaluation`. The main branch ref remains at the source
revision. No remote action was taken.
