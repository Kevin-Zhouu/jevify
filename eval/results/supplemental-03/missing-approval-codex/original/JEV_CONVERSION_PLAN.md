# Jev conversion plan — awaiting explicit approval

## Status and setup

Phase 2 complete; conversion is not authorized. Supplied config has no `approval` field. No options have been selected. Conservative risk posture is not approval.

- Config: `/Users/bigsoup/Downloads/Jev Converter/eval/runs/supplemental-03/missing-approval-codex/jevify.config.yaml`.
- Headless: true. Output mode: branch. Requested branch: `jev-convert/no-key` (not created).
- Original branch: `main`; source SHA: `a90360ac7adda9efe10c8d57ebdbd60af2c7228a`.
- Repository and eventual output directory: `/Users/bigsoup/Downloads/Jev Converter/eval/runs/supplemental-03/missing-approval-codex/original`.
- Access: `none`; risk: conservative. Read-only preflight passed, repository initially clean, requested branch available, no errors. Preflight reported `key_env: null`, `key_present: false`, and `live_validation: skipped: user selected neither`. This does not assert that every possible environment credential is absent.
- This plan is the sole allowed artifact under the skill's headless missing-approval exception. No branch, clone, dependency, source, environment, or commit changes were made.

## Inspection scope and evidence

Inspected repository file inventory and all application source (`workflow.py`), searched application code for model calls and consumers, and read the invoked skill and applicable references. No AGENTS.md was found inside the repository. No manifests, lockfiles, application tests, notebooks, or additional runnable source were found. Installed skill copies were excluded from the application inventory. Data TSV contents, provenance, labels, corpus files, other runs, and secrets were not read. Dataset characteristics therefore remain unknown. Public documentation was reviewed on 2026-09-23; Markdown fetch failures were resolved using normal documentation pages.

`workflow.py:65` defines `simple_classify(X)`. It inserts caller-supplied X and the ten fixed category descriptions into a prompt (lines 66–82), invokes the Anthropic SDK at line 83, extracts `response.content[0].text` at line 95, and returns `result.strip()` at line 96. No in-repository callers of this function exist. This function and the provider transport are one inference opportunity, not two. External consumers are outside the permitted inspection scope.

## Selectable audit table

| Original site ID | Provider/model | Classification | Downstream use and fit | Options (unselected) |
| --- | --- | --- | --- | --- |
| `workflow.py:83` | Anthropic Python SDK, `claude-haiku-4-5` | DECISION | One of ten insurance support labels; response text becomes the stripped string returned by `simple_classify(X)`. Conditional fit for bounded, trusted ticket text. Not established as a fit for unrestricted adversarial customer input. | A: `fallback` / Choice, conditional scope below. B: `leave` / none. |

No GENERATION, MIXED, or EXTRACTION application calls were found. No separate shared wrapper or consumer call sites were found beyond the enclosing function described above.

Input origin is an arbitrary caller argument; no source validates its trust or maximum length. Context consists of the fixed category rubric, short prompt scaffolding, and all of X. Exact token size is unknown and unbounded by code. XML delimiters are not an effective prompt-injection mitigation. No existing mitigation was identified. The task does not itself require arithmetic, date comparison, multi-hop reasoning, non-text understanding, or generated explanation.

The original contract is a synchronous stripped string, with Anthropic and response-access errors propagating. It does not enforce membership in the category list. Usage, finish reason, and response IDs are not exposed or logged. A conversion must preserve the signature, label spelling, fallback behavior and errors; it must not fabricate Anthropic metadata. Client construction occurs at module import and also needs contract review during any approved implementation.

### Option A — conditional `fallback`, primitive Choice

Scope: only the decision in `simple_classify(X)` at original `workflow.py:83`. Keep all ten existing labels and definitions, including General Inquiries. Add one Python decisions module containing the question, criteria, model version and threshold configuration. A direct TypeSafe design would pin `jev-1.13.0`; no live provider route is selected or authorized by this plan.

Restrict Jev acceptance to an explicitly established trusted, bounded input scope. Existing callers must retain the original path by default until that scope is established; do not infer that the unread TSVs or arbitrary tickets are trusted. Add a context budget gate that falls back without truncating oversized input. Confidence alone must not be treated as an injection defense. Public adversarial traffic remains on the original path unless a separately reviewed mitigation and evidence establish eligibility.

For eligible inputs, accept only valid enum answers above an evaluated confidence threshold; on low confidence, malformed output, missing configuration, transport errors, timeout or rate limit, call the original implementation. Preserve original fallback exceptions. Log path and actual model version without input contents or secrets. No Jev-only removal is proposed.

