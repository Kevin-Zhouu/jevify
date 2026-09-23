# Jev conversion plan

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

Execution scope: establish the requested branch, save these three audit artifacts, execute the supplied independent behavior smoke, verify artifact shape and unchanged source, and commit only the artifacts. No live comparisons are required with zero converted sites.
