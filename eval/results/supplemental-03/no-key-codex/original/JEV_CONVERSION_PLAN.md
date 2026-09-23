# Jev conversion plan

Source: `49de9153ceeb3dbd27df8b215022f795d1787417`, original branch `main`.
Output: branch `jev-convert/no-key` in the current repository
`/Users/bigsoup/Downloads/Jev Converter/eval/runs/supplemental-03/no-key-codex/original`.
Preflight: clean including untracked files; branch unused; provider `none`,
key_env null, key_present false, live validation skipped by configuration.
No secret files, external runs, labels or corpus contents inspected.

Approval: supplied headless config selects `fallback` for pure DECISION sites
with enumerated outputs, retaining behavior and the original fallback provider.
Risk is conservative. No push or PR authorized.

| Original ID | Provider | Class | Downstream and fit | Options and selection |
|---|---|---|---|---|
| workflow.py:83 | Anthropic SDK / claude-haiku-4-5 | DECISION | response.content[0].text.strip() returned synchronously by simple_classify(X); no internal callers, other wrappers, diagnostics or metadata consumers. Conditional fit for short, trusted support tickets. | Selected fallback: Choice, ten existing labels and descriptions, provisional 0.95 gate, original callable retained. Likely lower cost/latency for accepted decisions; misses add Jev cost and serial latency. Risk: semantic disagreement and injection. Alternative leave: primitive none, unchanged cost/latency, existing behavior retained. |

Only one inference site; wrapper entry `workflow.py:65` and transport
`workflow.py:83` are the same operation, not two savings opportunities.
There are no GENERATION, MIXED or EXTRACTION calls in executable project source.
Data files were not opened under the user's corpus restriction. No project test
suite or dependency manifest exists. No applicable AGENTS.md found in repository.

Input origin is the caller-supplied string X; original length is unbounded.
Jev state will be bounded to 8,000 UTF-8 bytes with fixed criteria well below
the documented 32k state-plus-question limit. Unsupported inputs fall back.
This site classifies topics, not arithmetic, date comparisons or policy advice.
No existing adversarial-input mitigation exists. Jev is therefore disabled
unless an operator explicitly selects a provider and attests that the input
distribution is trusted. This is an operational trust boundary, not an injection
detector or evidence of production robustness. Public untrusted traffic remains
ineligible; a confidence threshold does not make that traffic safe.

Provider remains none by default. The unactivated adapter supports TypeSafe
direct as a future explicit configuration, using the official versioned pin.
No provider or credential is chosen for this run. Environment placeholders are
blank. No live request will be made. Fallback Anthropic initialization, prompt,
prefill, stop sequence, model, parsing, exceptions and signature are retained.

Validation wiring: preserve original body as workflow._original_simple_classify;
public workflow.simple_classify invokes jev_decisions.classify, which invokes
jev_decisions.evaluate and accepted_choice. Offline validation imports those
actual symbols, compares original function AST against git source allowing only
the rename, and exercises transport failures and fallback exactly once.
No gateway adaptation is authorized. No fabricated successful Jev response is
permitted; accepted-path replay and 30-pair live validation remain skipped.
The supplied external smoke is executed unchanged, not read or edited.

Economics: expected cost = Jev cost + fallback fraction * original cost;
expected serial latency = Jev latency + fallback fraction * original latency.
No measured savings, parity, confidence curve or recommended production
threshold can be claimed with zero live pairs. Keep 0.95 provisional and retain
fallback even after future calibration; use a separate confirmation set.

Current documentation reviewed on 2026-09-23: [API](https://docs.typesafe.ai/api),
[Models](https://docs.typesafe.ai/models), [Confidence](https://docs.typesafe.ai/confidence),
[building guide](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md),
[coding agents](https://docs.typesafe.ai/introduction/coding-agents),
[limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13),
[Choice](https://docs.typesafe.ai/primitives/choice), the four Patterns pages
(intent-routing, confidence-routing, composite-scoring, fan-out), and
[hierarchical classification](https://docs.typesafe.ai/cookbooks/hierarchical_classification).
Markdown web reads failed; HTML reads succeeded, and the building guide was
retrieved directly over HTTPS. One flat Choice suffices for ten labels.
