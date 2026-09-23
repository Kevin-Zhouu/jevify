# Audit-first flow illustration

[Play animation](jevify-flow.gif)

This is a scripted product illustration, not a recording, test transcript, or benchmark. Every frame is labeled “ILLUSTRATIVE DEMO.” The 14 files, 6 calls, function names, conversion counts, passing tests, and diff are sample storyboard content. They do not claim that a real repository produced these results.

The animation demonstrates the new audit-first interaction: `/jevify` reads the current repo, shows reasons per call, asks one combined approval question, and hands back a branch, decisions module, report, and undo steps. Codex uses `$jevify`. Actual audits may find no suitable sites, tests may fail, and parity requires live credentials and representative inputs. All original evaluation records remain separate.

Generate with `python tools/render_jevify_flow.py` (Pillow required; font path is declared in the script). The demo has no provider calls and contains no developer logs.

[Historical real recorded run](jevify-session/README.md) — this used the old setup-first skill, so it is evidence for the earlier flow only. [Evaluation status](../../REPORT.md).
