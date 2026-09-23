# Jev conversion report

**No good Jev opportunities here.** Approval matched zero sites. `workflow.ts:15` remains GENERATION / NOT A FIT; `converted_sites` is empty.

Source revision: `2b868b36c1497fcdb07002f00f03c9dd076b49ad` on `main`. Output: branch `jev-convert/evaluation` at `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-01/langchain_completion-codex-interactive/original`. Only audit, plan and report artifacts were added. Original model, temperature, prompt forwarding, stream adapter, async POST signature, maxDuration=30, error propagation and diagnostics remain untouched.

The approved fallback action applies only to pure DECISION sites with enumerated outputs. The only call streams arbitrary text, so no conversion is authorized or suitable. No new router, guardrail, decomposition, provider switch or Jev dependency was introduced. Configured but unused Jev route: OpenRouter / `typesafe/jev-1.13-20260917`. The authorized same-model baseline evaluation route was not needed or exercised.

## Validation

No upstream project test command exists. Executed:

```sh
node '/Users/bigsoup/Downloads/Jev Converter/eval/smoke.cjs' '/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-01/langchain_completion-codex-interactive/original' langchain_completion
```

Exit status: **0**. Output: `PASS: observable TypeScript behavior and original-path fallback smoke`.

This smoke transpiles and executes the actual TypeScript entrypoint with an original-provider SDK double and network disabled. It checks `POST` returns `stream:hello`, maxDuration equals 30, and exactly one original-provider call occurs. It is behavioral smoke evidence, not live model parity or a comprehensive streaming/error test. The smoke file was read and executed, never edited. No generated test artifacts were observed.

Source verification: workflow.ts is byte-identical to the recorded source revision. Audit JSON parses and contains one GENERATION site and an empty converted_sites list.

Live validation skipped: zero converted sites, so no live calls were needed. Live sample count: 0. Input provenance for smoke: supplied synthetic prompt `hello`. Agreement, confidence curve, fallback rate, latency, cost, per-site threshold recommendations and Jev fault injection: not measured / not applicable. No parity claim and no JEV_PARITY.json. Credentials were not inspected. Live jaggedness documentation refresh was unavailable; the supplied prior audit and installed official skill agree on the generation limitation.

## Undo

From this repository after saving any later work:

```sh
git switch main
git branch -D jev-convert/evaluation
```

The original main ref remains at the source revision. No push or PR was performed.
