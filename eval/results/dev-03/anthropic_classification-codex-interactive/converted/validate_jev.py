"""Live confirmation and injected faults; never persist headers or exception text."""
import ast
import contextlib
import copy
import csv
import io
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import types
import urllib.request
from unittest.mock import patch

import jev_decisions as decisions

ROOT = Path(__file__).resolve().parent
SOURCE_REVISION = '1c953f75ebe1580de909072ce9a73b8ab8f11d05'
BASELINE_MODEL = 'anthropic/claude-haiku-4.5'


def load_workflows():
    sdk = types.ModuleType('anthropic')
    sdk.Anthropic = lambda **kwargs: types.SimpleNamespace(messages=types.SimpleNamespace(create=None))
    with patch.dict(sys.modules, {'anthropic': sdk}):
        import workflow
        source = subprocess.check_output(['git', 'show', SOURCE_REVISION + ':workflow.py'], cwd=ROOT, text=True)
        original = types.ModuleType('source_original')
        exec(compile(source, 'git:workflow.py', 'exec'), original.__dict__)
    before = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == 'simple_classify')
    after = next(n for n in ast.parse((ROOT/'workflow.py').read_text()).body if isinstance(n, ast.FunctionDef) and n.name == '_original_simple_classify')
    after.name = before.name
    assert ast.dump(before) == ast.dump(after), 'Original prompt and parsing AST changed'
    assert workflow.categories == original.categories and workflow.MODEL == original.MODEL
    return workflow, original


def capture_request(module, function, ticket):
    requests = []
    def record(**kwargs):
        requests.append(kwargs)
        return types.SimpleNamespace(content=[types.SimpleNamespace(text='  boundary sentinel  ')])
    with patch.object(module.client.messages, 'create', record):
        assert function(ticket) == 'boundary sentinel'
    assert len(requests) == 1
    return requests[0]


class BaselineAdapter:
    """Only SDK transport/response envelope is adapted; original builder/parser execute."""
    def __init__(self, expected):
        self.expected = expected
        self.evidence = None

    def create(self, **kwargs):
        assert kwargs == self.expected
        assert kwargs['model'] == 'claude-haiku-4-5'
        payload = copy.deepcopy(kwargs)
        payload['model'] = BASELINE_MODEL
        payload['stop'] = payload.pop('stop_sequences')
        # Fail rather than silently routing to a provider without required parameters.
        payload['provider'] = {'require_parameters': True}
        request = urllib.request.Request(
            'https://openrouter.ai/api/v1/chat/completions',
            data=json.dumps(payload).encode(),
            headers={'Authorization': 'Bearer ' + os.environ[decisions.KEY_ENV],
                     'Content-Type': 'application/json'})
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.load(response)
        assert body['model'] == BASELINE_MODEL, 'Baseline model mismatch'
        text = body['choices'][0]['message']['content']
        assert isinstance(text, str)
        self.evidence = {k: body.get(k) for k in ('id', 'model', 'usage', 'provider')}
        self.evidence['finish_reason'] = body['choices'][0].get('finish_reason')
        return types.SimpleNamespace(content=[types.SimpleNamespace(text=text)])


def replay(workflow, ticket, response, original_answer, reject=False):
    fallback_calls = []
    def fallback(value):
        assert value == ticket
        fallback_calls.append(value)
        return original_answer
    with patch.object(decisions, '_post', return_value=response), patch.object(workflow, '_original_simple_classify', fallback):
        gate = patch.object(decisions, 'accepts', return_value=False) if reject else contextlib.nullcontext()
        with gate, contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = workflow.simple_classify(ticket)
        assert stdout.getvalue() == ''
    label, confidence = decisions.parse_response(response)
    accepted = decisions.accepts(confidence) and not reject
    assert result == (label if accepted else original_answer)
    assert isinstance(result, str) and len(fallback_calls) == (0 if accepted else 1)
    return not accepted


