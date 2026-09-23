#!/usr/bin/env python3
"""Supplemental real-harness setup probes, separate from the frozen main matrix."""
import argparse,json,os,pathlib,shutil,subprocess,sys
from run import git,invoke,snapshot,write_json
ROOT=pathlib.Path(__file__).resolve().parents[1]

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--harness',choices=['codex','claude'],required=True)
 p.add_argument('--case',choices=['missing-setup','missing-approval','no-key'],required=True)
 p.add_argument('--iteration',default='supplemental-02')
 a=p.parse_args();run=ROOT/'eval/runs'/a.iteration/(a.case+'-'+a.harness);run.mkdir(parents=True,exist_ok=False)
 repo=run/'original';shutil.copytree(ROOT/'corpus/anthropic_classification',repo)
 for folder in ['.agents/skills/jevify','.claude/skills/jevify']:shutil.copytree(ROOT/'skills/jevify',repo/folder)
 (repo/'.gitignore').write_text('.env\n__pycache__/\nnode_modules/\n.venv/\n')
 git(repo,'init','-b','main');git(repo,'config','user.name','Jev Evaluation');git(repo,'config','user.email','jev-eval@example.invalid');git(repo,'add','.');git(repo,'commit','-m','Baseline probe')
 sha=git(repo,'rev-parse','HEAD');before=snapshot(repo,include_git=True)
 config={'headless':True} if a.case=='missing-setup' else {'headless':True,'output':{'mode':'branch','branch':'jev-convert/no-key'},'access':{'provider':'none'},'risk':'conservative'}
 if a.case=='no-key':config['approval']={'actions':['fallback'],'scope':'Only pure DECISION sites with enumerated outputs, preserve behavior and original fallback provider.'}
 cp=run/'jevify.config.yaml';write_json(cp,config)
 folder='.agents' if a.harness=='codex' else '.claude'
 prompt=f'Use the jevify skill at {folder}/skills/jevify/SKILL.md with the supplied config {cp}. This is headless. Do not guess missing answers or approval. Restrict inspection to this repository and current public documentation; do not read other eval runs, labels or corpus files. No secrets are supplied; do not search for keys in files or outside the process environment. If a conversion is approved, use this independent smoke command: {sys.executable} "{ROOT / "eval/smoke.py"}" "{repo}" anthropic_classification. Do not edit that smoke file. Use Python 3.10+, available at {sys.executable}. Never push or create a PR.'
 env={k:v for k,v in os.environ.items() if k not in {'OPENROUTER_API_KEY','TYPESAFE_API_KEY','AI_GATEWAY_API_KEY','ANTHROPIC_API_KEY','OPENAI_API_KEY'}}
 outcome=invoke(a.harness,repo,prompt,run/'probe.jsonl',env)
 after=snapshot(repo,include_git=True)
 changes=[n for n in set(before)|set(after) if before.get(n)!=after.get(n)]
 smoke=None
 if a.case=='no-key':
  s=subprocess.run([sys.executable,str(ROOT/'eval/smoke.py'),str(repo),'anthropic_classification'],capture_output=True,text=True,env=env)
  smoke={'exit_code':s.returncode,'stdout':s.stdout,'stderr':s.stderr}
 write_json(run/'evidence.json',{'case':a.case,'harness':a.harness,'outcome':outcome,'output_relative':'original','original_sha':sha,'main_unchanged':git(repo,'rev-parse','main')==sha,'branch':git(repo,'branch','--show-current'),'changes':sorted(changes),'smoke':smoke,'review_required':True})
 write_json(run/'before.json',before);write_json(run/'after.json',after)
 print(json.dumps({'case':a.case,'harness':a.harness,'exit_code':outcome['exit_code'],'changes':len(changes)}))
if __name__=='__main__':main()
