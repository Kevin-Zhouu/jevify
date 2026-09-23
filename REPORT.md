# Jevify — live evaluation in progress

Date: 2026-09-23

The skill and evaluation deliverables are **not complete**. OpenRouter live Jev access and both headless harnesses are now verified. Six DEV workflows and two unread HELD-OUT workflows have been vendored at pinned commits. DEV hand labels, grader, runner, and behavioral smoke checks are prepared. All six DEV baseline smokes and nine grader evidence-check tests pass.

The user authorized isolated HELD-OUT labeling and routing original baseline models through OpenRouter without changing production fallback providers. HELD-OUT labels were sealed by a separate labeling agent; the skill author has not read them. The evaluator, labels, config fixtures and corpus were frozen in commit `2d5bd71` before skill implementation in `489a5b3`.

The portable `skills/jevify/` implementation now exists. Its skill format and Claude plugin/marketplace manifests validate. The hidden-key launcher passes four behavioral tests, including a real terminal echo check; all nine grader self-tests also pass. DEV-01 completed all 24 runs: 9 passed the full grader. Failed outputs and reviews are retained under `eval/results/dev-01/`. DEV-02 is a full rerun after general instruction/helper repairs. Results are not yet complete.

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
| DEV workflow × harness matrix | DEV-01: 9/24 pass; DEV-02 running |
| HELD-OUT | Two workflows vendored but unread |
| Frozen grader and preimplementation hand labels | Frozen before skill implementation |
| Gating and output-mode behavior | Not tested |
| Project tests after conversion | Not run; no conversions |
| 30+ input parity per converted site | Not run |
| Negative controls / bad-fit findings | Not evaluated |
| Cross-harness consistency | Not evaluated |

DEV-01 completed; DEV-02 is in progress. No HELD-OUT attempt or repair has been used. The single live access probe establishes neither parity nor a recommended confidence threshold.

## Key provisioning

`tools/with_jev_key.py` is a Python 3.10+ launcher supporting TYPESAFE_API_KEY, OPENROUTER_API_KEY, and AI_GATEWAY_API_KEY. It uses an existing environment variable or hidden terminal input, does not save keys, and refuses headless prompting. The caller chooses the provider; no provider is silently switched.

Checks passed for environment forwarding for all three providers and refusal to run a child when its key is missing in headless mode. See `KEY_SETUP.md`. The same launcher is included in the skill.

## Next steps

Finish the DEV loop in both harnesses, run the final HELD-OUT check, and publish the reviewed artifacts. No evaluations or conversion results are claimed before those runs occur.

Sources: [OpenRouter TypeSafe SDK guide](https://openrouter.ai/docs/guides/community/typesafe-sdk), [TypeSafe Models](https://docs.typesafe.ai/models), [official TypeSafe skill](https://github.com/typesafe-ai/skills), [Gateway evaluation implementation](https://github.com/vercel/ai/blob/main/packages/gateway/src/gateway-evaluation-model.ts).
