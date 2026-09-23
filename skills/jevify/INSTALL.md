# Install jevify

The same `skills/jevify` folder is used in both harnesses. No harness-specific runtime tools or paths are required by the skill. Helper scripts need Python 3.10+; conversion targets may use their own existing dependencies.

## Codex

Copy `skills/jevify/` into your project's `.agents/skills/jevify/`, or into `~/.agents/skills/jevify/` for personal use. Invoke `$jevify`, or ask to migrate a workflow to Jev. These locations were checked against the [current Codex skill docs](https://learn.chatgpt.com/docs/build-skills) on 2026-09-23.

## Claude Code

Copy the same folder into `.claude/skills/jevify/` in a project, or `~/.claude/skills/jevify/` for personal use. Invoke `/jevify`. See [Claude Code skills](https://code.claude.com/docs/en/skills).

Alternatively, install the repository's marketplace:

```sh
claude plugin marketplace add Kevin-Zhouu/jevify
claude plugin install jevify@jevify-marketplace
```

The plugin form may expose the command as `/jevify:jevify`. Marketplace packaging follows [Claude's marketplace documentation](https://code.claude.com/docs/en/plugin-marketplaces). Choose either direct skill installation or plugin installation to avoid duplicates.

## Skills CLI

```sh
npx skills add Kevin-Zhouu/jevify
```

Choose `jevify` and the target harness(es) in the installer. See the [skills CLI](https://www.skills.sh/docs/cli). This is an installer convenience; runtime helpers do not require npx.

## Headless and keys

Use `jevify.config.yaml` as described in [configuration](references/configuration.md), supplying setup and explicit scope approval. Then:

```sh
codex exec 'Use jevify with jevify.config.yaml'
claude -p 'Use jevify with jevify.config.yaml'
```

Provide credentials via the [hidden-input launcher or environment](references/credentials.md). Missing answers never become guessed approvals. The official TypeSafe skill and exact API references are vendored under `references/official/`, with upstream license and source hashes. Live TypeSafe docs remain authoritative.
