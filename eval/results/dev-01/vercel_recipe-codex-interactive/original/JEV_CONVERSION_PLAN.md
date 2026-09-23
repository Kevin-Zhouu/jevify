# Jev conversion plan

No good Jev opportunities here.

## Setup and preflight

- Source branch: `main`; source revision: `c401444f0ce28166917950472c12af94424e44a8`.
- Output mode: branch; output branch: `jev-convert/evaluation` in this repository. The configured clone_path is inactive in branch mode.
- Preflight: Git available, tracked and untracked working tree clean, requested branch valid and unused. No applicable AGENTS.md was found within this repository.
- Selected access: OpenRouter, environment variable `OPENROUTER_API_KEY`, model pin `typesafe/jev-1.13-20260917`. No credentials accessed; no provider requests needed.
- Risk: conservative.

## Audit and options

| Original site | Provider | Downstream | Classification / fit | Option, primitive, benefit and risk |
| --- | --- | --- | --- | --- |
| `workflow.ts:7` | Vercel AI SDK / OpenAI `gpt-4o-mini`, structured outputs | Prints recipe JSON, blank line, usage and finish reason; errors reach console.error | GENERATION / NOT A FIT | `leave`; primitive none. Preserve generation and diagnostics; unchanged cost/latency, no migration risk or speculative savings. |

The fixed prompt is “Generate a lasagna recipe.” Its schema contains unrestricted strings for recipe name, ingredient names and amounts, and steps. There are no closed choices, candidate values, shared wrappers or additional model sites. Input context is a short fixed trusted fixture; no runtime untrusted input or mitigation is present. This assessment is limited to that fixture. Metadata is part of the observable contract.

## Approval resolution

User approved `fallback` only for pure DECISION sites with enumerated outputs, explicitly excluding MIXED and GENERATION and requiring all observable fields to remain intact. This predicate matches **zero sites**. All other conversion options are declined. The generation site remains unchanged under that explicit exclusion. Converted sites: `[]`.

Create only this plan, JEV_AUDIT.json and JEV_CONVERSION_REPORT.md. No source, dependencies, environment files, model routing, decisions module or fallback adapter changes are appropriate. Commit these artifacts on the selected branch; do not push or create a PR.

## Validation plan

Run the user-supplied independent behavior smoke against this repository on the output branch. Verify source bytes against the source revision. No project test command is present. No live paired comparisons, confidence thresholds or forced Jev failures apply because there are no converted sites. Do not create JEV_PARITY.json without measurements.
