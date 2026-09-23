# Jev conversion report

Converted `workflow.py:83` on branch `jev-convert/evaluation` in `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/anthropic_classification-codex-headless/original`.
Original source: `1c953f75ebe1580de909072ce9a73b8ab8f11d05` on `main`.
Config output mode is branch; its inactive clone path was ignored. Preflight found a clean repository, unused branch and the configured OpenRouter key present. No credential values were printed or saved.

## Scope and behavior

The configured predicate approved conservative fallback for pure enumerated DECISION sites; the only site qualified. `workflow.simple_classify(X)` remains synchronous and returns a category string. Its original body is preserved as `_original_simple_classify`; AST identity (except rename), exact request equality and original parsing were asserted during validation. The ten category definitions, Anthropic initialization, model, prompt, assistant prefill, stop sequence, temperature and max_tokens remain unchanged. There are no upstream printed usage/finish diagnostics or other public response fields to adapt. No other inference sites or local consumers exist.

`jev_decisions.py` owns the Choice policy, pin `typesafe/jev-1.13-20260917`, confidence threshold **0.90**, 8-second request deadline and 8,000-byte state bound. It uses the OpenRouter System One endpoint. Missing key, oversized/unsupported input, malformed response, wrong model/type/label, invalid confidence, timeout, rate limit, other errors and low confidence take the original Anthropic path. Original exceptions propagate without retry. Logging uses the module logger at INFO with only path, answering model and bounded reason; configure application logging to view it. Stdout stays unchanged. No dependencies were added.

## Actual validation

- Supplied independent smoke: **PASS**, observable Python behavior and original-path fallback.
- **36 live paired comparisons**, no transport failures: 30 unique repository test tickets (first three per category) plus six clearly labeled synthetic ambiguous, boundary and out-of-domain cases. Repository train/test fixtures each contain 68 rows, ten categories; maximum test ticket size is 352 UTF-8 bytes. All samples were confirmation; threshold was fixed beforehand, no calibration or retuning.
- Raw Jev/original agreement: **29/36 (80.6%)**.
- At deployed 0.90: **22 accepted; 21/22 (95.5%) agreement**, **14/36 (38.9%) fallback**. This exceeds the skill's 90% selective agreement target on this small check set, not proof of universal parity.
- Combined outputs agree with the original on 35/36 pairs, but this is not raw model parity.
- Real Jev response captures were replayed through the actual public wrapper, evaluator/parser and gate, proving zero/one original calls, correct returned string, unchanged stdout and correct path/model logs.
- Injected error, timeout, actual HTTP-status-429 transport exception, missing-key, malformed-response and forced low-confidence gate checks passed. Original exception identity propagated after exactly one original call. Mutations of actual captures tested NaN/infinity/bool/out-of-range confidence, unknown labels, wrong primitive and model. These are control-flow assertions, not extra live inference samples.

Accepted disagreement (retained in evidence):
- `data/test.tsv:28`: Jev `Coverage Explanations`, original `Policy Administration`, confidence 0.94.

| Confidence threshold | Accepted | Agreement among accepted | Fallback fraction |
| --- | ---: | ---: | ---: |
| 0.00 | 36 | 80.6% | 0.0% |
| 0.50 | 33 | 87.9% | 8.3% |
| 0.70 | 28 | 89.3% | 22.2% |
| 0.80 | 25 | 96.0% | 30.6% |
| 0.90 | 22 | 95.5% | 38.9% |
| 0.95 | 18 | 100.0% | 50.0% |
| 0.99 | 17 | 100.0% | 52.8% |

Recommendation for `workflow.py:83`: retain provisional **0.90** and original fallback. The observed 0.95 curve is exploratory; it was not used to change the deployed policy. Any tuning needs a new independent confirmation set.

## Measured economics

Jev p50/p95 latency: **399.3/667.5 ms**.
Original via authorized OpenRouter p50/p95: **1061.1/2276.7 ms**.
Mean original cost: **$0.000720889** per ticket.
Estimated cascade mean cost from measured per-row usage: **$0.000309688** (57.0% lower on these samples).
Estimated serial cascade mean latency: **960.6 ms** versus measured original mean **1215.7 ms**.
Costs are provider-reported `usage.cost`, not price-table estimates. Cascade estimates add each Jev cost/latency to the original only for rows that actually fell back. They are not measured direct-Anthropic production cascade benchmarks. Bounded four-worker evaluation and gateway routing may affect timing. Each miss adds Jev overhead.

## Proof, reproduction and limits

`validate_jev.py` loads original source from the recorded git revision and invokes its real prompt builder/parser. An isolated SDK-boundary transport adapter maps `stop_sequences` to OpenRouter `stop` and namespaces the SAME model as `anthropic/claude-haiku-4-5` (responses identify it as `anthropic/claude-haiku-4.5`). It keeps all messages, including assistant prefill, and every generation parameter. This route is explicitly authorized by config. It does not alter the production fallback. The validation adapter uses the standard-library HTTP client and returns the content shape consumed by the unchanged parser; it does not validate unrelated Anthropic SDK internals.

`JEV_PARITY.json` contains actual IDs, answers, probabilities, confidences, model versions, usage/cost and elapsed times, raw-versus-fallback flags, integration assertions and fault results. `JEV_VALIDATION_OUTPUT.txt` preserves the executed summary. No fabricated successful Jev responses or hand-label substitutes were used. Fixture labels select balanced samples, not baseline answers.

This small benign English fixture set does not establish adversarial robustness. Upstream has no injection mitigation; confidence is not one. Fit is scoped to benign examples. High-confidence disagreements remain possible. There are no claims of exact model-equivalent answers, production reliability or direct-Anthropic latency savings.

Commands (Python 3.14; no upstream project test command):

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 validate_jev.py
/opt/homebrew/opt/python@3.14/bin/python3.14 '/Users/bigsoup/Downloads/Jev Converter/eval/smoke.py' '/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/anthropic_classification-codex-headless/original' anthropic_classification
/opt/homebrew/opt/python@3.14/bin/python3.14 .agents/skills/jevify/scripts/check_artifacts.py . --require-live
git diff --check
```

Runtime setup: install upstream's `anthropic` dependency as usual and supply `ANTHROPIC_API_KEY` for original fallback plus `OPENROUTER_API_KEY` for Jev. `.env.example` contains empty placeholders only; code does not automatically load dotenv files. The installed `.agents/skills/jevify/scripts/with_jev_key.py` offers hidden-input launching (see its `--help`). Never place credentials in source or shell arguments.

Artifact checker and final diff status are recorded in `JEV_CHECKS.txt`. No pushes or PRs were performed.

Undo after committing: `git switch main`, then `git branch -D jev-convert/evaluation`. The original branch ref remains unchanged.
