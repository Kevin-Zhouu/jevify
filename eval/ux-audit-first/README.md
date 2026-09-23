# Audit-first invocation probes — 2026-09-23

These are narrow real-CLI UX probes on separate clean copies of the pinned Anthropic classification example with the current skill installed. No API keys/tokens were passed. They are not live Jev conversion tests and do not replace the frozen suite.

| Probe | Observed result |
|---|---|
| Codex, bare `$jevify`, first revision | Audited without setup questions; no filesystem changes. The approval tool was shown before the detailed table. |
| Claude Code, bare `/jevify` | Audited without setup questions; table before combined options; no filesystem changes. Audit-quality defects below remain. |
| Codex, after table-order clarification | Table appeared before the combined approval prompt; no filesystem changes. |

All CLI processes exited 0. Original raw evidence and statuses are preserved under round-1/; the second Codex probe is in this directory. No approvals were sent and no conversions were made. Claude output is a final JSON result, so intermediate tool order is not independently visible from that file.

Known issues: Claude invented a downstream test harness from a data TSV and overstated cost/latency savings as facts. These are explicitly NOT quality passes. See ../../ISSUES_FOUND.md. No updates to frozen grader, labels, corpus, metrics, thresholds or historic results were made. The new skill flow needs full conversion and parity re-evaluation before equivalent reliability can be claimed.

Reproduction: install skills/jevify unchanged into the appropriate project skill directory in a committed fresh copy of corpus/anthropic_classification, then run `python tools/check_audit_first_invocation.py codex|claude REPO OUTPUT`. The tool strips API credential environment variables, invokes the real bare command and retains stdout, stderr, exit status and final git status. No model override or simulated assistant responses.
