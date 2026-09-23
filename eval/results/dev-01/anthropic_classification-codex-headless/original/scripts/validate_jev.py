"""Offline fault tests; --live records actual paired calls through OpenRouter.
Only the evaluation process substitutes the Anthropic transport. Production does not.
"""
import argparse
import concurrent.futures
import contextlib
import csv
from datetime import datetime, timezone
import io
import json
import math
import os
from pathlib import Path
import runpy
import statistics
import sys
import time
import types
import urllib.error
import urllib.request
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import jev_decisions as jd


def load_workflow(create):
    sdk = types.ModuleType('anthropic')
    sdk.Anthropic = lambda **kwargs: types.SimpleNamespace(
        messages=types.SimpleNamespace(create=create))
    with patch.dict(sys.modules, {'anthropic': sdk}):
        return runpy.run_path(str(ROOT / 'workflow.py'))


def faults():
    calls = []
    def original(**kwargs):
        calls.append(kwargs)
        return types.SimpleNamespace(content=[types.SimpleNamespace(text='  Billing Inquiries  ')])
    workflow = load_workflow(original)
    ticket = 'Please explain my invoice.'
    results = {}
    cases = {
        'timeout': TimeoutError(),
        'rate_limit': urllib.error.HTTPError(jd.ENDPOINT, 429, 'rate limit', {}, None),
        'error': RuntimeError(),
        'malformed': json.JSONDecodeError('invalid', '', 0),
    }
    for name, error in cases.items():
        calls.clear()
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'offline-fault-test'}), \
             patch.object(urllib.request, 'urlopen', side_effect=error), \
             contextlib.redirect_stdout(io.StringIO()) as stdout:
            assert workflow['simple_classify'](ticket) == 'Billing Inquiries'
        assert len(calls) == 1 and not stdout.getvalue()
        assert calls[0]['model'] == 'claude-haiku-4-5'
        assert calls[0]['stop_sequences'] == ['</category>']
        assert calls[0]['messages'][1]['content'] == '<category>'
        results[name] = True
    calls.clear()
    with patch.dict(os.environ, {'OPENROUTER_API_KEY': ''}), \
         patch.object(urllib.request, 'urlopen') as transport:
        assert workflow['simple_classify'](ticket) == 'Billing Inquiries'
        transport.assert_not_called()
    assert len(calls) == 1
    results['missing_key'] = True
    # Deliberately invalid/low gate inputs, never mocked successful Jev inference.
    def gate_input(confidence, label='Billing Inquiries'):
        return {'model': jd.MODEL, 'answers': {'category': {
            'type': 'choice', 'choice': label, 'confidence': confidence,
            'probabilities': {k: 1.0 if k == 'Billing Inquiries' else 0.0 for k in jd.CRITERIA}}}}
    for name, response in [('below_threshold', gate_input(jd.THRESHOLD - .001)),
                           ('nonfinite', gate_input(float('nan'))),
                           ('out_of_range', gate_input(2)),
                           ('unknown_option', gate_input(.99, 'unknown')),
                           ('missing_schema', {})]:
        assert jd.accepted_label(response) is None
        calls.clear()
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'offline-gate-test'}), \
             patch.object(jd, 'evaluate', return_value=response):
            assert workflow['simple_classify'](ticket) == 'Billing Inquiries'
        assert len(calls) == 1
        results[name] = True
    for name, ticket_value, categories in [
            ('oversize', 'x' * (jd.MAX_TICKET_BYTES + 1), workflow['categories']),
            ('unsupported', None, workflow['categories']),
            ('changed_categories', ticket, 'different taxonomy')]:
        sent = []
        sentinel = object()
        with patch.object(jd, 'evaluate') as transport:
            value = jd.classify(ticket_value, categories,
                                lambda x: sent.append(x) or sentinel, workflow['MODEL'])
            transport.assert_not_called()
        assert value is sentinel and sent == [ticket_value]
        results[name] = True
    failure = RuntimeError('original failure sentinel')
    sent = []
    def raises(x):
        sent.append(x)
        raise failure
    with patch.dict(os.environ, {'OPENROUTER_API_KEY': ''}):
        try:
            jd.classify(ticket, workflow['categories'], raises, workflow['MODEL'])
        except RuntimeError as error:
            assert error is failure
        else:
            raise AssertionError('original exception swallowed')
    assert sent == [ticket]
    results['original_exception_once'] = True
    return results


