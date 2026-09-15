from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'projects/signal-atlas-data-quality'
CASE = PROJECT / 'case-study'
sys.path.insert(0, str(PROJECT))
sys.path.insert(0, str(ROOT / 'scripts'))
from check_events import check_feed, parse_timestamp
from build_demo import build

spec = importlib.util.spec_from_file_location('normalize_case', CASE / 'normalize.py')
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)

class DemoTests(unittest.TestCase):
    def test_real_case_reports_the_normalization_gap(self):
        collected = json.loads((CASE / 'collected-local-times.json').read_text(encoding='utf-8'))
        reviewed = json.loads((CASE / 'normalized-events.json').read_text(encoding='utf-8'))
        as_of = parse_timestamp('2026-09-15T14:44:41Z')
        before = check_feed(collected, as_of=as_of)
        after = check_feed(reviewed, as_of=as_of)
        self.assertEqual(before['summary'], {'events': 3, 'sources': 6, 'errors': 9, 'warnings': 0})
        self.assertEqual({issue['code'] for issue in before['issues']}, {'INVALID_TIMESTAMP'})
        self.assertEqual(after['status'], 'pass')
        self.assertEqual(after['issues'], [])

    def test_normalization_changes_only_reviewed_start_offsets(self):
        source = json.loads((CASE / 'collected-local-times.json').read_text(encoding='utf-8'))
        original = deepcopy(source)
        output = normalizer.normalize(source)
        self.assertEqual(output, json.loads((CASE / 'normalized-events.json').read_text(encoding='utf-8')))
        for event in output['events']:
            for record in [event, *event['sources']]:
                self.assertTrue(record['starts_at'].endswith('+01:00'))
                record['starts_at'] = record['starts_at'][:-6]
        self.assertEqual(output, original)
        self.assertEqual(source, original)

    def test_normalizer_rejects_unreviewed_dates(self):
        source = json.loads((CASE / 'collected-local-times.json').read_text(encoding='utf-8'))
        source['events'][0]['starts_at'] = '2026-10-25T01:30:00'
        with self.assertRaises(ValueError):
            normalizer.normalize(source)

    def test_site_packages_original_checker_and_only_public_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            build(output)
            self.assertEqual((output / 'check_events.py').read_bytes(), (PROJECT / 'check_events.py').read_bytes())
            expected = {'index.html','styles.css','app.js','worker.js','check_events.py','.nojekyll',
                        'data/clean-events.json','data/review-events.json',
                        'data/collected-local-times.json','data/normalized-events.json'}
            self.assertEqual({p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()}, expected)

if __name__ == '__main__':
    unittest.main()
