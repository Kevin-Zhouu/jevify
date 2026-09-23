"""Portable proof helpers; no model calls, keys, policy, or fabricated inference.

Use after approval. Load pre-conversion source and execute its actual callable
with a user-authorized SDK transport adapter. Copy this helper into the output's
validation tooling if needed for reproducibility. Python 3.10+, standard library.
"""
import ast
import math
from pathlib import Path
import subprocess
import sys
import types
from unittest.mock import patch


def load_baseline(repo, revision, relative_file, imports=None):
    """Execute git source with explicit import shims; return module and source.

    imports maps provider import names to SDK-boundary module shims. The shim
    must forward the original kwargs, not replace prompt construction/parsing.
    This executes repository code and belongs only in approved validation.
    """
    repo = Path(repo).resolve()
    if Path(relative_file).is_absolute() or '..' in Path(relative_file).parts:
        raise ValueError('Expected a repository-relative source file')
    source = subprocess.check_output(
        ['git', '-C', str(repo), 'show', f'{revision}:{relative_file}'], text=True)
    module = types.ModuleType('jevify_original')
    module.__file__ = str(repo / relative_file)
    with patch.dict(sys.modules, imports or {}):
        exec(compile(source, module.__file__, 'exec'), module.__dict__)
    return module, source


def assert_preserved_function(before, after, original_name, preserved_name):
    """Assert the actual original function body/signature is unchanged but renamed."""
    def normalized(source, name):
        candidates = [n for n in ast.parse(source).body
                      if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name]
        if len(candidates) != 1:
            raise AssertionError('Expected exactly one named top-level function')
        node = candidates[0]
        node.name = 'same_original_function'
        return ast.dump(node, include_attributes=False)
    assert normalized(before, original_name) == normalized(after, preserved_name), 'Original function changed'


def assert_fallback_once(invoke):
    """invoke(original) must call the actual public wrapper under a forced fault.

    Install the passed original with the project's injection/patch mechanism.
    Keep that patch active until invocation finishes. Run separately for each
    real exception/status, timeout, missing key and captured-response rejection.
    Never pass a rewritten proxy wrapper here.
    """
    sentinel = object()
    failure = RuntimeError('original exception identity sentinel')
    for raises in (False, True):
        calls = []
        def original(*args, **kwargs):
            calls.append((args, kwargs))
            if raises:
                raise failure
            return sentinel
        if raises:
            try:
                invoke(original)
            except RuntimeError as observed:
                assert observed is failure, 'Original exception replaced'
            else:
                raise AssertionError('Original exception swallowed')
        else:
            assert invoke(original) is sentinel, 'Original return value changed'
        assert len(calls) == 1, f'Expected one original call; observed {len(calls)}'
    return True


def response_cost(response, estimate=None, estimate_source=None):
    """Prefer provider cost; never replace it with remembered token prices."""
    usage = response.get('usage', {}) if isinstance(response, dict) else {}
    value = usage.get('cost') if isinstance(usage, dict) else None
    valid = lambda x: type(x) in (int, float) and math.isfinite(x) and x >= 0
    if valid(value):
        return value, 'provider-reported usage.cost'
    if valid(estimate) and estimate_source:
        return estimate, 'estimated: ' + estimate_source
    return None, 'unknown; validation economics incomplete'


async def assert_async_fallback_once(invoke):
    """Async equivalent; invoke(original) awaits the real async public wrapper."""
    sentinel = object()
    failure = RuntimeError('original exception identity sentinel')
    for raises in (False, True):
        calls = []
        async def original(*args, **kwargs):
            calls.append((args, kwargs))
            if raises:
                raise failure
            return sentinel
        if raises:
            try:
                await invoke(original)
            except RuntimeError as observed:
                assert observed is failure, 'Original exception replaced'
            else:
                raise AssertionError('Original exception swallowed')
        else:
            assert await invoke(original) is sentinel, 'Original return value changed'
        assert len(calls) == 1, f'Expected one original call; observed {len(calls)}'
    return True
