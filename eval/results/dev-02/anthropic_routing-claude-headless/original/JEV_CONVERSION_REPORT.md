# Jev Conversion Report

## Summary

| Field | Value |
|-------|-------|
| Source revision | `d59165390fbe6d96614dde2278dc4fec3a35d4c7` (main) |
| Output mode | report |
| Output directory | `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/anthropic_routing-claude-headless/original` |
| Provider | OpenRouter (`typesafe/jev-1.13-20260917`) |
| Key present | Yes (`OPENROUTER_API_KEY`) |
| Risk posture | conservative |

## Approval

**Predicate**: "Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged. Preserve all externally observable fields."

**Result**: No sites matched the approval predicate. All sites are MIXED or GENERATION.

## Sites

### Changed sites

None.

### Unchanged sites

| Site | Classification | Reason unchanged |
|------|---------------|-----------------|
| `workflow.py:24` | MIXED | Route selector generates printed reasoning alongside route selection. MIXED sites are excluded by the approval scope. |
| `workflow.py:34` | GENERATION | Pure prose generation. GENERATION sites are excluded by the approval scope and are never Jev-eligible. |
| `util.py:22` | MIXED | Shared wrapper serving both MIXED and GENERATION consumers. Not independently convertible. |

## Conclusion

**No good Jev opportunities here** under the approved scope.

The routing call at `workflow.py:24` contains a decision component (selecting from 4 enumerated support teams: billing, technical, account, product) that would be a natural fit for a Jev Choice primitive. However, the same call also generates chain-of-thought reasoning that is printed to stdout — making the entire site MIXED. The approval scope restricts conversion to pure DECISION sites only.

A decompose option (split into Jev Choice + separate reasoning call) exists but was not approved, as it requires modifying a MIXED site's generated component.

## Model and provider

- Jev model: `typesafe/jev-1.13-20260917` (OpenRouter)
- Original model: `claude-sonnet-4-6` (Anthropic SDK)

## Validation

**Live validation skipped** — no sites were converted, so no parity measurements are needed and no parity claim is made. The OpenRouter API key is present but unused because there are no converted sites to validate.

## Test commands

Smoke test (original behavior, offline):
```
/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/bigsoup/Downloads/Jev\ Converter/eval/smoke.py /Users/bigsoup/Downloads/Jev\ Converter/eval/runs/dev-02/anthropic_routing-claude-headless/original anthropic_routing
```

## Artifacts

| Artifact | Path |
|----------|------|
| Audit (JSON) | `JEV_AUDIT.json` |
| Conversion plan | `JEV_CONVERSION_PLAN.md` |
| Conversion report | `JEV_CONVERSION_REPORT.md` |

No `JEV_PARITY.json` is written because no sites were converted and no parity measurements were taken.

## Limitations

- The routing decision at `workflow.py:24` is a strong Jev candidate if the reasoning generation were separately approved for modification (decompose option). This would require a broader approval scope covering MIXED sites.
- Report mode: no code, dependency, environment, or git changes were made.

## Undo

No changes to undo. Only report artifacts (`JEV_AUDIT.json`, `JEV_CONVERSION_PLAN.md`, `JEV_CONVERSION_REPORT.md`) were written. Remove them with:
```
rm JEV_AUDIT.json JEV_CONVERSION_PLAN.md JEV_CONVERSION_REPORT.md
```
