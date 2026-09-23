# DEV findings (retained before repairs)

Iteration 1 uses skill commit 489a5b3; no grader thresholds or corpus code changed.

- Codex's enum runs correctly label the site DECISION but decline conversion because the generic SDK finish diagnostic lacks a native System One field. Review the semantics of adapter-owned completion metadata instead of assuming provider field names must match. Real usage must remain real; do not invent a provider finish reason.
- Claude's enum interactive run claims no OpenRouter key without checking the configured environment variable, and skips parity. The runner supplied the key. Require a value-free presence check and actual attempted validation before claiming unavailable credentials.
- Claude's enum headless run combines branch mode with an inactive clone_path. Treat output.mode as the sole selector; ancillary fields do not authorize a second mode.
- Codex's classification headless run measures 44 real pairs and passes selective agreement (29/30 at 0.90), but puts source paths in the provenance enum. Keep provenance category and source path in separate fields and validate evidence shape before handback.
- Claude's enum interactive audit uses null instead of the required primitive string for leave; it also omits .env.example. Validate the complete deliverable checklist.

These observations are provisional until independent reviews and grading finish. They motivate general skill corrections, not fixture-specific exceptions or edits to evaluation outputs.
