# Validation and evidence

Tests must exercise behavior, not only compile/import. Run the project's own command after conversion. For a vendored example without a test suite, use its smoke entrypoint or a clearly disclosed behavioral smoke that checks the original return and diagnostic contracts. Original-provider test doubles and transport fault injection are legitimate tests; they are NOT live Jev parity. Do not mock successful Jev inference or substitute another model for Jev.

## Paired live measurement

First check the selected key exists with the read-only preflight helper; never print it. Do not infer absence from the smoke test, which deliberately disables network. With key present and an authorized original route, live measurement is required, even when offline smoke already passes.


For each converted site use at least 30 **unique** realistic inputs, drawn from tests/fixtures/examples first. Trace the original input schema. If insufficient, ask interactively or construct clearly labeled synthetic cases headlessly. Cover normal, ambiguous, boundary and out-of-domain cases. Do not cherry-pick away disagreements. Separate calibration from a fresh confirmation set when choosing thresholds; report both and sample counts. Thirty examples is a small estimate, not production assurance.

For each input run (1) the original function/model/prompt/parsing, (2) the actual converted decisions module with the same state, and (3) check the observable integration contract. Import and invoke the actual production evaluator and gate. Importing constants while rewriting the evaluator is weaker and can miss integration defects. Import the module's actual questions and thresholds. Using a simplified new baseline prompt proves a different workflow and is invalid. Preserve original model parameters, structured-output behavior and stop sequences when routing an authorized baseline through a gateway. A provider's namespaced ID is fine if it is the same model, but a different model is not a valid baseline. Do not convert the production fallback provider just to make evals run.

If the original function imports a provider SDK, an isolated transport adapter may forward its unchanged request to a user-authorized equivalent endpoint, then return the same SDK response shape. Record this adapter and authorization. Do not copy the baseline prompt by hand: invoke the preserved original callable with its transport adapted, or capture the exact SDK request from that callable. Retain an assertion proving the original request and parsing are unchanged. Do not use hand labels as a substitute for original live outputs. If baseline access fails or a required capability does not exist, stop claiming parity; retain conservative fallback and report the blocking response without secrets.

Measure monotonic elapsed time, real usage/cost or a clearly labeled estimate using sourced token prices. Capture provider request IDs and pinned model ID plus sanitized response metadata. Consult the actual response schema for the ID (it may be in the JSON body, not an HTTP header); an empty ID or a fabricated identifier is not evidence. Do not report zero cost when unknown. Record whether cost is provider-reported or estimated; model pricing changes, so date the source. Log raw evidence only if input privacy permits; public fixture/synthetic inputs are suitable. Never save headers or credentials. Use bounded concurrency/timeouts and avoid unbounded retries.

## Threshold and error proof

Report raw agreement for all pairs and selective agreement at thresholds including the selected threshold, sample count accepted and fallback fraction. Selective agreement = matching accepted pairs / accepted pairs; zero accepted rows does not establish parity. Target at least 90% accepted agreement for a claimed successful conversion; keep all failures visible. Also report original and Jev p50/p95 latency and expected cascade cost/latency. Fallback can be slower and more expensive than the original on difficult inputs. Confidence measures distribution concentration, not correctness.

Exercise the actual wrapper with a fallback sentinel/counter: force low confidence at the **gate boundary**, timeout, rate-limit and generic error at transport boundaries. Verify exactly one original call and identical output/error propagation. Record these as injected control-flow tests, not Jev model outputs. For accepted-path assertions replay an ACTUAL captured live response. Do not build a fake successful Jev response with invented label/probabilities/usage; gate-only tests can call the pure predicate with numbers and transport tests can raise exceptions. For a low-confidence gate test, use a real captured response or directly call the pure gate with below-threshold confidence; never present a mocked success as measured inference. Include missing key, malformed/nonfinite response and unknown option tests where practical.

When conservative fallback remains, the recorded `jev_answer` is the raw Jev decision and `original_answer` the original result, before fallback; otherwise comparing fallback outputs falsely inflates parity. `fallback_taken` reflects actual gate behavior. Validate errors separately so successful inference rows aren't mixed with made-up responses.

## Artifacts

Write `JEV_CONVERSION_REPORT.md` with source revision, output mode, approvals, changed/unchanged sites, model/provider, test commands/results, input provenance, n, agreement curve, fallback rate, latency, cost assumptions, recommended threshold per site, faults, limitations, skipped work, and exact undo steps. Negative controls require the clear conclusion “No good Jev opportunities here” and no code/env/dependency edits.

For Choice/Score, save paired results to `JEV_PARITY.json`:

```json
{"sites":[{"site_id":"src/route.ts:42","threshold":0.9,"rows":[{"input":"public or synthetic sample","provenance":"repo","model":"typesafe/jev-1.13-20260917","live":true,"request_id":"real provider ID","jev_answer":"billing","original_answer":"billing","confidence":0.98,"fallback_taken":false,"latency_ms":42.1,"cost_usd":0.00001,"original_model":"openai/gpt-4o-mini","original_latency_ms":210.3,"original_cost_usd":0.0001}],"faults":{"below_threshold":true,"error":true,"timeout":true,"rate_limit":true}}]}
```

`provenance` is the literal enum `repo` or `synthetic`; put fixture paths and line numbers in a separate `source` field. `primitive` for leave options is the string `none`, not null. Include all metric fields; if a metric is unknown, say validation is incomplete rather than substituting zero. All four fault booleans require executed assertions, never a code-inspection checkmark. Run the artifact shape checker before handback; it cannot verify truth and does not replace reviewing real traces.

Values above illustrate the schema ONLY; never copy them as evidence. Store actual numbers, input provenance and IDs. Include scripts/commands or sanitized traces sufficient to reproduce the measurements, usage and cost source, calibration/check split, and fault assertions. `faults: true` requires an executed passing assertion. Noul evidence instead uses `probability`, `abstention_band` and probability bins; no fake confidence. No conversions means no parity calls are needed and no parity claim should be made. No key means explicitly **live validation skipped**, never “passed”.
