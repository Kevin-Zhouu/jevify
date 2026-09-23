# Jev Conversion Plan

## Source revision

- Branch: `main`
- Commit: `fd78ebf`
- Output mode: clone to `converted/` on branch `jev-convert/evaluation`

## Audit summary

### Site inventory

| ID | File | Line | Provider | Downstream | Classification | Fit |
|---|---|---|---|---|---|---|
| S1 | `workflow.py` | 83–92 | Anthropic SDK / `claude-haiku-4-5` | `.content[0].text` stripped → bare label string (one of 10 categories) | DECISION | FIT |

### Classification rationale

**DECISION**: The model's substantive answer is a single label from a closed set of exactly 10 insurance categories. The prompt enforces output format via `<category>` prefill and `</category>` stop sequence. No prose, reasoning, code, or free-form text is generated or consumed. No envelope metadata (usage, finish_reason, IDs) is used downstream — only the stripped label string.

### Fit rationale

**FIT**: Closed 10-label set with descriptions. Semantic classification of short insurance tickets. Benign fixed corpus. No math, date comparison, multi-hop reasoning, or adversarial input concerns.

## Options presented

### Site S1: `workflow.py:83`

| # | Action | Primitive | Benefit | Risk |
|---|---|---|---|---|
| A | `fallback` | Choice (10 options) | Lower cost and latency on accepted decisions. Jev input-token pricing is substantially cheaper than Claude Haiku. Most tickets classify at high confidence, avoiding the Claude call entirely. Expected cost = Jev cost + fallback_fraction × Claude cost. | Serial miss adds Jev latency before Claude fallback. Jev and Claude may disagree on ambiguous tickets; threshold tuning needed. |
| B | `jev_only` | Choice (10 options) | Removes Claude dependency entirely. Maximum savings. | No safety net. Excluded by conservative risk posture. |
| C | `leave` | — | No change, no risk. | No improvement. |

## Approval

- **Selected**: Option A (`fallback`) for site S1
- **Scope**: Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged. Preserve all externally observable fields.
- **Risk posture**: Conservative — fallback always retained.

## Conversion plan

1. Create `jev_decisions.py` containing:
   - Pinned Jev model ID: `typesafe/jev-1.13-20260917` (OpenRouter)
   - Choice question with 10 insurance category criteria matching the original labels
   - Confidence threshold (initial: 0.7, to be calibrated during parity)
   - `classify_with_jev()` function that calls Jev, checks confidence, returns label or `None`

2. Modify `workflow.py`:
   - Import `classify_with_jev` from `jev_decisions`
   - In `simple_classify()`, try Jev first; if high-confidence label returned, use it
   - On `None` (low confidence), error, timeout, or missing key: fall through to original Claude path unchanged
   - Log decision path to stderr (jev/original) without secrets or input content

3. Preserve:
   - Function signature: `simple_classify(X) -> str`
   - Synchronous behavior
   - Return type: bare stripped label string
   - No new required dependencies at module load (graceful import)

## Provider configuration

- Provider: OpenRouter
- Key env var: `OPENROUTER_API_KEY`
- Model: `typesafe/jev-1.13-20260917`
- SDK base URL: `https://openrouter.ai/api`
- Endpoint: System One via OpenRouter

## Preflight

- Git repo: clean
- Branch `jev-convert/evaluation`: created from `main` at `fd78ebf`
- Clone path: `converted/`
