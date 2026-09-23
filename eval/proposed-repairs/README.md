# Draft repairs — not installed or cross-harness evaluated

Drafted during DEV03 before the Claude usage-limit stop. These are NOT part of the active `skills/jevify` release and no DEV04 is claimed.

- `validation_support.py` / `.cjs`: actual-source loaders, exactly-once original return/exception assertions, and provider-cost preference. Small local checks caught a deliberately duplicated fallback and passed correct synchronous/async paths; no model responses were fabricated.
- `check_validation_source.py`: read-only heuristic syntax screen for duplicated model/transport policy, manually reconstructed baseline messages, copied prompt literals and fabricated response dictionaries. It flags the reviewed bad Python validator and accepts the four reviewed Codex validators. It is not semantic proof and needs generalization tests before activation.

Other pending general repairs: put the complete Phase0 question wording and missing-approval hard stop directly in the entrypoint; keep branch as the default suggestion and explicitly allow approved no-key code with skipped live validation. Resume DEV only once Claude headless access is available. Preserve the frozen grader/corpus and all failed outputs. Do not open HELD-OUT before finishing DEV.
