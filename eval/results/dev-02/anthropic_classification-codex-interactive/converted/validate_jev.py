"""Live paired evaluation and fault checks; no production provider changes."""
import ast
import concurrent.futures
import contextlib
import copy
import csv
import io
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import threading
import time
import types
import urllib.error
import urllib.request
from unittest.mock import patch
import jev_decisions as decisions

ROOT = Path(__file__).resolve().parent
LOCAL = threading.local()
BASELINE_MODEL = 'anthropic/claude-haiku-4.5'


def adapter_create(**kwargs):
    assert kwargs['model'] == 'claude-haiku-4-5'
    assert kwargs['messages'][-1] == {'role': 'assistant', 'content': '<category>'}
    assert kwargs['stop_sequences'] == ['</category>']
    assert kwargs['temperature'] == 0 and kwargs['max_tokens'] == 4096
    payload = dict(kwargs)
    payload['model'] = BASELINE_MODEL
    payload['stop'] = payload.pop('stop_sequences')
    request = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',
        data=json.dumps(payload).encode(), headers={
            'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'],
            'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=45) as response:
        result = json.load(response)
    LOCAL.baseline = result
    return types.SimpleNamespace(content=[types.SimpleNamespace(text=result['choices'][0]['message']['content'])])


def load_workflow():
    # Evaluation-only Anthropic transport shim. The preserved function builds requests/parses outputs.
    module = types.ModuleType('anthropic')
    module.Anthropic = lambda **kw: types.SimpleNamespace(messages=types.SimpleNamespace(create=adapter_create))
    sys.modules['anthropic'] = module
    import workflow
    before = ast.parse(subprocess.check_output(['git', 'show', 'eff84f8f58d676d6b3b2eb21ae7b906300e2ef1b:workflow.py'], cwd=ROOT, text=True))
    after = ast.parse((ROOT/'workflow.py').read_text())
    old = next(n for n in before.body if isinstance(n, ast.FunctionDef) and n.name == 'simple_classify')
    new = next(n for n in after.body if isinstance(n, ast.FunctionDef) and n.name == '_original_simple_classify')
    new.name = old.name
    assert ast.dump(old) == ast.dump(new), 'Original callable changed'
    return workflow


def cases():
    items = []
    for name, split in [('train', 'calibration'), ('test', 'confirmation')]:
        groups = {}
        with (ROOT/f'data/{name}.tsv').open() as f:
            for line, row in enumerate(csv.DictReader(f, delimiter='\t'), 2):
                bucket = groups.setdefault(row['label'], [])
                if len(bucket) < 2 and row['text'] not in [v['input'] for v in items]:
                    item = dict(input=row['text'], provenance='repo', source=f'data/{name}.tsv:{line}', split=split)
                    bucket.append(item); items.append(item)
    for ticket in ['Can you explain my bill and help reset my password?', 'Hello.', 'What is the weather tomorrow?', 'My claim was denied and I need to update my address.']:
        items.append(dict(input=ticket, provenance='synthetic', source='validate_jev.py boundary cases', split='confirmation'))
    return items


def fault_checks(workflow, captured=None):
    faults = {}
    ticket = 'Please explain my invoice.'
    sentinel = object()
    def verify(context):
        calls = []
        def original(value):
            calls.append(value); return sentinel
        with context, patch.object(workflow, '_original_simple_classify', original):
            assert workflow.simple_classify(ticket) is sentinel
        assert calls == [ticket]
    for name, exception in [('timeout', TimeoutError()), ('rate_limit', urllib.error.HTTPError(decisions.ENDPOINT,429,'rate limit',None,None)), ('error', RuntimeError())]:
        verify(patch.object(urllib.request, 'urlopen', side_effect=exception)); faults[name] = True
    verify(patch.dict(os.environ, {decisions.KEY_ENV: ''})); faults['missing_key'] = True
    for payload in [{}, {'answers': {'category': {'confidence': float('nan')}}}]:
        verify(patch.object(urllib.request, 'urlopen', return_value=io.StringIO(json.dumps(payload))))
    faults['malformed'] = True
    assert not decisions.accepts(decisions.THRESHOLD - .01)
    for value in [float('nan'), float('inf'), True, -1, 1.01, '1']:
        assert not decisions.accepts(value)
    faults['gate_invalid_numbers'] = True
    if captured:
        with patch.object(urllib.request, 'urlopen', return_value=io.StringIO(json.dumps(captured))):
            result = decisions.evaluate(ticket)
        assert result == captured
        # Gate-boundary injection; actual captured response, never invented inference.
        with patch.object(decisions, 'accepts', return_value=False):
            verify(patch.object(urllib.request, 'urlopen', return_value=io.StringIO(json.dumps(captured))))
        faults['below_threshold'] = True
        answer = captured['answers']['category']
        if decisions.accepts(answer['confidence']):
            with patch.object(urllib.request, 'urlopen', return_value=io.StringIO(json.dumps(captured))), patch.object(workflow, '_original_simple_classify', side_effect=AssertionError('Unexpected fallback')):
                assert workflow.simple_classify(ticket) == answer['choice']
            faults['accepted_replay'] = True
        for field, bad in [('confidence', float('nan')), ('confidence', True), ('choice', 'unknown')]:
            invalid = copy.deepcopy(captured); invalid['answers']['category'][field] = bad
            verify(patch.object(urllib.request, 'urlopen', return_value=io.StringIO(json.dumps(invalid))))
        invalid = copy.deepcopy(captured); del invalid['usage']
        verify(patch.object(urllib.request, 'urlopen', return_value=io.StringIO(json.dumps(invalid))))
        faults['invalid_response_fields'] = True
    else:
        # Pure predicate boundary tested; wrapper low-confidence branch needs a real response.
        faults['below_threshold'] = False
    error = RuntimeError('original sentinel')
    with patch.object(urllib.request, 'urlopen', side_effect=TimeoutError()), patch.object(workflow, '_original_simple_classify', side_effect=error) as original:
        try: workflow.simple_classify(ticket)
        except RuntimeError as exc: assert exc is error
        else: raise AssertionError('Original exception swallowed')
        assert original.call_count == 1
    faults['original_exception'] = True
    with patch.object(urllib.request, 'urlopen', side_effect=AssertionError('Unexpected network')), patch.object(workflow, '_original_simple_classify', return_value=sentinel) as original:
        assert workflow.simple_classify('x' * (decisions.MAX_STATE_BYTES+1)) is sentinel
        assert original.call_count == 1
    faults['oversize'] = True
    return faults


