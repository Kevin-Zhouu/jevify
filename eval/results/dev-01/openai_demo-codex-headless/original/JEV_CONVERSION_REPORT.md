# Jev conversion report

**No good Jev opportunities here.** All three OpenAI calls generate text. None qualifies for the configured pure-DECISION fallback approval.

Source revision: `2b8ff7b9c1cde431c889a2e6296305e18bb3d0e0`. Output mode: report, on original branch `main` at `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-01/openai_demo-codex-headless/original`. Conservative posture. Configured candidate provider/model: OpenRouter / `typesafe/jev-1.13-20260917`; never invoked. Production remains OpenAI / `gpt-5.5`.

## Results

| Original ID | Provider/model | Downstream | Class | Fit | Selected option, benefit and risk |
|---|---|---|---|---|---|
| workflow.py:10 | OpenAI SDK / gpt-5.5 | completion.choices[0].message.content -> print at workflow.py:19 | GENERATION | NOT A FIT | leave; primitive none. Preserve behavior; no savings. Existing provider costs/failures remain. |
| workflow.py:23 | OpenAI SDK / gpt-5.5 | stream iterator -> skip empty choices at lines 34-35 -> print delta.content with end="" at line 37 -> final newline at line 38 | GENERATION | NOT A FIT | leave; primitive none. Preserve behavior; no savings. Existing provider costs/failures remain. |
| workflow.py:42 | OpenAI SDK / gpt-5.5 | raw response -> parse() at line 51 -> print response.request_id at line 52 -> print message.content at line 53 | GENERATION | NOT A FIT | leave; primitive none. Preserve behavior; no savings. Existing provider costs/failures remain. |


Converted sites: **0**. Threshold recommendation for each site: **not applicable; leave unchanged**. No source, dependency, environment, skill or tracked configuration changes. Only JEV_CONVERSION_PLAN.md, JEV_AUDIT.json and this report are added. No branch, clone, commit, push or PR was created. See the plan for complete consumer tracing, approval resolution and current documentation links.

## Validation

Executed successfully with exit code 0:

```sh
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/opt/python@3.14/bin/python3.14 '/Users/bigsoup/Downloads/Jev Converter/eval/smoke.py' '/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-01/openai_demo-codex-headless/original' openai_demo
```

Output: `PASS: observable Python behavior and original-path fallback smoke`

This is an offline behavioral smoke using original-SDK doubles. For openai_demo it asserts three original calls, streamed text, and two non-streamed content outputs. Network access is faulted by the supplied smoke. Its generic success text mentions fallback, but no Jev fallback was added or exercised. The test does not establish live model quality, full SDK compatibility, or separately assert request-ID printing. The request-ID print and all diagnostics are preserved by keeping source unchanged. The upstream example has no project test command. No test output files were generated in the checkout (bytecode writing disabled).

**Live validation skipped** because no sites were converted and no eligible Jev replacement exists. Credential availability was not probed. The authorized equivalent-provider baseline evaluation adapter was unnecessary and was not created. Paired sample count: 0. Agreement, confidence curve, fallback rate, p50/p95 latency, cost and cascade economics: not measured. No threshold calibration or confirmation split; no Jev fault-injection assertions. No JEV_PARITY.json is written and no parity claim is made.

The workflow contains two unique fixed prompts. No synthetic inputs or new model requests were introduced. Leaving the workflow unchanged claims no speculative cost or latency reduction. Live documentation was retrieved; no model inference was performed.

## Undo

Remove only the three newly created report artifacts from this checkout: `JEV_CONVERSION_PLAN.md`, `JEV_AUDIT.json`, `JEV_CONVERSION_REPORT.md`. There is no conversion branch or clone to remove, and the original branch/revision remains unchanged.
