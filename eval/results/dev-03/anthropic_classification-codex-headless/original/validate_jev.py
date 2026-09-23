"""Reproducible live pairs and injected control-flow checks. No credential output."""
import ast
import concurrent.futures
import contextlib
import copy
import csv
import io
import json
import logging
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
import types
import urllib.error
import urllib.request
from unittest.mock import patch

import jev_decisions as decisions

ROOT = Path(__file__).resolve().parent
SOURCE_SHA = "1c953f75ebe1580de909072ce9a73b8ab8f11d05"
SITE = "workflow.py:83"


def load_workflow(source):
    # Only the SDK boundary is adapted. Execute the real source and parser.
    sdk = types.ModuleType("anthropic")
    sdk.Anthropic = lambda **kw: types.SimpleNamespace(messages=types.SimpleNamespace(create=None))
    module = types.ModuleType("isolated_workflow")
    with patch.dict(sys.modules, {"anthropic": sdk}):
        exec(compile(source, "workflow.py", "exec"), module.__dict__)
    return module


def identity(original, current):
    def function(src, name):
        node = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == name)
        node.name = "same_name"
        return ast.dump(node, include_attributes=False)
    assert function(original, "simple_classify") == function(current, "_original_simple_classify")


def baseline_transport(kwargs):
    # Config explicitly authorizes same-model OpenRouter evaluation transport.
    # All request options are mapped without changing messages or prefill.
    assert set(kwargs) == {"messages", "stop_sequences", "max_tokens", "temperature", "model"}
    payload = {k: v for k, v in kwargs.items() if k not in ("model", "stop_sequences")}
    payload.update(model="anthropic/" + kwargs["model"], stop=kwargs["stop_sequences"])
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions", json.dumps(payload).encode(),
        {"Authorization": "Bearer " + os.environ[decisions.KEY_ENV], "Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=45) as response:
        body = json.load(response)
    text = body["choices"][0]["message"]["content"]
    assert isinstance(text, str)
    return types.SimpleNamespace(content=[types.SimpleNamespace(text=text)]), body


def samples():
    result, counts = [], {}
    with (ROOT / "data/test.tsv").open() as f:
        for line, row in enumerate(csv.DictReader(f, delimiter="\t"), 2):
            label = row["label"]
            if counts.get(label, 0) < 3:
                result.append({"input": row["text"], "provenance": "repo", "source": f"data/test.tsv:{line}"})
                counts[label] = counts.get(label, 0) + 1
    for text in [
        "My claim was rejected, but I also need help uploading the receipt. Who can help?",
        "Please cancel my policy and refund the unexpected charge on my account.",
        "Does my current coverage include windscreen damage, and how do I file a claim?",
        "Hello.",
        "Can you recommend a recipe for vegetable soup?",
        "I forgot my password and need to update my postal address.",
    ]:
        result.append({"input": text, "provenance": "synthetic", "source": "validate_jev.py:samples"})
    assert len({r['input'] for r in result}) >= 30
    return result


def pair(sample, source, current):
    original = load_workflow(source)
    preserved = load_workflow(current)
    requests, captured = [], []
    def create(**kwargs):
        requests.append(copy.deepcopy(kwargs))
        response, body = baseline_transport(kwargs)
        captured.append((response, body))
        return response
    original.client.messages.create = create
    start = time.monotonic()
    answer = original.simple_classify(sample["input"])
    baseline_ms = (time.monotonic() - start) * 1000
    observed = []
    def replay_original(**kwargs):
        observed.append(kwargs)
        return captured[0][0]
    preserved.client.messages.create = replay_original
    assert preserved._original_simple_classify(sample["input"]) == answer
    assert observed == requests
    start = time.monotonic()
    response = decisions.evaluate(sample["input"], original.categories)
    latency = (time.monotonic() - start) * 1000
    choice, confidence = decisions.parse_answer(response, original.categories)
    body = captured[0][1]
    assert response.get("id") and body.get("id")
    return dict(sample, model=decisions.MODEL, live=True, request_id=response['id'],
                original_request_id=body['id'], jev_answer=choice, original_answer=answer,
                confidence=confidence, fallback_taken=not decisions.accepted(confidence),
                latency_ms=latency, cost_usd=response.get('usage', {}).get('cost'),
                original_model=requests[0]['model'], original_response_model=body.get('model'),
                original_latency_ms=baseline_ms, original_cost_usd=body.get('usage', {}).get('cost'),
                cost_source='provider-reported usage.cost',
                jev_response=response, original_usage=body.get('usage'),
                original_finish_reason=body['choices'][0].get('finish_reason'),
                source_and_request_identity=True)


def check_wrapper(workflow, response=None, failure=None, force_reject=False, missing=False, original_error=False):
    calls, transport_calls = [], []
    sentinel = " Original sentinel output \n"
    error = RuntimeError("original sentinel exception")
    def original(ticket):
        calls.append(ticket)
        if original_error:
            raise error
        return sentinel
    def transport(*args):
        transport_calls.append(True)
        if failure:
            raise failure
        return copy.deepcopy(response)
    with contextlib.ExitStack() as stack:
        stack.enter_context(patch.object(workflow, '_original_simple_classify', original))
        stack.enter_context(patch.object(decisions, '_post', transport))
        if missing:
            stack.enter_context(patch.dict(os.environ, {decisions.KEY_ENV: ''}))
        if force_reject:
            stack.enter_context(patch.object(decisions, 'accepted', return_value=False))
        stdout = stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
        if original_error:
            try:
                workflow.simple_classify('A ticket')
                raise AssertionError('Exception lost')
            except RuntimeError as observed:
                assert observed is error
        else:
            result = workflow.simple_classify('A ticket')
            assert result == sentinel
        assert calls == ['A ticket'] and stdout.getvalue() == ''
        assert len(transport_calls) == (0 if missing else 1)


def faults(workflow, captured):
    flags = {}
    for name, error in [('error', RuntimeError()), ('timeout', TimeoutError()),
                        ('rate_limit', decisions.TransportError(429))]:
        check_wrapper(workflow, failure=error)
        flags[name] = True
    check_wrapper(workflow, failure=RuntimeError(), original_error=True)
    flags['original_exception_identity'] = True
    check_wrapper(workflow, missing=True)
    flags['missing_key'] = True
    check_wrapper(workflow, response=[])
    flags['malformed'] = True
    flags['below_threshold'] = False
    if captured:
        check_wrapper(workflow, response=captured, force_reject=True)
        flags['below_threshold'] = True
        for value in [float('nan'), float('inf'), True, -0.1, 1.1]:
            response = copy.deepcopy(captured)
            response['answers']['category']['confidence'] = value
            check_wrapper(workflow, response=response)
        for key, value in [('choice', 'unknown'), ('type', 'noul')]:
            response = copy.deepcopy(captured)
            response['answers']['category'][key] = value
            check_wrapper(workflow, response=response)
        response = copy.deepcopy(captured); response['model'] = 'unexpected'
        check_wrapper(workflow, response=response)
        flags['invalid_fields'] = True
    return flags


def integrate(workflow, row):
    calls = []
    def original(ticket):
        calls.append(ticket)
        return row['original_answer']
    logs, stdout = io.StringIO(), io.StringIO()
    handler = logging.StreamHandler(logs)
    decisions.LOG.addHandler(handler)
    decisions.LOG.setLevel(logging.INFO)
    try:
        with patch.object(workflow, '_original_simple_classify', original), \
             patch.object(decisions, '_post', return_value=row['jev_response']) as transport, \
             contextlib.redirect_stdout(stdout):
            result = workflow.simple_classify(row['input'])
        assert transport.call_count == 1
        assert len(calls) == int(row['fallback_taken'])
        assert result == (row['original_answer'] if calls else row['jev_answer'])
        assert isinstance(result, str) and stdout.getvalue() == ''
        assert ('path=original' if calls else 'path=jev') in logs.getvalue()
        assert (workflow.MODEL if calls else decisions.MODEL) in logs.getvalue()
        row['integration_verified'] = True
    finally:
        decisions.LOG.removeHandler(handler)
        decisions.LOG.setLevel(logging.WARNING)


def summary(rows):
    if not rows:
        return {'n': 0, 'status': 'incomplete'}
    curve=[]
    for threshold in sorted({0, 0.5, 0.7, 0.8, decisions.THRESHOLD, 0.95, 0.99}):
        accepted=[r for r in rows if r['confidence'] >= threshold]
        curve.append({'threshold': threshold, 'accepted': len(accepted),
                      'agreement': sum(r['jev_answer']==r['original_answer'] for r in accepted)/len(accepted) if accepted else None,
                      'fallback_rate': 1-len(accepted)/len(rows)})
    def pct(values, p):
        return sorted(values)[max(0, __import__('math').ceil(len(values)*p)-1)]
    metrics={}
    for field in ['latency_ms','original_latency_ms']:
        values=[r[field] for r in rows]
        metrics[field]={'p50':statistics.median(values),'p95':pct(values,.95)}
    costs_known=all(type(r[k]) in (float,int) for r in rows for k in ['cost_usd','original_cost_usd'])
    if costs_known:
        metrics['mean_original_cost_usd']=statistics.mean(r['original_cost_usd'] for r in rows)
        metrics['mean_cascade_cost_usd']=statistics.mean(r['cost_usd']+r['fallback_taken']*r['original_cost_usd'] for r in rows)
    metrics['mean_cascade_latency_ms_estimate']=statistics.mean(r['latency_ms']+r['fallback_taken']*r['original_latency_ms'] for r in rows)
    return {'n':len(rows),'raw_agreement':sum(r['jev_answer']==r['original_answer'] for r in rows)/len(rows),
            'curve':curve,'metrics':metrics,'costs_known':costs_known,
            'split':'Fixed provisional threshold before all confirmation samples; no calibration or retuning.'}


def main():
    source=subprocess.check_output(['git','show',SOURCE_SHA+':workflow.py'],cwd=ROOT,text=True)
    current=(ROOT/'workflow.py').read_text()
    identity(source,current)
    workflow=load_workflow(current)
    rows, errors=[],[]
    # Bounded worker count; no retries or alternative models/providers.
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        pending={pool.submit(pair,s,source,current):s for s in samples()}
        for future in concurrent.futures.as_completed(pending):
            try:
                rows.append(future.result())
            except Exception as error:
                errors.append({'source':pending[future]['source'],'type':type(error).__name__,
                               'http_status':getattr(error,'code',getattr(error,'status',None))})
    rows.sort(key=lambda r:r['source'])
    for row in rows:
        integrate(workflow,row)
    flags=faults(workflow,rows[0]['jev_response'] if rows else None)
    result={'source_sha':SOURCE_SHA,'sites':[{'site_id':SITE,'primitive':'Choice','threshold':decisions.THRESHOLD,
            'rows':rows,'faults':flags,'errors':errors,'summary':summary(rows)}]}
    (ROOT/'JEV_PARITY.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'pairs':len(rows),'errors':errors,'faults':flags,'summary':summary(rows)},indent=2))

if __name__=='__main__':
    main()
