# Conversion report

Approved fallback conversion completed in `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/anthropic_classification-codex-interactive/converted` on branch
`jev-convert/evaluation`. Source revision: `1c953f75ebe1580de909072ce9a73b8ab8f11d05` (`main`).
Original repository remains unchanged. No push or PR was made.

Only `workflow.py:83` was converted: DECISION, ten insurance-support labels.
No MIXED, GENERATION, EXTRACTION, additional wrappers or consumers were found.
All options except conservative fallback were declined and remain unimplemented.

## Behavior and implementation

`workflow.simple_classify(X)` remains synchronous and returns a string. Its original
body is preserved verbatim apart from the function name, as `_original_simple_classify`.
AST identity and request equality assertions passed. Original category definitions,
prompt replacement behavior, assistant prefill, stop sequence, 4096 token budget,
temperature 0, `claude-haiku-4-5`, and `.strip()` parsing remain unchanged.
There were no upstream usage, finish-reason or reasoning diagnostics to adapt or remove.
Original exceptions propagate without retry; failure injection verified exception identity.

`jev_decisions.py` owns the Choice question, criteria, pin, confidence gate and size bounds.
Provider: OpenRouter. Pin: `typesafe/jev-1.13-20260917`. Selected threshold: **0.95**.
HTTP has a 15-second timeout/read deadline, no retries, 16,000-byte request bound and
1 MiB response bound. Oversize/unsupported inputs, missing key, transport failures,
HTTP errors, malformed responses and rejected confidence take the original path once.
Model, primitive, label, finite confidence, probability distribution and usage are validated
before acceptance. Logging emits path/model/bounded reason at INFO without inputs or secrets;
configure standard Python logging to view it. Stdout remains unchanged.
Production fallback remains Anthropic, requiring the existing SDK and `ANTHROPIC_API_KEY`.
The original eager Anthropic client initialization is preserved, including its startup requirements.
No additional packages were installed or added. `.env.example` contains variable names only.

## Live evidence and result

34 unique paired live evaluations completed with **no transport failures**:
30 repository confirmation tickets, three per each of ten labels from `data/test.tsv`,
and four separately identified synthetic diagnostics (ambiguous, empty and out-of-domain).
Fixture labels were used for sampling coverage, never as substitutes for original live answers.
No calibration set was used: 0.95 was fixed before measurements and was not retuned.
`data/train.tsv` was not used for tuning. The fixtures are a small, related example distribution.

The baseline executed the preserved original function through an explicitly authorized isolated
OpenRouter SDK-boundary adapter. Only authentication/transport, the same-model namespace
`anthropic/claude-haiku-4.5`, and `stop_sequences` -> `stop` changed in evaluation.
Original prompts, prefill, parsing and model parameters were preserved; provider support for
parameters was required. This measures a gateway baseline, not direct Anthropic latency/cost.

For each row, the actual production evaluator ran once. Its real response was replayed through
the actual public wrapper/gate, asserting the string return and zero/one fallback calls.
Raw Jev answers are recorded before fallback, along with request IDs, probabilities, usage,
provider-reported costs and monotonic timings. No successful Jev response was fabricated.
Captured-response mutations and forced rejection are explicitly injected control-flow tests.

Confirmation raw agreement: **26/30 (86.7%)**.
At deployed 0.95: **16/16 accepted agree (100%)**, **14/30 fallback (46.7%)**.
The >=90% accepted-agreement target passed on this sample. This is not a correctness guarantee.
All four raw disagreements were rejected by the deployed gate and remain visible below.

| Threshold | Accepted / 30 | Accepted agreement | Fallback fraction |
| --- | --- | --- | --- |
| 0.00 | 30 | 86.7% | 0.0% |
| 0.50 | 28 | 85.7% | 6.7% |
| 0.80 | 22 | 95.5% | 26.7% |
| 0.90 | 18 | 94.4% | 40.0% |
| 0.95 | 16 | 100.0% | 46.7% |
| 0.99 | 15 | 100.0% | 50.0% |
| 1.00 | 14 | 100.0% | 53.3% |

