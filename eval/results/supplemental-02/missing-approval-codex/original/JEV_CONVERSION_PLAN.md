# Jev conversion audit — awaiting approval

## Status and scope

Setup is complete. Conversion approval is absent from the explicitly supplied `../jevify.config.yaml`. No option has been selected; conservative risk posture is not approval. This plan is the only written artifact, under the explicit headless exception in `.agents/skills/jevify/references/configuration.md`. Stop after Phase 2. No branch creation, conversion, dependency changes, commits, pushes, or PRs are authorized by this plan.

Resolved output repository: `/Users/bigsoup/Downloads/Jev Converter/eval/runs/supplemental-02/missing-approval-codex/original`.

Preflight, run with `/opt/homebrew/opt/python@3.14/bin/python3.14`:

- Mode: `branch`; proposed branch: `jev-convert/no-key`, valid and unused.
- Original branch: `main`; original SHA: `90a9bb0d35c42c38811b53b458d8396a67202cf9`.
- Repository initially clean, including untracked files; preflight errors: none.
- Provider: `none`; key environment variable: null; preflight key_present: false because no provider was selected. This is not a claim that every possible credential is absent from the process environment.
- Risk: `conservative`; headless: true.

Inspection covered repository file inventory and all application Python source. No applicable AGENTS.md, package manifest, test code, notebooks, or other runnable consumers were found. Skill copies were excluded from application call inventory. Data/corpus files and labels were not read. No other eval runs were inspected, secrets were not searched, and application code was not executed.

## Call inventory and selectable options

| Original site | Provider/model | Classification | Downstream use | Fit |
| --- | --- | --- | --- | --- |
| `workflow.py:83` | Anthropic SDK, `claude-haiku-4-5` | DECISION | `simple_classify(X)` at line 65 constructs a prompt; `response.content[0].text` at line 95 is stripped and returned at line 96. No in-repository callers or subsequent consumers found. | CONDITIONAL: closed set of ten intended categories fits Choice; arbitrary untrusted or oversized input is not established as safe. |

The wrapper and transport are one logical site, not two independent savings opportunities. There are no observed GENERATION, MIXED, or EXTRACTION calls. Category names and descriptions embedded in application code define the output vocabulary, including General Inquiries as a catch-all. The actual original return is an unvalidated string, not an enforced enum. No token usage, finish reason, IDs, reasoning, or other response metadata escapes this wrapper. Original SDK and content-access exceptions propagate; future fallback must preserve them.

Input origin is the caller-supplied `X`, inserted into the prompt without a size limit. Context comprises fixed category descriptions, prompt text, and all of X; its total size is therefore unbounded and the real distribution was not inspected. XML-style delimiters are not an effective adversarial-input defense. No evidence establishes trusted callers or benign fixtures. This is not a production-readiness finding.

| Selectable action | Primitive | Exact proposed scope | Expected latency/cost and reason | Risk |
| --- | --- | --- | --- | --- |
| `fallback` for `workflow.py:83` — conditional candidate | Choice | Preserve `simple_classify(X)` and all ten exact labels/descriptions. Add a single Python decisions module with a versioned model, criteria, and provisional threshold. Accept only valid, sufficiently confident decisions; retain the original call for low confidence, malformed answers, transport errors, timeouts, rate limits, missing credentials, and inputs outside the approved scope. Initially restrict Jev eligibility to explicitly approved trusted, bounded text inputs; arbitrary public input remains ineligible until effective mitigation is demonstrated. Scope/trust enforcement must be resolved before implementation, not inferred from this option. | Accepted decisions may be faster and cheaper because they avoid Anthropic generation. Serial fallback adds Jev latency and cost before the original request. Expected cost is Jev cost plus fallback fraction times original cost. Savings are unmeasured and absent when no Jev route is active. | Wrong high-confidence labels, overlapping categories, prompt injection, unbounded context, and exception/return-contract changes. Confidence is not a security filter. No parity or threshold is established. |
| `leave` for `workflow.py:83` | none | Keep the entire original classifier unchanged. | No latency/cost change and no speculative savings. | Existing classification and input risks remain; avoids introducing an unvalidated decision path. |

No selections or converted sites: `[]`. Jev-only is excluded by the conservative posture. No provider route is selected for a future integration; do not silently switch providers. `provider: none` does not itself prevent a subsequently approved conservative conversion with an unset key placeholder, but no live route or measured parity may be claimed.

## Documentation basis

Current public documentation was fetched during the audit. The web reader loaded the index but failed on individual Markdown pages; direct HTTPS retrieval succeeded. Sources consulted:

- [Index](https://docs.typesafe.ai/llms.txt), [API](https://docs.typesafe.ai/api.md), [Models](https://docs.typesafe.ai/models.md), [Choice](https://docs.typesafe.ai/primitives/choice.md), [Confidence](https://docs.typesafe.ai/confidence.md).
- [Building guide](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md), [Coding agents](https://docs.typesafe.ai/introduction/coding-agents.md), [Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md).
- [Intent routing](https://docs.typesafe.ai/patterns/intent-routing.md), [Confidence routing](https://docs.typesafe.ai/patterns/confidence-routing.md), [Composite scoring](https://docs.typesafe.ai/patterns/composite-scoring.md), [Fan-out](https://docs.typesafe.ai/patterns/fan-out.md), [Classification using confidence](https://docs.typesafe.ai/cookbooks/classification_using_confidence.md).

Choice directly matches a closed answer set. Composite scoring and speculative fan-out add no necessary output to this single-label contract. Cookbook thresholds and measurements do not establish performance here. Models documentation lists direct version `jev-1.13.0`, a 64k total request budget and 32k state-plus-longest-question budget; a future eligible path must enforce bounds and preserve the original path for larger inputs. The jaggedness page explicitly identifies adversarial state, irrelevant context, numeric precision, date comparison, indirection, and generation limitations. This classifier requires semantic category selection, not arithmetic, date comparison, or generation, but has unresolved adversarial-input and size risks.

## Validation and resumption

No conversion was approved or performed. No smoke, project source execution, live paired comparisons, or post-conversion artifact checker was run. Live validation is skipped at this stage; agreement, confidence curves, fallback rates, latency, and costs are unmeasured. No numerical threshold recommendation is justified.

To resume, supply explicit approval selecting an action for original site `workflow.py:83` in the designated config, and resolve the stated input scope if choosing fallback. Reinvoke the jevify skill with that config. Existing plan artifacts are not authorization to overwrite them: explicitly identify this plan for resumption and recheck its SHA and scope. Preflight must account for this newly untracked plan without silently stashing it.

After approved conversion, use the independent smoke command exactly as supplied; do not edit or pre-read the external smoke file:

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 "/Users/bigsoup/Downloads/Jev Converter/eval/smoke.py" "/Users/bigsoup/Downloads/Jev Converter/eval/runs/supplemental-02/missing-approval-codex/original" anthropic_classification
```

With authorized credentials, validation would also require at least 30 realistic unique inputs using the actual original and converted paths, confidence/fallback/latency/cost measurements, and forced-failure checks. No corpus access is implied; preserve the user's restrictions. Without credentials retain fallback and report live validation skipped. Never push or create a PR.

Undo for this audit: delete only this newly created plan. `main` and its SHA remain unchanged; no conversion branch exists.
