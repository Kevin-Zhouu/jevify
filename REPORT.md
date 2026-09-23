# Jevify — live evaluation in progress

Date: 2026-09-23

The skill and evaluation deliverables are **not complete**. OpenRouter live Jev access and both headless harnesses are now verified. Six DEV workflows and two unread HELD-OUT workflows have been vendored at pinned commits. DEV hand labels, grader, runner, and behavioral smoke checks are prepared. All six DEV baseline smokes and nine grader evidence-check tests pass.

The user authorized isolated HELD-OUT labeling and routing original baseline models through OpenRouter without changing production fallback providers. HELD-OUT labels were sealed by a separate labeling agent; the skill author has not read them. The evaluator, labels, config fixtures and corpus were frozen in commit `2d5bd71` before skill implementation in `489a5b3`.

The portable `skills/jevify/` implementation now exists. Its skill format and Claude plugin/marketplace manifests validate. The hidden-key launcher passes four behavioral tests, including a real terminal echo check; all nine grader self-tests also pass. DEV-01 completed all 24 runs: 9 passed the full grader. Failed outputs and reviews are retained under `eval/results/dev-01/`. DEV-02 completed 24 runs with 14 full passes, including all 12 Codex runs. DEV-03 is a full rerun after further general repairs. Results are not yet complete.

## Preflight results

| Check | Observed result |
| --- | --- |
| Git | Executable available |
| Codex 0.153.4 | Headless prompt returned HEADLESS_OK, exit 0 |
| Claude Code 2.1.89 | After user reauthentication: HEADLESS_OK, exit 0 (3,168 ms) |
| Vercel Jev access | HTTP 403 customer_verification_required; account needs credit-card verification |
| OpenRouter, jev-1.13.0 | HTTP 400: model does not exist |
| OpenRouter, typesafe/jev-1.13-20260917 | HTTP 200; real Choice answer, probabilities, confidence, and usage |

Claude's local auth status reported logged in, but the live request failed after 188,982 ms. Two stripped-down retries timed out at 45 and 50 seconds. The user then reauthenticated; a fresh headless prompt succeeded. This earlier failure was not a skill compatibility result.

OpenRouter's dated model ID appears in its official SDK guide and was echoed by the live response. Keep this provider-specific pin for OpenRouter; the direct TypeSafe spelling is jev-1.13.0. No latest alias or substitute model was used. Vercel version pinning remains unverified because billing blocked the request.

## Evidence and scope

- `eval/preflight/openrouter.json`: observed live request/response with authorization omitted. The synthetic refund input returned billing at confidence 1.0; reported cost was $0.00001323 for 315 input tokens.
- `eval/preflight/harnesses.json`: observed harness result summaries.
- These are preflight records, not full skill-run transcripts or parity tests.
- Supplied keys were not saved in project files. Credential-pattern checks pass.

## Evaluation status

| Required result | Status |
| --- | --- |
| DEV workflow × harness matrix | DEV-01: 9/24; DEV-02: 14/24; DEV-03 running |
| HELD-OUT | Two workflows vendored but unread |
| Frozen grader and preimplementation hand labels | Frozen before skill implementation |
| Gating and output-mode behavior | DEV-02: no preapproval writes; two Claude turns read source too early; three Claude runs fail requested mode |
| Project tests after conversion | All 24 DEV-02 behavioral smokes pass; these examples have no upstream test suite |
| 30+ input parity per converted site | Four Codex DEV-02 conversions independently verified; Claude proxy measurements rejected |
| Negative controls / bad-fit findings | Generation left unchanged; some Claude negative reports/artifact locations incomplete |
| Cross-harness consistency | DEV-02: three discrepancies (omitted wrapper or missing saved audit) |

DEV-01 and DEV-02 completed; DEV-03 is in progress. No HELD-OUT attempt or repair has been used. The single live access probe establishes neither parity nor a recommended confidence threshold.

## Key provisioning

`tools/with_jev_key.py` is a Python 3.10+ launcher supporting TYPESAFE_API_KEY, OPENROUTER_API_KEY, and AI_GATEWAY_API_KEY. It uses an existing environment variable or hidden terminal input, does not save keys, and refuses headless prompting. The caller chooses the provider; no provider is silently switched.