| Fixture | Raw Jev answer | Original answer | Confidence |
| --- | --- | --- | --- |
| data/test.tsv:3 | Billing Disputes | Billing Inquiries | 0.75 |
| data/test.tsv:13 | Policy Comparisons | Coverage Explanations | 0.68 |
| data/test.tsv:28 | Coverage Explanations | Policy Administration | 0.91 |
| data/test.tsv:30 | Coverage Explanations | Policy Administration | 0.79 |

Synthetic diagnostic set: 3/4 raw agreement, 2/2 accepted agreement, 2/4 fallback.
The ambiguous claim/policy request differed (Claims Assistance vs General Inquiries),
at confidence 0.55; fallback occurred. Diagnostics did not influence the selected threshold.

## Measured latency and cost

Confirmation Jev p50/p95: **380.4/736.1 ms**.
Original via OpenRouter p50/p95: **1212.0/2481.9 ms**.
Original mean latency: 1331.4 ms. Estimated serial cascade mean:
**1030.5 ms** (22.6% lower).
This estimate sums measured Jev latency plus measured original latency on rejected rows;
it is not a separately timed production cascade. Individual fallback requests add latency.

Costs use actual `usage.cost` returned by OpenRouter on 2026-09-23; no token-price estimates.
Original mean: **$0.00072670/ticket**.
Estimated cascade mean: **$0.00036834/ticket**,
**49.3% lower**.
Formula: mean(Jev cost + actual rejection indicator * paired original cost).
This is a workload estimate; paired testing paid for both models on every row.
Gateway overhead, provider choice, caching and short-run variation limit generalization.

## Executed checks

- Supplied independent smoke: PASS (observable string result and exactly one original fallback).
- Source AST identity, original request equality, actual wrapper response replay: PASS.
- Forced gate rejection, generic error, timeout and HTTP 429: PASS, original called once.
- Original exception identity, missing key, malformed response, NaN/bool confidence,
  unknown option, invalid/missing usage, wrong model, unsupported/oversize input: PASS.
- Replay of saved genuine live responses and sanitized answer-path logs: PASS.
- Artifact checker with `--require-live`: recorded in `JEV_ARTIFACT_CHECK.json`.

Reproduce from the converted repository with Python 3.10+ (used Python 3.14):

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 validate_jev.py
/opt/homebrew/opt/python@3.14/bin/python3.14 validate_jev.py --replay-only
/opt/homebrew/opt/python@3.14/bin/python3.14 '/Users/bigsoup/Downloads/Jev Converter/eval/smoke.py' '/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/anthropic_classification-codex-interactive/converted' anthropic_classification
/opt/homebrew/opt/python@3.14/bin/python3.14 '../original/.agents/skills/jevify/scripts/check_artifacts.py' . --require-live
```

The live command requires the OpenRouter environment key and makes billable calls;
`--replay-only` uses saved real captures without network, with key presence needed by the
unchanged production evaluator. For hidden key entry, use the installed skill launcher
`../original/.agents/skills/jevify/scripts/with_jev_key.py --help`. Never put keys in artifacts.
The upstream example has no project test command. The external smoke file was read and run,
never edited. No labels, graders, other runs or other corpus files were inspected.

## Recommendation and limitations

Retain **0.95 plus original fallback** for this benign example distribution. Do not lower it
based only on this same confirmation set. Confidence is distribution concentration, not
correctness or injection resistance. Arbitrary hostile customer input remains unvalidated;
no effective input-injection mitigation existed upstream, and none is claimed here.
The ten-label vocabulary and General Inquiries catchall remain unchanged.
Conservative fallback remains even though accepted agreement passed.

Artifacts: `JEV_CONVERSION_PLAN.md`, `JEV_AUDIT.json`, `JEV_PARITY.json`, this report,
`validate_jev.py`, `JEV_VALIDATION.log`, and `JEV_ARTIFACT_CHECK.json`.
Documentation sources and preflight facts are recorded in the plan.

Undo: continue using the untouched `original` repository. To remove this conversion,
delete only the sibling `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/anthropic_classification-codex-interactive/converted` clone; no original branch changes need reversal.
