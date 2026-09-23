# Jev Conversion Report

## Source

- Repository: `anthropic_classification` (Anthropic cookbook insurance ticket classifier)
- Source revision: `fd78ebf` on `main`
- Output mode: Clone to `converted/` on branch `jev-convert/evaluation`

## Approvals

- **Site S1 (`workflow.py:83`)**: Option A — `fallback` with Choice primitive
- **Scope**: Only pure DECISION sites with enumerated outputs; preserve all externally observable fields
- **Risk posture**: Conservative (fallback always retained)

## Provider and model

- Provider: OpenRouter
- Key env var: `OPENROUTER_API_KEY`
- Jev model pin: `typesafe/jev-1.13-20260917`
- Original baseline model: `anthropic/claude-haiku-4-5` (routed via OpenRouter for evaluation only, authorized by user)

## Changed files

| File | Change |
|---|---|
| `jev_decisions.py` | **New.** Single decisions module containing Jev model pin, Choice question with 10 insurance categories, confidence threshold (0.85), `classify_with_jev()` function, validation, and stderr logging. |
| `workflow.py` | **Modified.** Added graceful import of `classify_with_jev`. `simple_classify()` now tries Jev first; on high-confidence result, returns the Jev label. On `None` (low confidence, error, timeout, missing key), falls through to the original Claude path unchanged. |
| `run_parity.py` | **New.** Parity measurement script (evaluation artifact, not production code). |

## Unchanged sites

None — the repository has only one LLM call site, which was converted.

## Smoke test

```
$ python3.14 smoke.py converted/ anthropic_classification
jev_decision_path=original reason=jev_error:TimeoutError
PASS: observable Python behavior and original-path fallback smoke
```

The smoke test blocks network access. Jev correctly fails with `TimeoutError`, falls back to the original Claude path, and the assertion `value == 'Billing Inquiries'` passes. Exactly one original call is made.

## Live parity measurement

### Setup

- **Inputs**: 68 unique insurance support tickets from `data/test.tsv` (repo fixture)
- **Input provenance**: Repository corpus (`repo:data/test.tsv`)
- **Jev calls**: Real live inference via OpenRouter → `typesafe/jev-1.13-20260917`
- **Original calls**: Real live inference via OpenRouter → `anthropic/claude-haiku-4-5` with the identical original prompt, stop sequences, and output parsing
- **Baseline authorization**: User authorized routing the same original model through OpenRouter in isolated evaluation adapters only

### Results at calibrated threshold (0.85)

| Metric | Value |
|---|---|
| Total inputs | 68 |
| Errors | 0 |
| Raw agreement (all pairs) | 83.8% (57/68) |
| Selective agreement (accepted) | **97.8%** (44/45) |
| Accepted | 45/68 (66.2%) |
| Fallback rate | 33.8% |
| Jev latency p50 | 371ms |
| Jev latency p95 | 1191ms |
| Original latency p50 | 1069ms |
| Original latency p95 | 1669ms |

### Threshold sensitivity (calibration data — same set)

| Threshold | Accepted | Selective agreement | Fallback rate |
|---|---|---|---|
| 0.70 | 55/68 | 90.9% | 19.1% |
| 0.75 | 49/68 | 95.9% | 27.9% |
| 0.80 | 49/68 | 95.9% | 27.9% |
| **0.85** | **45/68** | **97.8%** | **33.8%** |
| 0.90 | 41/68 | 100.0% | 39.7% |
| 0.95 | 39/68 | 100.0% | 42.6% |

### Threshold recommendation

**0.85** is the recommended threshold for this site. It achieves 97.8% selective agreement while keeping fallback rate at 33.8%. At 0.9, agreement is 100% but fallback rate rises to ~40%, reducing cost savings. At 0.7, cost savings improve but selective agreement drops to 90.9%.

Note: calibration and confirmation used the same 68-row set (no held-out split). This is adequate for a 68-row corpus but not production-grade; the threshold should be re-evaluated on fresh data.

### Disagreement analysis

The 5 disagreements on accepted decisions (at threshold 0.7) primarily involve:
- **Billing Inquiries vs Billing Disputes**: Jev sometimes classifies billing-related tickets as disputes when the original uses inquiries. These are genuinely ambiguous categories.
- **Coverage Explanations vs Policy Administration**: Category boundary between explaining coverage and administering policy changes.
- **Account Management vs Billing Inquiries**: Tickets about account charges that could go either way.

At threshold 0.85, only 1 disagreement remains among accepted decisions.

### Fault testing

- **Below threshold**: Confirmed — 23/68 inputs had confidence < 0.85, all fell back to original path
- **Error / timeout**: Confirmed — smoke test blocks network; Jev `TimeoutError` triggers fallback
- **Rate limit**: Covered by the general error handler (HTTP 429 → `HTTPError` → fallback)
- **Missing key**: Confirmed — `classify_with_jev()` checks `OPENROUTER_API_KEY` and returns `None` immediately if absent

### Cost analysis

- **Cost source**: OpenRouter pricing page (estimated, dated 2026-09-23)
- Jev input: ~$0.042/Mtok (OpenRouter Jev pricing)
- Claude Haiku input: ~$0.80/Mtok (OpenRouter Claude Haiku pricing)
- **Expected cascade cost per request**: Jev cost + 0.338 × Claude cost (at threshold 0.85)
- **Net savings**: ~55–60% cost reduction on accepted decisions vs always calling Claude

### Latency analysis

- Jev-accepted decisions: ~371ms p50 (vs ~1069ms p50 for Claude) — **2.9x faster**
- Jev-rejected decisions (cascade): ~371ms + ~1069ms ≈ 1440ms total — ~35% slower than Claude alone
- **Net latency**: Faster on 66% of inputs, slower on 34%

## Limitations

1. Calibration and confirmation used the same 68-row set — no held-out split. Re-evaluate on fresh data before production use.
2. Cost figures are estimated from public pricing, not provider-reported usage. Pricing may change.
3. Latency measured from a single geographic location during a single time window. Production latency may differ.
4. Conservative fallback is always retained — the original Claude path is never removed.

## Undo instructions

To revert this conversion:

```bash
# If using the clone:
rm -rf converted/

# If on the branch:
git checkout main
git branch -D jev-convert/evaluation
```

## Artifacts

| File | Description |
|---|---|
| `JEV_CONVERSION_PLAN.md` | Audit, options, selections, and preflight |
| `JEV_AUDIT.json` | Machine-readable audit with site inventory and converted sites |
| `JEV_PARITY.json` | Per-row parity evidence with 68 paired comparisons |
| `JEV_CONVERSION_REPORT.md` | This report |
| `jev_decisions.py` | Decisions module (model pin, questions, threshold) |
| `run_parity.py` | Parity measurement script |