def run_faults(workflow, capture):
    faults = {}
    def check_fault(name, target, **kwargs):
        count = []
        sentinel = 'original sentinel'
        def fallback(value):
            count.append(value)
            return sentinel
        with patch.object(decisions, target, **kwargs), patch.object(workflow, '_original_simple_classify', fallback):
            assert workflow.simple_classify('Invoice question') == sentinel
        assert len(count) == 1
        error = RuntimeError('original exception sentinel')
        count.clear()
        def fail(value):
            count.append(value)
            raise error
        with patch.object(decisions, target, **kwargs), patch.object(workflow, '_original_simple_classify', fail):
            try:
                workflow.simple_classify('Invoice question')
            except RuntimeError as actual:
                assert actual is error
            else:
                raise AssertionError('Original exception was swallowed')
        assert len(count) == 1
        faults[name] = True
    check_fault('error', '_post', side_effect=OSError())
    check_fault('timeout', '_post', side_effect=TimeoutError())
    check_fault('rate_limit', '_post', side_effect=decisions.HTTPFailure(429))
    check_fault('malformed', '_post', return_value=[])
    with patch.dict(os.environ, {decisions.KEY_ENV: ''}):
        check_fault('missing_key', '_post', side_effect=AssertionError('Transport must not run'))
    for ticket in (None, 'x' * decisions.MAX_REQUEST_BYTES):
        counter = []
        with patch.object(decisions, '_post', side_effect=AssertionError('Transport must not run')), patch.object(workflow, '_original_simple_classify', lambda x: counter.append(x) or 'original'):
            assert workflow.simple_classify(ticket) == 'original' and counter == [ticket]
    faults['unsupported_and_oversize'] = True
    if capture is not None:
        # Actual response with gate rejection, not invented successful inference.
        assert replay(workflow, 'Invoice question', capture, 'original sentinel', reject=True)
        faults['below_threshold'] = True
        for name, change in [
            ('nonfinite', lambda r: r['answers']['category'].update(confidence=float('nan'))),
            ('bool_confidence', lambda r: r['answers']['category'].update(confidence=True)),
            ('unknown_option', lambda r: r['answers']['category'].update(choice='unknown')),
            ('invalid_usage', lambda r: r.update(usage=[])),
            ('missing_usage', lambda r: r.pop('usage')),
            ('wrong_model', lambda r: r.update(model='invalid')),
        ]:
            malformed = copy.deepcopy(capture)
            change(malformed)
            check_fault(name, '_post', return_value=malformed)
    else:
        faults['below_threshold'] = False
    assert not decisions.accepts(decisions.THRESHOLD - .01)
    return faults


def cases():
    groups = {}
    with (ROOT/'data/test.tsv').open() as file:
        for line, row in enumerate(csv.DictReader(file, delimiter='\t'), 2):
            groups.setdefault(row['label'], []).append((row['text'], 'repo', f'data/test.tsv:{line}', 'confirmation'))
    selected = [row for group in groups.values() for row in group[:3]]
    assert len(selected) == 30 and len({row[0] for row in selected}) == 30
    selected += [(s, 'synthetic', 'validate_jev.py:cases', 'diagnostic') for s in [
        'I need help with a claim and changing my policy. Which should I do first?',
        'I do not recognize this charge. Is it a mistake or part of my premium?',
        '',
        'Can you recommend a pasta recipe?',
    ]]
    return selected


def safe_error(error):
    return {'type': type(error).__name__, 'http_status': getattr(error, 'code', getattr(error, 'status', None))}


def summarize(rows):
    def quantile(values, p):
        values = sorted(values)
        return values[max(0, math.ceil(len(values)*p)-1)] if values else None
    curve = []
    for threshold in sorted(set([0, .5, .8, .9, decisions.THRESHOLD, .99, 1])):
        accepted = [r for r in rows if r['confidence'] >= threshold]
        curve.append({'threshold': threshold, 'accepted': len(accepted), 'agreement': sum(r['jev_answer']==r['original_answer'] for r in accepted)/len(accepted) if accepted else None, 'fallback_fraction': 1-len(accepted)/len(rows) if rows else None})
    result = {'n': len(rows), 'raw_agreement': sum(r['jev_answer']==r['original_answer'] for r in rows)/len(rows) if rows else None, 'confidence_curve': curve}
    for name, field in [('jev', 'latency_ms'), ('original', 'original_latency_ms')]:
        result[name+'_latency_ms'] = {q:quantile([r[field] for r in rows], p) for q,p in [('p50',.5),('p95',.95)]}
    result['cascade_mean_latency_ms_estimate'] = sum(r['latency_ms'] + r['fallback_taken']*r['original_latency_ms'] for r in rows)/len(rows) if rows else None
    known = rows and all(r['cost_usd'] is not None and r['original_cost_usd'] is not None for r in rows)
    result['cascade_mean_cost_usd_estimate'] = sum(r['cost_usd']+r['fallback_taken']*r['original_cost_usd'] for r in rows)/len(rows) if known else None
    result['original_mean_cost_usd'] = sum(r['original_cost_usd'] for r in rows)/len(rows) if known else None
    return result


