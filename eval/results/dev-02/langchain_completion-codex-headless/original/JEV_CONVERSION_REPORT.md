# Jev conversion report

No good Jev opportunities here.

Source revision: `81b7cce7b483eebc6ab39e6317c3759192561e6d` on `main`. Output mode: report. Output directory: `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/langchain_completion-codex-headless/original`.

The only inference site, `workflow.ts:15`, is GENERATION and NOT A FIT: unrestricted completion text flows directly into a streaming HTTP response. Recommended action: leave (primitive none). Upfront fallback approval for enumerated pure decisions resolves to zero sites. All source semantics and diagnostics remain intact. `JEV_AUDIT.json` records `converted_sites: []`.

Changed files: only JEV_CONVERSION_PLAN.md, JEV_AUDIT.json, JEV_CONVERSION_REPORT.md. No source/env/dependency changes, branch/clone, commit, push or PR. The configured inactive clone destination was not used.

## Validation

The upstream example has no project test command. Executed the supplied independent behavior smoke against the actual report output repository:

```sh
node '/Users/bigsoup/Downloads/Jev Converter/eval/smoke.cjs' '/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/langchain_completion-codex-headless/original' langchain_completion
```

Exit 0: `PASS: observable TypeScript behavior and original-path fallback smoke`. This is offline behavioral evidence, not live provider parity or a newly added fallback. The original workflow itself remains the answering path.

Artifact shape check command:

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 .agents/skills/jevify/scripts/check_artifacts.py '/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/langchain_completion-codex-headless/original'
```

Exit 0: `shape_valid: true`, no errors. Shape checking does not establish model correctness. Final git verification found no tracked-file differences and only the three requested report artifacts untracked.

Live validation skipped: no converted sites in report-only mode. The selected OpenRouter key was present; skipping is not attributed to missing credentials. No inference requests, parity pairs, calibration/check split, confidence curve, fallback-rate measurements, latency measurements or cost estimates were performed. Sample count: 0. No JEV_PARITY.json is supplied and no parity or savings claim is made. Configured Jev model `typesafe/jev-1.13-20260917` was not called; original OpenAI `gpt-3.5-turbo-0125` remains unchanged. No forced Jev failures were tested because there is no Jev wrapper.

Per-site threshold recommendation, `workflow.ts:15`: not applicable; a confidence threshold cannot supply generated prose. No fallback gate is recommended.

Scope limitation: the audit covers this repository's source, not installed SDK internals or an external client application. The smoke result is limited to its independent observable-behavior checks. Required live documentation was available via urllib; see the plan for links and the consumer trace.

## Undo

Remove only these three newly created report artifacts from this directory: `JEV_CONVERSION_PLAN.md`, `JEV_AUDIT.json`, `JEV_CONVERSION_REPORT.md`. No branch switch, clone deletion or code rollback is needed.
