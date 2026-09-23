# Jev Conversion Plan

## Preflight

| Field | Value |
|---|---|
| Repository | `original/` (SHA `1c953f75`) |
| Branch | `jev-convert/evaluation` |
| Output mode | Clone → `converted/` |
| Status | Clean |
| Provider | OpenRouter (`OPENROUTER_API_KEY` present) |
| Model pin | `typesafe/jev-1.13-20260917` |
| Risk posture | Conservative |

## Audit Summary

One LLM call site identified:

### Site: `workflow.py:83` — `client.messages.create`

| Field | Detail |
|---|---|
| SDK / Provider | Anthropic SDK / `claude-haiku-4-5` |
| Input | Caller-supplied ticket text string |
| Prompt | Classifies support ticket into one of 10 insurance categories |
| Output | Single category label string (stripped) |
| Downstream | Return value from `simple_classify()` |
| Classification | DECISION |
| Fit | FIT |

## Wiring Record

| Component | Symbol / Path |
|---|---|
| Original callable | `workflow.simple_classify` (invokes `client.messages.create` at line 83) |
| Converted public callable | `workflow.simple_classify` (same signature, tries Jev first) |
| Decisions evaluator/gate | `jev_decisions.evaluate_classify` |
| Transport | `urllib.request.urlopen` → OpenRouter `/v1/systemone` |
| Baseline authorization | OpenRouter routing of `anthropic/claude-haiku-4-5` for eval only |

## Approved Options

| Site | Option | Primitive | Action |
|---|---|---|---|
| `workflow.py:83` | `fallback` | Choice (10 categories) | Jev Choice with confidence-gated fallback to original Anthropic call |

## Declined Options

- `jev_only` — excluded by conservative risk posture
- `leave` — declined by user

## Changes

1. **`jev_decisions.py`** (new) — All Jev model IDs, question definitions, category criteria, confidence threshold, and gate logic. Single `evaluate_classify(ticket_text)` entry point returns `(label, accepted)`.

2. **`workflow.py`** (modified) — `simple_classify()` now tries `jev_decisions.evaluate_classify()` first inside a try block. On acceptance, returns the Jev label. On rejection/error, falls through to the unchanged original Anthropic call.

3. **`.env.example`** (new) — Placeholder for `OPENROUTER_API_KEY`.

## Gate Policy

- Confidence threshold: 0.6 (conservative starting point)
- Below threshold → fallback to original
- Missing key → fallback to original
- Network error / timeout → fallback to original
- HTTP 429 → fallback to original
- Malformed response / unknown label / invalid confidence → fallback to original
- Bool as confidence → fallback to original
- Model mismatch → fallback to original
- Every path logs `{jev_decision, model, reason}` to stderr
