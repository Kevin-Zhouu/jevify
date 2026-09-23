# Evaluation changes

2026-09-23 — Initial grader and independent smoke/runner construction, before
skill implementation. Thresholds: >=90% audit agreement; zero generation-to-Jev-only
recommendations; >=30 unique live parity inputs per converted site; >=90%
agreement above chosen threshold; required below-threshold, error, timeout and
rate-limit fallback checks. Human review is mandatory for evidence that a regex
cannot establish (downstream contracts, question centralization, genuine live
results, provider authorization, and transcript gating).

No post-freeze changes yet. Freeze is not complete until sealed held-out labels
are prepared and grader self-tests pass.
