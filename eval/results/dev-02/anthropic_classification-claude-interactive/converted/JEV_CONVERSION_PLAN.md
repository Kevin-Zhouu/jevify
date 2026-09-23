# Jev Conversion Plan

## Source

- Repository: `anthropic_classification` (Anthropic cookbook example)
- Source SHA: `eff84f8f58d676d6b3b2eb21ae7b906300e2ef1b`
- Source branch: `main`
- Output mode: clone
- Output path: `converted/`
- Output branch: `jev-convert/evaluation`

## Preflight

- Git: available, repo clean
- Provider: OpenRouter
- Key env: `OPENROUTER_API_KEY` (present)
- Model pin: `typesafe/jev-1.13-20260917`

## Setup Answers

- Risk posture: **conservative** (fallback retained everywhere)
- Baseline routing: authorized via OpenRouter for isolated evaluation only

## Site Inventory

| Site | Provider | Downstream | Classification | Fit |
|---|---|---|---|---|
| `workflow.py:83` | Anthropic SDK / `claude-haiku-4-5` | Return value: bare category label string | DECISION | FIT |

## Approval

- **Approved**: Option A (fallback) for `workflow.py:83`
- **Declined**: Options B (jev_only), C (leave)
- **Scope**: Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged. Preserve all externally observable fields.

## Selected Plan: Option A — Jev with Fallback

### Changes

1. **New file: `jev_decisions.py`** — Single decisions module containing:
   - Model pin: `typesafe/jev-1.13-20260917` (OpenRouter dated pin)
   - 10 category criteria with structured `what`/`not_for` descriptions
   - Confidence threshold (calibrated during validation)
   - `classify_with_jev()` wrapper: tries Jev Choice first, falls back to original on low confidence, error, timeout, missing key, or unknown label
   - Pure `gate_accepts()` predicate for testing
   - Response validation for all consumed fields
   - Logging of path, model, and confidence on every code path (no secrets or input content)

2. **Modified file: `workflow.py`** — Minimal changes:
   - Original `simple_classify` renamed to `_original_classify` (unchanged internals)
   - New `simple_classify` delegates to `classify_with_jev(X, _original_classify)`
   - Function signature, return type, and all observable behavior preserved
   - Import of `jev_decisions` at module level; fallback works when package/key unavailable

3. **New file: `.env.example`** — Credential placeholder for `OPENROUTER_API_KEY`

### Preserved Contracts

- `simple_classify(X)` returns a stripped label string
- Anthropic SDK path unchanged (model, prompt, stop sequences, temperature)
- No new async behavior; all calls are synchronous
- No stdout contract changes; logging goes to stderr via `logging` module

### Fallback Triggers

- Missing `OPENROUTER_API_KEY`
- Network error, timeout (10s bound)
- HTTP 429 / server error
- Malformed/invalid Jev response
- Unknown label not in the 10 known categories
- Confidence below threshold
- Non-finite or out-of-range confidence

### Unchanged Sites

None — this workflow has only one LLM call site.
