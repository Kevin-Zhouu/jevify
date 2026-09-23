# Jev conversion report

No good Jev opportunities here. Zero sites converted; workflow source unchanged.

Source revision: `065ae67041864cf75b11206448d251d8f7871ce9` on original branch `main`.
Output mode: branch; output directory: `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/langchain_completion-codex-interactive/original`.
Output branch: `jev-convert/evaluation`. Inactive clone_path ignored; no clone created.
Setup and approval were supplied in the conversation; the external config was not read.
Preflight: clean repository, branch available, no errors, OPENROUTER_API_KEY present (presence only).
Selected access: OpenRouter, `typesafe/jev-1.13-20260917`; conservative risk posture.
This model was not invoked or integrated. Original provider/model remains OpenAI via LangChain, `gpt-3.5-turbo-0125`, temperature 0.

Approval: fallback only for pure DECISION sites with enumerated outputs, preserving every externally observable field. MIXED and GENERATION remain unchanged; all other conversion options declined.
Resolved selection: zero eligible sites. `workflow.ts:15` remains unchanged under the explicit generation exclusion.

Validation:
- Independent behavior smoke: `node /Users/bigsoup/Downloads/Jev\ Converter/eval/smoke.cjs "/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/langchain_completion-codex-interactive/original" langchain_completion`
- Result: exit 0, `PASS: observable TypeScript behavior and original-path fallback smoke`.
- The upstream example has no project test command. This smoke is behavioral evidence, not live model parity or proof of a new Jev fallback wrapper.
- Source equality: git diff against the source revision for workflow.ts passed (exit 0, no differences).
- Artifact check: `/opt/homebrew/opt/python@3.14/bin/python3.14 .agents/skills/jevify/scripts/check_artifacts.py .` — passed: shape_valid true, no errors. This validates artifact structure only.

Unchanged site: `workflow.ts:15`, unrestricted generation returned through the streaming adapter at line 17. No signatures, model parameters, parsing, diagnostics, exceptions or public fields were modified. No code, dependencies, environment placeholders or evaluation adapters were added.

Live validation: not applicable, zero converted sites. No provider requests were made. Input provenance, sample count, agreement curve, fallback rate, latency, costs and fault-injection measurements: not measured. Per-site threshold recommendation: none for workflow.ts:15; leave generation unchanged. No JEV_PARITY.json exists because no live parity was measured. Authorized baseline routing was unused.

Limitations: smoke coverage does not establish live provider behavior or quantify latency/cost. No Jev inference was attempted because there is no approved compatible site.

Undo after switching to this repository: `git switch main`, then `git branch -D jev-convert/evaluation`. The original main ref is unchanged. No push or PR was performed.