def samples():
    cases, seen = [], set()
    for filename, count, split in [('train.tsv', 10, 'calibration'), ('test.tsv', 30, 'confirmation')]:
        rows = list(csv.DictReader((ROOT / 'data' / filename).open(), delimiter='\t'))
        # Round robin categories: cover the complete taxonomy, not just the first labels.
        groups = {}
        for row in rows:
            groups.setdefault(row['label'], []).append(row['text'])
        added = 0
        for i in range(max(map(len, groups.values()))):
            for group in groups.values():
                if i < len(group) and group[i] not in seen and added < count:
                    value = group[i]
                    seen.add(value)
                    cases.append((value, 'data/' + filename, split))
                    added += 1
    for value in ['', 'My claim was denied and I also need to update my mailing address.',
                  'Can you help me repair my bicycle?',
                  'I need an explanation of a charge, and a refund if it is incorrect.']:
        if value not in seen:
            cases.append((value, 'synthetic boundary/ambiguous/out-of-domain', 'confirmation'))
    assert len({c[0] for c in cases}) >= 30
    return cases


def pair(case):
    ticket, provenance, split = case
    baseline_metadata = {}
    def create(**kwargs):
        assert kwargs['model'] == 'claude-haiku-4-5'
        payload = dict(kwargs)
        payload['model'] = 'anthropic/claude-haiku-4.5'
        payload['stop'] = payload.pop('stop_sequences')
        payload['provider'] = {'only': ['Anthropic'], 'require_parameters': True}
        request = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',
            data=json.dumps(payload).encode(), headers={
                'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'],
                'Content-Type': 'application/json'})
        with urllib.request.urlopen(request, timeout=45) as response:
            data = json.load(response)
        if 'error' in data:
            raise RuntimeError('baseline_response_error')
        baseline_metadata.update({k: data.get(k) for k in ('id', 'model', 'usage', 'provider')})
        return types.SimpleNamespace(content=[types.SimpleNamespace(text=data['choices'][0]['message']['content'])])
    # Run loading serially in main; runpy/sys.modules mutation is not thread-safe.
    workflow = BASE_WORKFLOW.copy()
    fn = BASE_WORKFLOW['_original_simple_classify']
    namespace = fn.__globals__.copy()
    namespace['client'] = types.SimpleNamespace(messages=types.SimpleNamespace(create=create))
    original = types.FunctionType(fn.__code__, namespace)
    started = time.monotonic()
    answer = original(ticket)
    original_ms = (time.monotonic() - started) * 1000
    started = time.monotonic()
    response = jd.evaluate(ticket)
    jev_ms = (time.monotonic() - started) * 1000
    raw = response['answers']['category']
    accepted = jd.accepted_label(response)
    # Replay the actual captured network result through the integration. No new
    # invented inference, and no additional billable calls for wrapper assertions.
    count = []
    def fallback(x):
        assert x == ticket
        count.append(x)
        return answer
    # Thread-safe replacement of the evaluator via a per-function globals copy.
    globals_copy = jd.classify.__globals__.copy()
    globals_copy['evaluate'] = lambda x: response
    wrapper = types.FunctionType(jd.classify.__code__, globals_copy)
    result = wrapper(ticket, workflow['categories'], fallback, workflow['MODEL'])
    assert result == (accepted if accepted is not None else answer)
    assert len(count) == (1 if accepted is None else 0)
    return {
        'input': ticket, 'provenance': provenance, 'split': split, 'live': True,
        'model': response.get('model'), 'request_id': response.get('id'),
        'jev_answer': raw['choice'], 'original_answer': answer,
        'confidence': raw['confidence'], 'fallback_taken': accepted is None,
        'latency_ms': jev_ms, 'cost_usd': response.get('usage', {}).get('cost'),
        'usage': response.get('usage'), 'original_model': baseline_metadata['model'],
        'original_request_id': baseline_metadata['id'],
        'original_latency_ms': original_ms,
        'original_cost_usd': (baseline_metadata.get('usage') or {}).get('cost'),
        'original_usage': baseline_metadata.get('usage'),
        'integration_contract_passed': True,
    }


