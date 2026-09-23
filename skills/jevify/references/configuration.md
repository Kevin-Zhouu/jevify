# Setup, approval and headless configuration

The same conversational workflow runs in Codex and Claude Code. Accept explicit invocation arguments (e.g. `output=branch branch=jev-convert/trial provider=openrouter risk=conservative approve=fallback:src/route.ts:42`) or a named `jevify.config.yaml`. Treat arguments as answers, not shell code. Parse normal YAML using the agent's reading ability; no YAML dependency is required. JSON is also valid YAML 1.2. Never execute config contents. A config is trusted only when supplied or explicitly designated by the user.

Example (no secret values):

```yaml
output:
  mode: branch                 # branch | clone | report
  branch: jev-convert/trial    # required for branch; suggest but never silently choose
  # clone_path: ../project-jev # required for clone; must not exist
access:
  provider: openrouter        # typesafe | openrouter | vercel | none
  key_env: OPENROUTER_API_KEY
  model: typesafe/jev-1.13-20260917
risk: conservative            # conservative | aggressive
headless: true
approval:
  sites:
    src/route.ts:42: fallback # fallback | jev_only | decompose | router | leave
validation:
  inputs: tests/route-cases.json
  baseline_routing_authorized: false
```

Instead of `approval.sites`, accept a bounded predicate:

```yaml
approval:
  actions: [fallback]
  scope: Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged. Preserve all externally observable fields.
```

Resolve approval before editing: predicates do not override jaggedness, contract preservation, output mode, or the requirement to prove Jev-only parity. Multiple actions without a clear selection are ambiguous; ask interactively or stop headlessly. `accept_all` only refers to a concrete previously presented plan, never options the user has not seen. Approval does not authorize provider switches or push.

## Missing answers

Interactive: ask missing Phase 0 answers and end the turn. No deeper reads or writes. After complete setup, audit, present Phase 2, and wait; no files yet.

Headless: never ask a tool that cannot receive a reply, never choose defaults. Missing Phase 2 approval with complete setup: audit and stop after Phase 2, writing only `JEV_CONVERSION_PLAN.md` as the explicit headless exception to the interactive no-write rule. Use a user-specified report destination; if none, the original repo plan path is the documented headless plan artifact. Do not create a branch/clone before approval just to store a plan.

Missing Phase 0: do not deep-audit a repo without setup. Emit an incomplete Phase 2 plan in the final response containing unanswered fields and the resumption command. If an explicit report destination was supplied, save this plan there; otherwise no filesystem writes before Phase 0. This resolves the conflict between “plan written” and “no writes before setup” without guessing an output location. Report the limitation clearly.

If no credentials: `provider: none` is a valid answer, not a blocker to an approved conservative conversion. Emit code with a configured but unset key variable, preserve fallback, record validation skipped. Do not set `live: true` or fabricate metrics.

## Output lifecycle

Read-only preflight checks git and cleanliness, `git check-ref-format --branch NAME` and existing refs, or clone path existence. Existing artifacts from a prior invocation are not permission to overwrite them. Resume an explicitly identified plan only after checking its source revision and scope still match.

After approval only:
- Branch: record original ref/SHA; `git switch -c NAME`; commit only approved files. Original branch ref remains unchanged.
- Clone: `git clone --no-hardlinks SOURCE DEST` from a clean repo into the unused path, then operate only there. Do not stash, checkout, install, or write in the source. Record source SHA and destination. A requested new hosted repo requires separate explicit remote creation authorization.
- Report: stay on the original branch; only plan, audit and final report artifacts may be written. No .env, dependency changes, commits or code changes. Running existing tests after approval is fine if they do not modify tracked code; disclose generated test output.

Do not alter global git settings. Use the existing author identity; if unavailable, save changes and report commits blocked rather than inventing an identity.
