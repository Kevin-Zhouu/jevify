# Approved conversion plan

Source: 4bc5e23750b6af7d32147d2480a5bde33bb935cb, original main. Clone: ../converted, branch jev-convert/evaluation. Preflight: clean, destination unused, OPENROUTER_API_KEY present (value never read into artifacts). No project manifest or test command; use supplied independent smoke.

| Original site | Provider | Downstream | Class / fit | Options | Selection |
|---|---|---|---|---|---|
| workflow.ts:6 | Vercel AI SDK / OpenAI gpt-4o-mini | main prints enum (16), usage (18), finish reason (19); errors console.error (22) | DECISION; conditional fit for short benign movie plots | A: fallback / Choice, avoids original inference on accepted results but serial fallback adds cost and latency; risk: disagreement and metadata mapping. B: leave / none, unchanged cost and behavior | A approved; B declined |

Only this provider site exists; no shared wrappers or additional consumers. Input is a fixed English movie plot, with five genres. No hostile-input mitigation is claimed. No generation or mixed site is approved. Preserve the original options, SDK parser, provider, stdout order, usage shape and error handler.

## Wiring proof (before validation implementation)

Original: workflow.ts main -> generateObject(options). Converted: main -> withGenreFallback(options, generateObject). The original options expression remains byte-identical; original SDK callable executes outside the protected Jev try/catch. jevDecisions.ts owns evaluateGenre, parseGenre, acceptsConfidence, withGenreFallback, questions and pinned model. Validation loads the actual TS modules with TypeScript transpilation, captures options by executing original source from git, and asserts identity with options entering the converted wrapper. For each synthetic case, replace only the original fixture string through its AST location in both entrypoints. Baseline runs real generateObject and its parser with createOpenAI transport; only auth, endpoint and model namespace change to authorized OpenRouter openai/gpt-4o-mini. Production remains OpenAI.

One Jev inference per row: capture actual response at fetch boundary while running the wrapper; count original callbacks; verify all four stdout calls and fallback identity. Replay captured responses for accepted-path and injected-fault assertions. Preserve sanitized response body only, never headers. Use 30 unique synthetic confirmation plots, preselect threshold 0.9 without calibration, retain disagreements. Report raw and accepted agreement, fallback rate, latency, provider-reported cost (unknown stays null).

## Contract and policy

Use OpenRouter System One with typesafe/jev-1.13-20260917. Single Choice, unchanged five labels. Provisional conservative confidence threshold 0.9, 10-second total timeout, no retries. Invalid model/type/label/confidence/distribution/usage, missing key, excessive state, transport failure or rejected confidence calls original once. Logs on stderr contain path/model/bounded reason only. Map actual input_tokens/output_tokens to promptTokens/completionTokens and arithmetic totalTokens. Adapter finishReason 'stop' means the typed decision completed; it is not native token termination metadata. The caller only prints generic completion status.

Documentation checked: https://docs.typesafe.ai/api, /models, /confidence, /primitives/choice, /model-jaggedness/jev-1.13, patterns and coding-agents pages; https://openrouter.ai/docs/guides/community/typesafe-sdk. Markdown URLs failed; normal pages used where available. Building-guide access limitations will be reported if unresolved.

Final documentation note: direct HTTP retrieval resolved building-guide access. A clone-local pinned package manifest/lockfile isolates the compatible original SDK versions for execution and reproducible validation. The deployed 0.9 threshold was not retuned.
