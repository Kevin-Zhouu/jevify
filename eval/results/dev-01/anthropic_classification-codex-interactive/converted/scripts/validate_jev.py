"""Offline control-flow assertions and optional real paired evaluation.
Run from repository root: python3 scripts/validate_jev.py [--live]
Only this process adapts the original Anthropic transport to OpenRouter.
"""
import contextlib
import csv
import io
import json
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
import jev_decisions as j
NS = types.SimpleNamespace


def load_workflow(create):
    sdk = types.ModuleType('anthropic')
    sdk.Anthropic = lambda **kw: NS(messages=NS(create=create))
    with patch.dict(sys.modules, {'anthropic': sdk}):
        return runpy.run_path(str(ROOT / 'workflow.py'))


def faults():
    results = {}
    failures = {'timeout': TimeoutError(), 'rate_limit': urllib.error.HTTPError(j.ENDPOINT, 429, 'rate limit', {}, None), 'error': RuntimeError()}
    for name, error in failures.items():
        calls = []
        w = load_workflow(lambda **kw: calls.append(kw) or NS(content=[NS(text='  sentinel  ')]))
        with patch.dict(os.environ, {j.KEY_ENV: 'offline-test'}), patch.object(urllib.request, 'urlopen', side_effect=error):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                assert w['simple_classify']('invoice') == 'sentinel'
            assert out.getvalue() == '' and len(calls) == 1
            assert calls[0]['stop_sequences'] == ['</category>']
            assert calls[0]['messages'][1]['content'] == '<category>'
            assert calls[0]['model'] == 'claude-haiku-4-5'
            assert calls[0]['max_tokens'] == 4096 and calls[0]['temperature'] == 0.0
        results[name] = True
    calls = []
    sentinel = object()
    def original(x):
        calls.append(x)
        return sentinel
    # Pure gate below boundary, followed by rejected-answer integration.
    assert not j.gate(next(iter(j.CRITERIA)), j.THRESHOLD - 0.001)
    with patch.dict(os.environ, {j.KEY_ENV: 'offline-test'}), patch.object(j, 'accepted_label', return_value=None), patch.object(j, 'evaluate', return_value=None):
        assert j.classify('ticket', original, 'original') is sentinel
    assert len(calls) == 1
    results['below_threshold'] = True
    for value in [float('nan'), float('inf'), -1, 2, True, '0.99', None]:
        assert not j.gate(next(iter(j.CRITERIA)), value)
    assert not j.gate('unknown', 1)
    results['nonfinite_and_unknown_option'] = True
    for name, response in [('malformed', {}), ('invalid_json', b'{')]:
        calls.clear()
        if isinstance(response, bytes):
            transport = patch.object(urllib.request, 'urlopen', return_value=io.BytesIO(response))
        else:
            transport = patch.object(urllib.request, 'urlopen', return_value=io.BytesIO(json.dumps(response).encode()))
        with patch.dict(os.environ, {j.KEY_ENV: 'offline-test'}), transport:
            assert j.classify('ticket', original, 'original') is sentinel
        assert len(calls) == 1
        results[name] = True
    for name, ticket in [('missing_key', 'ticket'), ('oversized', 'x'*(j.MAX_INPUT_BYTES+1)), ('unsupported', None)]:
        calls.clear()
        with patch.dict(os.environ, {j.KEY_ENV: ''}), patch.object(j, 'evaluate', side_effect=AssertionError('unexpected inference')):
            assert j.classify(ticket, original, 'original') is sentinel
        assert calls == [ticket]
        results[name] = True
    error = ValueError('original exception')
    calls.clear()
    def throwing(x):
        calls.append(x)
        raise error
    with patch.dict(os.environ, {j.KEY_ENV: ''}):
        try: j.classify('ticket', throwing, 'original')
        except ValueError as caught: assert caught is error
        else: raise AssertionError('exception swallowed')
    assert len(calls) == 1
    results['original_exception'] = True
    return results


def samples():
    # Round-robin by repository category for balanced coverage; labels are only
    # used for sampling, never as the baseline answer.
    seen = set()
    for split, count, kind in [('train', 1, 'calibration'), ('test', 99, 'confirmation')]:
        groups = {}
        with (ROOT / 'data' / (split+'.tsv')).open() as f:
            for line, row in enumerate(csv.DictReader(f, delimiter='\t'), 2):
                groups.setdefault(row['label'], []).append((line, row['text']))
        for index in range(min(count, max(map(len, groups.values())))):
            for group in groups.values():
                if index < len(group):
                    line, ticket = group[index]
                    if ticket not in seen:
                        seen.add(ticket)
                        yield ticket, f'data/{split}.tsv:{line}', kind


def baseline_create(record, **kw):
    assert kw['model'] == 'claude-haiku-4-5'
    payload = dict(kw, model='anthropic/claude-haiku-4.5')
    req = urllib.request.Request('https://openrouter.ai/api/v1/messages',
        data=json.dumps(payload).encode(), method='POST',
        headers={'Authorization': 'Bearer '+os.environ[j.KEY_ENV], 'Content-Type': 'application/json', 'anthropic-version': '2023-06-01'})
    with urllib.request.urlopen(req, timeout=45) as r:
        data = json.load(r)
    record.update(data)
    return NS(content=[NS(**c) for c in data['content']])


