# Skill iteration log

- DEV-01 (`489a5b3`): initial portable staged skill; 24 runs, 9 pass. Failures: output-mode confusion, unsupported credential-absence claims, metadata-adapter over-refusal, malformed/incomplete evidence, and unexecuted fault claims. All failed outputs retained.
- DEV-02 (`a33081d`): add read-only mode/key preflight and artifact shape checks; require actual evaluator/original-path execution, actual request IDs and executed fault assertions; clarify adapter-owned completion metadata. Full 24-run rerun in progress. No frozen grader, labels, configs or corpus changes.
