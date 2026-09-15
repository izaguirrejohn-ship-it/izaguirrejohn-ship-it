"""Assemble a public static site using the canonical checker and reviewed fixtures."""
from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'projects/signal-atlas-data-quality'
OUTPUT = ROOT / '_site'
RUNTIME = ROOT / 'node_modules/pyodide'
RUNTIME_FILES = ('pyodide.js', 'pyodide.asm.mjs', 'pyodide.asm.wasm',
                 'python_stdlib.zip', 'pyodide-lock.json')

def build(output=OUTPUT, runtime=RUNTIME):
    if json.loads((runtime / 'package.json').read_text())['version'] != '314.0.7':
        raise ValueError('The public demo requires Pyodide 314.0.7.')
    for name in RUNTIME_FILES:
        if not (runtime / name).is_file():
            raise FileNotFoundError(f'Missing runtime asset: {name}')
    output.mkdir(exist_ok=True)
    for name in ('index.html','styles.css','app.js','worker.js'):
        shutil.copyfile(ROOT / 'demo' / name, output / name)
    shutil.copyfile(PROJECT / 'check_events.py', output / 'check_events.py')
    (output / 'data').mkdir(exist_ok=True)
    for name in ('clean-events.json','review-events.json'):
        shutil.copyfile(PROJECT / 'examples' / name, output / 'data' / name)
    for name in ('collected-local-times.json','normalized-events.json'):
        shutil.copyfile(PROJECT / 'case-study' / name, output / 'data' / name)
    (output / '.nojekyll').touch()
    (output / 'runtime').mkdir(exist_ok=True)
    for name in RUNTIME_FILES:
        shutil.copyfile(runtime / name, output / 'runtime' / name)
    # Preserve the runtime's distributed license notices.
    for source in runtime.glob('*LICENSE*'):
        if source.is_file():
            shutil.copyfile(source, output / 'runtime' / source.name)
    for name in ('PYODIDE-LICENSE.txt', 'PYTHON-LICENSE.txt', 'RUNTIME-NOTICES.md'):
        shutil.copyfile(ROOT / 'demo' / name, output / 'runtime' / name)
    print(f'Built public demo: {output}')

if __name__ == '__main__':
    build()
