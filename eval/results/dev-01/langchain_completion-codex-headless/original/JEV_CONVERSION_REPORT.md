# Jev conversion report

No good Jev opportunities here.

`workflow.ts:15` is GENERATION / NOT A FIT: arbitrary caller prompts produce a text stream returned via LangChainAdapter. Replacing it with a Jev Choice, Score or Noul would change the public behavior. See `JEV_CONVERSION_PLAN.md` for the full call trace, documentation, options and approval resolution, and `JEV_AUDIT.json` for structured evidence.

## Outcome

- Source revision: `4ecb8ae6d541ae543e02e861f961dd18fe0caa79`; branch `main`; output mode report.
- Approved predicate matches zero sites; converted sites: `[]`. Unchanged inference site: `workflow.ts:15`.
- Artifacts reside in `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-01/langchain_completion-codex-headless/original`. No clone or branch created. Source, dependencies, environment configuration, diagnostics and original provider remain unchanged. No commits, push or PR.
- Configured candidate provider/model: OpenRouter / `typesafe/jev-1.13-20260917`; not invoked. Baseline remains OpenAI `gpt-3.5-turbo-0125`; no alternate baseline route was used.

## Validation

Executed command:

```sh
node '/Users/bigsoup/Downloads/Jev Converter/eval/smoke.cjs' '/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-01/langchain_completion-codex-headless/original' langchain_completion
```

Exit status **0**. Output: `PASS: observable TypeScript behavior and original-path fallback smoke`.

The supplied external smoke was read and executed without modification. It transpiles and executes the actual workflow using original-SDK test doubles, supplies prompt `hello`, checks response text `stream:hello`, checks `maxDuration === 30`, and asserts exactly one original-provider call. It uses a stream marker rather than real streamed model chunks. This is an offline behavior smoke, not a live provider test, full dependency type-check, actual network-failure propagation test, or measured Jev parity. No generated repository test output was observed. There is no project test command.

**Live validation skipped**: no eligible or converted sites. No credentials were inspected and no inference requests were sent. Paired sample count: 0 (no measurement); agreement curve, confidence thresholds, fallback rate, p50/p95 latency, cost and calibration/confirmation split: not applicable and not measured. No `JEV_PARITY.json` is written because there is no live evidence. No Jev wrapper exists, so injected low-confidence, timeout, 429, malformed-answer and fallback-once tests are not applicable and are not claimed.

Per-site threshold recommendation for `workflow.ts:15`: none; retain original generation. No inference savings are claimed.

## Limitations and undo

This repository contains an isolated example, without installed application dependency versions or a full server/client integration. The smoke checks only its disclosed contract with doubles; it does not establish real model availability, stream framing, token metadata or generation quality. Source preservation is the basis for preserving the broader upstream semantics and diagnostics.

To undo this report-only task, remove only `JEV_CONVERSION_PLAN.md`, `JEV_AUDIT.json` and `JEV_CONVERSION_REPORT.md` from this repository. No branch switch or clone deletion is needed.
