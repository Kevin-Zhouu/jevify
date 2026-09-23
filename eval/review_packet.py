#!/usr/bin/env python3
"""Print review evidence; never grants a pass or changes the frozen grader."""
import argparse,json,pathlib

def events(path):
    for line in path.read_text().splitlines():
        try:yield json.loads(line)
        except json.JSONDecodeError:continue

def calls(path):
    for event in events(path):
        if event.get('type') in {'item.started','item.completed'}:
            item=event.get('item',{})
            if item.get('type')=='command_execution' and event['type']=='item.completed':
                yield item.get('command','')
            elif item.get('type') in {'file_change','mcp_tool_call'}:
                yield json.dumps(item)
        if event.get('type')=='assistant':
            for item in event.get('message',{}).get('content',[]):
                if item.get('type')=='tool_use':yield item.get('name','')+' '+json.dumps(item.get('input',{}))

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('run',type=pathlib.Path)
p.add_argument('--gate',action='store_true')
a=p.parse_args()
if a.gate:
    for name in ['phase0.jsonl','phase2.jsonl']:
        path=a.run/name
        if path.exists():
            print('\n### '+name)
            print('\n'.join(calls(path)))
else:
    ep=a.run/'evidence.json'
    if not ep.exists():raise SystemExit('Run incomplete')
    e=json.loads(ep.read_text());print(json.dumps(e,indent=2))
    out=a.run/e['output_relative']
    for name in ['JEV_AUDIT.json','JEV_CONVERSION_REPORT.md']:
        path=out/name
        if path.exists():print('\n### '+name+'\n'+path.read_text())
    pp=out/'JEV_PARITY.json'
    if pp.exists():
        parity=json.loads(pp.read_text())
        for site in parity.get('sites',[]):
            rows=site.get('rows',[]);threshold=site.get('threshold')
            accepted=[r for r in rows if isinstance(r.get('confidence'),(float,int)) and threshold is not None and r['confidence']>=threshold and not r.get('error')]
            print(json.dumps({'site':site.get('site_id'),'n':len(rows),'threshold':threshold,'accepted':len(accepted),'agreement':sum(r.get('jev_answer')==r.get('original_answer') for r in accepted)/len(accepted) if accepted else None,'faults':site.get('faults')}))
