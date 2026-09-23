# Approved conversion plan

Source: eff84f8f58d676d6b3b2eb21ae7b906300e2ef1b, main. Output mode: clone, ../converted, branch jev-convert/evaluation. Source remains untouched.

Approval: fallback only for pure DECISION sites with enumerated outputs; preserve externally observable fields. Resolves to workflow.py:83, wrapped by simple_classify at original line 65. No other inference sites or consumers were found. Leave option declined. Audit and full option benefits/risks: JEV_AUDIT.json.

Preflight: clean repository, unused destination, git available, OPENROUTER_API_KEY present (value never recorded). Setup supplied in conversation is authoritative; external config need not be read.

Use OpenRouter typesafe/jev-1.13-20260917 Choice with the original ten categories. Keep all Jev policy in jev_decisions.py; initial conservative confidence threshold 0.9, subject to calibration. Retain the exact original Anthropic callable and parsing. No dependencies added. Unsupported input and all Jev failures fall back once. Log bounded path/model/reason through Python logging, without altering stdout.

Evaluate representative repository tickets, separately calibrating and confirming; include synthetic ambiguous/boundary/out-of-domain inputs. Invoke the original callable through an isolated authorized OpenRouter adapter for the SAME claude-haiku-4-5 model, preserving messages, assistant prefill, stop sequences, temperature and max_tokens. Measure actual responses, agreement curves, fallbacks, latency, provider costs; do not invent missing metrics. Exercise failure paths and replay only real successful responses. Run supplied independent smoke and artifact checker. Commit locally; no push or PR.

Eligibility is conditional on benign ticket inputs, not arbitrary adversarial public traffic. Confidence is not an injection defense. State over 16000 UTF-8 bytes bypasses Jev without truncation.

Documentation checked: https://docs.typesafe.ai/llms.txt and API, Choice, Models, Confidence, building guide, coding agents, jaggedness, four patterns and hierarchical classification cookbook; https://openrouter.ai/docs/guides/community/typesafe-sdk. Live markdown accessible with urllib despite browser fetch failures.

| Original site | Class / downstream | Option | Primitive | Benefit | Risk | Selection |
| --- | --- | --- | --- | --- | --- | --- |
| workflow.py:83 | DECISION; stripped string returned by simple_classify | fallback | Choice | Accepted decisions avoid Claude inference; possible cost and latency reduction | Confident misclassification; serial fallback adds Jev cost and latency | Approved |
| workflow.py:83 | Same site | leave | none | No added latency or implementation work | Retains original inference cost | Declined |
