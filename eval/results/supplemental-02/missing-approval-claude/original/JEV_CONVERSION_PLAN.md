# Jev Conversion Plan

## Setup

| Field | Value |
|---|---|
| Output mode | branch |
| Branch | `jev-convert/no-key` |
| Provider | none |
| Risk | conservative |
| Headless | true |
| Original SHA | `add45bfb9f8847b09c8b221494602da7992274a0` |
| Original branch | `main` |
| Repo clean | true |
| Key present | false |
| Live validation | skipped: user selected neither |

## Audit

### Sites

| Site | Provider | Downstream | Classification | Fit |
|---|---|---|---|---|
| `workflow.py:83` | Anthropic SDK / `claude-haiku-4-5` | Returned label string selects one of 10 insurance support categories in `simple_classify()` | DECISION | FIT |

### Classification Detail

**`workflow.py:83`** - `client.messages.create()` inside `simple_classify(X)`

- **SDK/Provider/Model:** Anthropic Python SDK / `claude-haiku-4-5`
- **Input origin:** Function parameter `X`, sourced from curated TSV dataset of insurance support tickets
- **Downstream path:** Returns stripped category label string to caller. No further LLM calls, side effects, or generation.
- **Classification:** DECISION - selects one label from a closed, enumerated set of 10 insurance support categories
- **Fit reason:** Bounded semantic classification over trusted text. Jev Choice is designed for exactly this pattern. No math, date comparison, multi-hop reasoning, generation, or adversarial input. Small context (one ticket + 10 category descriptions).
- **Context size:** Small (~200-500 tokens)
- **Untrusted-input mitigation:** Input is from a curated dataset (benign fixed fixtures). Fit verdict scoped to this distribution.

### Categories (closed set)

1. Billing Inquiries
2. Policy Administration
3. Claims Assistance
4. Coverage Explanations
5. Quotes and Proposals
6. Account Management
7. Billing Disputes
8. Claims Disputes
9. Policy Comparisons
10. General Inquiries

## Options

### `workflow.py:83`

| Option | Action | Primitive | Benefit | Risk | Scope |
|---|---|---|---|---|---|
| A | fallback | Choice | Lower cost and latency for accepted decisions (~100ms Jev vs ~500ms+ Haiku). Expected cost = Jev cost + fallback fraction x Anthropic cost. | Serial misses add Jev latency before original inference. Jev may disagree on ambiguous tickets near category boundaries. | Replace `client.messages.create` with Jev Choice call + confidence gate; keep original Anthropic call as fallback. Single `jev_decisions.py` module. |
| B | leave | none | No change, no risk. Current workflow works. | No cost/latency improvement. Continues requiring Anthropic API key. | No changes. |

`jev_only` excluded: conservative risk posture requires fallback retention.

## Approval Status

**No approval provided.** Headless run stopped after Phase 2.

### Unanswered Fields

- `approval.sites` or `approval.actions` + `approval.scope`: not specified in config

### Resumption

To resume and convert, re-run with approval in the config:

```yaml
headless: true
output:
  mode: branch
  branch: jev-convert/no-key
access:
  provider: none
risk: conservative
approval:
  sites:
    workflow.py:83: fallback
```

Or with a predicate:

```yaml
approval:
  actions: [fallback]
  scope: Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged.
```
