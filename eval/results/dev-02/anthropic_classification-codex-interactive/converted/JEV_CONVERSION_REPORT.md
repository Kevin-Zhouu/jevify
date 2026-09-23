# Jev conversion report

Converted the approved pure DECISION site `workflow.py:83` using Choice with permanent original Anthropic fallback. Original wrapper at line 65 is the same opportunity. No MIXED or GENERATION sites exist in this repository. No other options were implemented.

Source revision: `eff84f8f58d676d6b3b2eb21ae7b906300e2ef1b` (`main`). Output: sibling `converted` clone, branch `jev-convert/evaluation`. Original repository unchanged. No push or PR.

## Contract and implementation

`simple_classify(X)` remains synchronous and returns a string. The original callable was renamed `_original_simple_classify`; its complete AST is identical after normalizing that name. Categories, prompt substitutions, assistant prefill, stop sequence, temperature, max_tokens, model and `.strip()` parsing are unchanged. Production fallback is still `anthropic.Anthropic`, with its original initialization and exception behavior. No usage, response metadata or generated explanation was originally returned or printed.

`jev_decisions.py` owns all Jev policy: OpenRouter `typesafe/jev-1.13-20260917`, exact original ten category descriptions (whitespace normalized), Choice instructions, 0.90 confidence threshold, 10-second transport timeout, no retries, and 16000-byte UTF-8 state bound. Oversize/unsupported inputs bypass without truncation. Unknown labels, missing/malformed usage/model/probabilities, nonfinite or out-of-range confidence, missing key and transport failures call the original once. Original exceptions propagate unchanged. Path/model/bounded reason use Python INFO logging; configure the application logger to observe them. No raw inputs, credential values or exception text are logged. Stdout is unchanged. No dependency added.

## Live validation

44 unique live pairs completed with no transport failures: 20 calibration tickets from data/train.tsv, 20 confirmation tickets from data/test.tsv, and 4 synthetic ambiguous/short/out-of-domain confirmation tickets. Two tickets per category were selected deterministically from each fixture file. Fixture labels only stratify sampling; comparisons use actual original live responses, never fixture labels as a proxy baseline.

The evaluation-only Anthropic transport adapter in `validate_jev.py` invokes the preserved original callable, forwarding its unchanged messages (including assistant prefill), max_tokens and temperature to OpenRouter `anthropic/claude-haiku-4.5`, the authorized same-model route. `stop_sequences` maps to OpenRouter `stop`. Production provider is unchanged. This evaluates routed-model agreement, not direct-Anthropic service latency. An AST assertion verifies the original callable's request construction and parsing. Each live Jev response is also replayed through the public wrapper and actual gate, checking return value and exact fallback count. Replays are integration tests, not additional live measurements.

The 0.90 threshold was fixed before measurement and retained, without tuning on confirmation. It exceeded the 90% accepted-agreement target in both partitions. Calibration: 15/16 accepted agree (93.75%), 20% fallback. Confirmation: 14/15 accepted agree (93.33%), 37.5% fallback. All pairs: raw agreement 38/44 (86.36%); selective agreement 29/31 (93.55%); fallback 13/44 (29.55%). Cascade agreement after fallback is 42/44, not raw Jev parity.

| Threshold | Accepted / 44 | Accepted agreement | Fallback |
| --- | --- | --- | --- |
| 0.00 | 44 | 86.36% | 0.00% |
| 0.50 | 41 | 90.24% | 6.82% |
| 0.70 | 37 | 94.59% | 15.91% |
| 0.80 | 34 | 94.12% | 22.73% |
| 0.90 | 31 | 93.55% | 29.55% |
| 0.95 | 25 | 96.00% | 43.18% |
| 0.99 | 22 | 100.00% | 50.00% |
| 1.00 | 21 | 100.00% | 52.27% |

Two accepted disagreements remain: data/train.tsv:29 at 0.95 and data/test.tsv:28 at 0.91 both select Coverage Explanations where original Claude selects Policy Administration. All six raw disagreements remain visible in JEV_PARITY.json. Higher thresholds in the table are exploratory, not independently validated alternatives. Recommend retaining 0.90 only for the evaluated benign ticket distribution, with fallback; if exact agreement is required, retain the original classifier. This small sample does not prove semantic equivalence or production accuracy.

Measured latency (monotonic wall time): Jev p50 362 ms / p95 556 ms; routed original p50 1074 ms / p95 1703 ms. Mean original latency 1201 ms; estimated serial-cascade mean 737 ms. Cascade estimate sums each Jev duration and its paired original duration only when fallback is taken; it is not a separately measured production cascade. Four concurrent evaluation workers; per-request durations include transport overhead.

Costs are actual OpenRouter `usage.cost`, not price-table estimates: mean Jev $0.00003142, mean original $0.00071634, estimated cascade mean $0.00024192 (about 66.2% lower on this sample). Fallback calls add Jev cost and latency; savings depend on traffic. Request IDs, pinned response model, real usage and costs are recorded in JEV_PARITY.json. No pricing assumptions were needed.

## Executed checks

- `python3.14 validate_jev.py`: 44 live pairs; public-wrapper replay of every captured response; AST equality; timeout, HTTP 429, generic transport error, missing key, malformed response, invalid confidence, unknown label, missing usage, oversize input, exactly-once fallback, original exception propagation, and forced below-threshold gate checks passed. Successful Jev outputs were never fabricated.
- `/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/bigsoup/Downloads/Jev\ Converter/eval/smoke.py /Users/bigsoup/Downloads/Jev\ Converter/eval/runs/dev-02/anthropic_classification-codex-interactive/converted anthropic_classification`: PASS, original fallback behavior and return contract.
- `git diff --check`: PASS.
- Artifact checker with `--require-live`: PASS (shape_valid true; no errors). Shape checking does not itself prove live provenance.

No upstream project test command exists. Validation script uses a local evaluation transport shim; the production Anthropic SDK dependency and configuration are unchanged.

## Setup, limitations and undo

Set `OPENROUTER_API_KEY` and the existing `ANTHROPIC_API_KEY` through the environment; `.env.example` contains empty placeholders only. For hidden key entry, use `.agents/skills/jevify/scripts/with_jev_key.py` (consult `--help`) to launch a command without placing a key in shell arguments. No credentials are saved.

Approval and fit are limited to benign support tickets. Arbitrary adversarial input has no effective defense here; instruction wording and confidence do not establish injection resistance. Do not interpret these fixture results as validation for adversarial public traffic. The confirmation sample is small and repository tickets can be semantically similar. Same-model gateway routing can differ operationally from direct Anthropic. Production fallback remains mandatory.

Undo by deleting the sibling `converted` clone; the original repository and its main branch remain unchanged. Alternatively, within the clone, switch to `main` to use the unmodified workflow. All commits are local.
