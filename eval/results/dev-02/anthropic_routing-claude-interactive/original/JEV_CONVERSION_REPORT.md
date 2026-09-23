# Jev Conversion Report — `anthropic_routing`

## Summary

**No sites were converted.** The user-approved scope ("Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged") excluded all audited sites. This is a negative-control outcome.

## Context

| Field | Value |
|---|---|
| Source revision | `b4191f3` on `main` |
| Output mode | Branch (`jev-convert/evaluation`) |
| Risk posture | Conservative |
| Provider | OpenRouter |
| Model pin | `typesafe/jev-1.13-20260917` |
| `OPENROUTER_API_KEY` | Present (not inspected) |

## Audit results

| Site | File:line | Classification | Fit | Selected option |
|---|---|---|---|---|
| A | `workflow.py:24` | MIXED | CONDITIONAL FIT | **leave** (excluded by scope) |
| B | `workflow.py:34` | GENERATION | NOT A FIT | **leave** (excluded by scope) |

### Why Site A was excluded

Site A performs ticket routing via a single LLM call that produces both:
- `<selection>` — a closed-set route label (billing/technical/account/product), used as a dict key
- `<reasoning>` — explanatory text printed to stdout at lines 28–29

The `<reasoning>` output is observable generation. Per audit rules, this makes the site MIXED. The approval scope explicitly requires "pure DECISION sites" and says "leave MIXED … unchanged."

### Why Site B was excluded

Site B generates free-form prose support responses. Classification: GENERATION. Jev is not designed for text generation. Additionally excluded by the approval scope.

## Changed sites

None.

## Unchanged sites

- `workflow.py:24` (MIXED — excluded by approval scope)
- `workflow.py:34` (GENERATION — not a fit)
- `util.py:22` (shared wrapper — serves both sites, no independent conversion)

## Validation

**No conversions means no parity calls are needed and no parity claim is made.** Live validation skipped — no converted sites to measure.

No code, dependencies, or environment files were modified.

## Test commands

The upstream workflow has no project test command. Smoke command:
```
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/bigsoup/Downloads/Jev\ Converter/eval/smoke.py /Users/bigsoup/Downloads/Jev\ Converter/eval/runs/dev-02/anthropic_routing-claude-interactive/original anthropic_routing
```

Since no code was changed, the smoke test validates the unchanged original.

## Limitations

- Site A has a Jev-eligible routing component but cannot be converted under the current approval scope
- To unlock conversion, the user would need to approve `fallback` or `decompose` for MIXED sites

## Undo instructions

To revert to the original state:
```bash
git checkout main
git branch -d jev-convert/evaluation
```
