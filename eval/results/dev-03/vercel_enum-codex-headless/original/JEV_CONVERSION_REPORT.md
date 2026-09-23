# Jev conversion report

Completed the config-approved conservative conversion of **workflow.ts:6** on branch
`jev-convert/evaluation`. Original `main` remains at source revision
`4bc5e23750b6af7d32147d2480a5bde33bb935cb`. Output repository:
`/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/vercel_enum-codex-headless/original`.
No clone, push, PR, or changes to the external smoke script. No credentials printed or saved.

## Scope and behavior

The sole upstream provider call is DECISION, a five-label movie genre enum. No other call
sites or wrappers exist in the original. The config's pure-enumerated-DECISION/fallback
predicate selected it; no scope expansion. Audit and options: JEV_AUDIT.json and
JEV_CONVERSION_PLAN.md. Production uses OpenRouter `typesafe/jev-1.13-20260917` in
jevDecisions.ts with a frozen confidence threshold of 0.9 and a five-second timeout.
The original OpenAI `gpt-4o-mini` generateObject expression is unchanged byte for byte
and retained for every rejected/error path. Its original errors propagate once.

All four stdout calls remain: enum, blank line, token usage and finish reason. Accepted
Jev responses report actual input/output token counts using the upstream usage field
names, with their sum as totalTokens. `stop` is the adapter-owned successful decision
completion status, not a native Jev token termination claim. Path and answering model
are logged to stderr without raw input or secrets. The source's structuredOutputs flag,
enum, prompt, model, parsing and main().catch(console.error) remain intact.

## Actual live evidence

Live validation performed; **32 unique paired confirmation inputs**, one original fixture
and 31 explicitly synthetic plots spanning five genres, overlaps, sparse and out-of-domain
inputs. Threshold 0.9 was chosen before measurement; calibration count 0, confirmation
count 32; no tuning or cherry-picking. Raw Jev-versus-original agreement: **31/32 (96.875%)**.
At deployed threshold: **29/29 accepted agree (100%)**, **3/32 fallback (9.375%)**.
The disagreement is sample 31, the bus-stop conversation: Jev drama vs original comedy,
confidence 0.74; the integration correctly took the original path.

| Threshold | Accepted | Selective agreement | Fallback fraction |
|---|---:|---:|---:|
| 0 | 32 | 96.88% | 0.000% |
| 0.5 | 31 | 96.77% | 3.125% |
| 0.7 | 31 | 96.77% | 3.125% |
| 0.9 | 29 | 100.00% | 9.375% |
| 0.95 | 28 | 100.00% | 12.500% |
| 1 | 27 | 100.00% | 15.625% |

JEV_PARITY.json contains actual provider request IDs, pinned model, raw Jev answer,
confidence/probabilities, usage/cost, original answer/model/request ID/usage, monotonic
latencies and actual gate outcome. No fallback answer is substituted for the raw Jev
answer. Each Jev response was captured once and replayed through the actual converted
main/gate; no successful model inference was fabricated.

| Metric | Jev | Original |
|---|---:|---:|
| p50 latency | 307.05 ms | 1267.54 ms |
| p95 latency | 522.17 ms | 1978.84 ms |
| Mean provider-reported cost | $0.000014495 | $0.000015183 |

Expected serial cascade mean latency: **467.44 ms**, versus
original mean **1237.81 ms**. This is computed from measured Jev time plus original
time on fallback rows, not a separate live end-to-end cascade timing run; replay/adapter
and application overhead are not included. Expected cascade cost: **$0.000015920/input**,
**4.86% higher** than baseline on this small sample. All costs are actual
OpenRouter `usage.cost`, not price estimates or assumed zero costs. Measurement date:
2026-09-23. This conversion demonstrates lower latency here, not cost savings.

## Validation and reproducibility

Run from the output repository (Node 24.14.1 used):

```sh
npm install --prefix .jev-validation --no-audit --no-fund ai@4.3.19 @ai-sdk/openai@1.3.24 zod@3.25.76 typescript@5.9.3
node validate-jev.cjs
node /Users/bigsoup/Downloads/Jev\ Converter/eval/smoke.cjs "$PWD" vercel_enum
.jev-validation/node_modules/.bin/tsc --noEmit --target ES2022 --module commonjs --skipLibCheck --moduleResolution node --baseUrl .jev-validation/node_modules workflow.ts jevDecisions.ts
/opt/homebrew/opt/python@3.14/bin/python3.14 .agents/skills/jevify/scripts/check_artifacts.py "$PWD" --require-live
```

- Supplied independent behavior smoke: PASS, original called exactly once with Jev network failure.
- Actual baseline generateObject expression identity assertion: PASS.
- Every paired converted main: PASS on enum, blank stdout line, complete usage object,
  finishReason and exactly zero/one original calls according to the actual gate.
- Fault assertions: PASS for low confidence (mutation of genuine capture), generic
  transport exception, AbortError timeout, actual injected HTTP 429, malformed response,
  unknown option, missing usage, invalid confidence, wrong model and array-valued usage.
  For each, original sentinel identity, call count one, exception identity and no retry
  were asserted. Missing-key fallback and nonfinite/boolean confidence predicates also pass.
- TypeScript noEmit check: PASS using isolated upstream-compatible dependencies.
- Artifact checker with --require-live: PASS (shape only, not independent truth certification).
- git diff --check: PASS.

The supplied smoke has no live parity role. validate-jev.cjs is the retained executable
proof, and its executed flags/results and captures are in JEV_PARITY.json. It imports the
actual evaluator and gate, loads baseline source from git, modifies only fixture literal
values for new cases, and runs the real SDK/parser. Only model namespace/transport/auth
are adapted to the config-authorized OpenRouter baseline route; retries are disabled for
bounded evaluation. Production still falls back directly to OpenAI.

## Limitations and recommendation

Keep **0.9** for workflow.ts:6 and retain original fallback. This sample meets the skill's
90% accepted-agreement target; it does not establish accuracy against human genre labels,
production robustness, adversarial safety or stable savings. There is no public-input
entrypoint and no injection defense; the fit is for benign short text. Out-of-domain inputs
must still choose one of the existing five labels to preserve upstream behavior.

The upstream snapshot has no manifest, lockfile or test command. The ambient SDK import
initially failed due to a Zod export mismatch, before any live calls. Evaluation therefore
used the pinned isolated dependencies above in ignored .jev-validation; these package
versions and the authorized gateway route are reproducibility limitations relative to
an unspecified upstream environment. No new runtime dependencies were added. No live
transport failures occurred in the completed 32-pair run. Faults are injected control-flow
tests and are distinguished from live model outputs. Aggressive fallback removal was
neither requested nor performed.

## Setup and undo

.env.example lists only OPENROUTER_API_KEY and OPENAI_API_KEY placeholders. Supply secrets
privately through the runtime environment; the installed skill's scripts/with_jev_key.py
provides the documented hidden-input launcher (see its --help). Keep the OpenAI key for
production fallback. Validation uses the authorized OpenRouter route only.

After committing, undo the conversion by switching back to the unchanged original branch
and deleting the conversion branch:

```sh
git switch main
git branch -D jev-convert/evaluation
```

The ignored `.jev-validation` directory is local validation tooling and may be deleted
separately if no longer needed. Do not delete the original repository.
