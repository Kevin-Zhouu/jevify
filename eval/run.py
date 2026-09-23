#!/usr/bin/env python3
"""Run real harnesses in isolated repositories; capture output and file evidence."""
import argparse
import datetime
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import threading
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True, text=True, env={**os.environ, 'GIT_OPTIONAL_LOCKS': '0'}).stdout.strip()


def snapshot(root, include_git=False):
    result = {}
    if not root.exists():
        return result
    for directory, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in {'node_modules', '__pycache__', '.venv'} and (include_git or d != '.git')]
        for name in files:
            p = pathlib.Path(directory) / name
            if p.is_symlink():
                data = os.readlink(p).encode()
            else:
                try:
                    data = p.read_bytes()
                except FileNotFoundError:
                    continue
            result[str(p.relative_to(root))] = hashlib.sha256(data).hexdigest()
    return result


def watched_snapshot(root):
    result = snapshot(root)
    # Gate evidence includes branch switches, ref creation and reflog commits.
    for rel in ['.git/HEAD', '.git/packed-refs']:
        path = root / rel
        if path.is_file():
            result[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    for rel in ['.git/refs', '.git/logs']:
        path = root / rel
        for name, digest in snapshot(path).items():
            result[rel + '/' + name] = digest
    return result


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def invoke(harness, repo, prompt, destination, env, timeout=900):
    if harness == 'codex':
        cmd = ['codex', 'exec', '--ephemeral', '--json', '--skip-git-repo-check', '-s', 'danger-full-access', '-C', str(repo), '-']
    else:
        cmd = ['claude', '--no-session-persistence', '--output-format', 'stream-json', '--verbose', '--permission-mode', 'bypassPermissions', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '-p', prompt]
    destination.parent.mkdir(parents=True, exist_ok=True)
    (destination.with_suffix('.prompt.txt')).write_text(prompt)
    started = time.time_ns()
    with destination.open('w') as stdout, destination.with_suffix('.stderr.txt').open('w') as stderr:
        process = subprocess.Popen(cmd, cwd=repo, env=env, stdin=subprocess.PIPE if harness == 'codex' else subprocess.DEVNULL, stdout=stdout, stderr=stderr, text=True)
        try:
            process.communicate(prompt if harness == 'codex' else None, timeout=timeout)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
            return {'exit_code': 124, 'started_ns': started, 'ended_ns': time.time_ns()}
    return {'exit_code': process.returncode, 'started_ns': started, 'ended_ns': time.time_ns()}


def final_text(path, harness):
    texts = []
    for line in path.read_text().splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if harness == 'codex' and event.get('type') == 'item.completed' and event.get('item', {}).get('type') == 'agent_message':
            texts.append(event['item']['text'])
        if harness == 'claude' and event.get('type') == 'result':
            texts.append(event.get('result', ''))
    return '\n'.join(texts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fixture', required=True)
    parser.add_argument('--harness', choices=['codex','claude'], required=True)
    parser.add_argument('--scenario', choices=['headless','interactive'], required=True)
    parser.add_argument('--mode', choices=['branch','clone','report'], required=True)
    parser.add_argument('--iteration', required=True)
    parser.add_argument('--allow-heldout', action='store_true')
    parser.add_argument('--heldout-round', type=int, choices=[0,1,2])
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'corpus/manifest.json').read_text())
    entry = next(e for e in manifest if e['id'] == args.fixture)
    if entry['split'] == 'HELD-OUT' and not args.allow_heldout:
        parser.error('HELD-OUT is sealed; final-check authorization required')
    if entry['split'] == 'HELD-OUT':
        if args.heldout_round is None:
            parser.error('A HELD-OUT attempt must name round 0, 1 or 2')
        if args.heldout_round:
            lesson=ROOT/'eval/repairs'/f'round-{args.heldout_round}.md'
            if not lesson.exists() or not lesson.read_text().strip():
                parser.error('A repair requires a recorded general lesson before retrying HELD-OUT')
        claims=ROOT/'eval/heldout-claims'/f'round-{args.heldout_round}'
        claims.mkdir(parents=True,exist_ok=True)
        claim=claims/f'{args.fixture}-{args.harness}-{args.scenario}.json'
        with claim.open('x') as stream:
            json.dump({'started_ns':time.time_ns(),'iteration':args.iteration},stream)
    run = ROOT / 'eval/runs' / args.iteration / f'{args.fixture}-{args.harness}-{args.scenario}'
    run.mkdir(parents=True, exist_ok=False)
    repo = run / 'original'
    clone = run / 'converted'
    shutil.copytree(ROOT / 'corpus' / args.fixture, repo)
    skill_source = ROOT / 'skills/jevify'
    for folder in ['.agents/skills/jevify', '.claude/skills/jevify']:
        shutil.copytree(skill_source, repo / folder)
    (repo / '.gitignore').write_text('.env\n.env.local\n__pycache__/\nnode_modules/\n.venv/\n')
    git(repo, 'init', '-b', 'main')
    git(repo, 'config', 'user.name', 'Jev Evaluation')
    git(repo, 'config', 'user.email', 'jev-eval@example.invalid')
    git(repo, 'add', '.')
    git(repo, 'commit', '-m', 'Baseline pinned upstream workflow and installed skill')
    original_sha = git(repo, 'rev-parse', 'HEAD')
    remote = run / 'remote.git'
    subprocess.run(['git', 'clone', '--bare', str(repo), str(remote)], check=True, capture_output=True)
    git(repo, 'remote', 'add', 'origin', str(remote))
    remote_before = git(remote, 'show-ref')
    before = snapshot(repo)
    original_bytes = snapshot(repo, include_git=True)
    branch = 'jev-convert/evaluation'
    config = {'output':{'mode':args.mode,'branch':branch,'clone_path':str(clone)},'access':{'provider':'openrouter','key_env':'OPENROUTER_API_KEY','model':'typesafe/jev-1.13-20260917'},'risk':'conservative','headless':args.scenario=='headless','approval':{'actions':['fallback'],'scope':'Only pure DECISION sites with enumerated outputs; leave MIXED and GENERATION unchanged. Preserve all externally observable fields.'},'validation':{'baseline_provider':'openrouter','baseline_routing_authorized':True,'scope':'Route the SAME original model through OpenRouter in isolated evaluation adapters only. Preserve original prompts and output parsing; do not switch production fallback providers or substitute a different baseline model.'}}
    config_path = run / 'jevify.config.yaml'
    # JSON is a strict YAML 1.2 subset, readable without an extra parser.
    write_json(config_path, config)
    smoke_cmd = f'{sys.executable} {ROOT / "eval/smoke.py"} OUTPUT_DIRECTORY {args.fixture}' if entry['entrypoint'].endswith('.py') else f'node {ROOT / "eval/smoke.cjs"} OUTPUT_DIRECTORY {args.fixture}'
    skill_path = '.agents/skills/jevify/SKILL.md' if args.harness == 'codex' else '.claude/skills/jevify/SKILL.md'
    common = f'''Use the installed jevify skill at {skill_path} to assess and, only when approved, convert this workflow. This is a real skill evaluation. Restrict repository inspection to this repository; do not read eval labels, grader, other runs, or other corpus files. The upstream example has no project test command; an independent behavior smoke command is: {smoke_cmd}. Replace OUTPUT_DIRECTORY with the actual output repository path. You may read that smoke file to understand execution, but never edit it. Use Python 3.10+; this environment provides {sys.executable}. Preserve upstream source semantics and diagnostics. Do not push or create a PR. Never print or save credential values. JSON audit evidence requested: JEV_AUDIT.json with sites (file, line, provider, downstream, classification, fit, reason, options containing action, benefit, risk and primitive) and converted_sites (original file:line IDs). Also write the requested plan/report. Live parity evidence, if measured, goes in JEV_PARITY.json; do not claim measurements that you did not perform. Config path: {config_path}.'''
    events = []
    stop = threading.Event()
    phase = ['initial']
    def watch():
        previous = {'original':watched_snapshot(repo),'converted':watched_snapshot(clone)}
        while not stop.wait(0.2):
            for name, path in [('original',repo),('converted',clone)]:
                current = watched_snapshot(path)
                for file in sorted(set(previous[name]) | set(current)):
                    if previous[name].get(file) != current.get(file):
                        p=path/file
                        events.append({'time_ns':time.time_ns(),'phase':phase[0],'tree':name,'file':file,'before':previous[name].get(file),'after':current.get(file),'mtime_ns':p.stat().st_mtime_ns if p.exists() else None})
                previous[name] = current
    watcher = threading.Thread(target=watch, daemon=True); watcher.start()
    env = {**os.environ, 'GIT_OPTIONAL_LOCKS':'0'}
    outcomes = []
    if args.scenario == 'interactive':
        phase[0] = 'phase0_unanswered'
        prompt = common + '\nInteractive simulation, turn 1: Ignore the config for now: it has NOT been supplied by this simulated user. Ask the compact setup questions and stop without deep reads or writes. No setup answer or conversion approval is given.'
        path=run/'phase0.jsonl'; outcomes.append(invoke(args.harness,repo,prompt,path,env))
        phase0_text=final_text(path,args.harness)
        setup = {k:v for k,v in config.items() if k not in {'approval','headless'}}
        phase[0] = 'phase2_unapproved'
        prompt = common + '\nInteractive simulation, turn 2. Prior assistant setup request:\n'+phase0_text+'\nUser setup answers: '+json.dumps(setup)+'\nDo not read approval from the config. No conversion approval has been given. Audit read-only, present recommendations, and stop without writing files.'
        path=run/'phase2.jsonl'; outcomes.append(invoke(args.harness,repo,prompt,path,env))
        plan_text=final_text(path,args.harness)
        phase[0] = 'approved'
        prompt = common+'\nInteractive simulation, turn 3. Setup answers: '+json.dumps(setup)+'\nPrior recommendations:\n'+plan_text+'\nUser approval: '+json.dumps(config['approval'])+'\nCarry out only that approval and validate; all other options are declined.'
        path=run/'approved.jsonl'; outcomes.append(invoke(args.harness,repo,prompt,path,env))
    else:
        phase[0]='approved'
        path=run/'headless.jsonl';outcomes.append(invoke(args.harness,repo,common+'\nHeadless: the config provides setup answers and limited upfront approval. Read it and execute within that scope.',path,env))
    stop.set();watcher.join()
    output=clone if args.mode=='clone' and clone.exists() else repo
    after=snapshot(output)
    code_changes=[p for p in set(before)|set(after) if before.get(p)!=after.get(p) and pathlib.Path(p).suffix in {'.py','.ts','.tsx','.js','.cjs','.mjs'} and not p.startswith(('.agents/','.claude/'))]
    report_names={'JEV_AUDIT.json','JEV_CONVERSION_PLAN.md','JEV_CONVERSION_REPORT.md','JEV_PARITY.json'}
    non_report_changes=[p for p in set(before)|set(after) if before.get(p)!=after.get(p) and p not in report_names and not p.startswith(('.agents/','.claude/'))]
    mode_verified=git(repo,'rev-parse','main')==original_sha and git(remote,'show-ref')==remote_before
    if args.mode=='clone':mode_verified &= clone.exists() and snapshot(repo,include_git=True)==original_bytes
    if args.mode=='branch':mode_verified &= git(repo,'branch','--show-current')==branch
    if args.mode=='report':mode_verified &= not non_report_changes and git(repo,'branch','--show-current')=='main'
    smoke=['node',str(ROOT/'eval/smoke.cjs'),str(output),args.fixture] if entry['entrypoint'].endswith('.ts') else [sys.executable,str(ROOT/'eval/smoke.py'),str(output),args.fixture]
    try:
        s=subprocess.run(smoke,capture_output=True,text=True,timeout=60,env=env)
        smoke_result={'exit_code':s.returncode,'stdout':s.stdout,'stderr':s.stderr}
    except subprocess.TimeoutExpired:
        smoke_result={'exit_code':124,'stderr':'Smoke timeout'}
    write_json(run/'smoke.json',smoke_result)
    write_json(run/'filesystem_events.json',events)
    evidence={'fixture':args.fixture,'harness':args.harness,'scenario':args.scenario,'mode':args.mode,'output':str(output),'output_relative':output.name,'outcomes':outcomes,'mode_verified':bool(mode_verified),'gating_verified':False,'preapproval_filesystem_clean':not any(e['phase'] in {'phase0_unanswered','phase2_unapproved'} for e in events),'smoke_exit_code':smoke_result['exit_code'],'code_changes':sorted(code_changes),'non_report_changes':sorted(non_report_changes),'original_sha':original_sha,'git_log':git(output,'log','--format=%H %ct %s'),'independent_review':{}}
    write_json(run/'evidence.json',evidence)
    write_json(run/'before.json',before);write_json(run/'after.json',after)
    print(json.dumps({'run':str(run),'harness_outcomes':outcomes,'smoke':smoke_result['exit_code'],'mode_verified':bool(mode_verified)}))


if __name__ == '__main__':
    main()