def summary(rows):
    if not rows: return {'n': 0}
    curves = []
    for threshold in [0, 0.8, 0.9, j.THRESHOLD, 0.99]:
        accepted = [r for r in rows if r['confidence'] >= threshold]
        curves.append({'threshold': threshold, 'accepted': len(accepted), 'agreement': sum(r['jev_answer'] == r['original_answer'] for r in accepted)/len(accepted) if accepted else None, 'fallback_fraction': 1-len(accepted)/len(rows)})
    def pct(key):
        a = sorted(r[key] for r in rows)
        return {'p50': statistics.median(a), 'p95': a[max(0, __import__('math').ceil(.95*len(a))-1)]}
    costs = [r['cost_usd'] + (r['original_cost_usd'] if r['fallback_taken'] else 0) for r in rows if r['cost_usd'] is not None and r['original_cost_usd'] is not None]
    return {'n':len(rows), 'raw_agreement':sum(r['jev_answer']==r['original_answer'] for r in rows)/len(rows), 'confidence_curve': curves, 'fallback_rate':sum(r['fallback_taken'] for r in rows)/len(rows), 'jev_latency_ms':pct('latency_ms'), 'original_latency_ms':pct('original_latency_ms'), 'mean_cascade_latency_ms':statistics.mean(r['latency_ms']+(r['original_latency_ms'] if r['fallback_taken'] else 0) for r in rows), 'mean_cascade_cost_usd':statistics.mean(costs) if len(costs)==len(rows) else None}


def main():
    fault_results = faults()
    print('PASS: injected fallback control-flow assertions')
    (ROOT/'JEV_VALIDATION.json').write_text(json.dumps({'faults':fault_results}, indent=2)+'\n')
    if '--live' not in sys.argv: return
    site = {'site_id':'workflow.py:83','threshold':j.THRESHOLD,'rows':[], 'errors':[], 'faults':fault_results}
    evidence = {'baseline_adapter':'OpenRouter /api/v1/messages; same original model, request and parser; isolated adapter explicitly authorized', 'cost_source':'provider usage.cost; null when absent', 'threshold_policy':'0.95 chosen before measurement; no tuning on confirmation', 'sites':[site]}
    prior = ROOT / 'JEV_PARITY.json'
    if prior.exists():
        previous = json.loads(prior.read_text())
        evidence['prior_attempts'] = previous
        site['rows'] = previous['sites'][0]['rows'].copy()
        site['errors'] = previous['sites'][0]['errors'].copy()
    for ticket, provenance, split in samples():
        if any(r['provenance'] == provenance for r in site['rows']) or any(r['provenance'] == provenance for r in site['errors']):
            continue
        if sum(r['split'] == 'confirmation' for r in site['rows']) >= 40:
            break
        stage = 'original'
        try:
            record = {}
            w = load_workflow(lambda **kw: baseline_create(record, **kw))
            t = time.perf_counter()
            original = w['_original_simple_classify'](ticket)
            original_ms = (time.perf_counter()-t)*1000
            stage = 'jev'
            t = time.perf_counter()
            response = j.evaluate(ticket)
            jev_ms = (time.perf_counter()-t)*1000
            answer = response['answers']['category']
            label = j.accepted_label(response)
            # Replay actual captured live response through public integration.
            fallback_calls = []
            def cached_original(x):
                assert x == ticket
                fallback_calls.append(x)
                return original
            w['simple_classify'].__globals__['_original_simple_classify'] = cached_original
            with patch.object(j, 'evaluate', return_value=response):
                actual = w['simple_classify'](ticket)
            assert actual == (label if label is not None else original)
            assert len(fallback_calls) == (1 if label is None else 0)
            row = {'input':ticket,'provenance':provenance,'split':split,'live':True,'model':response['model'],'request_id':response.get('id'),'jev_answer':answer['choice'],'original_answer':original,'confidence':answer['confidence'],'probabilities':answer['probabilities'],'fallback_taken':label is None,'latency_ms':jev_ms,'cost_usd':response.get('usage',{}).get('cost'),'usage':response.get('usage'),'original_model':'anthropic/claude-haiku-4.5','original_request_id':record.get('id'),'original_latency_ms':original_ms,'original_cost_usd':record.get('usage',{}).get('cost'),'original_usage':record.get('usage')}
            site['rows'].append(row)
            print('Measured',len(site['rows']),split, flush=True)
        except Exception as e:
            # Do not serialize exception strings or raw provider error bodies.
            site['errors'].append({'stage':stage,'provenance':provenance,'error_type':type(e).__name__,'http_status':getattr(e,'code',None), 'original_request_id':record.get('id'), 'original_usage':record.get('usage'), 'original_answer':original if stage == 'jev' else None, 'original_latency_ms':original_ms if stage == 'jev' else None})
            print('Live blocked:',stage,type(e).__name__,getattr(e,'code',None),flush=True)
            if getattr(e, 'code', None) in (401, 403, 404, 400, 422):
                break
        finally:
            site['summary'] = summary(site['rows'])
            site['split_summary'] = {s:summary([r for r in site['rows'] if r['split']==s]) for s in ['calibration','confirmation']}
            (ROOT/'JEV_PARITY.json').write_text(json.dumps(evidence,indent=2,allow_nan=False)+'\n')
    print(json.dumps(site['summary']))

if __name__ == '__main__': main()
