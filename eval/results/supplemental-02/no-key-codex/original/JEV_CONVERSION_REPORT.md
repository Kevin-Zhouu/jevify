# Jev conversion report

Completed approved conservative code conversion on branch `jev-convert/no-key` in the original repository. Source branch `main` at `2160130f0ffe291eff8623e4f83bc38fef8499d5` remains unchanged. Approval came from the supplied headless config predicate: pure DECISION sites with enumerated outputs, fallback retained. Resolved site: `workflow.py:83` only.

`simple_classify(X)` delegates to `jev_decisions.py`, which owns the Choice question, ten original category definitions, `jev-1.13.0` pin, provisional 0.9 confidence threshold, 8000-byte input limit and 3-second transport timeout with no retries. No new dependencies. Anthropic `claude-haiku-4-5`, its prompt, assistant prefill, stop sequence, parameters, stripping and exceptions remain unchanged. AST equality verifies the preserved original implementation. No usage/finish metadata was exposed by the original API. Logs use the module logger, include path/model and bounded reasons, and do not include inputs or secrets.

Access selected: none. The dormant HTTP adapter supports TypeSafe direct; this run made no inference requests and switched no fallback provider. Process presence checks found neither TYPESAFE_API_KEY nor ANTHROPIC_API_KEY. `.env.example` contains placeholders only. For a future explicitly configured trusted offline run, use the skill's `.agents/skills/jevify/scripts/with_jev_key.py --help` hidden-input launcher, provide original Anthropic access, and set JEV_TRUSTED_INPUTS=1. No secret files were read or created.

Jev remains disabled without credentials and explicit trusted-input opt-in. This is conditional eligibility for reviewed offline inputs; it is not a prompt-injection defense. Public adversarial input use is not validated or recommended. Dataset/corpus and evaluation labels were not read. No data fixtures were used to infer suitability. Questions describe the same application taxonomy but semantic parity remains unknown.

Validation executed with `/opt/homebrew/opt/python@3.14/bin/python3.14`:

- User-supplied independent command: `/opt/homebrew/opt/python@3.14/bin/python3.14 "/Users/bigsoup/Downloads/Jev Converter/eval/smoke.py" "/Users/bigsoup/Downloads/Jev Converter/eval/runs/supplemental-02/no-key-codex/original" anthropic_classification` — PASS, observable Python behavior and original-path fallback. Smoke file was neither read nor edited.
- `-m unittest -v test_jev_decisions` — 6 tests passed. Missing credential and trust gate, malformed response, unknown label, nonfinite confidence, oversize input, timeout, HTTP 429, generic transport error, exactly-once fallback and original exception propagation. Below-threshold assertion uses the pure production predicate, not invented successful inference.
- `git diff --check` — passed.
- Artifact checker command: `python3.14 .agents/skills/jevify/scripts/check_artifacts.py .` (result recorded below).

**Live validation skipped.** No successful Jev response was mocked or replayed. Paired sample n=0; raw/selective agreement, confidence curve, fallback rate, p50/p95 latency and cost are unknown, not zero. Accepted-path end-to-end behavior has not been verified using a real Jev response. Synthetic strings in fault tests exercise control flow only. JEV_PARITY.json contains empty rows and executed fault evidence, not parity measurements.

Per-site recommendation for workflow.py:83: retain fallback and keep trusted-input opt-in disabled pending live calibration and an independent check set of at least 30 unique realistic pairs through the original callable and actual decisions module. The 0.9 threshold is provisional, not a measured recommendation. Compare accepted agreement across thresholds and measure fallback/latency/cost before deployment. Expected cascade cost is Jev cost plus fallback fraction times original cost; serial misses add latency. No savings have been measured.

Audit/options/preflight: JEV_CONVERSION_PLAN.md and JEV_AUDIT.json. No other model sites, generation, or extraction paths were changed. Public docs: [HTTP API](https://docs.typesafe.ai/api.md), [Models](https://docs.typesafe.ai/models.md), [limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md), plus the required patterns/building/confidence/coding-agent pages and classification cookbook were consulted on 2026-09-23.

Undo after saving any future work: `git switch main`, then `git branch -D jev-convert/no-key`. No push or PR was performed.

Artifact checker result: shape_valid=true, no errors. This validates artifact structure only.
