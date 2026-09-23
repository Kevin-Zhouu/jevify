# Jev Conversion Plan

## Preflight

| Field | Value |
|---|---|
| Repository | `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-03/anthropic_routing-claude-headless/original` |
| Source revision | `922b8f0749ed0b927595fdff9ae34aa49e33dd99` (main) |
| Output mode | **report** (no code changes) |
| Provider | OpenRouter (`OPENROUTER_API_KEY`) |
| Model pin | `typesafe/jev-1.13-20260917` |
| Risk posture | conservative |
| Repo clean | yes |
| Key present | yes |

## Audit

### LLM Call Sites

Three LLM call sites were identified. The `llm_call` wrapper in `util.py` is the shared transport; `workflow.py` has two consumer call sites.

#### Site 1: `util.py:22` — Shared wrapper (`client.messages.create`)

- **Provider:** Anthropic SDK / claude-sonnet-4-6
- **Consumers:** `workflow.py:24` (route selection + reasoning), `workflow.py:34` (prose generation)
- **Classification:** MIXED — serves both DECISION and GENERATION consumers
- **Fit:** NOT A FIT — cannot convert a shared wrapper that serves generation consumers

#### Site 2: `workflow.py:24` — Route selector (`llm_call(selector_prompt)`)

- **Provider:** Anthropic SDK / claude-sonnet-4-6 (via wrapper)
- **Input:** User ticket text + available route keys `{billing, technical, account, product}`
- **Downstream:** Extracts `<reasoning>` (printed to stdout, line 29) AND `<selection>` (used as dict key, line 33)
- **Classification:** MIXED — returns and prints explanatory reasoning alongside the routing decision
- **Fit:** CONDITIONAL — the routing selection is a strong Jev Choice candidate (closed 4-option set, semantic intent classification, trusted internal input), but the printed reasoning makes the site MIXED. Decomposition could separate the decision from reasoning, but `decompose` is not in the approved action set.

#### Site 3: `workflow.py:34` — Support response generator (`llm_call(selected_prompt...)`)

- **Provider:** Anthropic SDK / claude-sonnet-4-6 (via wrapper)
- **Input:** Specialized prompt template + user ticket
- **Downstream:** Returns prose support response to caller
- **Classification:** GENERATION — pure prose output
- **Fit:** NOT A FIT — Jev cannot generate text

### Wrapper Relationship

`util.py:llm_call` wraps `anthropic.Anthropic().messages.create()`. Both consumer sites in `workflow.py` call through this wrapper. The wrapper's MIXED classification reflects its combined usage; cost/latency savings from converting a consumer do not double-count with the wrapper.

## Approval Resolution

**Approval predicate:** "Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged."
**Approved actions:** `[fallback]`

| Site | Classification | Matches predicate? | Action |
|---|---|---|---|
| `util.py:22` | MIXED | No | leave |
| `workflow.py:24` | MIXED | No | leave |
| `workflow.py:34` | GENERATION | No | leave |

**Result: No sites qualify for conversion.** Zero sites are pure DECISION. The routing decision at `workflow.py:24` has a strong Jev fit for its selection component, but the printed reasoning text makes the entire site MIXED, which the approval explicitly excludes.

## Options Table

| Site | Classification | Fit | Option 1 | Option 2 |
|---|---|---|---|---|
| `util.py:22` | MIXED | NOT A FIT | **leave** — shared wrapper, no change | — |
| `workflow.py:24` | MIXED | CONDITIONAL | **decompose** (Choice) — split routing decision from reasoning; not approved | **leave** — preserve current behavior |
| `workflow.py:34` | GENERATION | NOT A FIT | **leave** — Jev cannot generate prose | — |

## Selected Actions

No conversions. All sites left unchanged per approval predicate resolution.

## Conclusion

**No good Jev opportunities here** under the given approval constraints. The routing decision at `workflow.py:24` is semantically well-suited for Jev Choice (closed 4-option intent classification over trusted text), but the site is MIXED because it also generates and prints explanatory reasoning. The approval scope requires pure DECISION sites and explicitly excludes MIXED sites. The generation site at `workflow.py:34` is inherently not a Jev candidate. A future approval authorizing `decompose` on `workflow.py:24` would enable extracting the routing decision to Jev Choice while retaining a separate LLM call (or removal) for reasoning text.
