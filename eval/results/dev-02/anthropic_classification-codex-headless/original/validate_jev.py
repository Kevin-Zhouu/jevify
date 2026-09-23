"""Reproduce live parity and injected fallback tests; never writes credentials."""
import ast
import concurrent.futures
import csv
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import threading
import time
from types import SimpleNamespace
from unittest.mock import patch
import urllib.error
import urllib.request

import jev_decisions as j

SOURCE_SHA = 'eff84f8f58d676d6b3b2eb21ae7b906300e2ef1b'
BASELINE_MODEL = 'anthropic/claude-haiku-4.5'
local = threading.local()


def baseline_transport(**kwargs):
    assert kwargs['model'] == 'claude-haiku-4-5'
    assert kwargs['messages'][-1] == {'role': 'assistant', 'content': '<category>'}
    assert kwargs['stop_sequences'] == ['</category>']
    assert kwargs['temperature'] == 0.0 and kwargs['max_tokens'] == 4096
    body = dict(kwargs)
    body['model'] = BASELINE_MODEL
    body['stop'] = body.pop('stop_sequences')
    request = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',
        data=json.dumps(body).encode(), headers={
            'Authorization': 'Bearer ' + os.environ[j.KEY_ENV],
            'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.load(response)
    local.original = result
    return SimpleNamespace(content=[SimpleNamespace(text=result['choices'][0]['message']['content'])])


def load_workflows():
    source = subprocess.check_output(['git', 'show', SOURCE_SHA + ':workflow.py'], text=True)
    current = Path('workflow.py').read_text()
    old_fn = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef))
    new_fn = next(n for n in ast.parse(current).body if isinstance(n, ast.FunctionDef) and n.name == '_original_simple_classify')
    old_fn.name = new_fn.name
    assert ast.dump(old_fn) == ast.dump(new_fn), 'Original function changed'
    shim = SimpleNamespace(Anthropic=lambda **_: SimpleNamespace(messages=SimpleNamespace(create=baseline_transport)))
    original, converted = {}, {}
    with patch.dict(sys.modules, {'anthropic': shim}):
        exec(compile(source, 'upstream_workflow.py', 'exec'), original)
        exec(compile(current, 'workflow.py', 'exec'), converted)
    assert original['categories'] == converted['categories']
    return original, converted


def samples():
    groups = {}
    with Path('data/test.tsv').open(newline='') as f:
        for line, row in enumerate(csv.DictReader(f, delimiter='\t'), 2):
            groups.setdefault(row['label'], []).append((row['text'], 'repo', f'data/test.tsv:{line}'))
    result = [row for group in groups.values() for row in group[:3]]
    for text in [
        'I need help with my bill and also want to cancel my policy.',
        'My claim was denied. How do I appeal?',
        'I do not understand this fee; is it correct or should I request a refund?',
        'What is the difference between your comprehensive and collision coverage?',
        'Hello.',
        'Can you recommend a pasta recipe?',
        '',
        'Where can I find your opening hours?',
    ]:
        result.append((text, 'synthetic', 'validate_jev.py:samples'))
    assert len({row[0] for row in result}) == len(result) and len(result) >= 30
    return result


def safe_error(exc):
    return {'type': type(exc).__name__, 'http_status': getattr(exc, 'code', None)}


def measure(sample, original):
    text, provenance, source = sample
    row = {'input': text, 'provenance': provenance, 'source': source, 'model': j.MODEL,
           'original_model': BASELINE_MODEL, 'live': True}
    start = time.perf_counter()
    try:
        raw = j.evaluate(text)
        row.update(latency_ms=(time.perf_counter()-start)*1000, request_id=raw.get('id'),
                   jev_response=raw, cost_usd=raw.get('usage', {}).get('cost'))
        answer = raw['answers']['category']
        row.update(jev_answer=answer['choice'], confidence=answer['confidence'],
                   fallback_taken=j.accepted_answer(raw) is None)
    except Exception as exc:
        row['jev_error'] = safe_error(exc)
    start = time.perf_counter()
    try:
        row['original_answer'] = original['simple_classify'](text)
        raw = local.original
        row.update(original_latency_ms=(time.perf_counter()-start)*1000,
                   original_cost_usd=raw.get('usage', {}).get('cost'),
                   original_request_id=raw.get('id'), original_response_model=raw.get('model'),
                   original_usage=raw.get('usage'), original_finish_reason=raw['choices'][0].get('finish_reason'))
    except Exception as exc:
        row['original_error'] = safe_error(exc)
    return row