Checks passed for environment forwarding for all three providers and refusal to run a child when its key is missing in headless mode. See `KEY_SETUP.md`. The same launcher is included in the skill.

## DEV results retained so far

Each cell is **headless / interactive**. PASS means all frozen checks plus independent review pass; FAIL remains a failure even if the smoke or numerical parity passes. Original failed outputs are retained, not repaired in place.

### DEV-01

| Workflow | Codex | Claude Code |
|---|---|---|
| anthropic_classification | FAIL / FAIL | FAIL / FAIL |
| vercel_enum | FAIL / FAIL | FAIL / FAIL |
| anthropic_routing | PASS / PASS | FAIL / FAIL |
| vercel_recipe | PASS / PASS | FAIL / FAIL |
| openai_demo | PASS / PASS | PASS / FAIL |
| langchain_completion | PASS / PASS | FAIL / FAIL |

[Full results and reasons](eval/results/dev-01/suite.json).

### DEV-02

| Workflow | Codex | Claude Code |
|---|---|---|
| anthropic_classification | PASS / PASS | FAIL / FAIL |
| vercel_enum | PASS / PASS | FAIL / FAIL |
| anthropic_routing | PASS / PASS | PASS / FAIL |
| vercel_recipe | PASS / PASS | PASS / FAIL |
| openai_demo | PASS / PASS | FAIL / FAIL |
| langchain_completion | PASS / PASS | FAIL / FAIL |

[Full results and reasons](eval/results/dev-02/suite.json).

### Independently valid DEV-02 live parity

| Workflow / Codex scenario | Unique pairs | Threshold | Accepted matches | Fallbacks |
|---|---:|---:|---:|---:|
| Anthropic classification / headless | 38 | .90 | 24/25 (96.0%) | 13 |
| Anthropic classification / interactive | 44 | .90 | 29/31 (93.5%) | 13 |
| Vercel enum / headless | 36 | .90 | 32/33 (97.0%) | 3 |
| Vercel enum / interactive | 36 | .90 | 32/33 (97.0%) | 3 |

These compare raw Jev decisions with the actual original path through the user-authorized same-model OpenRouter transport. Production fallback providers were preserved. Per-run reports include confidence curves, latency and provider-reported cost. For the short Vercel headless cases, estimated cascade cost rose 4.03%; speed does not guarantee savings. Claude runs with real API calls but rewritten proxy baselines/evaluators are NOT accepted as equivalent evidence.

### Bad fits and limitations

- Free-form recipes remain generation even when wrapped in a JSON schema.
- Streaming completion/tutorial and raw-response demos require generated content and provider diagnostics.
- The Anthropic router also prints generated reasoning: replacing only its label without preserving that output is not approved under this scope.
- Small, public/synthetic samples do not establish production robustness, including prompt injection. Confidence is not correctness.
- Examples are pinned source slices with disclosed provenance, not full application deployments. Behavioral smokes exercise their source and fallback contracts; they are not upstream integration suites.
- TypeScript live validation uses compatible AI SDK patch versions where the historical dependency combination fails module loading. Exact historical dependency identity is not claimed.
- Live positive corpus coverage currently exercises Choice, not every Jev primitive or every supported workflow framework.
- Missing Phase0 answers with no authorized destination produce an incomplete plan in the final response, not a file. This preserves the stronger no-writes-before-setup requirement; complete setup with missing approval writes only the headless plan.

## Iterations

- DEV-01: initial skill; 9/24 pass. Found wrong output location, schema omissions and proxy validation.
- DEV-02: added readonly preflight and artifact checks, metadata-adapter rules and actual-source validation guidance; 14/24 pass.
- DEV-03: stronger setup read boundary, negative-output mode handling, wrapper inventory, executable validation wiring and fallback/model logging rules; running.

## Next steps

Finish the DEV loop in both harnesses, run the final HELD-OUT check, and publish the reviewed artifacts. No evaluations or conversion results are claimed before those runs occur.

Sources: [OpenRouter TypeSafe SDK guide](https://openrouter.ai/docs/guides/community/typesafe-sdk), [TypeSafe Models](https://docs.typesafe.ai/models), [official TypeSafe skill](https://github.com/typesafe-ai/skills), [Gateway evaluation implementation](https://github.com/vercel/ai/blob/main/packages/gateway/src/gateway-evaluation-model.ts).
