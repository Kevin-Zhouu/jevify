# Jevify — implementation published; evaluation stopped

Date: 2026-09-23. **The requested cross-harness proof is incomplete.** The portable `skills/jevify/` skill, key-entry launcher, pinned corpus, frozen grader, labels, configs and retained transcripts are published. This is not a claim that the skill works identically in Codex and Claude Code.

The required stop condition was reached during DEV03: Claude Code began exiting headless runs with **“You're out of extra usage · resets 3:40pm (Australia/Melbourne)”**. No further evaluations were started after identifying the blocker. HELD-OUT remains unopened by the skill author and untested; no held-out repair round has been used.

DEV01 completed with **9/24** full passes; DEV02 improved to **14/24**. DEV03 has **12 completed passes, 3 completed failures, and 9 quota-blocked runs**. All 12 Codex runs passed in both DEV02 and DEV03. Completed Claude conversions still have substantive validation failures, independently of the usage limit.

## What is delivered

- [Portable skill](skills/jevify/SKILL.md): staged setup, read-only audit, selectable options and approval gate, scoped conversion, validation and reports. Detailed rules live in references. One folder is used in both harnesses.
- [Credential setup](KEY_SETUP.md): hidden terminal input or existing environment, never secret values in config. The launcher supports `TYPESAFE_API_KEY`, `OPENROUTER_API_KEY` and `AI_GATEWAY_API_KEY`. Approved no-key code is permitted with live validation explicitly skipped.
- [Install guide](skills/jevify/INSTALL.md): Codex project/personal paths, Claude Code project/personal paths, marketplace manifest and `npx skills add`.
- [Pinned corpus](corpus/README.md): six DEV and two HELD-OUT workflows from Anthropic's cookbook, Vercel AI SDK and OpenAI Python SDK. Exact source slices, upstream commits and licenses are recorded per fixture.
- [Evaluation protocol](eval/README.md), [hand labels](eval/labels/), [frozen manifest](eval/FROZEN.json), [iteration log](eval/ITERATIONS.md), [change log](eval/CHANGELOG.md), and [all exported evidence](eval/results/).
- [Draft repairs](eval/proposed-repairs/README.md): prepared before the usage-limit stop, not installed in the skill and not claimed as evaluated improvements.

The official TypeSafe skill and API/primitive references are vendored unchanged at commit `65a39f393687675ce170e6094757de20370365b9`, with hashes and upstream licensing in [SOURCES.json](skills/jevify/references/official/SOURCES.json). Live documentation remains authoritative; these are not rewritten API docs.

## Protocol and provenance

The evaluator, DEV labels, sealed HELD-OUT labels, config fixtures and corpus were frozen in commit `2d5bd71` **before** initial skill implementation in `489a5b3`. Skill revisions tested were DEV01 `489a5b3`, DEV02 `a33081d`, and DEV03 `dfd9854`. Frozen-file hashes still match; no corpus edits or threshold changes were used to improve scores.

The user authorized a separate agent to label HELD-OUT and keep its findings sealed. The author has not read its source or labels. [HELDOUT_STATUS.json](eval/HELDOUT_STATUS.json) records the sealed label hash and zero attempts. Automated integrity hashes do not expose source semantics.

Every DEV iteration attempted all six workflows in both harnesses, headless and through three simulated interactive CLI turns: unanswered setup, setup supplied without approval, and bounded approval. Separate git repositories, byte snapshots, filesystem timestamps, continuous mutation observations, original refs, git logs and local bare remotes establish ordering/isolation/no push. Positive cases use branch headlessly and clone interactively; other cases exercise report and branch modes. Simulation uses real CLI turns with scripted user answers, not a human UI session.

Both harnesses initially passed live headless probes. Codex 0.153.4 and Claude Code 2.1.89 used their configured models; no model substitution was used to impersonate either harness. The later Claude quota failure is an infrastructure blocker, not a conversion success.

The frozen grader checks artifacts plus explicit independent source/evidence review. **Its raw DEV03 artifact score is 13/24**, because one quota-interrupted routing report has sufficient artifacts. That run is still BLOCKED in the completion table below; a successful artifact grade does not erase a failed CLI run. This distinction is recorded without changing the grader. Exported evidence omits embedded git databases and dependency caches; before/after hashes and git logs are retained, and skill versions are preserved in root git history.

