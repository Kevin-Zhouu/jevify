# Skill iteration log

- DEV-01 (`489a5b3`): initial portable staged skill; 24 runs, 9 pass. Failures: output-mode confusion, unsupported credential-absence claims, metadata-adapter over-refusal, malformed/incomplete evidence, and unexecuted fault claims. All failed outputs retained.
- DEV-02 (`a33081d`): add read-only mode/key preflight and artifact shape checks; require actual evaluator/original-path execution, actual request IDs and executed fault assertions; clarify adapter-owned completion metadata. Full 24-run rerun in progress. No frozen grader, labels, configs or corpus changes.

- DEV02: 14/24 full passes (up from 9/24); all smokes and filesystem write gates pass, but two Claude setup turns read source too early. Claude parity proxies, false rate-limit proof, omitted wrapper inventory and negative-output artifacts remain failures.
- DEV03 change: hard setup read boundary; preserve branch/clone mode even for negative audits; include wrappers; require actual imported conversion/original source with one live response per row, HTTP429 fault proof, fresh confirmation after threshold changes, correct model logs and safe fallback structure. No corpus/grader changes.
