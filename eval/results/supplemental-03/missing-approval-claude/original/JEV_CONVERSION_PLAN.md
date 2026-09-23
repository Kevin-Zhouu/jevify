# Jev Conversion Plan

## Preflight

| Field | Value |
|---|---|
| Repository | `/Users/bigsoup/Downloads/Jev Converter/eval/runs/supplemental-03/missing-approval-claude/original` |
| Original branch | `main` |
| Original SHA | `306e7348cce7a7d004783c48849b7e6adb221c6e` |
| Output mode | `branch` |
| Target branch | `jev-convert/no-key` |
| Provider | `none` |
| Key present | No |
| Risk posture | Conservative |
| Live validation | Skipped: user selected no provider |

## Audit

### Site inventory

| Site | Provider | Model | Input origin | Downstream path | Classification | Fit |
|---|---|---|---|---|---|---|
| `workflow.py:83` | Anthropic SDK | `claude-haiku-4-5` | Caller-supplied ticket string | Stripped label string returned to caller; no metadata consumed | DECISION | FIT |

### Site detail: `workflow.py:83`

- **Function:** `simple_classify(X)` — takes a support ticket string, returns one of 10 category labels.
- **SDK call:** `client.messages.create(messages=..., stop_sequences=["</category>"], max_tokens=4096, temperature=0.0, model="claude-haiku-4-5")`
- **Prompt:** Instructs the model to classify a customer support ticket into one of 10 insurance categories and respond with just the label.
- **Return value:** `response.content[0].text.strip()` — a bare label string.
- **Metadata consumed:** None. Token usage, finish reason, and message ID are not read or returned.
- **Context size:** ~1.5k tokens (categories XML + short ticket). Well within Jev 32k state limit.
- **Untrusted-input mitigation:** Tickets are placed inside `<ticket>` XML tags. Data files are fixed TSV fixtures of benign insurance support tickets. Not a public-facing production endpoint. Fit verdict scoped to this benign distribution.

### Classification rationale

The call selects exactly one label from a closed set of 10 named categories. The prompt requests "just the label." No reasoning, explanation, or free-form text is generated or consumed. No response metadata is used downstream. This is a pure **DECISION**.

### Fit rationale

Semantic text classification into a bounded label set is a core Jev strength (Choice primitive). No math, date comparison, multi-hop reasoning, counting, or non-text input is involved. Context is small. The 10 categories map directly to Choice criteria with descriptions. Jev 1.13 jaggedness documentation does not flag concerns for this task shape.

### Categories (10 options)

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

### `workflow.py:83` — Option A: `fallback` (Choice)

- **Primitive:** Choice with 10 categories as options, descriptions drawn from existing category content.
- **Benefit:** Lower per-decision cost (Jev ~$0.042/Mtok input-only vs Claude Haiku input+output pricing) and likely lower latency for accepted decisions. Expected cost = Jev cost + fallback_fraction × original cost.
- **Risk:** Parity unproven without live measurement. Conservative fallback retains original path for low-confidence decisions, so observable behavior is preserved. Serial misses add Jev latency before the original inference.
- **Scope:** Add `typesafe_sdk` dependency. Create `jev_decisions.py` with model pin `jev-1.13.0`, Choice question, 10 criteria, and confidence threshold. Modify `simple_classify` to attempt Jev first; on high confidence return accepted label; on low confidence / error / timeout / missing key, fall back to existing Anthropic call unchanged. Log decision path and model. Add `TYPESAFE_API_KEY` placeholder to `.env.example`.

### `workflow.py:83` — Option B: `leave` (none)

- **Primitive:** none
- **Benefit:** No integration risk, no new dependency.
- **Risk:** No cost or latency improvement.
- **Scope:** No changes.

## Approval status

**Not approved.** This plan was generated in headless mode without approval. To proceed with conversion, re-invoke with an `approval` section in the config selecting an option for the site, for example:

```yaml
approval:
  sites:
    workflow.py:83: fallback
```

Or resume interactively to select options.

## Resumption

```
jevify config=jevify.config.yaml
# Add approval section to config before re-running
```
