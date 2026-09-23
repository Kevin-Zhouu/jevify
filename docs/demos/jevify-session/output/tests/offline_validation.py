"""Offline contract/fault proof. No simulated successful Jev inference."""
import ast
import contextlib
import io
import logging
import os
from pathlib import Path
import subprocess
import sys
import types
import unittest.mock as mock
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import jev_decisions as decisions

BASE_SHA = '7c497d21099fc916692f1dd45b5a6107b03754d5'
base = subprocess.check_output(['git', 'show', BASE_SHA + ':workflow.py'], cwd=ROOT, text=True)
current = (ROOT / 'workflow.py').read_text()
a = next(n for n in ast.parse(base).body if isinstance(n, ast.FunctionDef))
b = next(n for n in ast.parse(current).body if isinstance(n, ast.FunctionDef))
b.name = a.name
assert ast.dump(a) == ast.dump(b), 'Original function changed'
calls = []
def create(**kwargs):
    calls.append(kwargs)
    return types.SimpleNamespace(content=[types.SimpleNamespace(text='  Billing Inquiries  ')])
sdk = types.ModuleType('anthropic')
sdk.Anthropic = lambda **kwargs: types.SimpleNamespace(messages=types.SimpleNamespace(create=create))
with mock.patch.dict(sys.modules, {'anthropic': sdk}):
    import workflow
    baseline = {}
    exec(compile(base, 'baseline-workflow.py', 'exec'), baseline)

with mock.patch.dict(os.environ, {'JEV_PROVIDER': 'none'}, clear=True):
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        assert baseline['simple_classify']('Please explain my invoice.') == workflow.simple_classify('Please explain my invoice.')
    assert stdout.getvalue() == ''
    assert calls[0] == calls[1], 'Original request differs'
    assert len(calls) == 2

sentinel = object()
def check_public(reason, transport=None, missing=False, evaluator=None, gate=None):
    fallback = mock.Mock(return_value=sentinel)
    logger = io.StringIO()
    handler = logging.StreamHandler(logger)
    decisions.LOGGER.addHandler(handler)
    decisions.LOGGER.setLevel(logging.INFO)
    try:
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.dict(os.environ, {'JEV_PROVIDER': 'typesafe', 'TYPESAFE_API_KEY': '' if missing else 'offline-placeholder'}, clear=True))
            stack.enter_context(mock.patch.object(workflow, '_original_simple_classify', fallback))
            if transport is not None:
                stack.enter_context(mock.patch.object(decisions.urllib.request, 'urlopen', side_effect=transport))
            if evaluator is not None:
                stack.enter_context(mock.patch.object(decisions, 'evaluate', evaluator))
            if gate is not None:
                stack.enter_context(mock.patch.object(decisions, 'confidence_gate', gate))
            assert workflow.simple_classify('fixture') is sentinel
            fallback.assert_called_once_with('fixture')
            assert 'reason=' + reason in logger.getvalue()
            assert 'model=' + workflow.MODEL in logger.getvalue()
            assert 'offline-placeholder' not in logger.getvalue()
    finally:
        decisions.LOGGER.removeHandler(handler)

check_public('missing_key', missing=True)
check_public('invalid_or_error', transport=RuntimeError('injected'))
check_public('timeout', transport=TimeoutError('injected'))
check_public('rate_limit', transport=urllib.error.HTTPError(decisions.ENDPOINT, 429, 'injected', {}, None))
# Gate-boundary fault only: no invented HTTP body, label, distribution or usage.
reject = mock.Mock(return_value=False)
check_public('low_confidence', evaluator=mock.Mock(return_value=(object(), object())), gate=reject)
reject.assert_called_once()
for value in [True, None, float('nan'), float('inf'), -1, 2, decisions.THRESHOLD - 0.01]:
    assert not decisions.confidence_gate(value)
assert decisions.confidence_gate(decisions.THRESHOLD)
for malformed in [None, [], {}, {'model': decisions.MODEL, 'answers': []}]:
    try:
        decisions.parse_answer(malformed)
    except ValueError:
        pass
    else:
        raise AssertionError('Malformed response accepted')
check_public('invalid_or_error', evaluator=mock.Mock(side_effect=ValueError('malformed')))
with mock.patch.dict(os.environ, {'JEV_PROVIDER': 'typesafe', 'TYPESAFE_API_KEY': 'offline-placeholder'}, clear=True), mock.patch.object(decisions, 'evaluate') as evaluate, mock.patch.object(workflow, '_original_simple_classify', return_value=sentinel) as fallback:
    oversized = 'x' * (decisions.MAX_STATE_BYTES + 1)
    assert workflow.simple_classify(oversized) is sentinel
    fallback.assert_called_once_with(oversized)
    evaluate.assert_not_called()
err = RuntimeError('original failure')
fallback = mock.Mock(side_effect=err)
with mock.patch.dict(os.environ, {'JEV_PROVIDER': 'none'}, clear=True), mock.patch.object(workflow, '_original_simple_classify', fallback):
    try:
        workflow.simple_classify('fixture')
    except RuntimeError as caught:
        assert caught is err
    else:
        raise AssertionError('Original error swallowed')
    fallback.assert_called_once()
print('PASS: original AST/request/parser, stdout, exactly-once fallback/error identity, missing key, low-confidence gate boundary, generic error, timeout, HTTP 429, malformed response and confidence predicates')
print('SKIPPED: live validation and accepted Jev response replay; no credentials or genuine captured response')