def main():
    workflow, original = load_workflows()
    rows, errors, captures = [], [], []
    for ticket, provenance, source, split in cases():
        expected = capture_request(original, original.simple_classify, ticket)
        assert capture_request(workflow, workflow._original_simple_classify, ticket) == expected
        adapter = BaselineAdapter(expected)
        response = None
        try:
            start = time.monotonic()
            response = decisions.evaluate(ticket)
            latency = (time.monotonic()-start)*1000
            captures.append(response)
            start = time.monotonic()
            with patch.object(workflow.client.messages, 'create', adapter.create):
                baseline = workflow._original_simple_classify(ticket)
            original_latency = (time.monotonic()-start)*1000
            fallback_taken = replay(workflow, ticket, response, baseline)
            label, confidence = decisions.parse_response(response)
            assert response.get('id') and adapter.evidence['id']
            rows.append(dict(input=ticket, provenance=provenance, source=source, split=split,
                model=response['model'], live=True, request_id=response['id'],
                jev_answer=label, original_answer=baseline, confidence=confidence,
                fallback_taken=fallback_taken, latency_ms=latency,
                cost_usd=response.get('usage', {}).get('cost'), original_model=BASELINE_MODEL,
                original_latency_ms=original_latency, original_cost_usd=adapter.evidence['usage'].get('cost'),
                cost_source='provider-reported usage.cost', response=response, original_response=adapter.evidence))
            print(json.dumps({'pairs':len(rows),'split':split,'matched':label==baseline,'fallback':fallback_taken}), flush=True)
        except Exception as error:
            errors.append(dict(source=source, split=split, **safe_error(error), jev_response=response))
            print(json.dumps({'attempt_failed':errors[-1]['type'], 'http_status':errors[-1]['http_status']}), flush=True)
            # Systemic access failures do not warrant 34 repeated paid requests.
            if getattr(error, 'code', getattr(error, 'status', None)) in (401,403,404):
                break
    faults = run_faults(workflow, captures[0] if captures else None)
    evidence = {'source_revision': SOURCE_REVISION, 'baseline_adapter': 'Unchanged original callable via isolated OpenRouter same-model SDK boundary; namespace and stop field translated; prefill retained.',
        'threshold_policy': 'Provisional, frozen before confirmation; no calibration or retuning',
        'sites':[{'site_id':'workflow.py:83','primitive':'Choice','threshold':decisions.THRESHOLD,'rows':rows,'errors':errors,'faults':faults,
        'confirmation':summarize([r for r in rows if r['split']=='confirmation']), 'diagnostic':summarize([r for r in rows if r['split']=='diagnostic'])}],
        'checks': {'source_ast_identity':True,'request_identity':True,'public_wrapper_replay':bool(rows)},
        'unpaired_captures': captures if not rows else []}
    (ROOT/'JEV_PARITY.json').write_text(json.dumps(evidence,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'faults':faults,'confirmation':evidence['sites'][0]['confirmation']}),flush=True)


def replay_saved():
    """No network: verify every actual capture and all failure branches again."""
    workflow, original = load_workflows()
    evidence = json.loads((ROOT/'JEV_PARITY.json').read_text())
    rows = evidence['sites'][0]['rows']
    assert rows
    for row in rows:
        expected = capture_request(original, original.simple_classify, row['input'])
        assert capture_request(workflow, workflow._original_simple_classify, row['input']) == expected
        assert replay(workflow, row['input'], row['response'], row['original_answer']) == row['fallback_taken']
    faults = run_faults(workflow, rows[0]['response'])
    assert all(faults.values())
    # Prove logging contains path/version but neither raw state nor exception messages.
    import logging
    buffer = io.StringIO()
    handler = logging.StreamHandler(buffer)
    old_level = decisions.LOGGER.level
    decisions.LOGGER.addHandler(handler)
    decisions.LOGGER.setLevel(logging.INFO)
    try:
        accepted = next(row for row in rows if not row['fallback_taken'])
        replay(workflow, 'private input marker', accepted['response'], 'original')
        with patch.object(decisions, '_post', side_effect=OSError('private error marker')):
            decisions.classify_with_fallback('private input marker', lambda x:'original', workflow.MODEL)
        logs = buffer.getvalue()
        assert 'path=jev model=' + decisions.MODEL in logs
        assert 'path=original model=' + workflow.MODEL in logs
        assert 'private input marker' not in logs and 'private error marker' not in logs
    finally:
        decisions.LOGGER.removeHandler(handler)
        decisions.LOGGER.setLevel(old_level)
    print('PASS: saved live replay, source/request identity, fault propagation and sanitized path logs')


if __name__ == '__main__':
    if '--replay-only' in sys.argv:
        replay_saved()
    else:
        main()