def summary(rows):
    def metrics(group):
        curves = []
        for t in [0, .5, .7, .8, .9, .95, .99]:
            selected = [r for r in group if r['confidence'] >= t]
            curves.append({'threshold': t, 'accepted': len(selected),
                'selective_agreement': sum(r['jev_answer'] == r['original_answer'] for r in selected) / len(selected) if selected else None,
                'fallback_fraction': 1 - len(selected) / len(group)})
        return {'n': len(group), 'raw_agreement': sum(r['jev_answer'] == r['original_answer'] for r in group) / len(group), 'confidence_curve': curves}
    result = metrics(rows)
    for split in ['calibration', 'confirmation']:
        group = [r for r in rows if r['split'] == split]
        if group:
            result[split] = metrics(group)
    def quantiles(values):
        values = sorted(values)
        return {'p50': statistics.median(values), 'p95': values[math.ceil(len(values)*.95)-1]}
    result['jev_latency_ms'] = quantiles([r['latency_ms'] for r in rows])
    result['original_latency_ms'] = quantiles([r['original_latency_ms'] for r in rows])
    result['estimated_cascade_latency_ms'] = quantiles([r['latency_ms'] + (r['original_latency_ms'] if r['fallback_taken'] else 0) for r in rows])
    result['fallback_rate'] = sum(r['fallback_taken'] for r in rows)/len(rows)
    if all(r['cost_usd'] is not None and r['original_cost_usd'] is not None for r in rows):
        result['mean_original_cost_usd'] = statistics.mean(r['original_cost_usd'] for r in rows)
        result['mean_jev_cost_usd'] = statistics.mean(r['cost_usd'] for r in rows)
        result['estimated_mean_cascade_cost_usd'] = statistics.mean(r['cost_usd'] + (r['original_cost_usd'] if r['fallback_taken'] else 0) for r in rows)
    else:
        result['cost_status'] = 'unknown where provider did not report cost; no zero substitution'
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true')
    args = parser.parse_args()
    fault_results = faults()
    print('PASS:', len(fault_results), 'injected control-flow checks (not live inference)')
    if args.live:
        evidence = {'site_id': 'workflow.py:83', 'threshold': jd.THRESHOLD,
                    'started_at': datetime.now(timezone.utc).isoformat(),
                    'rows': [], 'faults': fault_results, 'errors': [],
                    'cost_source': 'OpenRouter response usage.cost, provider-reported USD',
                    'threshold_policy': '0.90 fixed before measurement; no data-driven tuning',
                    'adapter': 'Original function and parser, identical messages/prefill/parameters; stop_sequences maps to stop; same Claude Haiku 4.5 via authorized OpenRouter route, Anthropic provider only.'}
        BASE_WORKFLOW = load_workflow(lambda **kwargs: None)
        cases = samples()
        # Probe one real pair first; do not incur a full run on a blocked route.
        try:
            evidence['rows'].append(pair(cases[0]))
        except Exception as e:
            evidence['errors'].append({'case_index': 0, 'type': type(e).__name__, 'http_status': getattr(e, 'code', None)})
        if evidence['rows']:
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
                pending = {pool.submit(pair, c): i for i, c in enumerate(cases[1:], 1)}
                for future in concurrent.futures.as_completed(pending):
                    try:
                        evidence['rows'].append(future.result())
                    except Exception as e:
                        evidence['errors'].append({'case_index': pending[future], 'type': type(e).__name__, 'http_status': getattr(e, 'code', None)})
            evidence['summary'] = summary(evidence['rows'])
        evidence['status'] = 'measured' if len(evidence['rows']) >= 30 else 'blocked_or_incomplete'
        evidence['planned_inputs'] = len(cases)
        (ROOT / 'JEV_PARITY.json').write_text(json.dumps({'sites': [evidence]}, indent=2, allow_nan=False)+'\n')
        print(json.dumps({'status': evidence['status'], 'pairs': len(evidence['rows']), 'errors': evidence['errors'], 'summary': evidence.get('summary')}, indent=2))
