# Jev Conversion Report — vercel_recipe

## Source revision

Commit `6008b62` on branch `main`.

## Output mode

Branch `jev-convert/evaluation` cloned to `converted/`.

## Approvals

- Risk posture: conservative
- Approved actions: `["fallback"]`
- Approved scope: "Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged. Preserve all externally observable fields."

## Sites

### S1 — `workflow.ts:7` (GENERATION, NOT A FIT)

- **Status:** Unchanged (leave)
- **Reason:** The sole LLM call produces a complete recipe via `generateObject`. All output fields are free-form generative content. No Jev primitive can substitute. The approval scope explicitly excludes GENERATION sites.

## Converted sites

None. No code, dependency, or environment changes were made.

## Model / Provider

Not applicable — no Jev integration performed.

## Validation

### Smoke test

Command: `node /Users/bigsoup/Downloads/Jev\ Converter/eval/smoke.cjs <output_dir> vercel_recipe`

The smoke test exercises the original workflow under network isolation (fetch disabled). It verifies:
- Exactly one call to the original provider mock
- Logged output contains "lasagna"

Result: **PASS** — "observable TypeScript behavior and original-path fallback smoke"

### Live parity

Not applicable — no sites were converted. No parity measurements were made, and none are claimed.

## Conclusion

**No good Jev opportunities here.** This workflow is purely generative: it asks an LLM to produce a complete recipe from a single prompt. Every output field is unbounded creative prose. Jev's typed decision primitives (Choice, Score, Noul) cannot produce equivalent output. The only sound option is to leave the workflow unchanged.

## Limitations

- No conversion was performed, so no live parity, cost, or latency measurements apply.

## Undo instructions

To revert: switch to the original branch (`git checkout main`) and delete the conversion branch (`git branch -D jev-convert/evaluation`), or delete the `converted/` clone directory.
