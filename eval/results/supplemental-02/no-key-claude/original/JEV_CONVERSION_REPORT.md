# Jev Conversion Report

## Summary

| Field | Value |
|---|---|
| Source revision | `dcf0d680099815876708b8b6550bc2e5e8d10d9c` (`main`) |
| Output mode | `branch` |
| Branch | `jev-convert/no-key` |
| Provider | `none` (no key supplied) |
| Risk posture | `conservative` |
| Model pin | `jev-1.13.0` |

## Approvals

Config predicate: *"Only pure DECISION sites with enumerated outputs, preserve behavior and original fallback provider"*, actions: `["fallback"]`.

## Sites

### Changed: `workflow.py:83` → fallback via Jev Choice

- **Original**: `client.messages.create()` using Anthropic SDK / `claude-haiku-4-5`, returns one of 10 insurance support category labels.
- **Converted**: New `classify(X)` calls `classify_with_jev(X, simple_classify)` from `jev_decisions.py`. Jev Choice over the same 10 categories; confidence gate at 0.7. Falls back to unchanged `simple_classify` on: missing key, low confidence, unknown label, invalid response, timeout, HTTP errors, rate limits.
- **Primitive**: Choice with 10 options.
- **Decisions module**: `jev_decisions.py` — owns model pin, criteria, threshold, question, validation, and gate logic.
- **Signature preserved**: `classify(X) → str` (same as `simple_classify`). Synchronous. No new async. No new SDK import at module load that would break when the package is missing (uses `urllib.request`).
- **Logging**: Every path logs via `logging.getLogger(__name__)` to stderr: `path=jev|original`, `reason`, `model`, `confidence` (when available). Never logs keys, headers, or raw input.

### Unchanged

No other LLM call sites exist in this repository.

## Test commands and results

### Smoke test

```
/opt/homebrew/opt/python@3.14/bin/python3.14 "/Users/bigsoup/Downloads/Jev Converter/eval/smoke.py" \
  "/Users/bigsoup/Downloads/Jev Converter/eval/runs/supplemental-02/no-key-claude/original" \
  anthropic_classification
```

**Result**: `PASS: observable Python behavior and original-path fallback smoke`

### Live paired measurement

**Live validation skipped.** No `TYPESAFE_API_KEY` supplied (`provider: none`). No parity claim is made. Conservative fallback is retained.

No baseline key (`ANTHROPIC_API_KEY`) was supplied either; original-path parity cannot be measured without it.

## Parity

No live parity data. `JEV_PARITY.json` contains zero rows. Fault injection assertions (below_threshold, error, timeout, rate_limit) were not executed due to no key; all marked `false`. This is incomplete validation, not a pass.

## Threshold recommendation

Suggested confidence threshold: **0.7** for this 10-class insurance ticket classification. This is a starting point; calibrate on representative labeled data with a key present. The classification-using-confidence cookbook suggests 0.9 for high-stakes; 0.7 is appropriate for a low-stakes routing decision with conservative fallback.

## Cost and latency assumptions

| Path | Estimated latency | Estimated cost |
|---|---|---|
| Jev accepted | ~100 ms | ~$0.042/M input tokens (output free) |
| Jev → fallback | ~100 ms + original | Jev cost + original cost |
| Original only (no key) | ~500+ ms | Haiku pricing |

Cost source: TypeSafe models page, accessed 2026-09-23. Pricing may change.

## Limitations

1. **No live validation**: No TypeSafe key was supplied. All parity and fault assertions are deferred.
2. **No original baseline**: No Anthropic key was supplied. Cannot measure original-path outputs for comparison.
3. **Threshold not calibrated**: 0.7 is a reasonable default but not tuned on this dataset.
4. **Fault injection not exercised**: Below-threshold, error, timeout, and rate-limit fault paths exist in code but were not tested with live assertions.
5. **Dataset scope**: Input distribution is benign fixed fixtures. Fit verdict is scoped to this distribution, not a public production service.

## Files changed

- `jev_decisions.py` — new decisions module
- `workflow.py` — added `classify()` entry point (lines 98–103)
- `.env.example` — placeholder env vars
- `JEV_CONVERSION_PLAN.md` — audit, options, and selected plan
- `JEV_AUDIT.json` — machine-readable audit
- `JEV_PARITY.json` — parity artifact (empty rows, validation skipped)
- `JEV_CONVERSION_REPORT.md` — this report

## Undo instructions

```sh
git switch main
git branch -D jev-convert/no-key
```
