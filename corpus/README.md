# Pinned upstream workflow corpus

Six DEV workflows and two sealed HELD-OUT workflows are listed in manifest.json.
Each directory contains upstream source and license, with source commit and
SHA-256 provenance. Anthropic notebook slices concatenate unchanged cells or
exact AST source segments, as specified in PROVENANCE.json. We do not edit these
sources during the improvement loop.

DEV coverage:

| Workflow | Language | Provider abstraction | Purpose |
| --- | --- | --- | --- |
| anthropic_classification | Python | Anthropic SDK | Insurance support classification |
| anthropic_routing | Python | Anthropic SDK wrapper | Route selection, visible reasoning, specialist generation |
| vercel_enum | TypeScript | Vercel AI SDK / OpenAI | Movie genre classification |
| vercel_recipe | TypeScript | Vercel AI SDK / OpenAI | Recipe generation (negative control) |
| openai_demo | Python | OpenAI SDK | Text generation and streaming (negative control) |
| langchain_completion | TypeScript | LangChain / OpenAI | HTTP streaming completion (negative control) |

Upstream examples have no dedicated test suite. `eval/smoke.py` and
`eval/smoke.cjs` execute their behavior with original-provider test doubles;
they do not impersonate Jev. These evaluator-supplied smoke checks are separate
from the required live Jev parity checks. All six DEV baseline smokes pass.

For normal live use, Python examples require the matching `anthropic` or `openai`
package and provider credentials. TypeScript examples use the dependency versions
recorded in `eval/package.json` (Vercel source is pinned to the ai@4.3.16 release).
The LangChain example exports a Request-to-Response POST handler for a Next.js
application; the smoke invokes that handler directly. Python notebook slices
export `simple_classify(text)` and `route(text, support_routes)` respectively.

Assembly script: `tools/assemble_corpus.py`. Do not rerun it over the frozen corpus.
HELD-OUT directories must not be inspected or used for skill development.
