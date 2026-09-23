# Providing a Jev key

Run the launcher from a terminal. It uses an existing environment variable or
prompts with hidden input, then passes the credential to the child process.
It does not write credentials to disk or put them in command arguments.

```sh
python3 tools/with_jev_key.py --provider vercel -- codex
python3 tools/with_jev_key.py --provider vercel -- claude
```

Use `--provider typesafe` for `TYPESAFE_API_KEY`, `--provider openrouter` for
`OPENROUTER_API_KEY`, or `--provider vercel` for `AI_GATEWAY_API_KEY`.
The provider choice identifies the credential to supply; the launcher does not
change application providers, install a skill, or prove model access.

For headless runs, inject the appropriate environment variable using your shell,
CI secret store, or secret manager. The launcher refuses to prompt when stdin
is not a terminal. Never put a key in `jevify.config.yaml`; the eventual
config will identify the provider and environment variable name only.

You can pass headless commands through the same launcher:

```sh
python3 tools/with_jev_key.py --provider typesafe -- codex exec 'Your task'
python3 tools/with_jev_key.py --provider typesafe -- claude -p 'Your task'
```

Only launch trusted commands: the child receives the key and controls its own
logging. This launcher does not sanitize arbitrary child-process output.

Vercel currently blocks the supplied account with `customer_verification_required`.
Complete the billing verification in the Vercel dashboard before retrying.
Version-pinned Jev access through Vercel remains unverified.

The subsequently supplied OpenRouter credential passed a live access check with
`typesafe/jev-1.13-20260917`, the dated model ID shown in OpenRouter's official SDK
guide. OpenRouter rejects the direct TypeSafe spelling `jev-1.13.0`.
Use the provider-specific pinned ID; do not silently substitute a latest alias.
This is an access check only, not a conversion parity result.

For the official TypeSafe SDK over OpenRouter, pass `OPENROUTER_API_KEY` explicitly
as the SDK API key and use base URL `https://openrouter.ai/api`. The SDK appends
`/v1/systemone`. The launcher does not perform this application configuration.

References: [Vercel Gateway authentication](https://vercel.com/docs/ai-gateway/authentication-and-byok),
[official Gateway SDK environment handling](https://github.com/vercel/ai/blob/main/packages/gateway/src/gateway-provider.ts),
[OpenRouter TypeSafe SDK guide](https://openrouter.ai/docs/guides/community/typesafe-sdk).
