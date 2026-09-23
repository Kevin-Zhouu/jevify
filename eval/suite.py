#!/usr/bin/env python3
"""Require the full matrix and compare audit classifications across harnesses."""
import argparse
import json
import pathlib

from grader import grade

ROOT=pathlib.Path(__file__).resolve().parents[1]


def summarize(directory, labels):
    runs={}
    results=[]
    for evidence_path in sorted(directory.glob('*/evidence.json')):
        run=evidence_path.parent
        evidence=json.loads(evidence_path.read_text())
        if evidence['fixture'] not in labels:
            continue
        key=(evidence['fixture'],evidence['harness'],evidence['scenario'])
        if key in runs:
            raise ValueError('Duplicate fixture/harness/scenario: '+str(key))
        output=run/evidence['output_relative'] if evidence.get('output_relative') else pathlib.Path(evidence['output'])
        audit_path=output/'JEV_AUDIT.json'
        audit=json.loads(audit_path.read_text()) if audit_path.exists() else {'sites':[]}
        runs[key]=(evidence,audit)
        result=grade(run,labels)
        (run/'grade.json').write_text(json.dumps(result,indent=2)+'\n')
        results.append(result)
    required={(fixture,harness,scenario) for fixture in labels for harness in ['codex','claude'] for scenario in ['headless','interactive']}
    missing=sorted(required-set(runs))
    disagreements=[]
    for fixture in labels:
        for scenario in ['headless','interactive']:
            pair=[runs.get((fixture,h,scenario)) for h in ['codex','claude']]
            if not all(pair):
                continue
            normalized=[]
            for _,audit in pair:
                entries={}
                for site in audit.get('sites',[]):
                    targets=[s for s in labels[fixture]['sites'] if s['file']==site.get('file') and isinstance(site.get('line'),int) and abs(s['line']-site['line'])<=2]
                    line=targets[0]['line'] if len(targets)==1 else site.get('line')
                    entries[f'{site.get("file")}:{line}']=site.get('classification')
                normalized.append(entries)
            if normalized[0]!=normalized[1]:
                disagreements.append({'fixture':fixture,'scenario':scenario,'codex':normalized[0],'claude':normalized[1]})
    modes={e['mode'] for e,_ in runs.values()}
    positive_missing=[]
    for fixture,gold in labels.items():
        if not gold.get('must_convert'):
            continue
        for harness in ['codex','claude']:
            options=[runs.get((fixture,harness,s)) for s in ['headless','interactive']]
            if not any(v and v[0]['mode']!='report' and v[1].get('converted_sites') for v in options):
                positive_missing.append([fixture,harness])
    return {'pass':bool(results) and not missing and not disagreements and not positive_missing and modes=={'branch','clone','report'} and all(r['pass'] for r in results),'required_runs':len(required),'observed_runs':len(runs),'missing':missing,'cross_harness_disagreements':disagreements,'positive_conversion_missing':positive_missing,'modes_covered':sorted(modes),'runs':results}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('directory',type=pathlib.Path)
    p.add_argument('--split',choices=['DEV','HELD-OUT'],required=True)
    p.add_argument('--allow-heldout',action='store_true')
    a=p.parse_args()
    if a.split=='HELD-OUT' and not a.allow_heldout:
        p.error('HELD-OUT remains sealed until the final check')
    name='dev.json' if a.split=='DEV' else 'heldout.json'
    labels=json.loads((ROOT/'eval/labels'/name).read_text())
    result=summarize(a.directory,labels)
    a.directory.mkdir(parents=True,exist_ok=True)
    (a.directory/'suite.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['pass'] else 1)


if __name__=='__main__':
    main()
