# Jev conversion report

Completed only approved `fallback` conversion at original `workflow.py:83` (DECISION). Source revision: `fd78ebff05048c9ed2a20540f9f89cc7aeed09cb`. Output: sibling clone `converted`, local branch `jev-convert/evaluation`. Original repository remains clean and untouched. No push or PR.

`simple_classify(X)` stays synchronous and returns a string. Its original body is unchanged under `_original_simple_classify`: same categories, prompt, assistant prefill, stop sequence, max_tokens, temperature, Anthropic model, strip parsing and exception propagation. AST comparison passed. No upstream diagnostics or metadata were removed; none were emitted by this function. New INFO library logs contain only path, model and bounded reason and do not configure logging or write stdout. Other original files are unchanged.

`jev_decisions.py` contains the exact ten labels/descriptions, question, state bound, threshold and dated OpenRouter model `typesafe/jev-1.13-20260917`. The HTTP adapter uses the documented System One endpoint, 10-second socket timeout and no retries. Missing key, unsupported/oversized state, rejected schema/model/label/confidence, transport errors and low confidence return through the original path exactly once. The original exception is never caught and retried. The 2000-byte UTF-8 bound is a conservative application limit, not an adversarial-content detector.

## Validation

Python used: `/opt/homebrew/opt/python@3.14/bin/python3.14`. Upstream has no project test command.

- PASS: supplied `/Users/bigsoup/Downloads/Jev Converter/eval/smoke.py` with output path and `anthropic_classification`; original fallback returns the stripped string exactly once.
- PASS: `python3 scripts/validate_jev.py` control-flow assertions: timeout, HTTP 429, generic failure, pure below-threshold gate plus rejected-answer wrapper, invalid JSON/schema, nonfinite/out-of-range confidence and unknown label gates, missing key, oversized/unsupported input and original exception identity. See `JEV_VALIDATION.json`. These are injected control-flow tests, not inference measurements.
- PASS: AST comparison of original function body; `git diff --check`.
- Live: `python3 scripts/validate_jev.py --live`, resumed after transient timeouts. 49 unique successful paired inputs: 9 train/calibration and 40 test/confirmation (four per category). Inputs come exclusively from repository TSV fixtures; fixture labels guide sampling only and are never substituted for live original answers. All six confirmation disagreements are retained.

The explicitly authorized isolated adapter forwards the unchanged original request to OpenRouter `/api/v1/messages`, changing only the model ID to its equivalent `anthropic/claude-haiku-4.5`. It returns the Anthropic content shape to the unchanged parser. Production fallback still uses Anthropic. Real Jev responses are replayed through the public wrapper to assert accepted and fallback integration; this does not mock successful inference or make duplicate paid calls. Raw Jev labels are recorded before fallback.

## Measured results

Threshold was fixed at 0.95 before calibration and never tuned on confirmation.

| Set | Pairs | Raw agreement | Accepted at 0.95 | Accepted agreement | Fallback |
| --- | ---: | ---: | ---: | ---: | ---: |
| Calibration | 9 | 100% | 6 | 100% | 33.3% |
| Confirmation | 40 | 85% | 22 | 100% | 45% |
| Combined | 49 | 87.8% | 28 | 100% | 42.9% |

| Confirmation threshold | Accepted | Accepted agreement | Fallback |
| --- | ---: | ---: | ---: |
| 0 | 40 | 85% | 0% |
| 0.8 | 30 | 93.3% | 25% |
| 0.9 | 24 | 100% | 40% |
| 0.95 | 22 | 100% | 45% |
| 0.99 | 19 | 100% | 52.5% |

Confirmation latency p50/p95: Jev 355/588 ms; original via OpenRouter 1023/1704 ms. Combining separately measured timings gives an estimated serial-cascade mean of 946 ms on successful confirmation pairs. This is not measured production end-to-end latency.

Provider-reported `usage.cost` gives a confirmation cascade mean of $0.00035729215 per successful pair (Jev + original cost when fallback). Combined successful-pair cascade mean is $0.00034045563, versus $0.00072553061 original-only, about 53.1% lower on this sample. These are gateway costs from the measured calls, not Anthropic direct billing estimates. See full usage, request IDs, distributions, per-input latency, cost and split curves in `JEV_PARITY.json`.

Two Jev requests timed out across attempts, including one calibration case; these are visible separately in the evidence and are excluded from successful-pair aggregates. First-attempt original usage and latency were not retained. A separate successful Jev availability probe was also not included in paired aggregates. Total session spend is therefore not claimed. Timeouts add up to the configured wait before original fallback and can eliminate latency savings. No automatic retries or provider/model substitutions were added.

## Recommendation and limits

Retain threshold 0.95 and conservative fallback for fixture-like benign tickets. The accepted confirmation agreement exceeds the 90% target on this small sample, but 22 accepted cases do not establish production-wide parity. Overlapping labels cause disagreements; all observed confirmation disagreements fell below the chosen threshold. No generated or mixed content was converted.

The fixture sample includes overlapping billing/policy intents and General Inquiries; adversarial inputs, arbitrary out-of-domain content, non-English text and long inputs have not been live-validated. The API still accepts arbitrary caller strings: the benign-input scope is a usage constraint, not enforced trust classification. Confidence is not a prompt-injection defense. See [Jev limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md). Never infer that high confidence makes hostile inputs safe.

## Setup, artifacts and undo

No new dependency is required beyond upstream `anthropic`; the Jev adapter uses the standard library. Set `OPENROUTER_API_KEY` in runtime environment for Jev and retain `ANTHROPIC_API_KEY` for production fallback. `.env.example` contains names only; it is not automatically loaded. The existing `.agents/skills/jevify/scripts/with_jev_key.py` launcher supports hidden key entry (see its `--help`); never put secrets into source or command arguments. Production still requires upstream Anthropic client initialization.

Artifacts: `JEV_AUDIT.json`, `JEV_CONVERSION_PLAN.md`, `JEV_CONVERSION_REPORT.md`, `JEV_PARITY.json`, `JEV_VALIDATION.json`, and reproducible `scripts/validate_jev.py`.

Undo: return to the original repository and delete only the sibling `converted` clone when no longer needed. No original branch or remote was changed.
