# Jev conversion report

Source revision: `0c64fdf0c13a8b8609cc52d0f83e4f9d91eeca39` on original branch `main`.
Output: branch `jev-convert/evaluation` in `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/openai_demo-codex-interactive/original`. The inactive clone_path is unused.

Approval permits fallback conversion only for pure DECISION sites with enumerated outputs, preserving all externally observable fields. All other conversion options are declined. The predicate resolves to **zero selected sites**. All three GENERATION sites remain unchanged; no decomposition, router, fallback adapter, dependency, environment, or production provider change is authorized or needed.

| Original site | Classification / fit | Downstream contract | Option / resolution |
| --- | --- | --- | --- |
| workflow.py:10 | GENERATION / NOT A FIT | Print completion text | A: leave; excluded from conversion |
| workflow.py:23 | GENERATION / NOT A FIT | Stream explanation; skip empty choices; preserve deltas and newline | B: leave; excluded from conversion |
| workflow.py:42 | GENERATION / NOT A FIT | Parse raw response; print request ID and completion text | C: leave; excluded from conversion |

Each leave option has primitive `none`, unchanged cost/latency because the original request remains, and no migration risk. There are no additional local workflow calls or shared wrappers. The exact machine-readable options and downstream consumers are in `JEV_AUDIT.json`.

No good Jev opportunities here. The workflow generates text and a streamed explanation, rather than consuming bounded decisions. Replacing those outputs with typed decisions would alter public behavior. The prior recommendation cited Jev's generation limitation: https://docs.typesafe.ai/model-jaggedness/jev-1.13.md#generation .

Preflight: clean repository, requested branch unused, no errors; `OPENROUTER_API_KEY` presence verified without reading or recording its value. Selected access is OpenRouter with `typesafe/jev-1.13-20260917`, conservative risk. This model is not integrated or invoked. The original OpenAI `gpt-5.5` calls, prompts, parsing, diagnostics, and streaming remain intact. The authorized same-model baseline gateway route is unused.

Validation executed:

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 "/Users/bigsoup/Downloads/Jev Converter/eval/smoke.py" "/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/openai_demo-codex-interactive/original" openai_demo
```

Exit 0: `PASS: observable Python behavior and original-path fallback smoke`.
The upstream example has no project test command. This supplied behavioral smoke is not live inference or parity evidence.

Live parity: not applicable; zero converted sites, zero live pairs, no provider calls made for validation, and no `JEV_PARITY.json` created. Agreement, confidence curves, fallback rates, latency, cost, calibration/confirmation inputs, and per-site thresholds are not measured and are not applicable. Threshold recommendation for each of workflow.py:10, workflow.py:23, and workflow.py:42: none, leave unchanged. No new gate exists, so no gate fault-injection claims are made. No live model quality or provider availability claim is made.

Artifact shape and source preservation checks are recorded below after execution. Only the three requested report artifacts are intended for the commit. No push or PR.

Undo after saving any subsequent work:

```sh
git switch main
git branch -D jev-convert/evaluation
```

Final checks: `/opt/homebrew/opt/python@3.14/bin/python3.14 .agents/skills/jevify/scripts/check_artifacts.py .` exited 0 with `shape_valid: true` and no errors. This verifies shape only. `git diff --exit-code 0c64fdf0c13a8b8609cc52d0f83e4f9d91eeca39 -- workflow.py` exited 0, confirming unchanged source. Pre-commit status contained only the three requested artifacts.
