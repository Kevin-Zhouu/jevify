#!/usr/bin/env python3
"""Read-only setup verification. Never displays or persists credential values."""
import argparse,json,os,pathlib,re,shutil,subprocess

ENV={'typesafe':'TYPESAFE_API_KEY','openrouter':'OPENROUTER_API_KEY','vercel':'AI_GATEWAY_API_KEY'}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',default='.')
    p.add_argument('--mode',required=True,choices=['branch','clone','report'])
    p.add_argument('--branch')
    p.add_argument('--clone-path')
    p.add_argument('--provider',required=True,choices=[*ENV,'none'])
    p.add_argument('--key-env')
    a=p.parse_args()
    result={'mode':a.mode,'provider':a.provider,'read_only':True,'errors':[]}
    if not shutil.which('git'):
        result['errors'].append('git unavailable');print(json.dumps(result));return 2
    repo=pathlib.Path(a.repo).resolve()
    def git(*args):
        return subprocess.run(['git','-C',str(repo),*args],env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'},capture_output=True,text=True)
    base=git('rev-parse','--show-toplevel')
    if base.returncode:
        result['errors'].append('not a git repository');print(json.dumps(result));return 2
    result['repository']=base.stdout.strip()
    result['original_sha']=git('rev-parse','HEAD').stdout.strip()
    result['original_branch']=git('branch','--show-current').stdout.strip()
    dirty=git('status','--porcelain','--untracked-files=all')
    result['clean']=dirty.returncode==0 and not dirty.stdout.strip()
    if not result['clean']:result['errors'].append('working tree not clean; offer stash or stop, never auto-stash')
    # Exactly one mode: inactive branch/clone fields are not permissions.
    if a.mode=='branch':
        result['output_repository']=str(repo)
        result['branch']=a.branch
        if not a.branch or git('check-ref-format','--branch',a.branch).returncode:
            result['errors'].append('valid branch name required')
        elif git('show-ref','--verify','--quiet','refs/heads/'+a.branch).returncode==0:
            result['errors'].append('branch already exists')
    elif a.mode=='clone':
        if not a.clone_path:result['errors'].append('clone path required')
        else:
            out=pathlib.Path(a.clone_path).expanduser()
            if not out.is_absolute():out=repo/out
            out=out.resolve();result['output_repository']=str(out)
            if out.exists():result['errors'].append('clone path already exists')
            if out==repo or repo in out.parents:result['errors'].append('clone must be outside source repository')
    else:result['output_repository']=str(repo)
    key_env=a.key_env or ENV.get(a.provider)
    if a.provider=='none':
        result.update(key_env=None,key_present=False,live_validation='skipped: user selected neither')
    elif key_env and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',key_env):
        result.update(key_env=key_env,key_present=bool(os.environ.get(key_env)))
        if not result['key_present']:result['live_validation']='unavailable in this process; do not claim parity'
    else:result['errors'].append('invalid key variable NAME (never pass a value)')
    print(json.dumps(result,indent=2))
    return 2 if result['errors'] else 0
if __name__=='__main__':raise SystemExit(main())
