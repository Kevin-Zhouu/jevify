# Jev Conversion Report

## Source

| Item | Value |
|---|---|
| Source revision | `a7bb0145b1be5d03cc9212fc8eccf5589db83034` |
| Branch | `main` |
| Date | 2026-09-23 |

## Output

| Item | Value |
|---|---|
| Mode | Branch `jev-convert/evaluation` in cloned repo |
| Clone path | `eval/runs/dev-01/openai_demo-claude-interactive/converted` |
| Jev model | `typesafe/jev-1.13-20260917` (OpenRouter) |
| Risk posture | Conservative |

## Approval

- Approved actions: `fallback`
- Scope: Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged. Preserve all externally observable fields.

## Audit result

| Site ID | Classification | Fit | Action |
|---|---|---|---|
| `workflow.py:10` | GENERATION | NOT A FIT | leave |
| `workflow.py:23` | GENERATION | NOT A FIT | leave |
| `workflow.py:42` | GENERATION | NOT A FIT | leave |

**No good Jev opportunities here.**

All three LLM calls produce free-form generated text (prose, code explanations) printed directly to stdout. None produce a typed decision (label, boolean, route, ordered score, or closed-set selection). Jev's System One primitives (Choice, Score, Noul) do not apply.

Additional factors:
- Site 2 uses streaming, which has no Jev equivalent.
- Site 3 uses `with_raw_response` for provider envelope metadata (`request_id`), which has no Jev equivalent.

## Changed sites

None.

## Unchanged sites

All three sites (`workflow.py:10`, `workflow.py:23`, `workflow.py:42`) remain unchanged.

## Code / dependency / environment changes

None. No files were modified, no dependencies added, no environment variables introduced.

## Test commands and results

No conversion was performed, so no tests are applicable. The original workflow runs unchanged.

## Live validation

**Live validation skipped.** No sites were converted; no parity measurement is needed or claimed.

## Limitations

- This audit covers only the `workflow.py` demo script in the repository. If additional files with decision-type LLM calls are added in the future, a re-audit may find Jev opportunities.

## Undo instructions

To revert to the original state:
1. Switch to the original branch: `git checkout main`
2. Delete the conversion branch: `git branch -D jev-convert/evaluation`
3. Or simply delete the cloned directory at `eval/runs/dev-01/openai_demo-claude-interactive/converted`
