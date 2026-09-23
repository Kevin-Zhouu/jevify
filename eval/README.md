# Evaluation protocol

Preflight records are not scored as skill evaluations. The corpus consists of
unchanged upstream files or exact notebook function/cell slices, not invented
workflows. PROVENANCE.json records source commits, selections, and hashes.

DEV hand labels were authored from downstream code before skill implementation.
HELD-OUT source and labels must remain sealed from the skill author until the
final check. Do not run a broad recursive source read over corpus/.

The grader will be frozen before the skill is created. Any subsequent grader
change requires a dated justification in CHANGELOG.md; thresholds may not be
relaxed to improve scores. Corpus hashes may not change after assembly.

Keep baseline provider-route authorization separate from conversion approval.
Do not treat an OpenRouter key as permission to switch existing provider calls.
No live Jev payload may be invented or obtained from a substitute text model.
Fault injection is identified separately and never counted as live parity data.

`suite.py` requires both Codex and Claude Code, each with headless and simulated
interactive runs for every workflow. It reports missing runs and cross-harness
classification disagreements and requires branch, clone, and report modes to be
represented. An approved positive fixture must actually be converted in each
harness; report-only success cannot substitute for conversion evidence.

`run.py` records filesystem and git-ref changes during each gate, command
transcripts, exit codes, smoke results, original-branch identity, and local remote
refs. Independent transcript and code review is still required: polling alone
cannot prove that no transient write or attempted push occurred. The grader
fails closed until that review is recorded.

HELD-OUT runs require `--allow-heldout --heldout-round 0`. Each fixture/harness/
scenario claims a unique attempt before execution. Repair rounds 1 and 2 require
a general lesson in `eval/repairs/round-N.md`; round 3 is rejected. HELD-OUT source
or labels must not be inspected by the skill author during DEV.
