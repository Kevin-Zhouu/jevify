#!/usr/bin/env python3
"""Read-only syntax screen for copied policy, proxy requests and invented inference.

This is NOT a semantic proof. Review actual source wiring and execute assertions.
Pass only executable validation adapters/scripts (not saved response JSON/docs).
"""
import argparse
import ast
import json
import os
from pathlib import Path
import re
import subprocess

PIN = re.compile(r'(?:typesafe/)?jev-(?:latest|\d+\.\d+(?:\.\d+|-\d{8})?)')


def screen(path, baseline_text=''):
    text = path.read_text()
    findings = []
    def add(line, reason):
        item = {'file': str(path), 'line': line, 'reason': reason}
        if item not in findings:
            findings.append(item)
    for number, line in enumerate(text.splitlines(), 1):
        if PIN.search(line):
            add(number, 'Copied Jev model literal: import the decisions module pin instead')
        if '/v1/systemone' in line:
            add(number, 'Duplicate Jev transport URL: execute the production evaluator; import endpoint for faults')
    try:
        tree = ast.parse(text) if path.suffix == '.py' else None
    except SyntaxError:
        add(1, 'Python validation source does not parse')
        tree = None
    if tree:
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                keys = {k.value: v for k, v in zip(node.keys, node.values)
                        if isinstance(k, ast.Constant) and isinstance(k.value, str)}
                if 'answers' in keys and any(k in keys for k in ('model', 'usage')):
                    add(node.lineno, 'Constructed Jev response: replay a genuine capture or mutate it as an explicit fault')
                for key in ('messages', 'response_format', 'system'):
                    value = keys.get(key)
                    if isinstance(value, (ast.List, ast.Dict)) or isinstance(value, ast.Constant) and isinstance(value.value, str):
                        add(node.lineno, 'Manually constructed baseline messages/schema: capture original SDK request or execute original callable')
    else:
        for number, line in enumerate(text.splitlines(), 1):
            if re.search(r'\b(?:messages|response_format|system)\s*:\s*(?:\[|\{|[\'"`])', line):
                add(number, 'Possible manual baseline request: obtain messages/schema from actual original source/SDK')
    # Catch copied original prompt text, without looking for particular tasks.
    # Python originals expose literal strings; JS/TS originals expose quoted fragments.
    try:
        candidates = [n.value for n in ast.walk(ast.parse(baseline_text))
                      if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    except SyntaxError:
        candidates = [m.group(2) for m in re.finditer(r'([\'"`])([^\n]*?)\1', baseline_text)]
    normalized = re.sub(r'\s+', ' ', text)
    for candidate in candidates:
        fragment = re.sub(r'\s+', ' ', candidate).strip()
        if len(fragment) >= 32 and re.search(r'\b(?:classify|generate|respond|you are|you will|return only)\b', fragment, re.I) and fragment in normalized:
            add(1, 'Copied original prompt literal: execute/capture the original builder rather than reconstructing it')
            break
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--baseline', help='Pre-conversion git REV:path (repeat command for additional originals)')
    parser.add_argument('files', type=Path, nargs='+')
    args = parser.parse_args()
    baseline = ''
    if args.baseline:
        baseline = subprocess.check_output(['git', '-C', str(args.repo), 'show', args.baseline], text=True,
                                          env={**os.environ, 'GIT_OPTIONAL_LOCKS': '0'})
    findings = [item for path in args.files for item in screen(path, baseline)]
    print(json.dumps({'syntax_screen_passed': not findings, 'findings': findings,
                      'limitation': 'No findings does not prove source identity, real inference, or correct control flow'}, indent=2))
    return int(bool(findings))


if __name__ == '__main__':
    raise SystemExit(main())
