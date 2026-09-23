# Jev Conversion Report

## Summary

| Field | Value |
|---|---|
| Source revision | `ae150789691720a75f926ef792de4ae88c09ed89` |
| Output mode | Branch (`jev-convert/no-key`) |
| Provider | none |
| Key present | No |
| Risk posture | Conservative |
| Jev model pin | `jev-1.13.0` |

## Approvals

Predicate approval from config: `actions: [fallback]`, scope: "Only pure DECISION sites with enumerated outputs, preserve behavior and original fallback provider."

## Converted sites

### `workflow.py:83` — ticket classification (DECISION → Choice + fallback)

- **Original:** Anthropic Messages API / `claude-haiku-4-5`, returns one of 10 insurance support category labels
- **Converted:** Jev Choice with 10 criteria options, confidence threshold 0.7, conservative fallback to original Anthropic call
- **Decisions module:** `jev_decisions.py` — `classify_ticket(ticket_text, original_fn)`
- **Public wrapper:** `workflow.simple_classify(X)` — unchanged signature and return type

## Unchanged sites

None — single-site repository.

## Test commands and results

### Smoke test

```
/opt/homebrew/opt/python@3.14/bin/python3.14 "/Users/bigsoup/Downloads/Jev Converter/eval/smoke.py" "/Users/bigsoup/Downloads/Jev Converter/eval/runs/supplemental-03/no-key-claude/original" anthropic_classification
```

**Result:** PASS — observable Python behavior and original-path fallback smoke.

### Live validation

**Live validation skipped** — no TypeSafe API key provided (`provider: none`). The Jev path will always fall back to the original Anthropic call until `TYPESAFE_API_KEY` is configured.

No parity claim is made. Fallback is retained. `JEV_PARITY.json` contains zero measurement rows and no executed fault assertions.

## Threshold recommendation

- **Site `workflow.py:83`:** Provisional threshold 0.7. Should be calibrated on representative data with a live key before production use.

## Faults

No fault assertions were executed (no key available for live Jev responses to capture/replay). Fault branches exist in `jev_decisions.py` covering:
- Low confidence → fallback
- Missing key → fallback
- Unknown label → fallback
- Model mismatch → fallback
- Invalid confidence → fallback
- Invalid usage → fallback
- Timeout → fallback
- Generic error → fallback

## Limitations

1. **No live validation** — `provider: none`, no `TYPESAFE_API_KEY` in environment. Parity, latency, cost, and fault assertions cannot be measured.
2. **No baseline key verification** — without a TypeSafe key, the Jev path is untested end-to-end. The fallback path exercises the original Anthropic code unchanged.
3. **Threshold is provisional** — 0.7 chosen conservatively; should be calibrated with live data.

## Cost assumptions

- No Jev cost data (no key).
- Original path cost: Anthropic claude-haiku-4-5 pricing applies unchanged.

## Undo instructions

To revert to the original state:

```bash
git switch main
git branch -D jev-convert/no-key
```

## Files changed

| File | Change |
|---|---|
| `jev_decisions.py` | New — decisions module with Jev model pin, question, criteria, threshold, gate |
| `workflow.py` | Modified — `simple_classify` wraps original via `classify_ticket`; original preserved as `_original_classify` |
| `.env.example` | New — placeholder for `TYPESAFE_API_KEY` and `ANTHROPIC_API_KEY` |
| `JEV_CONVERSION_PLAN.md` | New — audit, options, selections |
| `JEV_AUDIT.json` | New — machine-readable audit |
| `JEV_PARITY.json` | New — empty parity evidence (no key) |
| `JEV_CONVERSION_REPORT.md` | New — this report |
