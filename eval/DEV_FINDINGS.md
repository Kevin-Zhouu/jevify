# DEV findings (retained before repairs)

Iteration 1 uses skill commit 489a5b3; no grader thresholds or corpus code changed.

- Codex's enum runs correctly label the site DECISION but decline conversion because the generic SDK finish diagnostic lacks a native System One field. Review the semantics of adapter-owned completion metadata instead of assuming provider field names must match. Real usage must remain real; do not invent a provider finish reason.
- Claude's enum interactive run claims no OpenRouter key without checking the configured environment variable, and skips parity. The runner supplied the key. Require a value-free presence check and actual attempted validation before claiming unavailable credentials.
- Claude's enum headless run combines branch mode with an inactive clone_path. Treat output.mode as the sole selector; ancillary fields do not authorize a second mode.
- Codex's classification headless run measures 44 real pairs and passes selective agreement (29/30 at 0.90), but puts source paths in the provenance enum. Keep provenance category and source path in separate fields and validate evidence shape before handback.
- Claude's enum interactive audit uses null instead of the required primitive string for leave; it also omits .env.example. Validate the complete deliverable checklist.

These observations are provisional until independent reviews and grading finish. They motivate general skill corrections, not fixture-specific exceptions or edits to evaluation outputs.

## DEV02

14/24 full passes. Every Codex run passes; Claude passes routing headless and recipe headless. Remaining failures: source reads before Phase0, omitted shared wrapper, skipped requested branch, wrong artifact names or missing negative conclusion, duplicated evaluator policies, manually reconstructed baselines, invented successful inference fault payloads, 401 mislabeled 429, missing answering-model logs, malformed-response and exception propagation defects. Four Codex positive runs have valid live paired evidence; Claude positive measurements are retained but not accepted as proof. Version3 repairs only the skill.

## DEV03 stop

Codex completes 12/12 passing runs. Three completed Claude positive runs still fail source-faithful parity or fault proof; nine Claude runs are interrupted/prevented by extra-usage exhaustion. Some real numerical comparisons exceed 90% but are rejected because proxy baselines, rewritten evaluators, fabricated successful fault payloads or untested integration cannot prove the actual conversion. Setup source-read boundary improved in both harnesses. Supplemental probes expose setup wording, missing-approval extra artifacts and double fallback on original exceptions. Stop per user condition, keeping HELD-OUT sealed. Proposed helper drafts are retained separately and are not active skill code or evaluated repairs.
