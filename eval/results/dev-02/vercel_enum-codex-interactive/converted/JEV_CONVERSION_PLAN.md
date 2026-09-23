# Approved conversion plan

Source: 6013ff5396ee175c76aa5feddd7e93d903e667a7 (main).
Output: clone at `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/vercel_enum-codex-interactive/converted`, branch `jev-convert/evaluation`. Original stays untouched.
Preflight: clean source, unused destination, OpenRouter key present (value never read into artifacts).
Approval: fallback only for pure DECISION sites with enumerated outputs; preserve observable fields. All other actions declined. Conservative fallback stays permanently.

| Site | Class / fit | Downstream | Options | Selected |
|---|---|---|---|---|
| workflow.ts:6 | DECISION / benign fixed fixture | genre, blank line, token usage, finish reason; errors to console.error | A: fallback / Choice; accepted requests may avoid original latency and cost, misses add both; confident errors remain. B: leave / none; no savings or new risk. | A |

One call, no shared wrappers or additional sites. See JEV_AUDIT.json for full options.
Use OpenRouter typesafe/jev-1.13-20260917 with bounded timeout and provisional confidence 0.9. Preserve exact original SDK options, prompt, enum, provider and parsing in production fallback. A decisions module owns question, criteria, pin, bounds, metadata adapter and gate. Generic stop means adapter-completed decision, not native Jev termination metadata. Real usage maps input/output tokens to prompt/completion and their sum.

Validate independent supplied smoke, full stdout contract, exactly-once fallback and original exception identity under faults. Attempt 30+ unique paired inputs, using the actual evaluator and same original gpt-4o-mini model through an isolated authorized OpenRouter transport. Synthetic cases extend the sole repository fixture. Threshold remains provisional if access fails; never invent metrics. Record IDs, real costs, latencies, confidence curve and held-out confirmation. Commit locally; no push or PR.
