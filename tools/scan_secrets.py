#!/usr/bin/env python3
"""Fail on credential-shaped values without printing those values.

Heuristic hygiene check, not a substitute for reviewing diffs and transcripts.
"""
import argparse,pathlib,re
PATTERNS=[re.compile(rb'sk-or-v1-[A-Fa-f0-9]{40,}'),re.compile(rb'vck_[A-Za-z0-9]{24,}'),re.compile(rb'sk-(?:proj-|ant-api\d+-)?[A-Za-z0-9_-]{40,}'),re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')]
SKIP={'.git','node_modules','__pycache__','.venv','remote.git'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('paths',nargs='+',type=pathlib.Path);a=p.parse_args()
    matches=[];count=0
    for root in a.paths:
        paths=[root] if root.is_file() else root.rglob('*')
        for path in paths:
            if not path.is_file() or set(path.parts)&SKIP:continue
            data=path.read_bytes();count+=1
            if any(pattern.search(data) for pattern in PATTERNS):matches.append(str(path))
    print(f'Scanned {count} files; credential-shaped values in {len(matches)} files.')
    for name in matches:print(name)
    return int(bool(matches))
if __name__=='__main__':raise SystemExit(main())
