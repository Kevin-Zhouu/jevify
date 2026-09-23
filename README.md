# Jevify

A skill for finding appropriate Jev decision-model opportunities in existing AI
workflows, presenting options, converting only approved sites, and validating
the result. The intended skill is portable between Codex and Claude Code.

**Status: evaluation preparation; the skill is not yet built or evaluated.**
This repository currently contains the pinned corpus, preimplementation DEV
labels, evaluation tooling, and a credential-entry launcher. See [REPORT.md](REPORT.md)
for verified results and remaining work.

- [Corpus and provenance](corpus/README.md): six DEV workflows and two sealed
  HELD-OUT workflows from three upstream repositories.
- [Evaluation protocol](eval/README.md): gating, output isolation, audit quality,
  conversion correctness, live parity, negative controls, and harness consistency.
- [Key setup](KEY_SETUP.md): provide TypeSafe, OpenRouter, or Vercel credentials
  through the environment or hidden terminal input without saving the key.

The user requested labels before implementation and a blind HELD-OUT check.
Sealed held-out labeling and baseline-provider routing decisions are pending;
the grader will be frozen before the `skills/jevify/` implementation is created.

Current checks:

```sh
python3 -m unittest discover -s eval -p test_grader.py
```

Python 3.10+ is required for project tooling. TypeScript smoke tests use Node and
the dependencies pinned in `eval/package-lock.json` (`cd eval && npm ci`).
No live key is needed for these offline evidence-check and smoke tests. They do
not establish live Jev parity or skill compatibility.
