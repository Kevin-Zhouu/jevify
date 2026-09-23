#!/usr/bin/env python3
"""Fetch pinned upstream workflow slices. Run once before freezing the corpus."""
import ast
import hashlib
import json
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
PINS = {
    'anthropic': ('anthropics/anthropic-cookbook', 'a4b0d89061bc65769fea7947c080b3b11d938515'),
    'vercel': ('vercel/ai', '05c2da505b4564074456ab9c544c9266cdd2244a'),
    'openai': ('openai/openai-python', 'cbde8a5691f9aef5d268bd506cd46f9fabec0ced'),
}


def fetch(repo, commit, path):
    return urllib.request.urlopen(f'https://raw.githubusercontent.com/{repo}/{commit}/{path}', timeout=30).read()


def main():
    entries = []
    specs = [
        ('anthropic_classification', 'DEV', 'anthropic', 'capabilities/classification/guide.ipynb', 'workflow.py', [3, 16, 18]),
        ('anthropic_routing', 'DEV', 'anthropic', 'patterns/agents/basic_workflows.ipynb', 'workflow.py', [1, 2, 6]),
        ('vercel_enum', 'DEV', 'vercel', 'examples/ai-core/src/generate-object/openai-enum.ts', 'workflow.ts', None),
        ('vercel_recipe', 'DEV', 'vercel', 'examples/ai-core/src/generate-object/openai.ts', 'workflow.ts', None),
        ('openai_demo', 'DEV', 'openai', 'examples/demo.py', 'workflow.py', None),
        ('langchain_completion', 'DEV', 'vercel', 'examples/next-langchain/app/api/completion/route.ts', 'workflow.ts', None),
        ('heldout_enum', 'HELD-OUT', 'vercel', 'examples/ai-core/src/generate-object/google-enum.ts', 'workflow.ts', None),
        ('heldout_generation', 'HELD-OUT', 'vercel', 'examples/ai-core/src/generate-text/google.ts', 'workflow.ts', None),
    ]
    for name, split, key, path, output, cells in specs:
        repo, commit = PINS[key]
        dest = ROOT / 'corpus' / name
        dest.mkdir(parents=True, exist_ok=False)
        raw = fetch(repo, commit, path)
        selection = None
        if cells:
            nb = json.loads(raw)
            sources = [''.join(nb['cells'][i]['source']) for i in cells]
            if name == 'anthropic_routing':
                # Exact function/assignment slices; exclude unrelated chain/parallel demos.
                route = next(n for n in ast.parse(sources[1]).body if isinstance(n, ast.FunctionDef) and n.name == 'route')
                sources[1] = ast.get_source_segment(sources[1], route)
                sources[2] = '\n\n'.join(ast.get_source_segment(sources[2], n) for n in ast.parse(sources[2]).body if isinstance(n, ast.Assign))
                (dest / 'util.py').write_bytes(fetch(repo, commit, 'patterns/agents/util.py'))
                selection = 'cell 2: route function; cell 6: assignments only; cell 1 unchanged'
            code = ('\n\n'.join(sources) + '\n').encode()
        else:
            code = raw
        (dest / output).write_bytes(code)
        if name == 'anthropic_classification':
            (dest / 'data').mkdir()
            for file in ['train.tsv', 'test.tsv']:
                (dest / 'data' / file).write_bytes(fetch(repo, commit, 'capabilities/classification/data/' + file))
        license_path = 'LICENSE' if key != 'anthropic' else 'LICENSE'
        (dest / 'LICENSE.upstream').write_bytes(fetch(repo, commit, license_path))
        entry = {'id': name, 'split': split, 'repository': 'https://github.com/' + repo, 'commit': commit, 'source_path': path, 'entrypoint': output, 'notebook_cells': cells, 'selection': selection, 'upstream_sha256': hashlib.sha256(raw).hexdigest(), 'files': {str(p.relative_to(dest)): hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.rglob('*') if p.is_file()}}
        (dest / 'PROVENANCE.json').write_text(json.dumps(entry, indent=2) + '\n')
        entries.append(entry)
    (ROOT / 'corpus' / 'manifest.json').write_text(json.dumps(entries, indent=2) + '\n')
    print('Vendored 6 DEV and 2 HELD-OUT workflows. HELD-OUT source was fetched without display.')


if __name__ == '__main__':
    main()