## Per-workflow × per-harness results

H = headless; I = simulated interactive. PASS means the completed run meets every frozen check and independent review. FAIL means substantive requirements remain unmet. BLOCKED means Claude quota interrupted or prevented completion; any partial artifacts and defects remain visible. Each result links to its review.

### DEV-01

| Workflow | Codex H / I | Claude Code H / I |
|---|---|---|
| anthropic_classification | [FAIL](eval/results/dev-01/anthropic_classification-codex-headless/REVIEW.md) / [FAIL](eval/results/dev-01/anthropic_classification-codex-interactive/REVIEW.md) | [FAIL](eval/results/dev-01/anthropic_classification-claude-headless/REVIEW.md) / [FAIL](eval/results/dev-01/anthropic_classification-claude-interactive/REVIEW.md) |
| vercel_enum | [FAIL](eval/results/dev-01/vercel_enum-codex-headless/REVIEW.md) / [FAIL](eval/results/dev-01/vercel_enum-codex-interactive/REVIEW.md) | [FAIL](eval/results/dev-01/vercel_enum-claude-headless/REVIEW.md) / [FAIL](eval/results/dev-01/vercel_enum-claude-interactive/REVIEW.md) |
| anthropic_routing | [PASS](eval/results/dev-01/anthropic_routing-codex-headless/REVIEW.md) / [PASS](eval/results/dev-01/anthropic_routing-codex-interactive/REVIEW.md) | [FAIL](eval/results/dev-01/anthropic_routing-claude-headless/REVIEW.md) / [FAIL](eval/results/dev-01/anthropic_routing-claude-interactive/REVIEW.md) |
| vercel_recipe | [PASS](eval/results/dev-01/vercel_recipe-codex-headless/REVIEW.md) / [PASS](eval/results/dev-01/vercel_recipe-codex-interactive/REVIEW.md) | [FAIL](eval/results/dev-01/vercel_recipe-claude-headless/REVIEW.md) / [FAIL](eval/results/dev-01/vercel_recipe-claude-interactive/REVIEW.md) |
| openai_demo | [PASS](eval/results/dev-01/openai_demo-codex-headless/REVIEW.md) / [PASS](eval/results/dev-01/openai_demo-codex-interactive/REVIEW.md) | [PASS](eval/results/dev-01/openai_demo-claude-headless/REVIEW.md) / [FAIL](eval/results/dev-01/openai_demo-claude-interactive/REVIEW.md) |
| langchain_completion | [PASS](eval/results/dev-01/langchain_completion-codex-headless/REVIEW.md) / [PASS](eval/results/dev-01/langchain_completion-codex-interactive/REVIEW.md) | [FAIL](eval/results/dev-01/langchain_completion-claude-headless/REVIEW.md) / [FAIL](eval/results/dev-01/langchain_completion-claude-interactive/REVIEW.md) |

[Full frozen-grader results](eval/results/dev-01/suite.json). Cross-harness inventory discrepancies: 7.

### DEV-02

