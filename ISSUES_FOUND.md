# Issues found

## Demo recording: target clarification (2026-09-23)

The first scripted recording said “this workflow” without naming a target. Codex correctly asked which file to audit. The fixed three-turn recorder then sent approval too early; capture was interrupted before conversion. The full interrupted transcript is retained in docs/demos/jevify-session-attempt-1. The recorder now names workflow.py explicitly; no skill behavior changed. This is a recording-script mistake, not a successful conversion.

## Audit-first UX probes (2026-09-23)

Both initial bare invocations audited the classifier without a setup questionnaire and made no filesystem changes. Codex presented its detailed table after opening the approval question; the instruction was clarified to emit the table before using a question tool. The first raw run remains in eval/ux-audit-first/round-1. Claude’s final audit invented a consumer “test harness comparisons in data/test.tsv” (the TSV is data, not executable consumer code) and overstated cheaper/faster as a fact. These are known audit-quality defects; this narrow UX check is not a conversion, parity, or cross-harness quality pass. No corpus, grader, thresholds, or historic results were edited.
