# Jev conversion plan

Source: `eff84f8f58d676d6b3b2eb21ae7b906300e2ef1b` on `main`.
Output: branch `jev-convert/evaluation` in `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/anthropic_classification-codex-headless/original`.
The inactive clone_path is ignored. Preflight: clean including untracked files,
branch unused, git available, OPENROUTER_API_KEY present (value never inspected).
No applicable AGENTS.md, dependency manifest, or project test command was found.

| Original site | Class / downstream | Fit | Options |
| --- | --- | --- | --- |
| workflow.py:83 | DECISION; simple_classify returns stripped category string | Fit for benign short English fixture tickets | fallback: Choice confidence gate, likely cheaper/faster accepted results, serial misses add cost/latency and misclassification risk; leave: no change or savings |

Config approval selects fallback for pure enumerated DECISION sites; resolved
selection: workflow.py:83. No other model calls/wrappers or consumers exist in
this repository. The wrapper and transport represent one inference, not two.
Ten label descriptions are preserved; General Inquiries covers no-match cases.
The original function body, prompt, assistant prefill, stop sequence, temperature,
max_tokens, provider/model and output parsing remain unchanged in a private callable.
No original usage/finish diagnostics are returned or printed. Additional path/model
logs use logging, never stdout or inputs. Original exceptions propagate once.

One stdlib decisions module owns the pinned OpenRouter model, Choice rubric,
0.9 provisional confidence threshold, validation and size bounds. Missing key,
invalid response, low confidence, oversize/non-string input, timeout, 429 and other
transport failures use original exactly once. No retries or new dependencies.
The fit verdict applies to the supplied benign fixtures, not hostile public tickets;
there is no proven injection mitigation and the confidence gate does not supply one.

Validation: independent supplied smoke; fault injection through actual wrapper;
live comparisons on at least 30 unique fixture/synthetic inputs using the actual
Jev evaluator. Isolated baseline adapter may route the SAME Haiku model via
OpenRouter while preserving original request/parsing. Production Anthropic fallback
must not change. Compare raw decisions, not fallback outputs. Preserve all failures;
report incomplete validation if either provider cannot serve the request.
Threshold is provisional, not tuned; any tuning requires separate calibration/check
sets. No Jev-only conversion, push, or PR is authorized.

Read live docs: https://docs.typesafe.ai/llms.txt and API, Models, Confidence,
building guide, coding-agents, Jev 1.13 jaggedness, all four Patterns,
hierarchical-classification cookbook; https://openrouter.ai/docs/guides/community/typesafe-sdk.
Web page fetches failed for several markdown pages; direct HTTPS reads succeeded.
Jev supports text and bounded choices; avoid counting, date arithmetic, generation,
complex indirection and unfiltered large state. This task needs one Choice, not a
hierarchical decomposition or composite score.

Setup: supply OPENROUTER_API_KEY and original ANTHROPIC_API_KEY through runtime
environment (names only in .env.example). The skill's scripts/with_jev_key.py
supports hidden credential entry; do not put credentials in tracked files.
Undo after committed work: git switch main; git branch -D jev-convert/evaluation.
