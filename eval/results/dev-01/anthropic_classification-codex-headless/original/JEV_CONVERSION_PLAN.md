# Jev conversion plan

Source: `main`, `9ad0ba53546ba42a9b50165c3fe51ec275a58d68`.
Output: branch `jev-convert/evaluation` in this repository. Config mode is branch;
its inactive clone_path is not used. Preflight: clean including untracked files,
valid and unused branch, git available; no local AGENTS.md found.

User-designated config supplies OpenRouter access, conservative risk and explicit
upfront approval for fallback at pure DECISION sites with enumerated outputs.
Resolved selection: `workflow.py:83` → `fallback`. No other LLM sites or consumers
exist outside the installed skills. `simple_classify` is the public wrapper for
that one transport; it is not counted as another saving.

| Original site | Provider | Downstream | Classification / fit | Options |
| --- | --- | --- | --- | --- |
| workflow.py:83 | Anthropic SDK, claude-haiku-4-5 | First text block stripped and returned as string | DECISION; FIT for benign fixture distribution | **fallback selected**: Choice over ten original labels; expected cost Jev + fallback fraction × original, accepted calls may be faster/cheaper, misses cost an additional serial call. Risks: overlapping labels, confident mistakes, adversarial inputs. **leave**: primitive none, unchanged cost/latency, retains upstream model/parsing risks. |

Inputs come from the caller; repository examples are short English insurance
support tickets in data/train.tsv and data/test.tsv. No repository consumer uses
usage, IDs, stop reasons or generated reasoning. Upstream public signature remains
synchronous `simple_classify(X)` returning a stripped string. Original client
initialization, prompt, model parameters, parsing and exceptions remain unchanged.

One decisions module owns criteria, pin, question, 0.90 provisional threshold,
12,000-byte ticket bound, ten-second network timeout and response validation.
Changed category definitions and unsupported/oversize inputs use the original.
Missing key, low confidence, malformed response and transport failures fall back
exactly once. Logs use the Python logger at INFO with path/model/bounded reason;
no stdout, input or credential logging. No new runtime dependency.

The fit is limited to benign tickets represented by this example. This is not a
validated public-service injection defense: neither confidence nor quoting text
proves adversarial robustness. No counting, arithmetic, date comparisons, multi-hop
reasoning, non-text or generation is delegated to Jev. The small state bound is
well below documented 32k state-plus-question / 64k request limits.

Validation: supplied independent Python smoke; injected failure/gate checks; at
least 30 unique live pairs if the selected key and equivalent baseline route work.
Use actual decisions module and original function with isolated transport forwarding
to the SAME `anthropic/claude-haiku-4.5`, preserving original prompt, assistant
prefill, stop sequence, temperature, max tokens and parser. Production fallback
stays Anthropic. Stop parity claims if baseline capabilities fail. Keep fallback
regardless of measured parity. No push or PR.

Documentation read 2026-09-23 (live Markdown via urllib after browser fetch errors):
- https://docs.typesafe.ai/llms.txt
- https://docs.typesafe.ai/api.md
- https://docs.typesafe.ai/models.md
- https://docs.typesafe.ai/confidence.md
- https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md
- https://docs.typesafe.ai/introduction/coding-agents.md
- https://docs.typesafe.ai/model-jaggedness/jev-1.13.md
- https://docs.typesafe.ai/primitives/choice.md
- https://docs.typesafe.ai/patterns/intent-routing.md
- https://docs.typesafe.ai/patterns/confidence-routing.md
- https://docs.typesafe.ai/patterns/composite-scoring.md
- https://docs.typesafe.ai/patterns/fan-out.md
- https://docs.typesafe.ai/cookbooks/hierarchical_classification.md
- https://openrouter.ai/docs/guides/community/typesafe-sdk

Setup: retain the original Anthropic SDK and ANTHROPIC_API_KEY. Set
OPENROUTER_API_KEY in runtime environment; .env.example contains names only, no
secrets. The skill's `.agents/skills/jevify/scripts/with_jev_key.py` supports hidden
key entry. No dotenv loader is added. To see path logs, configure Python logging
at INFO in the host application. Jev pin: `typesafe/jev-1.13-20260917`.
