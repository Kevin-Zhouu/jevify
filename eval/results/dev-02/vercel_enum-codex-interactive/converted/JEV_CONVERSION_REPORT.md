# Conversion and validation report

Approved `fallback` conversion completed for original site `workflow.ts:6` in the clone `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/vercel_enum-codex-interactive/converted`, branch `jev-convert/evaluation`. Source revision: `6013ff5396ee175c76aa5feddd7e93d903e667a7` (`main`). Original repository untouched. No push or PR.

Scope: one pure DECISION call; all other actions declined. No other workflow sites exist. `jevDecisions.ts` owns the Choice, five criteria, version pin, confidence gate, timeout, state bound and usage adapter. The original OpenAI `gpt-4o-mini` call, structuredOutputs setting, enum, prompt, output parser and error handler remain in the fallback. No production provider switch. New stderr path/model/reason logging contains no inputs or secrets. No Jev SDK dependency is needed; Node fetch is used. Validation-only dependencies are pinned under `validation/` because the upstream fixture has no manifest or test command.

The four stdout calls and their order remain intact. Jev usage maps actual input/output counts into promptTokens/completionTokens/totalTokens. `finishReason: 'stop'` is adapter-owned successful decision completion, not a native Jev termination field. Missing/invalid usage, wrong model, invalid labels/confidence/distribution, timeout (5 seconds), rate limit, transport failure, missing key or unsupported state invokes the original callable exactly once. Original exceptions propagate unchanged. Input is the original benign fixed plot; an 8000-character bound is not a prompt-injection defense and this conversion is not qualified for arbitrary hostile input.

## Live evidence (2026-09-23)

36 unique paired requests: one repository plot and 35 labeled synthetic cases, spanning all five genres, ambiguity, boundaries and out-of-domain films. Cases are in `validation/run.cjs`. First 16 are calibration, remaining 20 are fresh confirmation; confidence 0.9 was fixed before all measurements and was not tuned after seeing results. The groups are deliberately uneven in difficulty, so do not interpret their difference as statistical drift.

The evaluation imports and invokes the actual production evaluator and gate. An assertion captures SDK options from the original source revision and converted entrypoint and proves equality. The original `generateObject` and its enum parser execute using AI SDK 4.3.19 / OpenAI provider 1.3.24. The isolated, authorized transport forwards the same SDK request to OpenRouter, changing only endpoint, credentials and model namespace to `openai/gpt-4o-mini`. Synthetic cases replace only the plot inside the original prompt template. SDK retries are disabled for bounded evaluation; production defaults are unchanged. Upstream did not include a dependency lock, so the historical exact SDK version cannot be established from this repository.

All 36 live Jev requests used `typesafe/jev-1.13-20260917`. Real request IDs, sanitized bodies, usage, provider-reported `usage.cost`, original outputs and raw Jev decisions are in `JEV_PARITY.json`. No fallback outputs are passed off as raw Jev answers. No transport failures occurred. Original and Jev latency use monotonic timers. Cascade metrics below are estimates combining the paired timings/costs, not separate live production cascade timing. Live low-confidence fallback invoked a callback returning the already measured original result to avoid charging for duplicate baseline inference.

| Measure | All 36 | Confirmation 20 |
|---|---:|---:|
| Raw agreement | 32/36 (88.9%) | 16/20 (80.0%) |
| Accepted at 0.9 | 33 | 17 |
| Accepted agreement | 32/33 (97.0%) | 16/17 (94.1%) |
| Fallback fraction | 3/36 (8.3%) | 3/20 (15.0%) |
| Jev latency p50 / p95 | 330 / 563 ms | 330 / 406 ms |
| Original latency p50 / p95 | 902 / 1955 ms | 806 / 1749 ms |

Calibration: 16/16 accepted and matching. All four disagreements remain visible: robber/action vs drama (0.76), alien detective/sci-fi vs comedy (0.83), shelf tutorial/drama vs comedy (0.80), concert/drama vs action (1.0). The last remains accepted even at confidence 1. This is model agreement, not independent ground-truth accuracy; out-of-domain inputs must still choose one of the original five labels.

| Confidence threshold | Accepted / 36 | Accepted agreement | Fallback fraction |
|---|---:|---:|---:|
| 0, 0.5, 0.7 | 36 | 88.9% | 0% |
| 0.8 | 35 | 91.4% | 2.8% |
| **0.9** | **33** | **97.0%** | **8.3%** |
| 0.95 | 33 | 97.0% | 8.3% |
| 1.0 | 29 | 96.6% | 19.4% |

Per-site recommendation: retain 0.9 with conservative original fallback. Accepted agreement exceeds the skill's 90% criterion on confirmation, but this small synthetic suite does not establish universal parity. No Jev-only conversion is authorized or recommended. Confidence does not eliminate confident disagreements.

Mean provider-reported Jev cost: $0.0000146825; original: $0.00001495. Expected cascade cost = Jev + fallback-weighted original = $0.00001592 per input, **6.5% higher** than original. No cost savings demonstrated. Mean expected serial cascade latency: 434 ms versus original 1100 ms, about 60.5% lower. Confirmation-only estimated cost is 13.1% higher. These measurements use the authorized evaluation route, not direct OpenAI production routing; cost/latency may differ there. No token-price assumptions or unknown-zero substitutions were used.

## Checks and reproduction

From the clone, with credentials supplied only via runtime environment:

```sh
npm ci --prefix validation --ignore-scripts --no-audit --no-fund
node validation/run.cjs
node validation/replay.cjs
/opt/homebrew/opt/python@3.14/bin/python3.14 validation/summarize.py
./validation/node_modules/.bin/tsc -p validation/tsconfig.json
node '/Users/bigsoup/Downloads/Jev Converter/eval/smoke.cjs' "$PWD" vercel_enum
/opt/homebrew/opt/python@3.14/bin/python3.14 .agents/skills/jevify/scripts/check_artifacts.py "$PWD" --require-live
```

Executed: supplied smoke passed; strict typecheck passed; captured original/converted option equality and complete fallback stdout passed. Actual timeout abort, HTTP 429, generic transport error, malformed response and missing key tests passed with sentinel identity and exactly one original invocation, including original exception identity. Pure gate boundaries and mutated genuine response tests exercised low confidence, NaN, boolean confidence, unknown label, missing/negative/nonfinite usage and wrong model. Accepted stdout replay used an actual captured Jev response; no successful model answer was fabricated. Full confidence curves, fault results and reproducible metric computation are included. Artifact shape validation passed; this is a structural check, not proof of the claims by itself.

Setup placeholders: `.env.example` names `OPENROUTER_API_KEY` and the unchanged fallback's `OPENAI_API_KEY`. Keep real values in runtime environment; the installed skill's `scripts/with_jev_key.py --help` describes its hidden-input launcher. No credentials were printed or saved.

Current docs read: [API](https://docs.typesafe.ai/api), [Choice](https://docs.typesafe.ai/primitives/choice), [models](https://docs.typesafe.ai/models), [confidence](https://docs.typesafe.ai/confidence), building guide, coding-agents, all four patterns, hierarchical classification cookbook, [Jev limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13), and [OpenRouter contract](https://openrouter.ai/docs/guides/community/typesafe-sdk). Markdown pages unavailable in the browser tool were fetched successfully with Python HTTPS.

Undo: the original directory and `main` remain unchanged. Delete only `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/vercel_enum-codex-interactive/converted` to discard this clone and its local conversion branch. No remote cleanup is required.