def faults(converted, captured):
    results = {}
    for name, error in [('timeout', TimeoutError()), ('rate_limit', urllib.error.HTTPError(j.ENDPOINT, 429, 'rate_limit', {}, None)), ('error', RuntimeError())]:
        for raises in [False, True]:
            calls = []
            sentinel = object()
            original_error = RuntimeError('original sentinel')
            def original(text):
                calls.append(text)
                if raises:
                    raise original_error
                return sentinel
            with patch.object(j.urllib.request, 'urlopen', side_effect=error), patch.dict(os.environ, {j.KEY_ENV: 'fault-test-placeholder'}):
                try:
                    result = j.classify('ticket', original, 'claude-haiku-4-5')
                    assert not raises and result is sentinel
                except RuntimeError as exc:
                    assert raises and exc is original_error
            assert calls == ['ticket']
        results[name] = True
    assert not j.confident(j.THRESHOLD-0.01) and j.confident(j.THRESHOLD)
    assert all(not j.confident(x) for x in [True, None, float('nan'), float('inf'), -1, 1.1])
    results['gate_boundary'] = True
    if captured:
        calls = []
        with patch.object(j, 'evaluate', return_value=captured), patch.object(j, 'confident', return_value=False):
            assert j.classify('ticket', lambda x: calls.append(x) or 'original sentinel', 'claude-haiku-4-5') == 'original sentinel'
        assert calls == ['ticket']
        results['below_threshold'] = True
    for name, value in [('malformed', {}), ('unknown_option', {'model': j.MODEL, 'answers': {'category': {'type': 'choice', 'choice': 'invalid'}}})]:
        calls = []
        with patch.object(j, 'evaluate', return_value=value):
            assert j.classify('ticket', lambda x: calls.append(x) or 'sentinel', 'claude-haiku-4-5') == 'sentinel'
        assert calls == ['ticket']
        results[name] = True
    with patch.dict(os.environ, {}, clear=True):
        for text in ['ticket', 'x' * (j.MAX_INPUT_BYTES + 1), None]:
            calls = []
            assert j.classify(text, lambda x: calls.append(x) or 'sentinel', 'claude-haiku-4-5') == 'sentinel'
            assert calls == [text]
    results['missing_key_and_unsupported_input'] = True
    return results


def summary(rows):
    paired = [r for r in rows if 'jev_answer' in r and 'original_answer' in r]
    out = {'attempted': len(rows), 'paired': len(paired), 'cost_basis': 'provider-reported usage.cost; USD',
           'threshold_policy': '0.9 fixed before measurement, no tuning; all samples are confirmation, no calibration set'}
    if not paired:
        return out
    out['raw_agreement'] = sum(r['jev_answer']==r['original_answer'] for r in paired)/len(paired)
    out['confidence_curve'] = []
    for threshold in [0, .5, .7, .8, j.THRESHOLD, .95, 1]:
        accepted = [r for r in paired if r['confidence'] >= threshold]
        out['confidence_curve'].append({'threshold': threshold, 'accepted': len(accepted),
            'agreement': sum(r['jev_answer']==r['original_answer'] for r in accepted)/len(accepted) if accepted else None,
            'fallback_fraction': 1-len(accepted)/len(paired)})
    out['fallback_rate'] = sum(r['fallback_taken'] for r in paired)/len(paired)
    for field in ['latency_ms', 'original_latency_ms']:
        values = sorted(r[field] for r in paired)
        out[field] = {'p50': statistics.median(values), 'p95': values[min(len(values)-1, int(.95*len(values)))]}
    out['expected_cascade_latency_ms'] = statistics.mean(r['latency_ms'] + (r['original_latency_ms'] if r['fallback_taken'] else 0) for r in paired)
    if all(isinstance(r.get(f), (float, int)) for r in paired for f in ['cost_usd', 'original_cost_usd']):
        out['mean_original_cost_usd'] = statistics.mean(r['original_cost_usd'] for r in paired)
        out['expected_cascade_cost_usd'] = statistics.mean(r['cost_usd'] + (r['original_cost_usd'] if r['fallback_taken'] else 0) for r in paired)
    return out


def main():
    original, converted = load_workflows()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(lambda sample: measure(sample, original), samples()))
    # Exercise actual public wrapper with captured real responses, never invented successes.
    for row in rows:
        if 'jev_response' not in row or 'original_answer' not in row:
            continue
        calls = []
        with patch.object(j, 'evaluate', return_value=row['jev_response']):
            converted['_original_simple_classify'] = lambda x: calls.append(x) or row['original_answer']
            output = converted['simple_classify'](row['input'])
        assert output == (row['original_answer'] if row['fallback_taken'] else row['jev_answer'])
        assert len(calls) == int(row['fallback_taken']) and isinstance(output, str)
        row['integration_replay_passed'] = True
    captured = next((r['jev_response'] for r in rows if 'jev_response' in r), None)
    evidence = {'sites': [{'site_id': 'workflow.py:83', 'primitive': 'Choice', 'threshold': j.THRESHOLD,
                'rows': rows, 'faults': faults(converted, captured), 'summary': summary(rows)}],
                'source_sha': SOURCE_SHA, 'baseline_adapter': 'Original callable from git source; only transport maps model namespace and stop_sequences to stop. Request and parsing AST verified unchanged.',
                'date': '2026-09-23'}
    Path('JEV_PARITY.json').write_text(json.dumps(evidence, indent=2, allow_nan=False)+'\n')
    print(json.dumps(evidence['sites'][0]['summary'], indent=2))
    print('Faults:', json.dumps(evidence['sites'][0]['faults']))
    errors = [r for r in rows if 'jev_error' in r or 'original_error' in r]
    print('Failed pairs:', len(errors))
    if errors:
        print(json.dumps({k:v for k,v in errors[0].items() if k.endswith('_error')}))


if __name__ == '__main__':
    main()
