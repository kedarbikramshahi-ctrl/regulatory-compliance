"""Targeted malformed-state and lock recovery checks."""
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'regulatory-change-impact-brief/scripts'))
import run_review as w

class WorkflowSafetyTests(unittest.TestCase):
    def test_changed_archive_basis_stops_before_canonical_replacement(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp);(out/'observed.txt').write_text('before',encoding='utf-8')
            previous=w.inspect(out)
            (out/'observed.txt').write_text('after',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'changed during archive'): w.archive(out,previous,'test-attempt')
            self.assertEqual((out/'observed.txt').read_text(encoding='utf-8'),'after')
            self.assertTrue(list((out/'history').glob('*/observed.txt')))
    def test_unknown_lock_owner_is_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp);w.atomic(out/'.workflow.lock',{'created_at':'unknown owner'})
            before=(out/'.workflow.lock').read_bytes()
            with self.assertRaisesRegex(ValueError,'owner is unknown'): w.acquire(out)
            self.assertEqual((out/'.workflow.lock').read_bytes(),before)
    def test_malformed_snapshot_inspection_and_fresh_blocked_recovery(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'deliverables';(out/'snapshots').mkdir(parents=True)
            (out/'snapshots/01-scope.json').write_text('["invalid snapshot shape"]',encoding='utf-8')
            report=w.inspect(out);self.assertFalse(report['valid']);self.assertTrue(report['issues'])
            calls=[]
            def unavailable(url,headers):
                calls.append(url)
                return dict(body=b'',status=503,content_type='text/plain',final_url=url,redirects=[])
            result=w.run(w.c.PACKAGE/'references/sources.json',out,transport=unavailable,reason='Test-only unavailable source responses')
            self.assertEqual(len(calls),17);self.assertEqual(result['publication_status'],'blocked')
            self.assertIsNone(result['supersedes_run_id'])
            self.assertIn('unidentified-',result['history_path'])
            self.assertEqual((Path(result['history_path'])/'snapshots/01-scope.json').read_text(encoding='utf-8'),'["invalid snapshot shape"]')
            self.assertTrue(w.p.validate(out)['all_seven_run_ids_match'])

if __name__=='__main__': unittest.main()
