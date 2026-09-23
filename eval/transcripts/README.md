# Harness transcripts

Full transcripts are exported under `eval/results/<iteration>/<workflow>-<harness>-<scenario>/` alongside the evidence and generated output they describe.

- `headless.jsonl`, or `phase0.jsonl`, `phase2.jsonl`, `approved.jsonl`: actual CLI event streams.
- Matching `.prompt.txt` and `.stderr.txt`: exact evaluator request and process stderr.
- `filesystem_events.json`: observed path/hash/mtime changes tagged with phase.
- `evidence.json`: process outcomes, source ref, git log, mode/smoke checks and independent review flags.
- `REVIEW.md`, `grade.json`: review rationale and unchanged-grader result.
- `original/`, `converted/`: output snapshots, including failed/misplaced outputs when they occurred.

Live runtime repositories stay under ignored `eval/runs/`. Export omits embedded git databases, installed skill copies and dependency caches; their baseline hashes and git logs remain in the evidence. Skill revisions are preserved in the parent repository's commit history. Failed outputs are never repaired after a run. New skill versions run in fresh repositories.

Credential-shaped content is scanned before publication; authorization headers and actual key values must never be included. Public fixture and explicitly synthetic parity inputs may appear in these transcripts.
