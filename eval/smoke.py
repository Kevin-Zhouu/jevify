#!/usr/bin/env python3
"""Execute upstream Python workflow behavior with deterministic ORIGINAL-SDK doubles.

No double in this file impersonates Jev. Network failures exercise fallback.
These are evaluator-supplied smoke tests because the vendored examples have none.
"""
import contextlib
import io
import os
import pathlib
import runpy
import socket
import sys
import types
import unittest.mock
import urllib.request


def fail_network(*args, **kwargs):
    raise TimeoutError('Evaluator fault injection: network timeout')


def main():
    root = pathlib.Path(sys.argv[1]).resolve()
    fixture = sys.argv[2]
    sys.path.insert(0, str(root))
    os.environ.setdefault('ANTHROPIC_API_KEY', 'offline-original-sdk-test')
    os.environ.setdefault('OPENAI_API_KEY', 'offline-original-sdk-test')
    out = io.StringIO()
    ns = types.SimpleNamespace
    calls = []

    def anthropic_create(**kwargs):
        calls.append(kwargs)
        return ns(content=[ns(text='  Billing Inquiries  ')], model=kwargs['model'])

    anthropic = types.ModuleType('anthropic')
    anthropic.Anthropic = lambda **kwargs: ns(messages=ns(create=anthropic_create))
    anthropic.Anthropic.__module__ = 'anthropic'
    sys.modules['anthropic'] = anthropic

    def openai_create(**kwargs):
        calls.append(kwargs)
        if kwargs.get('stream'):
            return iter([ns(choices=[]), ns(choices=[ns(delta=ns(content='streamed-smoke'))])])
        return ns(choices=[ns(message=ns(content='original-smoke'))])

    openai = types.ModuleType('openai')
    openai.OpenAI = lambda **kwargs: ns(chat=ns(completions=ns(create=openai_create, with_raw_response=ns(create=lambda **kw: ns(parse=lambda: openai_create(**kw), request_id='offline-request')))))
    sys.modules['openai'] = openai
    with unittest.mock.patch.object(urllib.request, 'urlopen', fail_network), unittest.mock.patch.object(socket, 'create_connection', fail_network), contextlib.redirect_stdout(out):
        module = runpy.run_path(str(root / 'workflow.py'))
        if fixture == 'anthropic_classification':
            value = module['simple_classify']('Please explain my invoice.')
            assert value == 'Billing Inquiries', value
            assert len(calls) == 1, 'Original fallback must execute exactly once'
            assert calls[0]['model'] == 'claude-haiku-4-5'
        elif fixture == 'anthropic_routing':
            answers = iter(['<reasoning>observed reasoning</reasoning><selection>billing</selection>', 'specialist prose'])
            fn = module['route']
            fn.__globals__['llm_call'] = lambda *args, **kwargs: next(answers)
            assert fn('Invoice issue', module['support_routes']) == 'specialist prose'
            assert 'observed reasoning' in out.getvalue()
        elif fixture == 'openai_demo':
            assert len(calls) == 3
            assert 'streamed-smoke' in out.getvalue()
            assert out.getvalue().count('original-smoke') == 2
        else:
            raise ValueError('Unsupported Python smoke fixture')
    print('PASS: observable Python behavior and original-path fallback smoke')


if __name__ == '__main__':
    main()
