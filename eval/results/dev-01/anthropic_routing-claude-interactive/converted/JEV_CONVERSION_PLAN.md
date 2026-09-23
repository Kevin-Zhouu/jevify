# Jev Conversion Plan — `anthropic_routing`

## Source revision

- Branch: `main`
- Commit: `10e56a3` (Baseline pinned upstream workflow and installed skill)

## Output mode

- Mode: branch (`jev-convert/evaluation`)
- Clone path: `converted/`

## Setup answers

| Setting | Value |
|---|---|
| Provider | OpenRouter |
| Key env | `OPENROUTER_API_KEY` |
| Model pin | `typesafe/jev-1.13-20260917` |
| Risk posture | Conservative |

## Audit summary

| ID | File:Line | Classification | Fit | Selected option |
|---|---|---|---|---|
| S1 | `workflow.py:24` | MIXED | Conditional | **leave** (excluded by approval scope) |
| S2 | `workflow.py:34` | GENERATION | NOT A FIT | **leave** |
| W1 | `util.py:9` | MIXED | Not independently convertible | **leave** |

**Wrapper relationship:** W1 (`util.py:llm_call`) is a shared transport wrapper called by both S1 and S2. It is not independently convertible; any conversion would occur at the call sites.

## Approval

```json
{
  "actions": ["fallback"],
  "scope": "Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged. Preserve all externally observable fields."
}
```

## Resolution

**Zero sites converted.** The approval scope requires pure DECISION classification with enumerated outputs. All identified sites are classified MIXED or GENERATION:

- **S1** (`workflow.py:24`): MIXED — the routing call produces both a decision (route selection) and generated content (reasoning text printed to stdout). The decision component is a strong Choice fit, but the site as a whole is MIXED. The approval explicitly excludes MIXED sites.
- **S2** (`workflow.py:34`): GENERATION — pure prose generation. Not a Jev fit.
- **W1** (`util.py:9`): MIXED — shared wrapper serving both MIXED and GENERATION consumers.

No code, dependency, or environment changes are made. Report artifacts only.
