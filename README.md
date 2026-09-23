<div align="center">

<img src="docs/brand/jevify-logo.png" alt="jevify" width="300" />

### Turn your existing AI agents and workflows into Jev-powered workflows.

An agent skill for **Codex & Claude Code**. Convert suitable LLM decision calls to Jev—with your approval and an LLM fallback.

[Install](#install) · [Watch the demo](#claude-vs-jev) · [Docs](skills/jevify/INSTALL.md) · [Results](REPORT.md)

</div>

## Install

```sh
npx skills add Kevin-Zhouu/jevify
```

Then, in Claude Code:

```text
/jevify convert this workflow
```

In Codex: `$jevify convert this workflow`. Replace “this workflow” with a file, folder, or agent. Jevify asks for setup and shows a plan before editing.

Just exploring? `/jevify audit this repo` — no API key needed.

## Claude vs Jev

[![Claude streams JSON while Jev returns the structured decisions](docs/demos/preview.gif)](https://raw.githubusercontent.com/Kevin-Zhouu/jevify/main/docs/demos/claude-vs-jev.mp4)

**12 questions. 136 lines of JSON. Jev: 0.44s. Claude Haiku 4.5: 5.11s.**

All 12 category choices match. One synthetic example via OpenRouter, replayed from real stream timestamps—not a general benchmark. [Watch video](https://raw.githubusercontent.com/Kevin-Zhouu/jevify/main/docs/demos/claude-vs-jev.mp4) · [Raw data](docs/demos/README.md)

## How it works

**Audit → Recommend → You approve → Convert → Validate**

- **Your codebase:** finds call sites and traces how their outputs are used.
- **Your choice:** new branch, separate clone, or report only.
- **Your safety net:** keeps generation with your LLM and adds fallback for uncertain decisions.
- **Your evidence:** runs tests and, with a key, compares live outputs, latency, and cost.

Decisions such as routing, classification, and rubric scoring are candidates. Free-form generation stays with your LLM. You get a conversion plan and a results report.

## Bring your key

Use `TYPESAFE_API_KEY` or `OPENROUTER_API_KEY` through your environment or the [hidden-input launcher](skills/jevify/references/credentials.md). Keep your original provider key for fallback.

No Jev key? Audit and approved code changes still work; live validation is skipped.

## Status

**Codex:** all 12 DEV runs passed in each of the last two rounds. **Claude Code:** known validation failures remain, and later runs hit a usage limit. HELD-OUT is untested; equal reliability across both agents is not yet proven. [Full evaluation →](REPORT.md)

<details>
<summary><strong>Installation, headless usage, and development</strong></summary>

- [Manual installation for Codex and Claude Code](skills/jevify/INSTALL.md)
- [Headless configuration and approvals](skills/jevify/references/configuration.md)
- [API keys and Vercel access notes](skills/jevify/references/credentials.md)
- [Pinned corpus](corpus/README.md) · [Frozen evaluation protocol](eval/README.md)
- [Official TypeSafe reference provenance](skills/jevify/references/official/SOURCES.json)

```sh
codex exec 'Use jevify with jevify.config.yaml'
claude -p 'Use jevify with jevify.config.yaml'
```

Development checks (Python 3.10+, Node 18+, and `npm ci` in `eval/`):

```sh
python3 -m unittest discover -s eval -p 'test_*.py'
python3 eval/freeze.py --verify
```

Skill helpers use Python's standard library. Vendored material retains its upstream licenses.

</details>