def measure(workflow, case):
    row = dict(case)
    try:
        start = time.perf_counter()
        raw = decisions.evaluate(case['input'])
        elapsed = (time.perf_counter()-start)*1000
        start = time.perf_counter()
        original = workflow._original_simple_classify(case['input'])
        original_elapsed = (time.perf_counter()-start)*1000
        baseline = LOCAL.baseline
        answer = raw['answers']['category']
        row.update(live=True, model=raw['model'], request_id=raw.get('id'), jev_answer=answer['choice'], confidence=answer['confidence'],
            original_answer=original, original_model=baseline['model'], original_request_id=baseline.get('id'),
            fallback_taken=not decisions.accepts(answer['confidence']), latency_ms=elapsed, original_latency_ms=original_elapsed,
            cost_usd=raw['usage'].get('cost'), original_cost_usd=baseline['usage'].get('cost'),
            cost_source='provider-reported usage.cost', jev_response=raw,
            original_usage=baseline['usage'])
        return row
    except Exception as exc:
        # Exception strings and headers can contain credentials; retain only bounded diagnostics.
        row.update(error=type(exc).__name__, http_status=getattr(exc, 'code', None))
        return row


def summary(rows):
    output = {}
    for split in ['all', 'calibration', 'confirmation']:
        rs = [r for r in rows if split == 'all' or r['split'] == split]
        if not rs: continue
        curves = []
        for threshold in [0, .5, .7, .8, .9, .95, .99, 1]:
            accepted = [r for r in rs if r['confidence'] >= threshold]
            curves.append(dict(threshold=threshold, accepted=len(accepted), agreement=sum(r['jev_answer']==r['original_answer'] for r in accepted)/len(accepted) if accepted else None, fallback_fraction=1-len(accepted)/len(rs)))
        def percentiles(values):
            values=sorted(values); return {'p50':statistics.median(values),'p95':values[min(len(values)-1, int(.95*len(values)))]}
        costs_known = all(r['cost_usd'] is not None and r['original_cost_usd'] is not None for r in rs)
        output[split] = dict(n=len(rs), curve=curves, jev_latency_ms=percentiles([r['latency_ms'] for r in rs]), original_latency_ms=percentiles([r['original_latency_ms'] for r in rs]),
            estimated_cascade_mean_latency_ms=statistics.mean(r['latency_ms']+r['fallback_taken']*r['original_latency_ms'] for r in rs),
            estimated_cascade_mean_cost_usd=statistics.mean(r['cost_usd']+r['fallback_taken']*r['original_cost_usd'] for r in rs) if costs_known else None)
    return output


def main():
    workflow = load_workflow()
    samples = cases()
    first = measure(workflow, samples[0])
    results = [first]
    if 'error' not in first:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            results.extend(pool.map(lambda case: measure(workflow, case), samples[1:]))
    rows = [r for r in results if 'error' not in r]
    captured = next((r['jev_response'] for r in rows if not r['fallback_taken']), rows[0]['jev_response'] if rows else None)
    faults = fault_checks(workflow, captured)
    # Replay each actual response through the public integration and assert the real gate outcome.
    for row in rows:
        with patch.object(urllib.request, 'urlopen', return_value=io.StringIO(json.dumps(row['jev_response']))), patch.object(workflow, '_original_simple_classify', return_value=row['original_answer']) as fallback:
            value=workflow.simple_classify(row['input'])
            assert value == (row['original_answer'] if row['fallback_taken'] else row['jev_answer'])
            assert fallback.call_count == int(row['fallback_taken'])
    evidence = {'sites':[dict(site_id='workflow.py:83', primitive='Choice', threshold=decisions.THRESHOLD, rows=rows, errors=[r for r in results if 'error' in r], faults=faults, summary=summary(rows))],
        'planned_inputs':len(samples), 'attempted_inputs':len(results),
        'baseline_adapter':'Unchanged original callable; evaluation-only Anthropic transport mapped to authorized OpenRouter same-model route, with stop_sequences renamed stop; AST equality asserted.',
        'threshold_policy':'0.9 fixed before confirmation; calibration and confirmation reported separately; no tuning on confirmation.',
        'status':'measured' if len(rows)>=30 else 'incomplete'}
    (ROOT/'JEV_PARITY.json').write_text(json.dumps(evidence,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':evidence['status'],'pairs':len(rows),'errors':evidence['sites'][0]['errors'],'faults':faults,'summary':summary(rows)},indent=2))

if __name__ == '__main__': main()
