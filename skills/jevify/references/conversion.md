# Conversion contracts

Read the official skill and the appropriate API/SDK references, not remembered API shapes. Vendored `official/` files are unchanged upstream snapshots with hashes in SOURCES.json. Check live docs for changes; do not change the selected version pin silently. Official SDK packages are `typesafe_sdk` and `@typesafe-ai/sdk`. Use the codebase's language, style, dependency manager and env conventions. For a dependency-free example, a small HTTP adapter using Python standard library or Node 18 fetch is acceptable when built from the official API contract. Do not add a framework just to convert one call.

## Reviewable decisions

One `jev_decisions.py` / `jevDecisions.ts` per language owns ALL Jev model IDs, question instructions, criteria, option mappings, score levels, thresholds, state bounds and gate policy. Call sites supply runtime state and the original callable. If the project uses JS, use an equivalent single JS module and report the name. Validation imports that same module; never maintain a separate Jev prompt or model pin in the parity script. No duplicated question definitions in tests.

Choice handles one closed label, Score ordered descriptive levels; Noul returns yes probability with NO confidence. For Noul use an explicit abstention band and report probability versus agreement (never fabricate a confidence field). If confidence gating is required, a two-option Choice may be more suitable. Compute weighted scores, date comparisons, counts and exact rules in code. Multiple independent questions may share one request; a later question cannot see an earlier answer in the same request. Filter irrelevant state before calling; oversize/unsupported input takes the original path.

## Preserve behavior

Capture baseline function signature, sync/async behavior, return type, parsed value, public fields, side effects, logs and error semantics. Do not replace a synchronous API with an async one. Keep fallback code/prompt/model/output parsing unchanged unless separately approved. Avoid importing a new optional SDK at module load in a way that prevents fallback when the key/package is missing.

For confidence below the chosen threshold, nonfinite/out-of-range confidence, unknown labels, invalid schema, missing credentials, network errors, timeout, HTTP 429 and server errors: call original exactly once and return its result. Set a bounded Jev timeout; avoid SDK retries that silently multiply latency. Do not catch an original-path exception and retry the original again. Log only path (`jev` or `original`), answering model/version and a bounded reason. Never log keys, headers or raw input, and do not change stdout contracts—prefer the project's logger/stderr.

Token usage and finish reasons are observable if returned or printed. Preserve their shape using real Jev usage and documented adapter semantics; never copy original-model token numbers onto Jev or invent usage. If a faithful mapping is impossible, leave the site unchanged and explain why; do not delete the diagnostics to get a passing test. Do not fabricate reasoning to preserve a MIXED call: retain the original generated component unless the user approves changing that contract.

Aggressive Jev-only still needs an explicit failure policy approved by the user; do not remove fallback before parity has passed on an independent check set. Conservative approval never permits removal. New decomposition/router behavior must be included in the selected option, not slipped into a generic fallback migration.

## Provider and credentials

Use the user-selected provider and credential variable. TypeSafe direct uses the versioned `jev-1.13.0`. OpenRouter has a distinct versioned catalog ID: `typesafe/jev-1.13-20260917`, verified for this release. Its System One route is `https://openrouter.ai/api/v1/systemone`; consult https://openrouter.ai/docs/guides/community/typesafe-sdk and official SDK configuration to avoid doubling `/v1` (SDK base `https://openrouter.ai/api`). A model-not-found response must not trigger trying another provider/model automatically.

Vercel AI Gateway supports Jev evaluation models, but an unversioned `typesafe-ai/jev` alias is not acceptable for a pinned conversion or evaluation. Verify a supported versioned route through current docs/live request first; if unavailable, report unsupported pinning and ask for TypeSafe/OpenRouter access rather than switching. Do not send a gateway key to another endpoint.

Add only the needed variable names/placeholders to `.env.example` (or equivalent). Keep actual secrets in runtime env or a user-approved ignored local secret store. Explain setup using `scripts/with_jev_key.py`. Do not read/print an entire env or secret file. Do not switch the original fallback provider because only a Jev key is available. An explicitly authorized baseline gateway route belongs in an isolated evaluation adapter, not production code.

Commit after approved output setup: e.g. plan, conversion, measured validation. Use specific paths in `git add` after reviewing the diff; exclude secrets, dependencies/caches, unrelated edits and live private data. Never push or create a PR without explicit authorization.
