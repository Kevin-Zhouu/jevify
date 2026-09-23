# Jev conversion plan

No good Jev opportunities here.

## Setup and preflight

- Source revision: `2875b87b890f1a9c61dbfe34121c1ca04f52c2e9`; original branch: `main`.
- Output mode: branch, `jev-convert/evaluation`, in this repository. The supplied clone path is inactive in branch mode.
- Preflight: Git repository present, clean including untracked files; requested branch unused before creation. No applicable AGENTS.md was found in the repository inventory.
- Setup and approval supplied in the conversation are authoritative; config and credential values were not read.
- Requested access: OpenRouter, environment variable `OPENROUTER_API_KEY`, pinned model `typesafe/jev-1.13-20260917`; conservative risk. No Jev integration or credential access is needed.
- Isolated baseline evaluation routing is authorized only for the same original model and unchanged prompts/parsing. No evaluation routing or production provider change is needed.

## Audit and options

| Original site | Provider/model | Downstream | Classification / fit | Option, primitive, benefit and risk |
|---|---|---|---|---|
| workflow.py:10 | OpenAI SDK / OpenAI / gpt-5.5 | Prints message.content at line 19 | GENERATION / NOT A FIT | A: leave; none. Preserve generated text. Unchanged cost/latency; no migration risk. |
| workflow.py:23 | OpenAI SDK / OpenAI / gpt-5.5 | Streams delta.content, skips chunks without choices, prints final newline | GENERATION / NOT A FIT | B: leave; none. Preserve generated guidance and streaming. Unchanged cost/latency; no migration risk. |
| workflow.py:42 | OpenAI SDK / OpenAI / gpt-5.5 | Parses raw response, prints actual request ID and message.content | GENERATION / NOT A FIT | C: leave; none. Preserve generated text and truthful diagnostics. Unchanged cost/latency; no migration risk. |

The standard and raw-response prompts request text, not an enumerated label. The streaming prompt requests open-ended Python guidance. Jev typed decisions cannot replace any of these outputs while preserving behavior. All inputs are short fixed text literals; no external untrusted input enters this example. There are three direct SDK call sites and no repository-defined wrappers or additional consumers, so no wrapper savings are double-counted. The fit verdict applies to these fixed inputs.

## Approval resolution

Approved action: `fallback`, only for pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged and preserve all externally observable fields. All other options were declined.

The predicate matches **zero sites**. No fallback conversion is selected or performed. All three generation sites remain unchanged as explicitly required by the approval scope; this does not treat declined options as permission to implement anything. `converted_sites` is empty.

## Execution and validation

Create the requested branch and write this plan, `JEV_AUDIT.json`, and `JEV_CONVERSION_REPORT.md`. Do not edit source, dependencies, environment files, prompts, output parsing or diagnostics. Run the supplied independent behavior smoke with Python 3.14 against this repository, then verify source identity against the original revision. No project test command exists. No converted sites means live parity calls and threshold/fault testing of a Jev adapter are inapplicable. Do not create `JEV_PARITY.json` without measurements. Commit only the three report artifacts; do not push or create a PR.
