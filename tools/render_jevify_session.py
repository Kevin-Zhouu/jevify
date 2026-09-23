#!/usr/bin/env python3
"""Retiming only: preserve every captured terminal output byte, then render with agg.

Requires agg 1.9+; invoke from the repository root after record_jevify_session.py.
The raw full.cast retains actual wall-clock timing. Preview is NOT a speed benchmark.
"""
import json, pathlib, subprocess
root = pathlib.Path(__file__).resolve().parents[1]
directory = root / 'docs/demos/jevify-session'
lines = (directory/'full.cast').read_text().splitlines()
header, *events = [json.loads(line) for line in lines]
weights = []
for e in events:
    text = e[2] if e[1] == 'o' else ''
    weight = .03
    if '$jevify convert workflow.py' in text: weight = 1.3
    if 'Output location?' in text: weight = 2.6
    if 'Select A or B' in text: weight = 3.5
    if 'Approve only the pure DECISION' in text: weight = 1.7
    if 'live validation' in text.lower() and ('committed' in text.lower() or 'converted' in text.lower()): weight = 2.6
    if 'return ' in text and ('@@' in text or '+def ' in text): weight = 3.5
    weights.append(weight)
# Display all events; compress waits only. 17 s + agg's final 1.5 s hold.
scale = 17 / sum(weights)
t = 0.0
preview = [header]
for event, weight in zip(events, weights):
    preview.append([round(t, 6), *event[1:]])
    t += weight * scale
# Empty output holds the last captured terminal state without changing text.
preview.append([17.0, 'o', ''])
assert ''.join(e[2] for e in events if e[1]=='o') == ''.join(e[2] for e in preview[1:] if e[1]=='o')
(directory/'preview.cast').write_text('\n'.join(json.dumps(e,ensure_ascii=False) for e in preview)+'\n')
subprocess.run(['agg', '--theme','github-dark','--font-size','16','--line-height','1.2','--idle-time-limit','999','--last-frame-duration','1.5',str(directory/'preview.cast'),str(root/'docs/demos/jevify-session.gif')],check=True)
