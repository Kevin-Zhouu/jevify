# Jev conversion report

Approved fallback conversion completed for workflow.ts:6 in the sibling converted clone, branch jev-convert/evaluation. Original source revision: 4bc5e23750b6af7d32147d2480a5bde33bb935cb (main); original repository unchanged. No push or PR. User approved only pure enumerated DECISION fallback; all other options declined. Only one inference site exists, so no unrelated sites changed.

## Behavior

workflow.ts retains its byte-identical original generateObject options, OpenAI gpt-4o-mini model/settings, five labels, prompt, downstream console calls and error handler. The new wrapper attempts OpenRouter typesafe/jev-1.13-20260917 and retains original OpenAI fallback at confidence below 0.9 or any validation/transport failure. All policy resides in jevDecisions.ts. There is one Jev request, no retries, and a 10-second timeout through body parsing. Original exceptions propagate without a second original call. Structured path/model/reason diagnostics use stderr and exclude inputs and secrets.

Accepted results preserve the externally consumed object, usage and finishReason fields. Usage maps actual Jev input/output tokens to promptTokens/completionTokens, with totalTokens computed by addition. finishReason 'stop' is explicitly an adapter-owned completed-decision status, not a native Jev generation/stop-sequence claim. Original fallback metadata is returned unchanged. No arbitrary SDK envelope fields were previously exposed outside main.

## Executed validation

- Independent supplied smoke: `node '/Users/bigsoup/Downloads/Jev Converter/eval/smoke.cjs' '/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/vercel_enum-codex-interactive/converted' vercel_enum` — PASS.
- `npm run typecheck` in converted — PASS after correcting wrapper contextual types.
- `npm run validate` in converted — PASS: 30 actual live pairs, source identity, all four stdout calls, zero/one original calls, actual SDK parsing, accepted response replay and forced faults. Sanitized transcript: validation/results.log.
- `node validation/replay.cjs` — PASS: final module replay, namespace-only request transformation assertion, NaN/Infinity/boolean/out-of-range confidence, and real 10-second body-read timeout; result in validation/replay-results.log.
- Artifact checker with `--require-live` — PASS; result in validation/artifact-check.json. It checks evidence shape, not truth.

Source identity proof compares the full original entrypoint from git after undoing only wrapper wiring, and compares the exact request object expression. Each case executes that original source; an AST edit replaces only the fixed plot literals while retaining the prefix and quote framing. A recording SDK boundary captures real options. The real AI SDK generateObject call and parser execute them with the user's authorized OpenRouter transport/auth and same-model namespace adaptation to openai/gpt-4o-mini. Evaluation disables SDK retries and bounds request time; production fallback remains unchanged. Each converted entrypoint calls the actual decisions module exactly once; its captured raw response supplies the paired row. Fallback outputs never replace raw Jev answers in agreement calculations.

## Live results

Measured 2026-09-23T03:36:46.182Z; all 30 unique inputs are clearly labeled synthetic. They cover five genres, ambiguous mixed genres, an out-of-set documentary and an abstract film. The repository contains only one fixed plot. Threshold 0.9 was frozen before this confirmation set; zero calibration samples, no post-result retuning. Small benign synthetic sample; not production assurance or adversarial testing.

Raw agreement: 29/30 (96.7%). Accepted agreement at deployed threshold: 27/27 (100%); fallback: 3/30 (10%). The one raw disagreement remains in JEV_PARITY.json and was rejected by the gate. This meets the skill's 90% selective-agreement target on this sample.

| Threshold | Accepted | Accepted agreement | Fallback fraction |
|---|---:|---:|---:|
| 0 | 30 | 96.7% | 0.0% |
| 0.5 | 28 | 100.0% | 6.7% |
| 0.7 | 28 | 100.0% | 6.7% |
| 0.9 | 27 | 100.0% | 10.0% |
| 0.95 | 27 | 100.0% | 10.0% |
| 1 | 26 | 100.0% | 13.3% |

Jev request latency p50/p95: 337.7/487.8 ms. Original SDK latency p50/p95: 898.8/1614.1 ms. Jev timing includes network and captured response-body read; original timing includes SDK parsing. Expected serial cascade mean: 462.8 ms versus original mean 1080.4 ms. This cascade estimate sums measured Jev latency and original latency only for fallback rows; it is not an independently timed production deployment.

Provider-reported usage.cost, not estimated token prices, supplies all row costs. Mean original cost: $0.00001525; expected cascade cost: $0.00001603 per input, 5.1% higher. No cost-savings claim. These very short prompts favor the original's low token count; Jev question overhead plus fallback cost offsets avoided original calls. Results are specific to these requests and billing at measurement time.

Recommended threshold for workflow.ts:6: retain 0.9 provisionally with conservative fallback. It passed this confirmation set; gather representative real inputs before broader use. Confidence is not correctness or a defense against malicious instructions. The production fixture is benign, and no public-input deployment is claimed.

Executed injected faults: below-threshold confidence mutated from a real response, generic transport error, abort timeout, real HTTP 429, malformed container, missing key, unknown option, missing/array usage, wrong model, and invalid confidence. Each verifies exactly one fallback call and original exception identity. Accepted-path tests use genuine captured live responses. The replay test separately exercises nonfinite JS numbers and body-read timeout. These are control-flow tests, not inference measurements.

## Dependencies, setup and limitations

Upstream supplied no package manifest/test suite. Existing ambient ai 4.3.16 and @ai-sdk/openai 1.3.22 had an incompatible zod dependency; initial validation could not import the SDK. The clone now pins those same SDK versions, compatible zod 3.25.76, dotenv, TypeScript/tsx and Node types in package.json/package-lock.json. No Jev SDK dependency is needed; the adapter follows the documented HTTP API with Node fetch. Run npm ci (Node 18+), populate runtime OPENROUTER_API_KEY and OPENAI_API_KEY using .env.example names, and npm start. Never put real values in committed files. The original production fallback still needs OPENAI_API_KEY; only live evaluation was authorized to use OpenRouter for the original model.

For hidden key entry, use the original installed skill's `.agents/skills/jevify/scripts/with_jev_key.py --help` and its launcher; do not put keys in shell command arguments. No credential values were printed or saved. No source/dependency/corpus inspection outside the permitted repository was used; the supplied smoke file was read but never edited. Installed package APIs were executed as dependencies.

Docs: [HTTP API](https://docs.typesafe.ai/api), [OpenRouter route and metadata](https://openrouter.ai/docs/guides/community/typesafe-sdk), [confidence](https://docs.typesafe.ai/confidence), [limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13). Required models, Choice, coding-agents, patterns and relevant classification cookbook were consulted. Markdown web fetches failed; normal pages and direct fetch resolved access, including the building guide. No provider/model substitution was made.

## Artifacts and undo

JEV_CONVERSION_PLAN.md records audit/options/selection/preflight and validation wiring. JEV_AUDIT.json identifies only original workflow.ts:6 as converted. JEV_PARITY.json contains real IDs, model pins, answers, probabilities, usage, costs, timing, request body (no headers), synthetic inputs, original outputs and fault results. validation/ holds reproducible scripts and sanitized execution logs.

Undo by deleting only `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/vercel_enum-codex-interactive/converted`; the original remains on main and unchanged. No remote changes exist.
