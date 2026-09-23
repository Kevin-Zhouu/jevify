# Jev conversion report

**No good Jev opportunities here.** `workflow.ts:15` is GENERATION: arbitrary streamed
completion text is the endpoint's result. Jev's typed decisions cannot preserve that
contract. See [Jev 1.13 generation limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md#generation).

Source revision: `f16140e0900995cd09ae48d9ec833b9866309f56`; original branch: `main`.
Output mode: **report**. Output directory: `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/langchain_completion-codex-headless/original`.
The config's inactive branch and clone_path fields do not authorize either operation.
Preflight passed: git available, repository clean (including untracked files), no errors.
`OPENROUTER_API_KEY` was present; only presence was checked. Configured Jev provider/model:
OpenRouter / `typesafe/jev-1.13-20260917`; neither was invoked or added to production.
Risk posture: conservative. Upfront approval permits fallback only for pure DECISION sites
with enumerated outputs. It matches **zero sites**. GENERATION remains unchanged.
The isolated same-model OpenRouter baseline authorization was not needed.

## Outcome

| Original site | Provider/model | Classification | Downstream | Fit | Option, primitive, benefit and risk |
| --- | --- | --- | --- | --- | --- |
| workflow.ts:15 | LangChain ChatOpenAI / OpenAI gpt-3.5-turbo-0125, temperature 0 | GENERATION | Stream → LangChainAdapter.toDataStreamResponse → HTTP caller | NOT A FIT | leave; none; preserve complete streaming generation, unchanged latency/cost; no migration-induced risk, existing provider/input risks remain |

Changed sites: none. Unchanged sites: `workflow.ts:15`. Converted sites: `[]`.
Only the three requested report artifacts were created. Production code and diagnostics
remain byte-for-byte unchanged. No dependencies, env placeholders or decisions module
were added because this is report-only with no eligible conversion. No commit, branch,
clone, push or PR was created.

`workflow.ts` is the only application source found. There is no package manifest,
lockfile, project test command, local SDK wrapper, notebook, or local AGENTS.md guidance.
Installed skill directories were excluded from application call searches.
`ChatOpenAI` construction at lines 10–13 configures the single inference call at line 15;
it is not an additional inference site. The imported SDK contains the provider transport,
but there is no local wrapper/provider implementation to inventory separately.
`LangChainAdapter` at line 17 consumes the stream; it is not another model call.

Input flows from `req.json().prompt` (line 8), unchanged into `model.stream(prompt)`.
There is no local prompt template, extraction parser, finite candidate list, branching
classification, or generated decision consumed by code. The entire generated stream is
public output. Its SDK/adapter semantics, errors, metadata and diagnostics must remain
intact; upstream has no explicit logging or catch/retry logic here. `POST` remains async,
and the exported `maxDuration` stays 30. Context is request-dependent, with no local
size bound or effective untrusted-input mitigation demonstrated. No robustness is inferred.

A new router or guardrail would require new policy and change behavior; it is neither an
existing decision to replace nor covered by the fallback-only approval. Jev cannot supply
the arbitrary generated text required by this endpoint.

## Validation

The example has no project test command. Executed supplied independent smoke:

```sh
node /Users/bigsoup/Downloads/Jev\ Converter/eval/smoke.cjs "/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/langchain_completion-codex-headless/original" langchain_completion
```

Exit code: 0. Output: `PASS: observable TypeScript behavior and original-path fallback smoke`.
It transpiles and executes the actual TypeScript entrypoint using original SDK test doubles,
checks prompt `hello` yields response `stream:hello`, checks `maxDuration === 30`, and checks
exactly one original provider call. Network is disabled by the harness. It does not prove
real SDK streaming wire details, full type checking, provider availability or model quality.
The smoke file was read but never edited; it generated no repository artifacts.

Live validation skipped as not applicable: zero converted sites, although the configured
key is present. No paired inputs, live requests, parity measurements, confidence curve,
fallback rate, latency, cost or injected Jev fault assertions were performed. No
`JEV_PARITY.json` was created, and no parity or measured savings are claimed.
Per-site threshold recommendation for `workflow.ts:15`: not applicable; leave generation
unchanged. There is no Jev gate to calibrate or fallback policy to validate.

Artifact check command:

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 .agents/skills/jevify/scripts/check_artifacts.py .
```

Artifact checker passed with exit code 0, `shape_valid: true` and no errors; it checks shape only.
Final git diff was empty; status listed only the three new report artifacts.
The `--require-live` flag is inapplicable because no sites were converted.

## Undo

From `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/langchain_completion-codex-headless/original`, delete only these newly created artifacts:

```sh
rm -- JEV_CONVERSION_PLAN.md JEV_AUDIT.json JEV_CONVERSION_REPORT.md
```

No branch switch or clone removal is necessary. Source revision remains `f16140e0900995cd09ae48d9ec833b9866309f56`.
