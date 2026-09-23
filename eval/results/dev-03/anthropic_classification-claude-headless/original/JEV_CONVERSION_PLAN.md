# Jev Conversion Plan

## Preflight

- **Repository:** `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/anthropic_classification-claude-headless/original`
- **Original SHA:** `1c953f75ebe1580de909072ce9a73b8ab8f11d05`
- **Original branch:** `main`
- **Output mode:** branch (`jev-convert/evaluation`)
- **Provider:** OpenRouter (`OPENROUTER_API_KEY`)
- **Model pin:** `typesafe/jev-1.13-20260917`
- **Risk posture:** conservative (fallback retained)
- **Key present:** yes

## Audit

### Site 1: `workflow.py:83`

| Field | Value |
|---|---|
| Provider | Anthropic SDK / `claude-haiku-4-5` |
| Function | `simple_classify(X)` |
| Input origin | Ticket text argument; benign insurance fixtures in `data/` |
| Downstream | Returns stripped category label string |
| Classification | DECISION |
| Fit | FIT |
| Reason | Closed-set classification over 10 enumerated insurance categories. Short text input. No math, dates, multi-hop reasoning, generation, or adversarial input. Textbook Choice primitive. |
| Context size | Small (well under 32k) |
| Untrusted input | N/A — curated data files |

No other LLM call sites found. No wrappers.

## Options

### `workflow.py:83` — Option 1: `fallback` (SELECTED)

- **Primitive:** Choice (10 options)
- **Action:** Add Jev Choice call before Anthropic; gate on confidence threshold; fall back to original on low confidence, error, timeout, rate-limit, or missing key.
- **Benefit:** Likely cheaper per accepted decision ($0.042/Mtok input-only vs Haiku pricing); faster for high-confidence decisions.
- **Risk:** Serial miss adds Jev latency + cost before original inference. Expected cost = Jev cost + fallback_fraction x original cost.

### `workflow.py:83` — Option 2: `jev_only`

- **Primitive:** Choice
- **Excluded** by conservative risk posture.

### `workflow.py:83` — Option 3: `leave`

- **Primitive:** none
- **No change, no cost improvement.**

## Approval

Headless config approval: `actions: [fallback]`, scope: "Only pure DECISION sites with enumerated outputs." Site `workflow.py:83` matches. **Option 1 selected.**

## Plan

1. Create `jev_decisions.py` — single decisions module with Jev model pin, Choice question, criteria, confidence threshold, and gate logic.
2. Modify `workflow.py` — import decisions module; wrap `simple_classify` to try Jev first, fall back to original on low confidence/error/missing key.
3. Add `.env.example` with `OPENROUTER_API_KEY` placeholder.
4. Run smoke test for behavioral parity.
5. Run live paired validation (30+ inputs) measuring agreement, latency, cost.
6. Write `JEV_AUDIT.json`, `JEV_PARITY.json`, `JEV_CONVERSION_REPORT.md`.
