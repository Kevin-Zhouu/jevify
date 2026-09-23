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
