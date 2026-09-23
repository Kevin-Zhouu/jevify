# Jev Conversion Plan

## Preflight

| Field | Value |
|---|---|
| Source revision | `091077883e33b4725f61b08add3e42312193f8e7` |
| Branch | `main` |
| Repo status | Clean |
| Output mode | **Report** (no code changes) |
| Risk posture | Conservative |
| Provider | OpenRouter (`typesafe/jev-1.13-20260917`) |
| Key env variable | `OPENROUTER_API_KEY` |
| Config path | `jevify.config.yaml` |

## Audit Summary

Three LLM call sites identified across two files. The shared wrapper `llm_call()` in `util.py` serves both call sites in `workflow.py`.

### Site Table

| ID | Provider | Downstream | Classification | Fit | Selected Option |
|---|---|---|---|---|---|
| `workflow.py:24` | Anthropic / claude-sonnet-4-6 | Route selection (closed set: billing, technical, account, product) + printed reasoning | MIXED | CONDITIONAL | **leave** |
| `workflow.py:34` | Anthropic / claude-sonnet-4-6 | Free-form specialist support response | GENERATION | NOT A FIT | **leave** |
| `util.py:21` | Anthropic / claude-sonnet-4-6 | Shared transport wrapper for both sites | MIXED | NOT A FIT | **leave** |

### Options Considered

#### workflow.py:24 — Routing selector (MIXED)

**Option 1: decompose (Choice)** — Split routing into Jev Choice for route selection + retain LLM for reasoning generation. Would reduce routing cost significantly (Jev ~$0.042/Mtok input-only vs Claude Sonnet ~$3/$15 input/output). However, this acts on a MIXED site and changes the observable reasoning output contract.

**Option 2: leave** — No change. Preserves all behavior including printed reasoning.

**Selected: leave** — The approval scope explicitly restricts conversion to "Only pure DECISION sites with enumerated outputs" and states "leave MIXED and GENERATION unchanged." This site is MIXED because the LLM call generates reasoning text that is printed to stdout (lines 28-29), not just a route label.

#### workflow.py:34 — Specialist response (GENERATION)

**Option 1: leave** — Generation is never Jev-suitable.

**Selected: leave**

#### util.py:21 — Shared wrapper (MIXED)

**Option 1: leave** — Wrapper serves generation consumers.

**Selected: leave**

## Approval Resolution

The config provides a bounded predicate:
- **Actions:** `[fallback]`
- **Scope:** "Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged. Preserve all externally observable fields."

**Resolution:** No sites match this predicate. The only site with decision-like behavior (`workflow.py:24`) is classified MIXED because it generates and prints reasoning text alongside the route selection. The predicate explicitly excludes MIXED sites.

## Conclusion

**No good Jev opportunities here** under the current approval scope.

The routing decision at `workflow.py:24` selects from a closed set of 4 support teams, which maps naturally to a Jev Choice primitive. However, the same LLM call also produces explanatory reasoning that is printed to stdout. This makes the site MIXED per audit rules. Converting only the decision portion would require a `decompose` action on a MIXED site, which falls outside the approved scope.

If the reasoning output were not a required observable (i.e., if it could be dropped or the contract could be changed), the route selection alone would be a strong fit for Jev Choice with confidence-gated fallback. A future approval that includes `decompose` for this specific site could unlock that conversion.

## Converted Sites

None. No code, dependency, or environment changes were made.
