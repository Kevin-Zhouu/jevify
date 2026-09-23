# Jev Conversion Plan

## Preflight

- **Repository:** `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/anthropic_classification-claude-headless/original`
- **Original branch:** `main`
- **Original SHA:** `eff84f8f58d676d6b3b2eb21ae7b906300e2ef1b`
- **Output mode:** branch (`jev-convert/evaluation`)
- **Provider:** OpenRouter (`OPENROUTER_API_KEY`)
- **Model pin:** `typesafe/jev-1.13-20260917`
- **Risk posture:** conservative (fallback always retained)
- **Key present:** yes

## Audit

| Site ID | Provider | Downstream | Classification | Fit | Reason |
|---|---|---|---|---|---|
| `workflow.py:83` | Anthropic SDK / `claude-haiku-4-5` | `simple_classify()` returns one of 10 enumerated insurance category labels | DECISION | FIT | Closed-set classification over trusted text; maps directly to Choice primitive |

### Wrapper relationships

Single call site; no shared wrappers. The `simple_classify` function is the only consumer of `client.messages.create`.

## Options

| Site | Option | Action | Primitive | Benefit | Risk |
|---|---|---|---|---|---|
| `workflow.py:83` | A | fallback | Choice | Jev Choice is purpose-built for closed-set classification; accepted decisions are faster and cheaper than Claude Haiku. Expected cost = Jev cost + fallback_fraction x Anthropic cost. | Serial miss adds Jev latency before original. Conservative fallback always retained. |
| `workflow.py:83` | B | leave | none | No change, no risk. | No cost/latency improvement. |

## Selections

- `workflow.py:83`: **Option A (fallback)** — approved by headless config predicate: `actions: [fallback]`, `scope: "Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged."` Site is a pure DECISION with 10 enumerated outputs.

## Implementation Plan

1. Create `jev_decisions.py` — single decisions module owning all Jev model ID, questions, criteria, option mappings, threshold, and gate logic.
2. Modify `workflow.py` — add Jev-first path in `simple_classify()` with confidence-gated fallback to original Anthropic path. Preserve function signature, return type, sync behavior, and all observable diagnostics. Log decision path to stderr.
3. Add `.env.example` with `OPENROUTER_API_KEY` placeholder.
4. Run smoke test to verify original-path behavior preserved.
5. Run live paired validation with 30+ unique inputs from `data/test.tsv`.
6. Write `JEV_PARITY.json`, `JEV_CONVERSION_REPORT.md`, `JEV_AUDIT.json`.
