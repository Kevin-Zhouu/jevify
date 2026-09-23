#!/usr/bin/env python3
"""Export completed run evidence as ordinary files, without embedded git repos.

This does not modify runs, scores, transcripts, or the frozen evaluator.
Installed skill copies/caches/git databases are omitted; their hashes are retained
in before/after.json and the root commit history preserves each skill revision.
"""
import argparse,hashlib,json,pathlib,shutil

ROOT=pathlib.Path(__file__).resolve().parents[1]
SKIP={'.git','remote.git','node_modules','__pycache__','.venv','.agents','.claude'}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('iteration')
    a=p.parse_args()
    source=ROOT/'eval/runs'/a.iteration
    target=ROOT/'eval/results'/a.iteration
    hashes={}
    for run in sorted(source.iterdir()):
        if not (run/'evidence.json').exists():continue
        out=target/run.name
        if out.exists():shutil.rmtree(out)
        shutil.copytree(run,out,ignore=lambda directory,names:[n for n in names if n in SKIP])
        for path in out.rglob('*'):
            if path.is_file():hashes[str(path.relative_to(target))]=hashlib.sha256(path.read_bytes()).hexdigest()
    target.mkdir(parents=True,exist_ok=True)
    for name in ['suite.json','iteration.json']:
        path=source/name
        if path.is_file():
            shutil.copyfile(path,target/name)
            hashes[name]=hashlib.sha256(path.read_bytes()).hexdigest()
    (target/'EXPORT.json').write_text(json.dumps({'source':'eval/runs/'+a.iteration,'omitted':sorted(SKIP),'sha256':hashes},indent=2)+'\n')
    print(f'Exported {len(hashes)} evidence files to {target.relative_to(ROOT)}')

if __name__=='__main__':main()
