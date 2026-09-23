# Jev conversion report

Implemented one conservative, opt-in conversion on `jev-convert/no-key`.
Source revision: `49de9153ceeb3dbd27df8b215022f795d1787417` (`main`).
Output mode: branch, in `/Users/bigsoup/Downloads/Jev Converter/eval/runs/supplemental-03/no-key-codex/original`.
The supplied headless predicate approved fallback for pure enumerated decisions.
Resolved selection: `workflow.py:83`, the provider call inside `simple_classify`.
No other inference sites were found; no generation behavior was converted.

`simple_classify(X)` retains its synchronous signature and string result.
The original Anthropic body is preserved as `_original_simple_classify`; an AST
comparison against the source revision passed. Its model, prompt, prefill,
stop sequence, parser and exception propagation are unchanged. No dependencies
were added. All Jev questions, categories, limits and gating live in
`jev_decisions.py`. Original initialization still requires Anthropic access.

Provider selection remains `none` for this run. The dormant direct TypeSafe
adapter pins `jev-1.13.0`, as documented in [Models](https://docs.typesafe.ai/models).
It can only run after future explicit `JEV_PROVIDER=typesafe`, a process
`TYPESAFE_API_KEY`, and `JEV_INPUT_POLICY=trusted` configuration. Blank placeholders
are in `.env.example`. No secret file was read, created or populated; no key was
sought beyond the skill's preflight process check. The optional skill launcher
`.agents/skills/jevify/scripts/with_jev_key.py --help` describes hidden-input setup.
No live provider was selected or contacted in this run.

Eligibility remains conditional. Arbitrary public tickets have no proven
adversarial mitigation and must not be marked trusted. The setting is an operator
attestation about a reviewed input distribution, not a detector. Confidence and
instruction wording do not establish robustness. See [Jev limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13).
No corpus or labels were read or used to claim accuracy.

## Validation

**Live validation skipped** because access is `none`; preflight reported
key_present false and no selected key variable. Zero live pairs and no accepted
Jev response capture. Parity, confidence-agreement curve, observed fallback rate,
latency percentiles and dollar costs are unknown, not zero or passed.
The deployed 0.95 confidence threshold is provisional, not a production
recommendation. Retain fallback and calibrate with at least 30 unique realistic
pairs per site and an independent confirmation set before relying on it.

Executed with `/opt/homebrew/opt/python@3.14/bin/python3.14`:

- `-m unittest -v test_jev_fallback`: **10 tests passed**. Covers original AST
  identity; disabled provider, untrusted configuration and missing key; oversized
  state; invalid confidence and malformed container rejection; gate-boundary
  low-confidence injection; transport-boundary generic error, timeout and HTTP
  429; original exception identity and exactly-once fallback.
- `"/Users/bigsoup/Downloads/Jev Converter/eval/smoke.py" "/Users/bigsoup/Downloads/Jev Converter/eval/runs/supplemental-03/no-key-codex/original" anthropic_classification`:
  **PASS: observable Python behavior and original-path fallback smoke**.
  The supplied smoke was executed unchanged and was not inspected or edited.

These are offline tests with transport faults and original-provider doubles,
not measured inference. No successful Jev response, distribution, usage, request
ID or agreement was fabricated. Test inputs are synthetic strings in the test
file, not a representative benchmark. No pre-existing project test suite exists.
`JEV_PARITY.json` records empty rows and only executed fault assertions.

The adapter uses a three-second socket timeout during connection and body reads,
an elapsed-time check through parsing, and a 64 KiB response cap, without retries.
This is not a hard wall-clock cancellation guarantee for OS DNS resolution or
a blocking socket operation already in progress. Rejected/malformed answers,
missing credentials and all Jev exceptions call the original exactly once.
Standard Python INFO logging records path, actual answering model and bounded
reason codes; application logging configuration controls visibility. Inputs,
headers and secrets are not logged. Stdout remains unchanged.

Economics are unmeasured. Expected cascade cost is Jev cost plus fallback
fraction times original cost. Accepted decisions may be cheaper/faster; misses
add a request before Anthropic. No savings are claimed.

## Artifacts and undo

Plan: `JEV_CONVERSION_PLAN.md`; audit: `JEV_AUDIT.json`; offline tests:
`test_jev_fallback.py`; validation status: `JEV_PARITY.json`.
The artifact shape checker passed (`shape_valid: true`, no errors); it verifies structure only. `git diff --check` also passed.
Live integration and successful Jev answer acceptance remain incomplete.
No push or PR was performed.

To undo after preserving any later work: `git switch main`, then
`git branch -D jev-convert/no-key`. The original branch remains at the source SHA.
