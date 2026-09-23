# Jev conversion report

**No good Jev opportunities here.** The approved pure-DECISION predicate matches zero sites. `workflow.ts:7` remains unchanged; converted sites: `[]`.

## Output and scope

Source revision: `c401444f0ce28166917950472c12af94424e44a8` on `main`. Output: branch `jev-convert/evaluation` in the original repository (branch mode, not clone mode). Only JEV_CONVERSION_PLAN.md, JEV_AUDIT.json and this report are added. All source behavior, schema, prompt, OpenAI model/provider, recipe fields, token usage, finish reason and error handling are preserved. No dependencies or environment files changed.

The selected Jev provider/pin would be OpenRouter / `typesafe/jev-1.13-20260917`, but no Jev integration or provider call was warranted. The authorized same-model baseline route was not used. No credentials were accessed, printed or saved.

## Executed validation

Command:

```sh
node '/Users/bigsoup/Downloads/Jev Converter/eval/smoke.cjs' '/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-01/vercel_recipe-codex-interactive/original' vercel_recipe
```

Result: exit 0; `PASS: observable TypeScript behavior and original-path fallback smoke`.

This smoke transpiles and executes the actual workflow with original-provider SDK doubles. It asserts one original call and logged recipe text containing lasagna. It does not prove real-provider inference or assert every diagnostic field. Source equality against the recorded revision independently verifies that diagnostics, original parameters and error handling were not edited. There is no project test command or manifest in this vendored example. The smoke file was read and executed, never edited.

## Evidence and limitations

Live validation skipped: no converted sites, so paired measurement is not applicable. Live pairs n=0; agreement, confidence curves, fallback rates, latency, cost, calibration/check sets and threshold recommendations are not measured or applicable. No new wrapper exists, so no Jev fault-injection assertions were executed. No parity or savings claim is made and no JEV_PARITY.json is created.

The prior supplied audit identified generation as unsupported. A fresh live jaggedness-document fetch failed in this turn; the installed skill and vendored official TypeSafe skill also explicitly distinguish typed decisions from text generation. No version-dependent integration was introduced. Repository inspection stayed within this repository, except the explicitly supplied config and permitted smoke script. No labels, graders, other runs or corpus files were read.

## Undo

The original branch ref is unchanged. From this repository, after preserving any subsequent work:

```sh
git switch main
git branch -D jev-convert/evaluation
```

No push or PR was performed.
