# Approved conversion plan

Source revision: fd78ebff05048c9ed2a20540f9f89cc7aeed09cb. Output: sibling clone `converted`, branch `jev-convert/evaluation`. Original clean including untracked files; destination and branch unused before setup. No applicable AGENTS.md found in this repository.

| Site | Classification / downstream | Fit | Options | Selection |
| --- | --- | --- | --- | --- |
| workflow.py:83 | DECISION; simple_classify(X), stripped string, no callers/diagnostics | Conditional: benign short insurance tickets, ten categories | fallback / Choice: avoid Claude on accepted decisions, risk confident errors and serial overhead; leave / none: unchanged cost and behavior | fallback |

Approval: only pure DECISION sites with enumerated outputs; preserve all observable fields. All other options declined. One wrapper and one transport site represent one opportunity, not two.

Keep original function body as fallback, including prompt, model, prefill, stop sequence, max_tokens, temperature, stripping and error propagation. Centralize Jev policy in jev_decisions.py, use standard-library HTTP, pinned OpenRouter typesafe/jev-1.13-20260917, 10 second timeout, no retries. Initial conservative confidence threshold 0.95; bounded inputs up to 2000 UTF-8 bytes; unsupported/oversized state and any Jev failure go to original exactly once. Log only path/model/bounded reason at INFO through a library logger (no stdout changes).

Run supplied independent smoke, fault-injection checks and at least 30 unique paired fixture inputs when access permits. Baseline adapter only: route unchanged original request to the SAME Claude Haiku 4.5 via OpenRouter; retain Anthropic production fallback. No proxy prompt or model substitution. Record real costs/latencies and raw decisions separately from fallback. Threshold remains provisional if blocked. No push or PR.

Scope is benign fixture-like tickets; no effective adversarial mitigation exists. Confidence and length bounds do not establish security or production parity.

References: https://docs.typesafe.ai/api.md ; https://docs.typesafe.ai/confidence.md ; https://docs.typesafe.ai/model-jaggedness/jev-1.13.md ; https://openrouter.ai/docs/guides/community/typesafe-sdk . Live docs read 2026-09-23 (via urllib where browser fetch failed).
