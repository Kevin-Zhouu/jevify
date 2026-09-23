# Evaluation authorization

The user approved both items in conversation on 2026-09-23:

1. An isolated agent may inspect and hand-label the two HELD-OUT workflows before
   skill implementation, while withholding the labels and source from the skill
   author until the final check.
2. Original model baselines may be routed through OpenRouter using the provided
   credential for isolated parity evaluation. Preserve original model identity,
   prompts, and output parsing. This does not authorize changing production
   fallback providers or replacing Jev with a generative model.

The user also requested renaming the skill to `jevify` and authorized pushing
the project to https://github.com/Kevin-Zhouu/jevify.git. That authorization does
not apply to repositories the skill converts during its evaluations: those
runs must never push or open pull requests.

Credentials are supplied only to evaluation child-process environments; their
values must never be written to configs, reports, commits, or transcripts.
