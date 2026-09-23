# Jev Conversion Report — `anthropic_routing`

## Source

- Repository: `anthropic_routing-claude-interactive/original`
- Commit: `10e56a3` (Baseline pinned upstream workflow and installed skill)
- Date: 2026-09-23

## Output

- Mode: branch (`jev-convert/evaluation`) in clone at `converted/`
- No code, dependency, or environment changes made

## Approvals

| Approval | Value |
|---|---|
| Actions | `fallback` |
| Scope | Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged. Preserve all externally observable fields. |

## Sites — unchanged

| ID | File:Line | Classification | Reason unchanged |
|---|---|---|---|
| S1 | `workflow.py:24` | MIXED | Approval excludes MIXED. Routing call produces both a route decision and printed reasoning text. |
| S2 | `workflow.py:34` | GENERATION | Approval excludes GENERATION. Free-form prose output. |
| W1 | `util.py:9` | MIXED | Shared transport wrapper; not independently convertible. |

## Converted sites

None. Zero sites match the approved scope (pure DECISION with enumerated outputs).

## Provider / model

- Jev provider: OpenRouter
- Jev model pin: `typesafe/jev-1.13-20260917`
- Not used (no conversions)

## Validation

**No conversions — no parity measurements performed.**

No live validation was conducted because no sites were converted. No parity claim is made.

## Smoke test

Source semantics preserved: no files were modified. The original workflow runs unchanged on the `jev-convert/evaluation` branch.

## Limitations

- S1 contains a strong Choice opportunity for the routing decision component, but the site is MIXED due to printed reasoning text. A `decompose` option was available but excluded by the approval scope.
- S2 is pure generation with no Jev opportunity.

## Undo

To revert: switch to `main` branch and delete the `jev-convert/evaluation` branch, or delete the `converted/` clone directory.

```bash
# Option 1: delete branch
cd converted && git checkout main && git branch -D jev-convert/evaluation

# Option 2: delete clone
rm -rf converted/
```
