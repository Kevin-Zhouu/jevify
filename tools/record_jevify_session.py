#!/usr/bin/env python3
"""Record real Codex turns with asciinema; never manufacture assistant output.

Usage: asciinema rec --command 'python3 tools/record_jevify_session.py REPO EVIDENCE' session.cast
REPO must be a fresh committed corpus copy with the unmodified skill installed.
This is a scripted interactive demonstration, with deliberate no-key setup.
"""
import json, os, pathlib, subprocess, sys

repo = pathlib.Path(sys.argv[1]).resolve()
out = pathlib.Path(sys.argv[2]).resolve()
out.mkdir(parents=True, exist_ok=True)
env = {k: v for k, v in os.environ.items() if not any(s in k.upper() for s in ('API_KEY', 'API_TOKEN'))}
prompts = [
    '$jevify convert workflow.py. Keep user-facing answers compact. Ask setup first.',
    'New branch jev-convert/demo. Neither key; conservative with the original fallback. Audit workflow.py and show the options, then wait for my approval. Keep the plan compact.',
    'Approve only the pure DECISION classifier with a confidence gate and original fallback. Proceed on jev-convert/demo. No keys: explicitly skip live validation. Run the offline project smoke at ' + str(pathlib.Path(__file__).resolve().parents[1] / 'eval/smoke.py') + ' against this repository with fixture anthropic_classification. Finish with a brief report summary. Do not push.'
]
(out / 'prompts.json').write_text(json.dumps(prompts, indent=2)+'\n')
thread = None
for n, prompt in enumerate(prompts, 1):
    print('\n\033[1;32mYou\033[0m\n' + prompt + '\n', flush=True)
    cmd = ['codex', 'exec'] + (['resume', thread] if thread else [])
    cmd += ['--json', '--dangerously-bypass-approvals-and-sandbox', prompt]
    proc = subprocess.Popen(cmd, cwd=repo, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    with (out / f'turn-{n}.jsonl').open('w') as raw:
        for line in proc.stdout:
            raw.write(line); raw.flush()
            try: event = json.loads(line)
            except ValueError: continue
            if event.get('type') == 'thread.started': thread = event['thread_id']
            item = event.get('item', {})
            if event.get('type') == 'item.completed' and item.get('type') == 'agent_message':
                print('\033[1;36mJevify · Codex\033[0m\n' + item['text'] + '\n', flush=True)
    err = proc.stderr.read()
    rc = proc.wait()
    (out / f'turn-{n}.stderr.txt').write_text(err)
    (out / f'turn-{n}.status.json').write_text(json.dumps({'returncode': rc, 'thread': thread})+'\n')
    snapshot = subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True)
    (out / f'turn-{n}.git-status.txt').write_text(snapshot)
    if rc: raise SystemExit(f'Codex turn {n} failed ({rc}); retained all evidence.')
    if n < 3 and snapshot: raise SystemExit('Unexpected writes before approval; retained evidence, stopping.')
print('\n\033[1;32m$ git diff main -- workflow.py\033[0m', flush=True)
diff = subprocess.check_output(['git','diff','main','--','workflow.py'],cwd=repo,text=True)
print(diff, flush=True)
(out/'workflow.diff').write_text(diff)
subprocess.run(['git','log','--oneline','-3'],cwd=repo,check=True)
