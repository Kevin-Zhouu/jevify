# Jev conversion report

No good Jev opportunities here.

Source revision: `8b1da0a4d7505b22c1f92283ef848616de773eab`; branch: `main`.
Output mode: **report**. Output repository: `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/openai_demo-codex-headless/original`.
The inactive branch and clone_path config fields do not authorize branch creation or cloning.
Preflight passed: git available, repository initially clean including untracked files, no errors.
Selected access: OpenRouter, environment variable `OPENROUTER_API_KEY`; presence checked and true. No credential value was printed or saved.
Configured Jev pin: `typesafe/jev-1.13-20260917`; not invoked. Risk: conservative.

Approval resolves to zero eligible sites. All three are GENERATION. The configured fallback predicate covers only pure DECISION sites with enumerated outputs. Report mode permits only report artifacts. The authorized same-model OpenRouter baseline route is unused because nothing is converted.

## Result

Zero sites converted. All three original sites remain unchanged for the site-specific reasons below.

| Original site | Provider | Class / fit | Downstream | Option / primitive | Benefit and economics | Risk |
|---|---|---|---|---|---|---|
| `workflow.py:10` | OpenAI Python SDK / OpenAI / gpt-5.5 | GENERATION / NOT A FIT | completion.choices[0].message.content is printed at workflow.py:19, after the standard-request banner at line 9. | `leave` / `none` | Preserves original generation and diagnostics. Expected latency and cost unchanged because the original request remains; no speculative Jev savings. | Existing OpenAI dependency remains; replacing the call with a canned phrase or Choice would change the demonstrated completion behavior. |
| `workflow.py:23` | OpenAI Python SDK / OpenAI / gpt-5.5 | GENERATION / NOT A FIT | The stream is iterated at lines 33–37; empty choices are skipped, delta.content is printed with end="", then a newline at line 38. | `leave` / `none` | Preserves original generation and diagnostics. Expected latency and cost unchanged because the original request remains; no speculative Jev savings. | Existing OpenAI dependency remains; a typed answer or synthetic stream would lose generated guidance and native delta semantics. |
| `workflow.py:42` | OpenAI Python SDK / OpenAI / gpt-5.5 | GENERATION / NOT A FIT | with_raw_response.create returns a response parsed at line 51; response.request_id is printed at line 52 and completion text at line 53. | `leave` / `none` | Preserves original generation and diagnostics. Expected latency and cost unchanged because the original request remains; no speculative Jev savings. | Existing OpenAI dependency remains; fabricating request IDs or changing the raw response/parser would corrupt observable diagnostics. |

Only the plan, JSON audit and this report were added. No source, dependency, environment, branch or commit changes; no push or PR. Upstream source semantics and diagnostics remain intact.

## Validation

The user-supplied independent behavior smoke was executed using Python 3.14 and exited 0:

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/bigsoup/Downloads/Jev\ Converter/eval/smoke.py "/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/openai_demo-codex-headless/original" openai_demo
```

Output: `PASS: observable Python behavior and original-path fallback smoke`.
The smoke executes the actual workflow with original-SDK doubles and network disabled. For this example it asserts three original calls, streamed content, and two standard content outputs. Its generic output mentions fallback; there is no Jev fallback integration in this repository. It does not establish live provider or Jev correctness, and does not independently assert every diagnostic. A clean tracked-file diff confirms the original diagnostics and implementation are unmodified.

Live validation skipped: no sites converted, so paired inference is not applicable, despite the selected credential being present. No model endpoint was tested, no same-model baseline routing was attempted, and no JEV_PARITY.json was written. Sample count, agreement/confidence curves, fallback rate, latency, cost and injected Jev gate faults are all not applicable/unmeasured. No parity or cost-saving claim is made.

Threshold recommendations: workflow.py:10 — none; workflow.py:23 — none; workflow.py:42 — none. All are generation and should stay on the original path. No decision gate is justified.

Artifact checker command:

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 .agents/skills/jevify/scripts/check_artifacts.py "/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/openai_demo-codex-headless/original"
```

Artifact checker result: exit 0; `shape_valid: true`, no errors. This validates artifact shape only, not live inference.

## Limitations and undo

Assessment covers the repository's fixed demonstration prompts. There is no evidence for broader input distributions or production Jev quality. Documentation references and the full approved-scope resolution are in JEV_CONVERSION_PLAN.md.

To undo this report-only run, delete only JEV_CONVERSION_PLAN.md, JEV_AUDIT.json and JEV_CONVERSION_REPORT.md from this repository. No branch switch or clone deletion is necessary.
