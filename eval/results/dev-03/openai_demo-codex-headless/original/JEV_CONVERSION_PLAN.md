# Jev conversion plan

No good Jev opportunities here.

Source revision: `8b1da0a4d7505b22c1f92283ef848616de773eab`; branch: `main`.
Output mode: **report**. Output repository: `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/openai_demo-codex-headless/original`.
The inactive branch and clone_path config fields do not authorize branch creation or cloning.
Preflight passed: git available, repository initially clean including untracked files, no errors.
Selected access: OpenRouter, environment variable `OPENROUTER_API_KEY`; presence checked and true. No credential value was printed or saved.
Configured Jev pin: `typesafe/jev-1.13-20260917`; not invoked. Risk: conservative.

Approval resolves to zero eligible sites. All three are GENERATION. The configured fallback predicate covers only pure DECISION sites with enumerated outputs. Report mode permits only report artifacts. The authorized same-model OpenRouter baseline route is unused because nothing is converted.

## Audit and options

| Original site | Provider | Class / fit | Downstream | Option / primitive | Benefit and economics | Risk |
|---|---|---|---|---|---|---|
| `workflow.py:10` | OpenAI Python SDK / OpenAI / gpt-5.5 | GENERATION / NOT A FIT | completion.choices[0].message.content is printed at workflow.py:19, after the standard-request banner at line 9. | `leave` / `none` | Preserves original generation and diagnostics. Expected latency and cost unchanged because the original request remains; no speculative Jev savings. | Existing OpenAI dependency remains; replacing the call with a canned phrase or Choice would change the demonstrated completion behavior. |
| `workflow.py:23` | OpenAI Python SDK / OpenAI / gpt-5.5 | GENERATION / NOT A FIT | The stream is iterated at lines 33–37; empty choices are skipped, delta.content is printed with end="", then a newline at line 38. | `leave` / `none` | Preserves original generation and diagnostics. Expected latency and cost unchanged because the original request remains; no speculative Jev savings. | Existing OpenAI dependency remains; a typed answer or synthetic stream would lose generated guidance and native delta semantics. |
| `workflow.py:42` | OpenAI Python SDK / OpenAI / gpt-5.5 | GENERATION / NOT A FIT | with_raw_response.create returns a response parsed at line 51; response.request_id is printed at line 52 and completion text at line 53. | `leave` / `none` | Preserves original generation and diagnostics. Expected latency and cost unchanged because the original request remains; no speculative Jev savings. | Existing OpenAI dependency remains; fabricating request IDs or changing the raw response/parser would corrupt observable diagnostics. |

All requests use fixed short text, not runtime user input. Text lengths are recorded in JEV_AUDIT.json; tokens were not measured. No adversarial robustness is claimed beyond the fixed fixtures.
The repository contains one runnable workflow, no shared local provider wrapper, no project test command, and no applicable AGENTS.md was found within the repository. The three direct provider calls are three independent sites; parsing, printing and stream iteration are consumers, not extra inference sites. Installed skills are not workflow call sites.

Line 10 is generation even though its prompt requests a short known phrase: downstream prints arbitrary response content rather than parsing an enum. Line 23 needs generated Python guidance and streaming. Line 42 needs generated text plus truthful raw-response diagnostics. Candidate-span extraction, routing, scoring and fan-out do not match these contracts. Adding a router would add an unrequested decision and could suppress required SDK demonstrations.

## Selected work

Leave all sites unchanged. Write only JEV_CONVERSION_PLAN.md, JEV_AUDIT.json and JEV_CONVERSION_REPORT.md in the original repository. Preserve source, prompts, model, exceptions, stdout banners, delta behavior, request ID, dependencies and environment files. No branch, clone, commit, push or PR.
Run the supplied independent behavior smoke using Python 3.14, then the skill artifact checker. No converted sites means no live paired comparisons are required and no JEV_PARITY.json should be fabricated.

## Documentation basis

Reviewed the installed official TypeSafe skill and live documentation on 2026-09-23. The index was accessible through web; individual Markdown pages were fetched successfully with Python HTTPS after web-tool failures. Generation limitations are explicit in coding-agents and Jev 1.13 jaggedness. Pre-parsed extraction was reviewed to check whether fixed text could justify a selection task; this workflow has no such consumer.

- [api](https://docs.typesafe.ai/api.md)
- [models](https://docs.typesafe.ai/models.md)
- [confidence](https://docs.typesafe.ai/confidence.md)
- [concepts/how-to-build-with-system-one](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md)
- [introduction/coding-agents](https://docs.typesafe.ai/introduction/coding-agents.md)
- [model-jaggedness/jev-1.13](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md)
- [patterns/intent-routing](https://docs.typesafe.ai/patterns/intent-routing.md)
- [patterns/confidence-routing](https://docs.typesafe.ai/patterns/confidence-routing.md)
- [patterns/composite-scoring](https://docs.typesafe.ai/patterns/composite-scoring.md)
- [patterns/fan-out](https://docs.typesafe.ai/patterns/fan-out.md)
- [cookbooks/pre_parsed_value_extraction_cookbook](https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook.md)
