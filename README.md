# Jevify

An agent skill for finding where TypeSafe Jev fits in an existing AI workflow, presenting options, and converting only what the developer approves. Jev supplies typed decisions; existing LLMs retain generation and uncertain cases.

**Status: implemented; live cross-harness evaluation in progress.** See [REPORT.md](REPORT.md) for measured results and limitations. No production-readiness claim is made from the API access probe.

## Install

```sh
npx skills add Kevin-Zhouu/jevify
```

Or copy [skills/jevify](skills/jevify) into `.agents/skills/jevify/` for Codex or `.claude/skills/jevify/` for Claude Code. User-level paths and Claude marketplace installation are in [INSTALL.md](skills/jevify/INSTALL.md).

Ask “Use jevify to find where Jev could replace LLM calls in this workflow.” It asks for output mode, provider and risk posture before auditing; shows options; waits for approval; then converts and validates. Output choices are a new branch, a new clone, or a report without code changes.

## Bring your key

Use your normal environment/secret manager, or enter a key with echo disabled:

```sh
python3 skills/jevify/scripts/with_jev_key.py --provider openrouter -- codex
python3 skills/jevify/scripts/with_jev_key.py --provider typesafe -- claude
```

The launcher never saves the key. [Key setup](skills/jevify/references/credentials.md) covers TypeSafe, OpenRouter and Vercel. With neither key, approved code changes remain possible, but live validation is explicitly skipped. Vercel requires a verified versioned model route; an unversioned alias is not accepted as a pin.

## Headless

Supply the [setup and approval config](skills/jevify/references/configuration.md), then:

```sh
codex exec 'Use jevify with jevify.config.yaml'
claude -p 'Use jevify with jevify.config.yaml'
```

Missing answers stop the workflow; they never become guessed approval.

## Evidence

- [Corpus](corpus/README.md): six DEV and two HELD-OUT workflows from three real upstream repositories at pinned commits.
- [Evaluation protocol](eval/README.md): frozen grader, labels before implementation, both harnesses, headless and simulated interactive runs, output isolation, negative controls, live parity, and retained transcripts.
- [Report](REPORT.md): outcomes, bad fits, iteration history and known limitations.
- [Official TypeSafe reference](skills/jevify/references/official/SOURCES.json): upstream skill and unmodified reference snapshots with provenance. Live docs win.

Development checks require Python 3.10+, Node 18+ and the evaluation dependencies (`cd eval && npm ci`):

```sh
python3 -m unittest discover -s eval -p 'test_*.py'
python3 eval/freeze.py --verify
```

The skill helpers themselves use only Python's standard library. Vendored upstream material retains its own licenses and notices.
