# Jev Conversion Report

## Summary

| Field | Value |
|---|---|
| Source revision | `000037c3f4e39806927748be49e8f05c7a3c01a9` |
| Source branch | `main` |
| Output mode | report |
| Provider | OpenRouter |
| Model pin | `typesafe/jev-1.13-20260917` |
| Risk posture | conservative |
| Key present | yes |
| Headless | yes |

## Approval

Headless config approved `fallback` action on pure DECISION sites with enumerated outputs. No DECISION sites were found, so no conversions were approved or performed.

## Sites audited

| ID | Classification | Fit | Action |
|---|---|---|---|
| `workflow.py:10` | GENERATION | NOT A FIT | leave |
| `workflow.py:23` | GENERATION | NOT A FIT | leave |
| `workflow.py:42` | GENERATION | NOT A FIT | leave |

## Changed sites

None.

## Unchanged sites

All three sites remain unchanged. Each produces free-form text via the OpenAI SDK (`gpt-5.5`). Jev returns typed decisions over closed option sets and cannot generate prose, code, or explanations.

### Per-site reasoning

- **workflow.py:10** — Non-streaming completion asking for free-form reply to "Say this is a test." Pure generation with no decision component.
- **workflow.py:23** — Streaming completion asking "How do I output all files in a directory using Python?" Produces a tutorial-style answer streamed token by token. Streaming generation is doubly incompatible: Jev does not generate text and does not support streaming.
- **workflow.py:42** — Same generation prompt as line 10, but accessed via `with_raw_response` to extract the HTTP `request_id` header. Exercises provider-specific transport metadata unrelated to Jev's System One endpoint.

## Validation

No conversions were performed. Live validation is not applicable — there are no converted sites to measure parity against. No parity claim is made.

## Smoke test

```
$ python3.14 smoke.py . openai_demo
PASS: observable Python behavior and original-path fallback smoke
```

The upstream smoke test passes on the unmodified repository, confirming all three call sites produce expected output.

## Artifacts

| File | Contents |
|---|---|
| `JEV_AUDIT.json` | Machine-readable site inventory with classifications and options |
| `JEV_CONVERSION_PLAN.md` | Audit, options, and approval resolution |
| `JEV_CONVERSION_REPORT.md` | This file |

## Limitations

- All sites are GENERATION. No Jev conversion is possible for this workflow.
- No `JEV_PARITY.json` is produced because no conversions were made and no parity measurements are applicable.

## Undo

No code was changed. No branches were created. No dependencies were added. No undo action is required.
