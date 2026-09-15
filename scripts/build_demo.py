"""Assemble a public static site using the canonical checker and reviewed fixtures."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'projects/signal-atlas-data-quality'
OUTPUT = ROOT / '_site'

def build(output=OUTPUT):
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
    print(f'Built public demo: {output}')

if __name__ == '__main__':
    build()
