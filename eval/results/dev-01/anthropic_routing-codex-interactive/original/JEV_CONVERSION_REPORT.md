# Jev conversion report

No good Jev opportunities here. The approved predicate matched zero sites; no workflow conversion was performed.

Source revision: `444c1aad9442a670679de44a5ab786edb9e11cce` on `main`.
Output: branch `jev-convert/evaluation` in `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-01/anthropic_routing-codex-interactive/original`. Only the three audit/plan/report artifacts were added.

`workflow.py:24` remains MIXED because its generated routing explanation is printed. `workflow.py:34` remains GENERATION. `util.py:23` remains their shared MIXED transport. All source semantics, observable diagnostics, original Anthropic provider/model (`claude-sonnet-4-6`), parameters, parsing and exception behavior remain unchanged. See JEV_AUDIT.json for full site evidence and JEV_CONVERSION_PLAN.md for approval resolution.

## Validation

Executed with Python 3.14:

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 '/Users/bigsoup/Downloads/Jev Converter/eval/smoke.py' '/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-01/anthropic_routing-codex-interactive/original' anthropic_routing
```

Result: exit 0, `PASS: observable Python behavior and original-path fallback smoke`.
This supplied offline behavior check injects an original-SDK double and replaces route's llm_call with deterministic selector and specialist responses. It asserts returned specialist prose and printed routing reasoning. It does not establish real provider inference, complete error-path coverage, or Jev fallback behavior. No new fallback exists to validate. The smoke file was read and executed without modification. There is no upstream project test command.

Live validation skipped: no converted sites, so paired comparisons are not applicable. No live requests, baseline adapters, measurements, confidence curves, fallback rates, latency or cost estimates were produced. Live input count: 0. No parity claim and no JEV_PARITY.json. Per-site thresholds and injected Jev fault tests: not applicable. The authorized same-model OpenRouter evaluation route was unnecessary and was not used; production provider remains unchanged.

## Handoff and undo

Artifacts: JEV_AUDIT.json, JEV_CONVERSION_PLAN.md, JEV_CONVERSION_REPORT.md. Work is committed on the conversion branch; no push or PR.

To undo after ensuring no unrelated uncommitted work is present:

```sh
git switch main
git branch -D jev-convert/evaluation
```

The original main branch remains at the source revision. No clone was created.
