# Jev Conversion Plan

## Preflight

- **Source revision:** `ab53bd4` (branch `main`, clean)
- **Output mode:** branch `jev-convert/evaluation` cloned to `converted/`
- **Provider:** OpenRouter (`OPENROUTER_API_KEY`), pin `typesafe/jev-1.13-20260917`
- **Risk posture:** conservative
- **Baseline validation:** authorized to route original model through OpenRouter

## Audit Summary

| Site | Provider | Downstream | Classification | Fit |
|---|---|---|---|---|
| `workflow.ts:7` | Vercel AI SDK / `gpt-4o-mini` via `generateObject` | Recipe object printed to stdout; `usage` and `finishReason` logged | GENERATION | NOT A FIT |

### Site Detail: `workflow.ts:7`

The `generateObject` call generates a lasagna recipe. Every schema field contains open-ended strings (recipe name, ingredient names/amounts, cooking steps). Per audit rules, a schema with open-ended strings remains GENERATION. Jev 1.13 jaggedness confirms text generation "will not work well and will be very slow." No decision, routing, classification, or selection behavior is present to decompose.

Additionally, `result.usage` and `result.finishReason` are observable diagnostics tied to the original provider's response shape.

### Options

| Site | Option | Action | Primitive | Benefit | Risk |
|---|---|---|---|---|---|
| `workflow.ts:7` | A | **leave** | none | No change, no risk | N/A |

No other options are applicable. There is no decision component to extract.

## Approval

User approved: "Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged. Preserve all externally observable fields."

**Result:** Zero sites match the approval predicate. No DECISION sites exist in this workflow. All sites remain unchanged.

## Selected Conversions

None. No sites qualify under the approved scope.
