# Jev conversion plan

Source: main at 2160130f0ffe291eff8623e4f83bc38fef8499d5.
Output: branch jev-convert/no-key in this repository. Preflight: clean, unused branch, no errors. Provider none; no key selected. Process presence checks for TYPESAFE_API_KEY and ANTHROPIC_API_KEY were both false; no secret files read.

Supplied headless config authorizes conservative fallback for pure DECISION sites with enumerated outputs and preservation of the original provider. Resolved selection: workflow.py:83, fallback. No Jev-only approval. No pushes or PRs.

| Original site | Provider / class / downstream | Option | Scope, benefit, risk |
|---|---|---|---|
| workflow.py:83 | Anthropic claude-haiku-4-5 / DECISION / stripped label returned by simple_classify | fallback / Choice (selected) | Ten existing categories and descriptions, original callable retained. Trusted offline inputs only; explicit runtime opt-in. Accepted decisions may avoid generative latency/cost; misses add Jev overhead. Unvalidated threshold and semantic parity. |
| workflow.py:83 | same | leave / none | No changes, no speculative savings; existing latency/cost. |

Only Python workflow source exists outside installed skills; no wrappers or additional code consumers were found. No generation, mixed, or extraction sites. Categories are application definitions, not evaluation labels. Corpus data and provenance were not read, per user restriction. Signature simple_classify(X), synchronous string return, stripped original output, original prompt/model/stop sequences and exceptions remain intact. No original usage or finish diagnostics are exposed.

Conditional fit: short semantic classification requires no arithmetic, date comparison or generation. Input provenance is caller-controlled and no existing injection defense exists. Jev stays off unless an operator explicitly opts into trusted offline inputs. This is a scope gate, not a claim of adversarial robustness. Oversize/non-string inputs go to the original path. No evidence establishes the corpus as benign.

One decisions module owns criteria, questions, model jev-1.13.0, threshold 0.9, bounds, and gate policy. Provider none permits dormant conservative code under the skill configuration rule; TypeSafe direct credential placeholder is unset. No live provider is contacted. Anthropic fallback provider is unchanged.

Validation: independent user smoke, offline gate/fault assertions, unchanged-original AST comparison, artifact checker. Live validation skipped; no paired inputs or fabricated successful inference. Threshold 0.9 is provisional, not calibrated. Keep disabled pending representative paired validation (at least 30 unique inputs, calibration and independent check sets).

Current public documentation consulted on 2026-09-23: https://docs.typesafe.ai/llms.txt and its API, Models, Confidence, Choice, building guide, coding-agents, Jev 1.13 jaggedness, all four Patterns, and classification_using_confidence cookbook. Markdown pages were retrieved directly with urllib after browser fetch errors. HTTP contract: https://docs.typesafe.ai/api.md ; limitations: https://docs.typesafe.ai/model-jaggedness/jev-1.13.md .
