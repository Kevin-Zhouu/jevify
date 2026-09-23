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
