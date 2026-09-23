# Evaluation changes

2026-09-23 — Initial grader and independent smoke/runner construction, before
skill implementation. Thresholds: >=90% audit agreement; zero generation-to-Jev-only
recommendations; >=30 unique live parity inputs per converted site; >=90%
agreement above chosen threshold; required below-threshold, error, timeout and
rate-limit fallback checks. Human review is mandatory for evidence that a regex
cannot establish (downstream contracts, question centralization, genuine live
results, provider authorization, and transcript gating).

2026-09-23 — Pre-freeze evidence review: count dependency/config edits as changes,
require the complete workflow × harness × scenario matrix, compare cross-harness
classifications, reject invalid or missing parity metrics, and enforce one
HELD-OUT attempt per scenario per round with at most two documented repair rounds.
Nine evidence-check tests pass. No thresholds changed.

No post-freeze changes yet. Freeze is not complete until sealed held-out labels
are prepared and grader self-tests pass.

## 2026-09-23 — supplemental checks after freeze

No frozen grader, runner, label, config fixture, corpus byte or threshold changed.
Added skill-helper unit tests, a read-only review packet utility, secret scanning,
and ordinary-file evidence export. Independent reviews retain the runner's original
mode result when tightening it: a report-mode run that writes into an inactive
clone path is a mode failure even though the automatic original-tree check passes.
This supplements (rather than weakens) the required transcript/filesystem review.
Additional missing-answer/no-key prompt probes exercise product edge cases outside
the frozen primary matrix; they do not replace or inflate its scores.

- Added supplemental automatic-discovery probes (migration request vs general Jev API question). These record real harness transcripts and filesystem changes separately; they do not modify the frozen primary grader, labels, corpus, thresholds or matrix.

- DEV03 reporting adds a separate harness-completion status because the frozen grader does not require a successful CLI exit. One quota-interrupted run passes artifact checks; it is reported BLOCKED, not a completed pass. Frozen checks/thresholds remain unchanged.

## 2026-09-23 — short invocation UX

Added portable task/target interpretation to the skill entrypoint and documented `/jevify convert …` for Claude Code and `$jevify convert …` for Codex. Existing setup and plan-approval gates remain. No frozen grader, labels, corpus, or thresholds changed. This documentation/instruction adjustment was format-validated; it is not a new full evaluation round and the published DEV results remain historical.

## 2026-09-23 — user-directed audit-first UX revision

The user explicitly replaced the original setup-before-audit contract with a bare `/jevify` / `$jevify` read-only audit and one combined scope/output approval. Skill instructions and configuration now adopt that flow, conservative by default, keys deferred until validation. JEVIFY_REPORT.md is the handback name; the old report name remains a compatibility copy. No frozen grader, corpus, labels, thresholds or historical results changed. The old setup-gating checks describe the previous contract and must not be represented as proof of this revision. A new full cross-harness evaluation remains outstanding. The new promotional shell animation is explicitly illustrative; sample counts and test lines are not benchmark evidence.
