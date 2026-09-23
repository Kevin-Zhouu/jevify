# Jev conversion report

No good Jev opportunities here. The approved pure-DECISION predicate matches no sites. Zero sites converted; all upstream source, diagnostics, dependencies and environment files remain unchanged.

Source revision: `6fa3fbbdfca247d087ec4a7454ae2990bb401330` on `main`.
Output mode: branch, `jev-convert/evaluation`, in `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/anthropic_routing-codex-interactive/original` (clone_path inactive).
Approval: fallback only for pure DECISION sites with enumerated outputs; preserve all externally observable fields, leave MIXED and GENERATION unchanged. The full audit/options and approval resolution are in JEV_CONVERSION_PLAN.md and JEV_AUDIT.json.

Unchanged sites and threshold recommendations:
- workflow.py:24 — MIXED: generated reasoning is printed alongside the routing selection. Threshold: not applicable.
- workflow.py:34 — GENERATION: specialist prose is returned. Threshold: not applicable.
- util.py:23 — MIXED shared transport for both calls. Threshold: not applicable.

Original provider/model remains Anthropic / claude-sonnet-4-6. Configured Jev access is OpenRouter / typesafe/jev-1.13-20260917, unused. Preflight passed with the OpenRouter credential present (presence only). No production fallback-provider change or isolated baseline adapter was made.

## Executed validation

Independent behavior smoke command:

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 '/Users/bigsoup/Downloads/Jev Converter/eval/smoke.py' '/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/anthropic_routing-codex-interactive/original' anthropic_routing
```

Result: exit 0, `PASS: observable Python behavior and original-path fallback smoke`.
The anthropic_routing fixture specifically asserts the specialist prose return and preservation of observed routing reasoning using deterministic original-path doubles. It disables network; it is not live parity and does not demonstrate Jev fallback behavior. The external smoke file was read and executed, never edited. There is no upstream project test command.

Live validation: not applicable and not run because no sites were converted (not skipped due to missing credentials). Live sample count: 0. Agreement, confidence curve, fallback rate, latency, cost and fault assertions: not measured/not applicable. No JEV_PARITY.json is produced. No savings or model parity is claimed.

Artifact validation: `/opt/homebrew/opt/python@3.14/bin/python3.14 .agents/skills/jevify/scripts/check_artifacts.py .` exited 0 with `shape_valid: true` and no errors. The artifact checker verifies structure only.

Source verification: `git diff --exit-code 6fa3fbbdfca247d087ec4a7454ae2990bb401330 -- .` exited 0 before adding the three new report artifacts; all existing tracked files were unchanged.

## Undo

From the output repository, switch to the unchanged original branch and delete the local report branch:

```sh
git switch main
git branch -D jev-convert/evaluation
```

Only report artifacts are committed. No push or PR is performed.
