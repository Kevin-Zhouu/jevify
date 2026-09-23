<div align="center">

# jevify

### Let Jev handle the decisions. Keep your LLM for the rest.

Turn suitable LLM calls into fast, typed decisions—without rewriting your agent.

**Review the plan. Approve the changes. Keep a fallback.**

[Get started](#try-it-in-your-repo) · [Watch the demos](#see-the-speed-difference) · [Results](#what-weve-measured) · [Installation guide](skills/jevify/INSTALL.md)

</div>

---

Your agent may use a full language model just to choose a route, assign a label, or return a yes/no answer. **Jevify finds those calls, explains the tradeoffs, and helps you move the right ones to TypeSafe's Jev decision model.**

It is an agent skill you run inside **Codex or Claude Code**. It audits your existing workflow, proposes changes, and waits for your approval before converting anything. Your LLM stays available for generation and uncertain decisions.

> **Start small:** ask for a report-only audit. See where Jev could help before changing a line of application code. No API key is needed for the audit.

## See the speed difference

[![Claude versus Jev: watch the same ticket and inbox get routed side by side](docs/demos/preview.gif)](https://raw.githubusercontent.com/Kevin-Zhouu/jevify/main/docs/demos/claude-vs-jev.mp4)

**[Watch Claude vs Jev →](https://raw.githubusercontent.com/Kevin-Zhouu/jevify/main/docs/demos/claude-vs-jev.mp4)** · 20 seconds · one ticket, then a six-ticket inbox

Same decisions. Two timers. Watch Jev finish first.

<sub>Replay of recorded API timings, using selected matching decisions. Queue times sum separate calls; ticket previews are shortened. [Measurements and limitations](docs/demos/README.md).</sub>

Want to see Jev playing Doom or racing through Wikipedia? [Watch TypeSafe's official demos →](https://typesafe.ai/blog/introducing-system-one-models-and-jev)

## Try it in your repo

### 1. Install the skill

From your project directory:

```sh
npx skills add Kevin-Zhouu/jevify
```

Choose **jevify** and your coding agent in the installer. [Manual installation and Claude plugin options →](skills/jevify/INSTALL.md)

### 2. Ask for an audit

Open Codex or Claude Code in your project and paste:

```text
Use jevify to find where Jev could replace LLM calls in this workflow.
Start with a report-only audit. Keep the original LLM as a fallback.
```

Jevify asks for three choices before auditing:

| Choice | Your options |
| --- | --- |
| **Where should the work go?** | A new branch, a separate clone, or a report only |
| **How will you access Jev?** | TypeSafe key, OpenRouter key, or neither |
| **How cautious should it be?** | Keep LLM fallbacks, or use Jev alone where parity is proven |

### 3. Pick the changes you want

Review the recommendations by call site. Approve individual options, edit the plan, or leave everything as is. For an approved conversion, Jevify groups the decision policy in one module per language, preserves the existing interfaces, and runs validation.

You get **`JEV_CONVERSION_PLAN.md`** and **`JEV_CONVERSION_REPORT.md`** with the choices, changes, results, and undo instructions.

## What is a good fit?

| Your workflow does this… | Jevify can recommend… |
| --- | --- |
| Assigns one of ten support categories | A **Choice** question with a confidence gate |
| Selects a specialist or tool | A Jev router in front of the existing LLM |
| Rates text against an ordered rubric | A **Score** question |
| Makes a bounded yes/no judgment | A **Noul** question; Noul has no confidence field |
| Mixes classification with a written response | Separate the decision and keep the generation path |
| Writes prose or code, counts, compares dates, or needs multi-hop reasoning | Leave the call as is and explain why |

**Jev is a decision model.** It doesn't replace free-form generation. Extraction is only a Choice candidate when the possible answers can be enumerated first. Unsupported inputs and unmitigated adversarial cases are screened out during the audit.

## Add your API key when you're ready

Use your normal environment or secret manager:

| Access | Environment variable |
| --- | --- |
| TypeSafe | `TYPESAFE_API_KEY` |
| OpenRouter | `OPENROUTER_API_KEY` |

For a hidden-input prompt, run the bundled launcher from the installed skill directory. For example, with a project-local Codex installation:

```sh
python3 .agents/skills/jevify/scripts/with_jev_key.py --provider openrouter -- codex
```

For a project-local Claude Code installation:

```sh
python3 .claude/skills/jevify/scripts/with_jev_key.py --provider typesafe -- claude
```

The launcher passes the key to the coding agent without saving it or putting it in command arguments. Keep your original provider's credentials available for fallback. With no Jev key, you can still audit and approve code changes; live validation is explicitly skipped.

[Full key setup, personal install paths, and Vercel caveats →](skills/jevify/references/credentials.md)

## What we've measured

In one **36-input insurance-classification check**, with a preset **0.90 confidence gate**:

| Measurement | Result |
| --- | ---: |
| Agreement with Claude among accepted Jev decisions | **21/22 · 95.5%** |
| Requests sent to the original fallback | **14/36 · 38.9%** |
| Median standalone request time: Jev / Claude | **399 ms / 1,061 ms** |
| Estimated total API cost with fallback included | **57.0% lower** on this set |

These are small-sample results, not a production guarantee. One accepted Jev answer disagreed with Claude. The set uses 30 public fixture inputs and six labeled synthetic inputs. Cost estimates sum provider-reported costs; fallback adds latency and cost. Other examples in the evaluation had **higher** estimated costs after conversion. [Full measurement report →](eval/results/dev-03/anthropic_classification-codex-headless/original/JEV_CONVERSION_REPORT.md)

### Current validation status

- **Codex:** all 12 DEV runs passed in each of the last two rounds, across six workflows in headless and simulated interactive use.
- **Claude Code:** installation and execution were exercised, but conversion and validation failures remain. Later runs were blocked by its usage limit.
- **HELD-OUT:** unopened and untested. Identical reliability across both coding agents is **not yet proven**.

The demo's **Claude model baseline** is separate from the **Claude Code coding-agent evaluation**. [All results, failures, and limitations →](REPORT.md)

<details>
<summary><strong>Headless runs and configuration</strong></summary>

Supply setup answers and explicit conversion approval in `jevify.config.yaml`, then run:

```sh
codex exec 'Use jevify with jevify.config.yaml'
claude -p 'Use jevify with jevify.config.yaml'
```

Missing answers are not permission to guess. [Configuration reference →](skills/jevify/references/configuration.md)

</details>

<details>
<summary><strong>For contributors: corpus, evaluation, and references</strong></summary>

- [Corpus](corpus/README.md): six DEV and two HELD-OUT workflows from three upstream repositories at pinned commits.
- [Evaluation protocol](eval/README.md): frozen grader, prewritten labels, retained transcripts, and independent review.
- [Official TypeSafe references](skills/jevify/references/official/SOURCES.json): unmodified upstream snapshots with provenance; live docs win.
- [Demo source and rendering](docs/demos/README.md): recorded inputs, outputs, request IDs, and reproducible videos.

Development checks require Python 3.10+, Node 18+, and the evaluation dependencies (`cd eval && npm ci`):

```sh
python3 -m unittest discover -s eval -p 'test_*.py'
python3 eval/freeze.py --verify
```

The skill helpers use only Python's standard library. Vendored upstream material retains its own licenses and notices.

</details>

---

**Find your first Jev opportunity.** Install the skill, ask for an audit, and decide what to convert.
