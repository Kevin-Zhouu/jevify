# Jevify in use — real recorded session

[Animated preview](../jevify-session.gif) · [Full terminal recording](full.cast) · [Conversion report](output/JEV_CONVERSION_REPORT.md) · [Full diff](conversion.patch) · [Decisions module](output/jev_decisions.py)

Recorded 2026-09-23 in Codex, using its configured model and the unchanged Jevify skill. The recorder supplies three user replies; these are scripted interaction, not a human typing live. Codex actually audits and edits a fresh copy of the pinned Anthropic classification corpus. This is a no-key usage demonstration, not a live Jev benchmark. Live validation is skipped; Jev is disabled by default pending provider setup and validation. The original fallback remains.

The GIF is 18.47 seconds / 568,285 bytes. All captured terminal output bytes are preserved: only timing is changed to shorten waits. `full.cast` retains original timing; `preview.cast` has the GIF timing. The plan is the actual agent output, including its limitations. Use the full recording to read at your own pace.

## Three-panel overview

The top-of-page [overview](../jevify-story.svg) is an editorial diagram, not a screenshot of either coding agent. It summarizes this single real conversion. Its code fragments are literal excerpts, with omissions marked, and its plan summary comes from JEV_CONVERSION_PLAN.md. `tools/render_jevify_story.py` checks those fragments against the committed output and generates the SVG. The original GIF remains available below the overview as a full-output recording. No multi-call conversion counts are invented.

## Evidence

- `turn-*.jsonl`: complete Codex events; `prompts.json`: supplied user replies.
- Empty `turn-1.git-status.txt` and `turn-2.git-status.txt`: clean repository before setup and plan approval.
- `output/`: exact generated code, audit, report, and offline tests. No successful Jev responses were fabricated.
- `commits.txt` and `conversion.bundle`: actual conversion commits and the original main branch. Original main stayed at `7c497d21099fc916692f1dd45b5a6107b03754d5`; conversion ends at `f8e192e`. No push was performed inside the recorded session.
- The first interrupted attempt is retained in [../jevify-session-attempt-1](../jevify-session-attempt-1/), with the reason in [ISSUES_FOUND.md](../../../ISSUES_FOUND.md). It omitted the target, so Codex asked for clarification; the recording script was corrected without changing the skill.

## Reproduce

Requires Python, Codex authentication, asciinema 2.4, and agg 1.9. Set up a fresh git repository from `corpus/anthropic_classification`, install the unchanged `skills/jevify` at `.agents/skills/jevify`, and commit the baseline. Then from the Jevify repository:

```sh
asciinema rec --cols 100 --rows 28 -c 'python3 tools/record_jevify_session.py /path/to/fresh/repo docs/demos/jevify-session' docs/demos/jevify-session/full.cast
python3 tools/render_jevify_session.py
```

Use a new output directory or archive the previous capture before recording again. The recorder removes API key/token environment variables from the child process and explicitly selects neither provider. It does not change the model or synthesize assistant text. Review the plan before reusing a scripted approval in a different repository.

Replay the original session with `asciinema play full.cast`. Restore the exact output with `git clone conversion.bundle restored-demo` then `git -C restored-demo switch jev-convert/demo`.
