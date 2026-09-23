#!/usr/bin/env python3
"""Supplemental skill discovery probes; not part of the frozen matrix."""
import argparse,json,os,pathlib,shutil,sys
from run import git,invoke,snapshot,write_json
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--harness',choices=['codex','claude'],required=True)
p.add_argument('--case',choices=['migration','api-question'],required=True)
a=p.parse_args();run=ROOT/'eval/runs/trigger-03'/(a.case+'-'+a.harness);run.mkdir(parents=True,exist_ok=False)
repo=run/'original';shutil.copytree(ROOT/'corpus/vercel_enum',repo)
for folder in ['.agents/skills/jevify','.claude/skills/jevify']:shutil.copytree(ROOT/'skills/jevify',repo/folder)
git(repo,'init','-b','main');git(repo,'config','user.name','Jev Evaluation');git(repo,'config','user.email','jev-eval@example.invalid');git(repo,'add','.');git(repo,'commit','-m','Baseline discovery probe')
before=snapshot(repo,include_git=True)
prompt=('Where could Jev replace LLM calls in this workflow? I have not chosen an output mode or provider yet.' if a.case=='migration' else 'What is the difference between Jev Choice and Noul? This is only an API concept question; do not audit or modify this repository.')
prompt+=' Restrict any file inspection to this repository and public documentation. Do not read sibling directories or search for credentials. If you need answers from me, ask and stop.'
env={k:v for k,v in os.environ.items() if k not in {'OPENROUTER_API_KEY','TYPESAFE_API_KEY','AI_GATEWAY_API_KEY','ANTHROPIC_API_KEY','OPENAI_API_KEY'}}
outcome=invoke(a.harness,repo,prompt,run/'probe.jsonl',env)
after=snapshot(repo,include_git=True)
write_json(run/'evidence.json',{'case':a.case,'harness':a.harness,'outcome':outcome,'output_relative':'original','changes':sorted(n for n in set(before)|set(after) if before.get(n)!=after.get(n)),'review_required':True})
write_json(run/'before.json',before);write_json(run/'after.json',after)
print(json.dumps({'case':a.case,'harness':a.harness,'exit_code':outcome['exit_code']}))
