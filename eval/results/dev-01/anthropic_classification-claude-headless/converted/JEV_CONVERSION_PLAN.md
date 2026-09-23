# Jev Conversion Plan

## Source

- Repository: `anthropic_classification` (Anthropic Cookbook — classification guide)
- Source revision: `9ad0ba53546ba42a9b50165c3fe51ec275a58d68`
- Output mode: clone → `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-01/anthropic_classification-claude-headless/converted`
- Branch: `jev-convert/evaluation`
- Provider: OpenRouter (`typesafe/jev-1.13-20260917`)
- Key variable: `OPENROUTER_API_KEY`
- Risk posture: conservative (fallback retained everywhere)

## Preflight

- Git repo: clean, no untracked files
- Clone destination: available (did not exist before clone)
- Branch `jev-convert/evaluation`: created fresh on clone

## Audit

| Site | Provider | Downstream | Classification | Fit | Reason |
|---|---|---|---|---|---|
| `workflow.py:83` | Anthropic SDK / `claude-haiku-4-5` | Returns stripped category label (one of 10 insurance categories) consumed by callers of `simple_classify()` | DECISION | FIT | Bounded semantic classification selecting one label from a closed, enumerated set of 10 categories. Text-only input. Trusted fixtures (train/test TSV data). No generation, no reasoning returned. Context well within limits. |

### Wrapper relationships

Single call site — no shared wrapper. `simple_classify()` is the only consumer of the Anthropic `messages.create()` call. No double-counting.

## Options

### `workflow.py:83` — DECISION / FIT

| # | Action | Primitive | Benefit | Risk |
|---|---|---|---|---|
| 1 | **fallback** | Choice | Likely cheaper accepted decisions (Jev input-only pricing ~$0.042/Mtok vs Claude Haiku ~$0.80/Mtok input + $4/Mtok output). Serial misses add Jev latency + cost before original inference. Expected cost = Jev cost + fallback fraction × original cost. | Jev may disagree on ambiguous tickets; confidence gating sends uncertain cases to original path. Conservative fallback always retained. |
| 2 | jev_only | Choice | Removes original cost entirely after proven parity. | Conservative posture excludes this option. |
| 3 | leave | — | No speculative savings; no change. | No risk. |

## Approval resolution

Config predicate: "Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged. Preserve all externally observable fields."

- `workflow.py:83` is a pure DECISION with 10 enumerated category outputs → **approved for option 1 (fallback)**

## Selected plan

| Site | Selected option | Action |
|---|---|---|
| `workflow.py:83` | 1 | `fallback` with Choice primitive, confidence threshold to be calibrated during validation |

## Files to create/modify

1. `jev_decisions.py` — decisions module with all Jev questions, criteria, thresholds, model pin
2. `workflow.py` — integrate Jev with confidence-gated fallback to original Anthropic path
3. `.env.example` — add `OPENROUTER_API_KEY` placeholder
4. `JEV_AUDIT.json` — machine-readable audit
5. `JEV_CONVERSION_REPORT.md` — final report with validation results
