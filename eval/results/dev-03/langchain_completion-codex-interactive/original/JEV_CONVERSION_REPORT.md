# Jev conversion report

No good Jev opportunities here. `workflow.ts:15` streams unrestricted generated text into an HTTP response. A typed decision cannot preserve that contract.

Source revision: `00af35f119161b793a756fb96c69abfcba2225d1` on `main`.
Output mode: branch, `jev-convert/evaluation`, in `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/langchain_completion-codex-interactive/original`. No clone was created.

The approved predicate was fallback only for pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged and preserve all externally observable fields. It matches zero sites. Converted sites: none. Unchanged site: `workflow.ts:15` (GENERATION / NOT A FIT).

Only the plan, JSON audit and this report were added. Source, public fields, streaming adapter, diagnostics, model parameters, dependencies and credential configuration are unchanged. The original provider remains OpenAI through LangChain using `gpt-3.5-turbo-0125` at temperature 0. Selected Jev access was OpenRouter / `typesafe/jev-1.13-20260917`, but no Jev calls or integration were made.

## Validation

No upstream project test command exists. Executed independent behavior smoke:

```sh
node '/Users/bigsoup/Downloads/Jev Converter/eval/smoke.cjs' '/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/langchain_completion-codex-interactive/original' langchain_completion
```

Exit 0: `PASS: observable TypeScript behavior and original-path fallback smoke`.
This is behavior smoke evidence, not live model parity or a test of any new Jev fallback wrapper.

Preflight passed and confirmed key presence without exposing its value. No live validation was performed because there are zero converted sites. Live sample count: 0; input provenance, agreement curve, fallback rate, latency, cost, injected Jev faults and threshold recommendation are not applicable. No JEV_PARITY.json was created and no measured parity or savings are claimed. The authorized isolated baseline route was unused.

Artifact shape validation is run with:

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 .agents/skills/jevify/scripts/check_artifacts.py .
```

Artifact checker result: exit 0, `shape_valid: true`, no errors. This checks artifact structure only.

## Limitations and undo

The smoke validates observable behavior under its harness, not live provider availability or unrestricted production inputs. No generative quality measurements were performed. The original unrestricted input handling remains intact.

After the report commit, undo by running `git switch main` then `git branch -D jev-convert/evaluation`. The original main branch remains at the recorded source revision. Nothing was pushed and no PR was created.
