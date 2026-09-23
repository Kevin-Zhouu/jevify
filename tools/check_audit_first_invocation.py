#!/usr/bin/env python3
"""Run a bare-invocation probe against an already prepared clean isolated repo.
Usage: python tools/check_audit_first_invocation.py codex|claude REPO OUTPUT
No API key/token environment variables are passed. Outputs are raw evidence,
not an automatic quality grade. Original source must be committed first.
"""
import os,subprocess,json,sys,pathlib
h=sys.argv[1];root=pathlib.Path(__file__).resolve().parents[1];out=pathlib.Path(sys.argv[3]);repo=pathlib.Path(sys.argv[2]).resolve();out.mkdir(parents=True,exist_ok=True)
env={k:v for k,v in os.environ.items() if not any(s in k.upper() for s in ('API_KEY','API_TOKEN'))}
cmd=['codex','exec','--json','--dangerously-bypass-approvals-and-sandbox','$jevify'] if h=='codex' else ['claude','-p','/jevify','--dangerously-skip-permissions','--output-format','json']
with (out/(h+'.jsonl')).open('w') as stdout,(out/(h+'.stderr.txt')).open('w') as stderr:
 try:r=subprocess.run(cmd,cwd=repo,env=env,stdout=stdout,stderr=stderr,timeout=360);rc=r.returncode
 except subprocess.TimeoutExpired:rc=124
status=subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True)
(out/(h+'-status.json')).write_text(json.dumps({'command':cmd,'returncode':rc,'git_status':status},indent=2)+'\n')
plan=repo/'JEV_CONVERSION_PLAN.md'
if plan.exists():(out/(h+'-plan.md')).write_bytes(plan.read_bytes())
print(h,rc,status)
