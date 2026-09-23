# Jev Conversion Plan

## Preflight

| Field | Value |
|---|---|
| Repository | `/Users/bigsoup/Downloads/Jev Converter/eval/runs/supplemental-02/no-key-claude/original` |
| Original branch | `main` |
| Original SHA | `dcf0d680099815876708b8b6550bc2e5e8d10d9c` |
| Output mode | `branch` |
| Branch | `jev-convert/no-key` |
| Provider | `none` |
| Key present | `false` |
| Risk posture | `conservative` |
| Live validation | skipped (no key) |

## Audit

### Site inventory

| ID | Provider | Downstream | Classification | Fit | Reason |
|---|---|---|---|---|---|
| `workflow.py:83` | Anthropic SDK / `claude-haiku-4-5` | Returned label string selects one of 10 insurance support categories | DECISION | FIT | Bounded semantic classification over trusted, benign text into a closed enumerated set; no math, dates, multi-hop reasoning, generation, or adversarial input |

One LLM call site found. No wrappers, no shared consumers. One site = one conversion opportunity.

### Options

| Site | Option | Action | Primitive | Benefit | Risk | Scope |
|---|---|---|---|---|---|---|
| `workflow.py:83` | A | `fallback` | Choice | Accepted Jev decisions are faster (~100 ms vs ~500 ms+) and cheaper ($0.042/M tokens vs Haiku pricing); serial misses add Jev latency before original | Jev may disagree on ambiguous boundary cases between similar categories; conservative fallback retains original for low-confidence answers | Replace `simple_classify` entry point with `classify` that calls Jev Choice, gating on confidence ≥ 0.7, falling back to original `simple_classify` on low confidence, missing key, errors, or timeouts |
| `workflow.py:83` | B | `leave` | none | No risk; no change | No cost/latency benefit | Leave as-is |

## Approval resolution

Config predicate: `"Only pure DECISION sites with enumerated outputs, preserve behavior and original fallback provider"` with actions `["fallback"]`.

- `workflow.py:83` is a pure DECISION site with 10 enumerated outputs. **Matches.** Selected: **Option A (fallback)**.

## Selected plan

1. Create `jev_decisions.py` with model pin `jev-1.13.0`, all 10 category criteria, confidence threshold 0.7, timeout 10 s, validation, and gate logic.
2. Add `classify(X)` to `workflow.py` that calls `classify_with_jev(X, simple_classify)`.
3. Preserve `simple_classify` unchanged as the fallback path.
4. Add `.env.example` with `TYPESAFE_API_KEY` and `ANTHROPIC_API_KEY` placeholders.
5. Validate with smoke test. Live validation skipped (no key).