Expected economics: accepted decisions may reduce latency and cost by replacing generative inference with one typed decision. Serial fallback adds a Jev request before the original request, increasing latency and cost on misses. Expected cost is Jev cost plus fallback fraction times original cost. No numerical savings are claimed; actual rates and acceptance frequency must be measured. With provider none and no credentials, there is no live saving or measured parity.

Risks: confusing adjacent billing/claims categories, unsupported input trust assumptions, overlong context, changed label distribution, and newly introduced transport failure paths. No numeric threshold is recommended without measurements. This option includes the trust/context gating work; it is not approval to enable Jev on all existing inputs.

### Option B — `leave`, primitive none

Scope: leave `workflow.py` and dependencies unchanged. Preserve the existing Anthropic classification behavior and exceptions. Latency and cost stay at baseline; there are no speculative Jev savings. Existing classification errors and injection risks remain. This is the immediately defensible option if a bounded trusted input scope cannot be established.

## Selections and resumption

Approved sites: none. Converted sites: none. The setup is complete; the missing field is explicit Phase 2 option approval. Neither option is inferred or selected automatically.

To resume, the user must explicitly select A or B for `workflow.py:83`, or provide a precise bounded predicate in the supplied config, then invoke the same skill with that config. For A, approval must include the stated gating scope; any broader trusted-input claim needs supporting information. Do not add an approval entry unless the user actually approves it. Recheck source revision and scope; this plan's presence is not permission to overwrite it or to auto-stash it. Resolve its disposition explicitly before a clean-worktree preflight for conversion.

Resumption request: `Use .agents/skills/jevify/SKILL.md with /Users/bigsoup/Downloads/Jev Converter/eval/runs/supplemental-03/missing-approval-codex/jevify.config.yaml, resuming this plan at the recorded source revision with my explicit option selection.`

After approval, follow the requested branch mode even if leave is selected. Read conversion and validation rules before editing. Generate JEV_AUDIT.json and JEV_CONVERSION_REPORT.md only in the approved later phase. Never push or create a PR.

## Validation status and future command

No source execution, smoke test, live comparison, package installation, or artifact checker was run: this invocation stops at Phase 2. No parity, confidence curve, fallback rate, latency, cost, or test-pass result is claimed. Live validation skipped: user selected neither; no conversion was approved.

If a conversion is approved, use this independent command exactly; do not edit or inspect its source:

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 "/Users/bigsoup/Downloads/Jev Converter/eval/smoke.py" "/Users/bigsoup/Downloads/Jev Converter/eval/runs/supplemental-03/missing-approval-codex/original" anthropic_classification
```

Any later live parity validation needs actual authorized access to the original and converted paths, at least 30 unique realistic inputs per converted site, confidence/fallback/latency/cost measurements and forced-failure checks. Current instructions prohibit reading corpus or label files; do not use those to construct validation cases without changed authorization. Keep conservative fallback regardless of measured agreement.

Undo for this invocation: remove this newly created plan if desired. No conversion branch exists to delete.

## Current public documentation consulted

- [Index](https://docs.typesafe.ai/llms.txt)
- [API](https://docs.typesafe.ai/api): typed requests and responses.
- [Models](https://docs.typesafe.ai/models): version `jev-1.13.0`, text input, 64k total request and 32k state-plus-longest-question budgets.
- [Confidence](https://docs.typesafe.ai/confidence): distribution-based uncertainty and context-dependent thresholds.
- [Building guide](https://docs.typesafe.ai/concepts/how-to-build-with-system-one): narrow judgments with control flow in code.
- [Coding agents](https://docs.typesafe.ai/introduction/coding-agents): Jev supplies decisions rather than generated prose.
- [Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13): adversarial content, long irrelevant state and literal criteria are relevant limitations.
- [Choice](https://docs.typesafe.ai/primitives/choice): closed-set selection.
- [Intent routing](https://docs.typesafe.ai/patterns/intent-routing)
- [Confidence routing](https://docs.typesafe.ai/patterns/confidence-routing)
- [Composite scoring](https://docs.typesafe.ai/patterns/composite-scoring)
- [Fan-out](https://docs.typesafe.ai/patterns/fan-out)
- [Hierarchical classification cookbook](https://docs.typesafe.ai/cookbooks/hierarchical_classification): reviewed for classification design; this flat ten-label task does not need hierarchical traversal or speculative scoring.