| Workflow | Codex H / I | Claude Code H / I |
|---|---|---|
| anthropic_classification | [PASS](eval/results/dev-02/anthropic_classification-codex-headless/REVIEW.md) / [PASS](eval/results/dev-02/anthropic_classification-codex-interactive/REVIEW.md) | [FAIL](eval/results/dev-02/anthropic_classification-claude-headless/REVIEW.md) / [FAIL](eval/results/dev-02/anthropic_classification-claude-interactive/REVIEW.md) |
| vercel_enum | [PASS](eval/results/dev-02/vercel_enum-codex-headless/REVIEW.md) / [PASS](eval/results/dev-02/vercel_enum-codex-interactive/REVIEW.md) | [FAIL](eval/results/dev-02/vercel_enum-claude-headless/REVIEW.md) / [FAIL](eval/results/dev-02/vercel_enum-claude-interactive/REVIEW.md) |
| anthropic_routing | [PASS](eval/results/dev-02/anthropic_routing-codex-headless/REVIEW.md) / [PASS](eval/results/dev-02/anthropic_routing-codex-interactive/REVIEW.md) | [PASS](eval/results/dev-02/anthropic_routing-claude-headless/REVIEW.md) / [FAIL](eval/results/dev-02/anthropic_routing-claude-interactive/REVIEW.md) |
| vercel_recipe | [PASS](eval/results/dev-02/vercel_recipe-codex-headless/REVIEW.md) / [PASS](eval/results/dev-02/vercel_recipe-codex-interactive/REVIEW.md) | [PASS](eval/results/dev-02/vercel_recipe-claude-headless/REVIEW.md) / [FAIL](eval/results/dev-02/vercel_recipe-claude-interactive/REVIEW.md) |
| openai_demo | [PASS](eval/results/dev-02/openai_demo-codex-headless/REVIEW.md) / [PASS](eval/results/dev-02/openai_demo-codex-interactive/REVIEW.md) | [FAIL](eval/results/dev-02/openai_demo-claude-headless/REVIEW.md) / [FAIL](eval/results/dev-02/openai_demo-claude-interactive/REVIEW.md) |
| langchain_completion | [PASS](eval/results/dev-02/langchain_completion-codex-headless/REVIEW.md) / [PASS](eval/results/dev-02/langchain_completion-codex-interactive/REVIEW.md) | [FAIL](eval/results/dev-02/langchain_completion-claude-headless/REVIEW.md) / [FAIL](eval/results/dev-02/langchain_completion-claude-interactive/REVIEW.md) |

[Full frozen-grader results](eval/results/dev-02/suite.json). Cross-harness inventory discrepancies: 3.

### DEV-03

| Workflow | Codex H / I | Claude Code H / I |
|---|---|---|
| anthropic_classification | [PASS](eval/results/dev-03/anthropic_classification-codex-headless/REVIEW.md) / [PASS](eval/results/dev-03/anthropic_classification-codex-interactive/REVIEW.md) | [FAIL](eval/results/dev-03/anthropic_classification-claude-headless/REVIEW.md) / [FAIL](eval/results/dev-03/anthropic_classification-claude-interactive/REVIEW.md) |
| vercel_enum | [PASS](eval/results/dev-03/vercel_enum-codex-headless/REVIEW.md) / [PASS](eval/results/dev-03/vercel_enum-codex-interactive/REVIEW.md) | [FAIL](eval/results/dev-03/vercel_enum-claude-headless/REVIEW.md) / [BLOCKED](eval/results/dev-03/vercel_enum-claude-interactive/REVIEW.md) |
| anthropic_routing | [PASS](eval/results/dev-03/anthropic_routing-codex-headless/REVIEW.md) / [PASS](eval/results/dev-03/anthropic_routing-codex-interactive/REVIEW.md) | [BLOCKED](eval/results/dev-03/anthropic_routing-claude-headless/REVIEW.md) / [BLOCKED](eval/results/dev-03/anthropic_routing-claude-interactive/REVIEW.md) |
| vercel_recipe | [PASS](eval/results/dev-03/vercel_recipe-codex-headless/REVIEW.md) / [PASS](eval/results/dev-03/vercel_recipe-codex-interactive/REVIEW.md) | [BLOCKED](eval/results/dev-03/vercel_recipe-claude-headless/REVIEW.md) / [BLOCKED](eval/results/dev-03/vercel_recipe-claude-interactive/REVIEW.md) |
| openai_demo | [PASS](eval/results/dev-03/openai_demo-codex-headless/REVIEW.md) / [PASS](eval/results/dev-03/openai_demo-codex-interactive/REVIEW.md) | [BLOCKED](eval/results/dev-03/openai_demo-claude-headless/REVIEW.md) / [BLOCKED](eval/results/dev-03/openai_demo-claude-interactive/REVIEW.md) |
| langchain_completion | [PASS](eval/results/dev-03/langchain_completion-codex-headless/REVIEW.md) / [PASS](eval/results/dev-03/langchain_completion-codex-interactive/REVIEW.md) | [BLOCKED](eval/results/dev-03/langchain_completion-claude-headless/REVIEW.md) / [BLOCKED](eval/results/dev-03/langchain_completion-claude-interactive/REVIEW.md) |

