import copy
import csv
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from compile_review import build, InputError

FIXTURE=Path(__file__).resolve().parents[1]/'assets/procurement-input.json'

class ReviewTests(unittest.TestCase):
    def setUp(self): self.src=json.loads(FIXTURE.read_text())
    def document(self): return json.loads(build(self.src)['mandate-draft.json'])
    def codes(self): return {x['code'] for x in self.document()['findings']}
    def test_fixture_is_inactive(self):
        d=self.document(); self.assertEqual(d['status'],'draft'); self.assertFalse(d['active']); self.assertFalse(d['runtime_verified'])
        self.assertEqual(d['review_status'],'complete_for_human_review')
    def test_no_live_scenario_results(self):
        s=json.loads(build(self.src)['scenario-tests.json']); self.assertFalse(s['live_actions'])
        self.assertTrue(all(c['status']=='not_run' and 'expected_assertion' in c for c in s['cases']))
        self.assertGreaterEqual(len(s['cases']),10)
    def test_unknowns_are_preserved(self):
        self.src['mandate']={'purpose':'Research'}; self.src['evidence']={'purpose':'User: Research'}
        d=self.document(); self.assertIsNone(d['mandate']['period_limit_cents']); self.assertIsNone(d['mandate']['principal'])
        self.assertEqual(d['review_status'],'needs_human_input')
    def test_activation_field_rejected(self):
        self.src['mandate']['active']=True
        with self.assertRaises(InputError): build(self.src)
    def test_unknown_root_rejected(self):
        self.src['execute']=True
        with self.assertRaises(InputError): build(self.src)
    def test_negative_boolean_float_and_unsafe_amounts_rejected(self):
        for v in (-1,True,1.5,9_007_199_254_740_991):
            with self.subTest(v=v):
                self.src['mandate']['per_action_limit_cents']=v
                with self.assertRaises(InputError): build(self.src)
    def test_unknown_currency_not_converted(self):
        self.src['mandate']['currency']='USD'
        with self.assertRaises(InputError): build(self.src)
    def test_naive_date_rejected(self):
        self.src['mandate']['expires_at']='2026-09-30T12:00:00'
        with self.assertRaises(InputError): build(self.src)
    def test_reversed_window_flagged(self):
        self.src['mandate']['expires_at']='2026-09-01T00:00:00Z'; self.assertIn('invalid_window',self.codes())
    def test_zero_and_empty_scope_flagged(self):
        self.src['mandate']['per_action_limit_cents']=0; self.src['mandate']['allowed_categories']=[]
        self.assertTrue({'zero_boundary','empty_allowlist'}<=self.codes())
    def test_category_conflict_flagged(self):
        self.src['mandate']['blocked_categories']=['Data']; self.assertIn('category_conflict',self.codes())
    def test_missing_provenance_flagged(self):
        del self.src['evidence']['approval_owner']; self.assertIn('missing_provenance',self.codes())
    def test_approval_routes_remain_distinct(self):
        self.src['mandate']['approval_owner']=None; self.src['evidence'].pop('approval_owner')
        self.src['mandate']['new_counterparty_approval_owner']='Vendor committee'
        self.src['evidence']['new_counterparty_approval_owner']='User: new vendors need Vendor committee approval'
        d=self.document(); self.assertIsNone(d['mandate']['approval_owner'])
        cases=json.loads(build(self.src)['scenario-tests.json'])['cases']
        by_id={x['id']:x for x in cases}; self.assertIsNone(by_id['S05']['setup']['approval_owner'])
        self.assertEqual(by_id['S06']['setup']['approval_owner'],'Vendor committee')
    def test_exact_boundary_and_blocked_category_cases(self):
        cases={x['id']:x for x in json.loads(build(self.src)['scenario-tests.json'])['cases']}
        self.assertEqual(cases['S13']['setup']['amount_cents'],1000)
        self.assertEqual(cases['S14']['setup']['amount_cents'],2000)
        self.assertEqual(cases['S15']['setup']['category'],'marketing lists')
    def test_unreachable_threshold_flagged(self):
        self.src['mandate']['approval_threshold_cents']=self.src['mandate']['per_action_limit_cents']
        self.assertIn('unreachable_amount_review',self.codes())
    def test_duplicate_categories_rejected(self):
        self.src['mandate']['allowed_categories']=['Data',' data ']
        with self.assertRaises(InputError): build(self.src)
    def test_output_is_repeatable_and_does_not_mutate_input(self):
        before=copy.deepcopy(self.src); self.assertEqual(build(self.src),build(self.src)); self.assertEqual(before,self.src)
    def test_csv_formula_inert_and_markdown_escaped(self):
        self.src['mandate']['agent_name']='=SUM(1,2)'; self.src['mandate']['notes']='<script>|not code'
        files=build(self.src); rows=list(csv.reader(io.StringIO(files['permission-matrix.csv'])))
        self.assertEqual(next(r[1] for r in rows if r[0]=='agent_name'),"'=SUM(1,2)")
        self.assertNotIn('<script>',files['authority-review.md'])
    def test_cli_creates_four_files_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as root:
            out=Path(root)/'review'; cmd=[sys.executable,str(Path(__file__).with_name('compile_review.py')),'--input',str(FIXTURE),'--out',str(out)]
            first=subprocess.run(cmd,capture_output=True,text=True); self.assertEqual(first.returncode,0,first.stderr)
            self.assertEqual(len(list(out.iterdir())),4)
            before={p.name:p.read_bytes() for p in out.iterdir()}
            again=subprocess.run(cmd,capture_output=True,text=True); self.assertEqual(again.returncode,2)
            self.assertEqual(before,{p.name:p.read_bytes() for p in out.iterdir()})

if __name__=='__main__': unittest.main()
