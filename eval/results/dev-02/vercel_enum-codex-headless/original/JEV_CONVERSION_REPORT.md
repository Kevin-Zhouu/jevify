# Jev conversion report

Converted the single approved DECISION site, original ID `workflow.ts:6`, on branch `jev-convert/evaluation`. Source revision: `6013ff5396ee175c76aa5feddd7e93d903e667a7` (`main`). Output: `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/vercel_enum-codex-headless/original`. The configured sibling clone destination was inactive and was not used.

Config approval: only pure enumerated DECISION sites, action fallback, conservative risk, preserve observable fields. No other sites exist. No push or PR. All retained original behavior includes model `gpt-4o-mini`, `structuredOutputs: true`, enum, exact prompt bytes, stdout labels/order and top-level error handling. Real Jev token usage maps to the three printed token fields; generic `stop` means completed decision in this adapter, not native token termination. Stderr identifies answer path/model with bounded reasons, without inputs or secrets.

## Changes and setup

`jevDecisions.ts` owns the Choice, pinned OpenRouter model `typesafe/jev-1.13-20260917`, 0.9 gate, 5-second timeout and 8000-byte bound. `workflow.ts` wraps its unchanged original provider call. `.env.example` contains only empty placeholders. `JEV_AUDIT.json` inventories the original site and resolved conversion; the plan records options and preflight.

Set `OPENROUTER_API_KEY` privately for Jev and `OPENAI_API_KEY` for the original production fallback. The skill's `.agents/skills/jevify/scripts/with_jev_key.py --help` describes its hidden-input launcher. Node 18+ built-in fetch is used; no production SDK dependency added. Production execution still needs the original example's AI SDK/OpenAI provider/dotenv setup.

Validation-only locked dependencies are under `validation/`; install with `npm ci --prefix validation --ignore-scripts`. The inherited SDK installation could not load due to an incompatible Zod export. AI SDK 4.3.19 / OpenAI provider 1.3.24 reproduce this example's interface. No upstream lockfile was supplied, so exact historical dependency identity is not asserted.

## Executed validation

- Independent smoke: `node /Users/bigsoup/Downloads/Jev Converter/eval/smoke.cjs "$PWD" vercel_enum` — PASS.
- Live pairs and fault assertions: `node validation/check.cjs --live` — completed 36 unique pairs with real provider IDs, usage and provider-reported cost.
- TypeScript: `node validation/node_modules/typescript/bin/tsc --noEmit --strict --target ES2022 --module commonjs --lib ES2022,DOM jevDecisions.ts` — PASS.
- `git diff --check` — PASS.
- Artifact checker command: `/opt/homebrew/opt/python@3.14/bin/python3.14 .agents/skills/jevify/scripts/check_artifacts.py . --require-live` — PASS (`shape_valid: true`; shape check is not proof of model correctness).

The harness executes the original source from git with the real AI SDK, replacing only the fixed plot fixture and exporting main inside the isolated VM. The authorized adapter sends the SAME model through OpenRouter, retaining structured-output schema generation and SDK output parsing. It maps the model namespace to `openai/gpt-4o-mini` and disables SDK retries for bounded evaluation. Production fallback remains direct OpenAI. Exact original versus converted callable options and stdout are asserted with original-provider doubles. No successful Jev inference is fabricated: accepted diagnostic tests replay a captured live response, and malformed variants are explicitly fault injections.

Executed failure assertions cover timeout, HTTP 429, HTTP 503, generic transport error, invalid JSON/schema, missing key, low/nonfinite/out-of-range confidence, unknown enum, invalid model/probabilities/usage. Original fallback runs exactly once; original exceptions propagate by identity without retry. These are control-flow tests, not parity measurements. Direct OpenAI transport was not live-tested; the baseline route was the expressly authorized OpenRouter adapter.

## Live evidence and threshold recommendation

`JEV_PARITY.json` contains all raw paired decisions before fallback, request IDs, sanitized original request bodies, actual Jev responses, costs and monotonic timings. Inputs: one repository plot, 35 predeclared synthetic benign English plots spanning genres, ambiguity, minimal and out-of-domain text. Alternating split declared before measurement: 18 calibration, 18 confirmation. The threshold was fixed before calls and never tuned using confirmation results.

Raw agreement: 34/36 (94.44%). At threshold 0.9: accepted agreement 32/33 (96.97%); fallback 3/36 (8.33%). Calibration accepted agreement 17/17; confirmation 15/16 (93.75%). Keep **0.9 with conservative fallback** for this example; this small synthetic check exceeds the skill's 90% accepted-agreement target but does not establish general production reliability. Do not remove fallback. A threshold of 1.0 appears stronger on this sample but has not been independently selected and confirmed, so it is not adopted.

| Threshold | Accepted | Accepted agreement | Fallback fraction |
|---|---:|---:|---:|
| 0 | 36 | 94.44% | 0.00% |
| 0.5 | 36 | 94.44% | 0.00% |
| 0.7 | 34 | 97.06% | 5.56% |
| 0.8 | 34 | 97.06% | 5.56% |
| 0.9 | 33 | 96.97% | 8.33% |
| 0.95 | 32 | 96.88% | 11.11% |
| 1 | 29 | 100.00% | 19.44% |

Disagreements (none omitted):

- An astronaut in a failing spaceship hears a terrifying voice from outside. Jev: `sci-fi`; original: `horror`; confidence 0.68; fallback True.
- A chef prepares a meal with ingredients from the garden. Jev: `drama`; original: `comedy`; confidence 0.95; fallback False.

Jev latency p50/p95: 325.7/403.8 ms. Original p50/p95: 865.2/1775.1 ms. Estimated serial cascade mean: 463.7 ms, calculated per pair as Jev latency plus original latency only when fallback is taken. This is an estimate assembled from paired calls, not independently measured end-to-end cascade traffic.

Provider-reported mean costs: Jev $0.0000143885; original $0.0000150333; estimated cascade $0.0000156385. Cascade is 4.03% more expensive on these short inputs. No savings claim: accepting Jev avoids generation latency, but request overhead and serial fallbacks erase the small per-call cost benefit. Costs use actual usage.cost returned by OpenRouter on 2026-09-23, not pricing estimates. Both models were measured on the same gateway route; timings are not a comparison against direct production OpenAI networking.

## Limitations and undo

Scope remains the fixed benign example. No effective public-input prompt-injection defense was present or added; confidence and length bounds do not provide one. Small synthetic samples and shared model errors limit what agreement proves. Finish status adaptation preserves generic completion semantics only. No native Jev termination metadata is invented.

To undo tracked changes, run `git switch main` then `git branch -D jev-convert/evaluation`. Original main remains at the source revision. The ignored local `validation/node_modules` installation is not removed by switching branches; it may be deleted separately if no longer needed. Never delete broader dependency directories.
