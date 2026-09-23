# Jev conversion plan

Source: `1c953f75ebe1580de909072ce9a73b8ab8f11d05`, original branch `main`.
Output mode: branch, `jev-convert/evaluation`, in this repository:
`/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/anthropic_classification-codex-headless/original`.
The configured clone_path is inactive and ignored. Preflight: clean including untracked files, branch unused, git available, OPENROUTER_API_KEY present (value never inspected or persisted).

## Audit and resolved approval

| Original site | Provider | Class | Downstream | Fit | Options |
| --- | --- | --- | --- | --- | --- |
| workflow.py:83 | Anthropic SDK / claude-haiku-4-5 | DECISION | content[0].text.strip() returned by synchronous simple_classify(X) | FIT on benign fixture distribution | Selected fallback / Choice: avoid Claude latency/cost when accepted; misses add Jev cost/latency; risk of confident disagreement. Alternative leave / none: no savings, unchanged behavior. |

The sole source entrypoint is workflow.py. No shared local wrappers or additional in-repository consumers exist. Fixture TSVs supply customer ticket strings; ten categories include a general/no-match category. No usage, stop reason, reasoning or diagnostics are exposed. The SDK request is the only model call; do not count the enclosing callable as a second inference.

Approval: supplied headless predicate authorizes fallback for pure enumerated DECISION sites. It resolves to workflow.py:83 only. Conservative fallback stays. No push or PR.

Use OpenRouter typesafe/jev-1.13-20260917 with one Choice, criteria derived from the unchanged category definitions, provisional confidence threshold 0.90 fixed before confirmation. One jev_decisions.py owns instructions, criteria construction, model, bounds and gate. Input over 8,000 UTF-8 bytes goes to original; no truncation. Fixture tickets are short plain English. Arbitrary hostile input has no proven mitigation; confidence is not a security defense. No generation, exact calculations or decomposition needed.

## Contracts and validation wiring

Preserve original callable as workflow._original_simple_classify, allowing only its name to change. Preserve client initialization, model, prompt substitution, assistant prefill, stop sequence, max_tokens, temperature, parser, synchronous signature and exceptions. Public workflow.simple_classify(X) delegates to jev_decisions.classify with the original callable. Decisions module evaluate() owns real inference; parse_answer()/accepted() own validation and confidence gate. Original fallback must run exactly once, outside Jev exception handling. Add sanitized path/model/reason logging to stderr via logging; no raw input or secrets.

Validation loads pre-conversion workflow.py from the recorded git SHA, asserts AST identity of the preserved original function and captures matching SDK requests/parsing. An isolated SDK-boundary adapter routes the SAME original model through authorized OpenRouter chat transport, retaining messages/prefill/stop/max_tokens/temperature. No production fallback-provider changes. Replay each actual evaluate() response through the public wrapper and count zero/one original calls. No invented successful Jev responses.

Use >=30 unique repository/synthetic ticket inputs, including all ten categories and ambiguous/out-of-domain boundaries. Fixed 0.90 provisional threshold; all samples are confirmation, no threshold fitting. Record raw agreement, selective confidence curve, fallback, p50/p95 latency and provider-reported costs, request IDs and sanitized response evidence. Execute injected low-confidence, error, timeout, HTTP 429, malformed and missing-key paths with exact output/exception assertions. Any blocked baseline/transport means incomplete parity, never a substituted model or prompt.

Run supplied independent smoke with Python 3.14 and actual repository output path; upstream has no project test command. Run artifact checker --require-live. Commit approved files only.

## Documentation

Live pages read on 2026-09-23 via HTTPS (web tool failed on Markdown; Python HTTPS succeeded):
[API](https://docs.typesafe.ai/api.md), [Models](https://docs.typesafe.ai/models.md), [Confidence](https://docs.typesafe.ai/confidence.md), [building](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md), [coding agents](https://docs.typesafe.ai/introduction/coding-agents.md), [jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md), all four Patterns (intent-routing, confidence-routing, composite-scoring, fan-out), [classification cookbook](https://docs.typesafe.ai/cookbooks/classification_using_confidence.md), [Choice](https://docs.typesafe.ai/primitives/choice.md), [OpenRouter SDK route](https://openrouter.ai/docs/guides/community/typesafe-sdk).
