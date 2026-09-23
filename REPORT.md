# Jevify — evaluation preparation in progress

Date: 2026-09-23

The skill and evaluation deliverables are **not complete**. OpenRouter live Jev access and both headless harnesses are now verified. Six DEV workflows and two unread HELD-OUT workflows have been vendored at pinned commits. DEV hand labels, grader, runner, and behavioral smoke checks are prepared. All six DEV baseline smokes and six grader evidence-check tests pass.

Pending user decisions: isolated blind HELD-OUT labeling, and authorization to route baseline models through OpenRouter for live parity. The grader has not yet been frozen; the skill has not yet been authored, preserving the requested labels-before-skill order. The skill is now named **jevify**, and the user authorized pushing the completed work to https://github.com/Kevin-Zhouu/jevify.git. The remote was empty when checked.

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
| DEV workflow × harness matrix | Not run; corpus assembled and DEV labels prepared |
| HELD-OUT | Two workflows vendored but unread |
| Frozen grader and preimplementation hand labels | Prepared; awaiting sealed HELD-OUT labels and freeze |
| Gating and output-mode behavior | Not tested |
| Project tests after conversion | Not run; no conversions |
| 30+ input parity per converted site | Not run |
| Negative controls / bad-fit findings | Not evaluated |
| Cross-harness consistency | Not evaluated |

No DEV iterations or HELD-OUT repairs have been used. The single live access probe establishes neither parity nor a recommended confidence threshold.

## Key provisioning

`tools/with_jev_key.py` is a Python 3.10+ launcher supporting TYPESAFE_API_KEY, OPENROUTER_API_KEY, and AI_GATEWAY_API_KEY. It uses an existing environment variable or hidden terminal input, does not save keys, and refuses headless prompting. The caller chooses the provider; no provider is silently switched.

Checks passed for environment forwarding for all three providers and refusal to run a child when its key is missing in headless mode. See `KEY_SETUP.md`. This is preparatory tooling, not the completed converter skill.

## Next steps

Resolve the two evaluation decisions, seal HELD-OUT labels, freeze the grader, author skills/jevify, run the DEV loop in both harnesses, run the final HELD-OUT check, and publish the reviewed artifacts. No evaluations or conversion results are claimed before those runs occur.

Sources: [OpenRouter TypeSafe SDK guide](https://openrouter.ai/docs/guides/community/typesafe-sdk), [TypeSafe Models](https://docs.typesafe.ai/models), [official TypeSafe skill](https://github.com/typesafe-ai/skills), [Gateway evaluation implementation](https://github.com/vercel/ai/blob/main/packages/gateway/src/gateway-evaluation-model.ts).