[Full frozen-grader results](eval/results/dev-03/suite.json). Cross-harness inventory discrepancies: 5.

## HELD-OUT

| Workflow | Codex H / I | Claude Code H / I |
|---|---|---|
| heldout_enum | NOT RUN / NOT RUN | NOT RUN / NOT RUN |
| heldout_generation (negative control) | NOT RUN / NOT RUN | NOT RUN / NOT RUN |

No final check or post-held-out repair was attempted. Unseen-code generalization is therefore **not proven**. The user-required stop condition took precedence over opening the sealed split.

## Independently valid live parity

OpenRouter access was verified with real Jev responses using **`typesafe/jev-1.13-20260917`**. The direct TypeSafe pin is **`jev-1.13.0`**; that spelling returns model-not-found on OpenRouter, so the verified provider-specific dated pin is used. No `jev-latest` or generative-model substitute was used. Vercel access returned HTTP403 `customer_verification_required`; its versioned route remains unverified. No billing/account settings were changed.

The user explicitly authorized original-baseline models through OpenRouter for evaluation. Valid runs execute the actual original callable or capture its unchanged SDK request/options and use its actual parser. The same original model, prompts, prefill, stop settings and output semantics are retained. Production fallback providers remain unchanged. Gateway timing is not direct-provider production timing.

Latest independently accepted DEV03 measurements (all Codex):

| Workflow / scenario | Unique pairs | Threshold | Accepted agreement | Fallbacks | Median ms Jev / original | Estimated cascade cost change |
|---|---:|---:|---:|---:|---:|---:|
| anthropic_classification / headless | 36 | 0.90 | 21/22 (95.5%) | 14/36 | 399 / 1061 | -57.0% |
| anthropic_classification / interactive | 34 | 0.95 | 18/18 (100.0%) | 16/34 | 367 / 1213 | -48.9% |
| vercel_enum / headless | 32 | 0.90 | 29/29 (100.0%) | 3/32 | 310 / 1291 | +4.9% |
| vercel_enum / interactive | 30 | 0.90 | 27/27 (100.0%) | 3/30 | 338 / 959 | +5.1% |

All four runs exceed 90% raw-answer agreement among accepted decisions, retain fallback, and execute low-confidence, generic error, timeout and HTTP429 control-flow assertions. Actual captured responses are replayed through production integration; original return values and exception identity are checked with exactly zero/one fallback calls. Per-run `JEV_PARITY.json`, executable validation scripts and reports contain confidence curves, p50/p95, provider request IDs, raw response/usage evidence, provenance and cost details. Thresholds were preset before confirmation, not selected from the same confirmation results.

Classification inputs use public repository tickets plus labeled synthetic boundary cases. The genre headless set uses one original example plus synthetic plots; the genre interactive set is entirely labeled synthetic. Original labels are not substituted for original live model outputs. Costs use provider-reported `usage.cost`; cascade estimates add original cost/latency only on fallback rows. They are estimates from paired measurements, not separate live end-to-end production timings. Short genre inputs demonstrate that lower latency can coincide with **higher cost**.

Four DEV02 Codex conversions also have valid live evidence: classification 24/25 accepted matches at .90 over 38 pairs and 29/31 at .90 over 44 pairs; genre 32/33 at .90 over 36 pairs in each scenario. The retained failed Claude comparisons may show >90% numerical agreement, but they are **not accepted as parity proof** where they reconstruct baselines, bypass the actual evaluator/gate, invent successful fault payloads, or omit full fallback assertions.

## Bad fits and remaining failures

- Recipe JSON contains unrestricted recipe names, ingredients and instructions: GENERATION, even with a schema.
- OpenAI demos require generated prose/code, streaming deltas or raw provider response diagnostics. A typed Jev decision cannot replace that behavior.
- LangChain's completion endpoint returns an unrestricted text stream: GENERATION, with no closed decision consumer.
- Anthropic routing is MIXED because the selection response also supplies printed generated reasoning. Pure-decision approval cannot remove that observable output; the shared provider wrapper must also appear in the audit.
- Claude runs still sometimes reconstruct original prompts/schema/parsing in validation, or import policy constants while reimplementing the evaluator. Live API calls alone do not prove the shipped conversion.
- Some Claude fault tests invent successful Jev response payloads or check only evaluator rejection rather than proving original fallback and error propagation. These are recorded failures, not permitted examples.
- Setup wording can drift: report-only recommended instead of the default branch, or neither-key mode incorrectly described as audit-only. Missing-approval Claude probe wrote extra audit/report artifacts instead of stopping after the plan.
- A no-key Claude wrapper called the original twice when it raised. An independent exception probe reproduced two calls; the basic smoke alone did not catch it.

