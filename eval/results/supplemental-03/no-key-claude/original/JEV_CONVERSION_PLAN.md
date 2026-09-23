# Jev Conversion Plan

## Preflight

| Field | Value |
|---|---|
| Repository | `/Users/bigsoup/Downloads/Jev Converter/eval/runs/supplemental-03/no-key-claude/original` |
| Original SHA | `ae150789691720a75f926ef792de4ae88c09ed89` |
| Original branch | `main` |
| Output mode | `branch` |
| Output branch | `jev-convert/no-key` |
| Provider | `none` |
| Key present | No |
| Risk posture | Conservative |
| Live validation | Skipped (no key) |

## Audit

### Site: `workflow.py:83`

| Field | Value |
|---|---|
| SDK/Provider | Anthropic Messages API / `claude-haiku-4-5` |
| Input origin | Customer support ticket text (`X` parameter) |
| Downstream | Returns category label string to caller of `simple_classify()` |
| Classification | DECISION |
| Fit | FIT |
| Reason | Selects one of 10 enumerated insurance support categories. No math, dates, multi-hop reasoning, generation, or non-text input. Benign fixed-fixture distribution. |
| Context size | Small (single ticket + category descriptions) |
| Untrusted input | Ticket text from repo data files; benign domain |

## Options

| Site | Option | Action | Primitive | Benefit | Risk |
|---|---|---|---|---|---|
| `workflow.py:83` | 1 | `fallback` | Choice | Jev is faster/cheaper; accepted decisions save Anthropic cost; fallback fraction × original cost added | Low — conservative fallback preserves original behavior |
| `workflow.py:83` | 2 | `leave` | none | No changes needed | None |

## Selected

| Site | Selected option | Action |
|---|---|---|
| `workflow.py:83` | 1 | `fallback` |

Approval predicate: `actions: [fallback]`, scope: "Only pure DECISION sites with enumerated outputs, preserve behavior and original fallback provider." Site matches: pure DECISION, 10 enumerated category labels.

## Wiring Record

| Role | Symbol |
|---|---|
| Original callable | `workflow.simple_classify` (builds Anthropic prompt, calls `client.messages.create`, parses label) |
| Converted public callable | `workflow.simple_classify` (tries Jev first, falls back to original) |
| Decisions evaluator/gate | `jev_decisions.classify_ticket` (Choice primitive, confidence gate) |
| Transport | TypeSafe Python SDK (`typesafe_sdk.TypeSafeClient`), env var `TYPESAFE_API_KEY` |
| Validation import | `jev_decisions.classify_ticket` imported directly; original preserved as `_original_classify` |

## Conversion scope

1. Create `jev_decisions.py` — single decisions module with model pin, question, criteria, threshold, gate.
2. Modify `workflow.py` — wrap `simple_classify` to try Jev, fall back to original Anthropic call on low confidence, error, missing key.
3. Add `.env.example` with `TYPESAFE_API_KEY` placeholder.
