# Jev Conversion Report

## Summary

| Field | Value |
|---|---|
| Source revision | `091077883e33b4725f61b08add3e42312193f8e7` |
| Output mode | Report (no code changes) |
| Risk posture | Conservative |
| Provider | OpenRouter (`typesafe/jev-1.13-20260917`) |
| Approval scope | Pure DECISION sites only; leave MIXED and GENERATION unchanged |
| Sites audited | 3 (2 unique call sites + 1 shared wrapper) |
| Sites converted | 0 |

## Conclusion

**No good Jev opportunities here** under the approved scope.

## Site Analysis

### workflow.py:24 — Routing selector (MIXED)

The `route()` function calls `llm_call()` with a prompt that requests both:
- `<selection>` — a route label from the closed set {billing, technical, account, product}
- `<reasoning>` — explanatory text about why that route was chosen

The reasoning is printed to stdout at lines 28-29. The selection is used as a dict key to look up a specialist prompt. Because the same LLM call produces both a closed-set decision and generated reasoning that is observably output, this site is **MIXED**.

The route selection alone would be a strong fit for Jev Choice (4 enumerated options, short input text, semantic classification task). However, the approval predicate excludes MIXED sites, and decomposing the call would change the observable reasoning output.

### workflow.py:34 — Specialist response (GENERATION)

Generates free-form support prose using a role-specific system prompt. This is pure generation and is never suitable for Jev.

### util.py:21 — llm_call wrapper (MIXED)

Shared Anthropic SDK transport wrapper serving both call sites. Classification follows its broadest consumer (MIXED). Not a separate conversion target.

## Changed Files

None.

## Unchanged Sites

All three sites remain unchanged:
- `workflow.py:24` — MIXED (excluded by approval scope)
- `workflow.py:34` — GENERATION (not Jev-suitable)
- `util.py:21` — shared wrapper (not a separate target)

## Validation

### Project tests
No project test command is configured. The upstream example has no test suite.

### Smoke test
No conversion was performed, so behavioral smoke testing of converted code is not applicable.

### Live parity
No conversion was performed. **Live validation skipped** — no parity claim is made. No `JEV_PARITY.json` is written because no Jev calls were made and no measurements were taken.

## Cost and Latency

No conversion means no cost or latency impact.

## Limitations

- The only decision-like site is MIXED due to printed reasoning. A `decompose` option could split the routing decision from reasoning generation, but this requires explicit approval for MIXED site modification.
- No baseline provider key was tested since no conversion occurred.

## Recommendations

If a future approval includes `decompose` for `workflow.py:24`:
1. Use Jev Choice with criteria mapping the 4 support teams
2. Set a confidence threshold (suggest starting at 0.7, calibrate on representative tickets)
3. Below threshold, fall back to the original Claude call for both routing and reasoning
4. Above threshold, use the Jev route selection; either drop the printed reasoning or generate it separately if the stdout contract must be preserved
5. Measure agreement on ≥30 diverse ticket samples before considering Jev-only

## Undo

No changes were made. No undo steps are needed. Report artifacts (`JEV_AUDIT.json`, `JEV_CONVERSION_PLAN.md`, `JEV_CONVERSION_REPORT.md`) can be deleted if unwanted.
