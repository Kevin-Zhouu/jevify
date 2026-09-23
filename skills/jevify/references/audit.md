# Read-only audit and recommendations

Start with manifests, lockfiles, configs and entrypoints. Search SDK imports, aliases and calls: OpenAI chat/responses/parse/stream, Anthropic messages, OpenRouter base URLs, LiteLLM completion/acompletion, LangChain invoke/ainvoke/stream/batch, Vercel generateText/streamText/generateObject/streamObject, custom HTTP URLs, tool/agent abstractions. Exclude dependencies/build caches/installed skills, but inspect runnable examples, notebooks and tests. Use AST where available and text search plus reference tracing; a search hit alone is not a classification. Record relevant wrapper call sites as well as their transport site; tie them together to avoid double-counting savings. Trace all shared wrapper consumers, not just the most promising one.

For every site record original file and line, SDK/provider/model, input origin, complete downstream path, classification, fit reason, context size and untrusted-input mitigation. Distinguish value semantics from envelope metadata (usage, IDs, finish reasons).

| Classification | Meaning |
|---|---|
| DECISION | The model's substantive answer is a label, bool, route, ordered score or one closed-set selection. Metadata is a separate contract concern. |
| GENERATION | Prose, code, explanations, recipes, arbitrary schema strings or other free-form content. Structured JSON does not make it a decision. |
| MIXED | One site supplies both decisions and generation, including reasoning that is printed, returned or logged, or a shared wrapper serving both kinds of consumer. |
| EXTRACTION | Pulls values from text. Only consider Choice once code can enumerate all candidates and explicitly handle missing/ambiguous candidates. |

Do not relabel a call just to make conversion convenient. A router that returns and prints explanatory reasoning is MIXED even if only its route controls execution. A closed enum with token/finish diagnostics is DECISION but must preserve truthful diagnostics in any adapter. A schema with open-ended strings remains GENERATION. The shared SDK wrapper gets the classification of its entire observed usage.

Use the live jaggedness page: https://docs.typesafe.ai/model-jaggedness/jev-1.13.md . Mark NOT A FIT with concrete evidence for math/counting, date comparison, multi-hop reasoning, generation, non-text input, context beyond documented limits without filtering, or likely adversarial input without an effective mitigation. A proposed mitigation is not an existing mitigation: mark conditional eligibility and include that change in the option for approval. Exact rules/calculations stay in code. Confidence is not a prompt-injection defense. Quoting user text alone does not prove adversarial robustness. For benign fixed fixtures, scope the verdict to that distribution, not a public production service.

Read these before recommending: building guide and coding-agents; Models and Confidence; Patterns intent-routing, confidence-routing, composite-scoring, fan-out. Choose relevant cookbooks from the official skill's index (e.g. pre-parsed extraction, function calling, guardrails, hierarchical classification). Do not blindly clone cookbook thresholds.

## Table and artifacts

Each row has an original `file:line` ID, provider, downstream use, class and fit. Give 1–3 options per site. Use action names `fallback`, `jev_only`, `decompose`, `router`, `leave`. Every option needs nonempty string fields; use primitive `none` for leave (not null). Describe exact scope and primitive (Choice/Score/Noul or none). For each, state benefits, risk and economics:
- Choice plus confidence fallback: likely cheaper accepted decisions; serial misses add Jev latency and cost before original inference. Expected cost = Jev cost + fallback fraction × original cost.
- Jev-only: removes original cost only after representative parity is proven; residual errors and outage policy remain. Conservative posture excludes this option from selections.
- Atomic questions combined in code: interpretable dimensions, potentially extra tokens/questions; preserve dependencies, do not invent arithmetic reasoning by Jev.
- Router/guardrail: retains generation, saves cost only on traffic actually avoided or rerouted; false blocks/routes must be evaluated.
- Leave: no speculative savings; explain mismatch or contract risk.

A leave-only option is valid for no-fit sites. Do not invent an opportunity to satisfy the request. For all-negative audits explicitly say “No good Jev opportunities here,” with site-specific reasons. Never offer GENERATION as Jev-only.

After approval, save the full table and selected plan in `JEV_CONVERSION_PLAN.md`. Also write:

```json
{"sites":[{"file":"src/route.ts","line":42,"provider":"OpenAI SDK / gpt-4o-mini","downstream":"returned enum selects handler in dispatch()","classification":"DECISION","fit":"FIT","reason":"bounded semantic routing over trusted text","options":[{"action":"fallback","primitive":"Choice","benefit":"...cost and latency direction with reason...","risk":"..."}]}],"converted_sites":["src/route.ts:42"]}
```

Use original IDs even when edits shift line numbers. `converted_sites` lists actually converted sites, not merely approved ones; an empty list is mandatory if nothing changed. Summarize wrapper relationships in the plan so totals do not double count.
