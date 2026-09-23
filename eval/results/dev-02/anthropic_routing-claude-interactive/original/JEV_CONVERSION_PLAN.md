# Jev Conversion Plan — `anthropic_routing`

## Source revision

- **Branch:** `jev-convert/evaluation` (from `main` at `b4191f3`)
- **Repository:** `anthropic_routing-claude-interactive/original`

## Preflight facts

- Git status: clean
- Branch `jev-convert/evaluation`: created from clean main
- `OPENROUTER_API_KEY`: present (value not inspected)
- Risk posture: **conservative**
- Output mode: **branch**
- Provider: OpenRouter, model pin `typesafe/jev-1.13-20260917`

## Audit summary

| # | File:line | Provider | Downstream | Classification | Fit |
|---|---|---|---|---|---|
| A | `workflow.py:24` | Anthropic SDK / claude-sonnet-4-6 | `<selection>` → route key; `<reasoning>` → printed to stdout | MIXED | CONDITIONAL FIT |
| B | `workflow.py:34` | Anthropic SDK / claude-sonnet-4-6 | Free-form prose support response | GENERATION | NOT A FIT |

**Wrapper note:** `llm_call()` in `util.py` serves both sites. Its aggregate classification is MIXED. It is not a separate conversion target.

## Options presented

### Site A (`workflow.py:24`)

1. **fallback** — Jev Choice with original LLM fallback for routing; synthetic reasoning diagnostic on Jev path
2. **decompose** — Separate routing decision (Jev Choice) from reasoning generation (original LLM)
3. **leave** — No conversion

### Site B (`workflow.py:34`)

4. **leave** — No conversion (generation site)

## User approval

```json
{
  "actions": ["fallback"],
  "scope": "Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged. Preserve all externally observable fields."
}
```

## Resolved selections

The approval authorizes `fallback` but restricts scope to **pure DECISION sites only**. Resolving the predicate against the audit:

- **Site A** (`workflow.py:24`): classified **MIXED** (routing decision + printed reasoning diagnostic) → **excluded** by scope predicate "leave MIXED … unchanged"
- **Site B** (`workflow.py:34`): classified **GENERATION** → **excluded** by scope predicate "leave … GENERATION unchanged"

**Result: zero sites selected for conversion.** No code changes, dependencies, or environment modifications are made.

## Rationale

Site A is the only site with a Jev-eligible component (the routing decision), but the same LLM call also produces `<reasoning>` text that is printed to stdout (lines 28–29). Per audit rules, "a router that returns and prints explanatory reasoning is MIXED even if only its route controls execution." The user's approval explicitly excludes MIXED sites, so this site cannot be converted under the current scope.

To convert Site A, the user would need to either:
1. Approve the `fallback` option for MIXED sites (accepting synthetic reasoning on the Jev path), or
2. Approve the `decompose` option to split the routing decision from reasoning generation.
