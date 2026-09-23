#!/usr/bin/env python3
"""Run a command with a Jev provider credential, without saving the credential."""

import argparse
import getpass
import os
import subprocess
import sys
import warnings


ENV_NAMES = {
    "typesafe": "TYPESAFE_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "vercel": "AI_GATEWAY_API_KEY",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", required=True, choices=ENV_NAMES)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command
    if command[:1] == ["--"]:
        command = command[1:]
    if not command:
        parser.error("supply a command after --")
    env_name = ENV_NAMES[args.provider]
    env = os.environ.copy()
    if not env.get(env_name):
        if not sys.stdin.isatty():
            parser.error(f"set {env_name} through your secret manager for headless use")
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", getpass.GetPassWarning)
                key = getpass.getpass(f"{env_name} (hidden; not saved): ")
        except (getpass.GetPassWarning, EOFError, KeyboardInterrupt):
            print("Secure key entry unavailable or cancelled.", file=sys.stderr)
            return 2
        if not key or key != key.strip() or any(c.isspace() for c in key):
            print("Key must be nonempty and contain no whitespace.", file=sys.stderr)
            return 2
        env[env_name] = key
    try:
        return subprocess.run(command, env=env, check=False).returncode
    except FileNotFoundError:
        print("Requested executable was not found.", file=sys.stderr)
        return 127
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