## Supplemental checks

- **18 local tests pass**: nine frozen grader tests, four credential-launcher tests (including terminal echo), and five preflight/artifact-helper tests. Preflight rejects dirty trees/colliding branches or clone paths without stashing or writing. These do not replace real harness evaluation.
- Agent Skills format and Claude plugin/marketplace manifests validate. Current Codex/Claude install paths were checked against official documentation.
- Real `npx skills add Kevin-Zhouu/jevify --skill jevify --agent codex claude-code --yes --copy --json` in a fresh temporary project exited 0 and created identical skill hashes at both project paths. [Installation evidence](eval/preflight/npx-install.json).
- DEV03 missing-setup probes: both harnesses stop without source reads or writes. Missing-approval: Codex writes only the plan; Claude's extra artifacts fail the stop-boundary check. No-key: both skip live validation honestly, but Claude's double-fallback defect remains. [Setup probes](eval/results/supplemental-03/).
- Natural migration requests automatically activate the skill in both harnesses; general Jev API questions do not. These prove the trigger distinction only, not general API-answer quality. Setup wording deviations are retained. [Discovery probes](eval/results/trigger-03/).
- Credential-shaped-value scans found no supplied secrets in the published files/transcripts. This is a heuristic check plus review, not a guarantee against every possible secret encoding.

## Known limits

The full acceptance bar is not met: Claude failures remain and HELD-OUT is untested. Small, benign public/synthetic samples do not establish adversarial robustness or production reliability. Confidence is not correctness. Positive corpus measurements exercise Choice; Score/Noul guidance is present but not equivalently proved by this corpus.

The corpus uses real pinned runnable examples/source slices, not complete deployed applications. They have no upstream test suites in the slices, so supplied behavioral smokes execute the source and check observable behavior/fallback with original-provider doubles. Those smokes are not live inference. TypeScript parity uses disclosed compatible AI SDK patch dependencies where the historical ambient dependency combination failed module loading; exact historical dependency identity is not claimed. Only the sampled providers/languages have empirical coverage; support for other workflows remains a general instruction-level capability.

With missing Phase0 answers and no authorized destination, the skill emits an incomplete plan in the final response rather than writing a file. This resolves the conflicting requirements “plan written” and “no writes before setup” without guessing a location. With complete setup and missing approval, only the headless plan should be written.

## Iteration log and stopping point

- DEV01: initial portable staged skill; 9/24 pass. Found output-location errors, artifact omissions, over-strict metadata interpretation and proxy validation.
- DEV02: added read-only preflight/artifact checks, truthful metadata-adapter rules and actual-source proof guidance; improved to 14/24.
- DEV03: strengthened setup read boundary, negative-output mode handling, wrapper inventory, validation wiring and fallback/model logging rules; 12 completed passes, 3 completed failures, 9 quota-blocked. Stopped under the explicit harness-unavailable condition.

No DEV04 or HELD-OUT repair is claimed. Draft reusable source/fallback/cost helpers and a heuristic validation-source screen are retained separately for resumption; they were not activated after the stop. To continue, restore Claude headless availability, finish general DEV repairs and rerun, then open HELD-OUT once with at most two general repair rounds. Do not change frozen corpus/thresholds or repair old outputs in place.

Sources: [TypeSafe docs index](https://docs.typesafe.ai/llms.txt), [Models](https://docs.typesafe.ai/models), [OpenRouter TypeSafe SDK guide](https://openrouter.ai/docs/guides/community/typesafe-sdk), [official TypeSafe skill](https://github.com/typesafe-ai/skills), [Codex skills](https://learn.chatgpt.com/docs/build-skills), [Claude Code skills](https://code.claude.com/docs/en/skills).
