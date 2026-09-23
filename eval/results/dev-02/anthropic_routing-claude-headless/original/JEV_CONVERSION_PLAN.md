# Jev Conversion Plan

## Preflight

| Field | Value |
|-------|-------|
| Source revision | `d59165390fbe6d96614dde2278dc4fec3a35d4c7` (main) |
| Repository | `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/anthropic_routing-claude-headless/original` |
| Output mode | **report** (no code changes) |
| Provider | OpenRouter (`typesafe/jev-1.13-20260917`) |
| Key env | `OPENROUTER_API_KEY` (present) |
| Risk posture | conservative |
| Repo status | clean |

## Audit

### Site inventory

| ID | Provider | Downstream | Classification | Fit |
|----|----------|-----------|----------------|-----|
| `workflow.py:24` | Anthropic SDK / claude-sonnet-4-6 | Reasoning printed to stdout; selection used as dict key to route to specialist prompt | MIXED | CONDITIONAL |
| `workflow.py:34` | Anthropic SDK / claude-sonnet-4-6 | Free-form specialist response returned from `route()` | GENERATION | NOT A FIT |
| `util.py:22` | Anthropic SDK / claude-sonnet-4-6 | Shared `llm_call()` wrapper serving both sites above | MIXED | NOT A FIT |

### Wrapper relationships

`util.py:22` (`llm_call`) is the single shared transport wrapper. Both `workflow.py:24` and `workflow.py:34` call it. The wrapper itself is not a separate conversion target — any conversion applies at the consumer call sites. Total unique LLM integration points: **2** (the two `llm_call()` invocations in `workflow.py`). The wrapper does not add an independent third site for cost/latency accounting.

### Site details

#### `workflow.py:24` — Route selector (MIXED)

The `route()` function builds a prompt that asks the LLM to:
1. Analyze the input and select a support team from a closed set: `billing`, `technical`, `account`, `product`
2. Provide chain-of-thought reasoning in `<reasoning>` XML tags

Both outputs are consumed:
- **Reasoning** (generated prose): extracted at line 26 and printed to stdout at lines 28-29. This is observable output.
- **Selection** (decision): extracted at line 26, stripped/lowered at line 26, used as a dict key at line 33 to select the specialist prompt.

Classification rationale: Per audit rules, "A router that returns and prints explanatory reasoning is MIXED even if only its route controls execution." The reasoning is printed, making it externally observable generated content alongside the route decision.

The decision component (4-option closed-set classification) would be a natural fit for Jev Choice. However, the MIXED classification means the site cannot be treated as a pure DECISION.

**Context size**: Input tickets are short (< 500 tokens). Well within Jev's 64k context limit.

**Untrusted input mitigation**: The ticket text is interpolated directly into the prompt. In the current example, tickets are fixed fixtures (benign). For a public production service, adversarial input would need mitigation, but this is a vendored cookbook example with fixed test data.

#### `workflow.py:34` — Specialist response (GENERATION)

After routing, the selected specialist prompt is combined with the user input and sent to the LLM for a free-form response. This is pure text generation — Jev does not generate prose, code, or explanations.

#### `util.py:22` — Shared wrapper (MIXED)

The `llm_call()` function wraps `client.messages.create()` and returns `response.content[0].text`. It serves both call sites. Its classification follows its entire observed usage (MIXED + GENERATION = MIXED).

### Options per site

#### `workflow.py:24`

| # | Action | Primitive | Benefit | Risk |
|---|--------|-----------|---------|------|
| A | `decompose` | Choice | Jev Choice for route selection would be faster and cheaper (~$0.042/Mtok vs ~$3/Mtok). Requires a second call for reasoning generation. | Changes the MIXED site by splitting one call into two. Requires approval for modifying reasoning generation. Reasoning style may differ when generated separately. |
| B | `leave` | `none` | No risk to existing behavior. | No cost/latency improvement. |

#### `workflow.py:34`

| # | Action | Primitive | Benefit | Risk |
|---|--------|-----------|---------|------|
| A | `leave` | `none` | No risk. Generation is outside Jev's capability. | No improvement possible. |

#### `util.py:22`

| # | Action | Primitive | Benefit | Risk |
|---|--------|-----------|---------|------|
| A | `leave` | `none` | No risk. Wrapper semantics unchanged. | No improvement possible. |

## Approval resolution

**Approval predicate**: "Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged. Preserve all externally observable fields."

Resolved selections:

| Site | Classification | Matches predicate? | Selected option |
|------|---------------|--------------------|-|
| `workflow.py:24` | MIXED | **No** — not a pure DECISION | `leave` |
| `workflow.py:34` | GENERATION | **No** | `leave` |
| `util.py:22` | MIXED | **No** | `leave` |

## Conclusion

**No good Jev opportunities here** under the approved scope.

The routing decision at `workflow.py:24` is the closest candidate — it selects from 4 enumerated support teams, which maps well to a Jev Choice primitive. However, the same LLM call also generates chain-of-thought reasoning that is printed to stdout as observable output. This makes the site MIXED, not a pure DECISION. The approval scope explicitly excludes MIXED sites.

A `decompose` option exists (split into Jev Choice + original-model reasoning), but it would require explicit approval to modify a MIXED site's generated component, which the current scope does not grant.

No code changes, dependency additions, or environment modifications are made.
