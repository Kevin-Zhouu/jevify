# Jev conversion report

No good Jev opportunities here.

The approved `fallback` action was restricted to pure DECISION sites with enumerated outputs. Zero sites met that predicate. All three sites (`workflow.py:10`, `workflow.py:23`, `workflow.py:42`) are GENERATION and remain unchanged. No source, dependency, environment, prompt, parsing, logging or provider changes were made. Actual request-ID diagnostics remain intact.

Source revision: `2875b87b890f1a9c61dbfe34121c1ca04f52c2e9` on `main`. Output mode: branch `jev-convert/evaluation` in `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-01/openai_demo-codex-interactive/original`. The clone path does not apply to branch mode. Setup, audit, options and approval resolution are recorded in `JEV_CONVERSION_PLAN.md` and `JEV_AUDIT.json`.

## Validation performed

The supplied independent smoke command passed with exit code 0:

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 '/Users/bigsoup/Downloads/Jev Converter/eval/smoke.py' '/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-01/openai_demo-codex-interactive/original' openai_demo
```

Output: `PASS: observable Python behavior and original-path fallback smoke`.

This is an offline behavioral smoke using deterministic original-SDK doubles, not live inference. The openai_demo assertions verify three original requests, streamed content and two standard generated outputs. The supplied fixture injects network timeouts, but this unchanged workflow introduces no Jev wrapper; the generic smoke success message is not evidence of Jev fallback testing. It does not independently assert every diagnostic or error path.

An additional byte-for-byte comparison of `workflow.py` against the source revision passed, preserving all upstream source semantics and diagnostics. JSON checks passed for the three original site IDs, their GENERATION classifications and empty selected/converted lists. No project test command exists.

## Live evidence and limitations

Live validation skipped: no converted sites, so no parity calls are needed. No credentials were read, printed or saved. Requested Jev provider/model was OpenRouter / `typesafe/jev-1.13-20260917`; it was not called. Production retains OpenAI / `gpt-5.5` unchanged. The authorized isolated baseline routing adapter was unnecessary and was not created.

Live sample count: 0. No live input set, calibration/check split, agreement curve, fallback rate, latency, cost or request-ID measurements exist. No parity claim is made and no `JEV_PARITY.json` is written. Per-site thresholds for all three sites: not applicable. Jev transport/gate fault assertions: not applicable; no adapter exists. No savings are claimed.

Only the audit, plan and report artifacts are included in the branch commit. No push or PR is performed.

## Undo

From this repository, after ensuring no later work would be lost:

```sh
git switch main
git branch -D jev-convert/evaluation
```
