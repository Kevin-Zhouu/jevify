# Jev Conversion Report

## Summary

| Field | Value |
|---|---|
| Source revision | `306e7348cce7a7d004783c48849b7e6adb221c6e` (`main`) |
| Output mode | `branch` (target: `jev-convert/no-key`) |
| Provider | `none` |
| Risk posture | Conservative |
| Approval | **Not supplied** — headless run stopped after Phase 2 |

## Audit result

One site found: `workflow.py:83` — a pure DECISION (10-category insurance ticket classification via Anthropic Claude Haiku). Classified as **FIT** for Jev Choice with confidence-gated fallback.

## Converted sites

None. No approval was supplied in the headless config.

## Unchanged sites

| Site | Reason |
|---|---|
| `workflow.py:83` | No approval supplied; conversion not authorized |

## Smoke test

```
PASS: observable Python behavior and original-path fallback smoke
```

Command: `/opt/homebrew/opt/python@3.14/bin/python3.14 "/Users/bigsoup/Downloads/Jev Converter/eval/smoke.py" "/Users/bigsoup/Downloads/Jev Converter/eval/runs/supplemental-03/missing-approval-claude/original" anthropic_classification`

## Live validation

**Live validation skipped.** No provider key configured (`provider: none`). No parity claim is made.

## Code / dependency / env changes

None. No branch was created. No code was modified. No dependencies were added. No `.env` file was created.

## Limitations

- Headless mode with no `approval` section: audit and plan were produced but no conversion was performed.
- No TypeSafe API key available: even if approved, live validation would be skipped and fallback would be retained.
- No Anthropic API key available: original-path live baseline cannot be exercised.
- Parity is unknown; threshold recommendations require live measurement.

## Threshold recommendations

Cannot recommend thresholds without live paired measurement. A starting point of 0.7 confidence for conservative fallback is suggested for calibration once keys are available, but must be validated on representative data before deployment.

## Undo instructions

No changes were made to the repository beyond this report and the plan/audit artifacts. To clean up:

```bash
rm JEV_CONVERSION_PLAN.md JEV_AUDIT.json JEV_CONVERSION_REPORT.md
```
