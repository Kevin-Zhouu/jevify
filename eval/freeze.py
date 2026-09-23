#!/usr/bin/env python3
"""Freeze grader, runner, smoke tests, labels, config fixtures, and corpus bytes."""
import hashlib
import json
import pathlib
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
TARGET = ROOT / 'eval/FROZEN.json'


def current():
    paths = [ROOT / 'eval' / p for p in ['grader.py','suite.py','run.py','smoke.py','smoke.cjs','test_grader.py','package.json','package-lock.json','labels/dev.json','labels/heldout.json']]
    paths += sorted((ROOT / 'eval/configs').glob('*.yaml'))
    paths += sorted(p for p in (ROOT / 'corpus').rglob('*') if p.is_file())
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def main():
    if '--verify' in sys.argv:
        expected = json.loads(TARGET.read_text())['sha256']
        actual = current()
        differences = [p for p in set(expected)|set(actual) if expected.get(p)!=actual.get(p)]
        if differences:
            raise SystemExit('Frozen evidence changed: '+', '.join(sorted(differences)))
        print('Frozen grader, labels, configs and corpus hashes verified.')
        return
    if TARGET.exists():
        raise SystemExit('Already frozen; justify any change in eval/CHANGELOG.md first. Never silently overwrite.')
    payload={'frozen_at':datetime.now(timezone.utc).isoformat(),'sha256':current()}
    TARGET.write_text(json.dumps(payload,indent=2)+'\n')
    print('Frozen '+str(len(payload['sha256']))+' files without displaying held-out source or labels.')


if __name__=='__main__':
    main()
