# Providing a key without saving it

The audit never requires a key. The approval plan names the provider; approved code can be written before a key is supplied. Explain key setup at handback as the next step for live validation, using the runtime environment. Never ask them to paste a secret into chat, a prompt, config, source code or a command argument. A shell export is an option only if they understand their shell's history policy. Prefer the included hidden-input launcher (Python 3.10+):

```sh
python3 /path/to/jevify/scripts/with_jev_key.py --provider openrouter -- codex exec 'Use jevify with jevify.config.yaml'
python3 /path/to/jevify/scripts/with_jev_key.py --provider typesafe -- claude -p 'Use jevify with jevify.config.yaml'
```

It asks on the user's terminal with echo disabled and forwards the key only to the child environment; it does not save it. If the key already exists in the environment, no prompt occurs. Headless callers must inject credentials with their CI/OS secret facility; absence yields a clear error, never a fallback to echoing input. The launcher requires the chosen harness executable only because it runs that user command, not because the skill depends on a harness API.

| Provider | Variable | Notes |
|---|---|---|
| TypeSafe | `TYPESAFE_API_KEY` | Direct API; `jev-1.13.0` |
| OpenRouter | `OPENROUTER_API_KEY` | System One endpoint, versioned provider ID |
| Vercel Gateway | `AI_GATEWAY_API_KEY` | Verify model version and account access before conversion |
| None | no key | Audit/code possible; live validation skipped; keep fallback |

For an already running agent, the user can restart it through the launcher, or use the codebase's existing ignored local env file/secret manager. Do not assume child processes can change their parent's environment. `.env.example` contains names and empty values only. If using an ignored local file, verify ignore status before writing, ask the user to populate it locally, and never display its contents.

A Jev credential does not authorize routing the original LLM to a new provider. Ask for an original-provider credential or explicit baseline gateway authorization. Never map a Jev key to a different vendor's env variable as a silent workaround. Authentication failures and unavailable pins are reported as blocked validation, not hidden behind synthetic results.
