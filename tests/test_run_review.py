"""End-to-end/recovery tests; transport fixture is never used by the production CLI."""
import sys
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'regulatory-change-impact-brief/scripts'))
import run_review as w

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.out=Path(self.temp.name)/'deliverables'
        self.manifest=w.c.PACKAGE/'references/sources.json'
        prior=ROOT/'deliverables/history/live-070d798484d1497495fa28fac99dcb2f'
        self.fixture=prior if (prior/'snapshots/02-source-capture.json').exists() else ROOT/'deliverables'
        sources=w.c.load(self.fixture/'snapshots/02-source-capture.json')['state']['sources']
        self.responses={}
        for s in sources:
            body=(self.fixture/s['diagnostic_reference']).read_bytes() if s.get('diagnostic_reference') else b''
            self.responses[(s['locator'],s['request_headers'].get('Accept'))]=dict(body=body,status=s.get('http_status',503),
                content_type=s['content_type'],final_url=s.get('final_url',s['locator']),redirects=s.get('redirects',[]))
        self.calls=[]
    def tearDown(self): self.temp.cleanup()
    def transport(self,url,headers):
        self.calls.append((url,headers.get('Accept')))
        return dict(self.responses[(url,headers.get('Accept'))])
    def execute(self,**kwargs): return w.run(self.manifest,self.out,transport=self.transport,**kwargs)
    def test_two_fresh_runs_all_stages_history_and_hashes(self):
        first=self.execute();original=w.inventory(self.out/'sources');second=self.execute()
        self.assertNotEqual(first['run_id'],second['run_id']);self.assertEqual(len(self.calls),34)
        archived=Path(second['history_path'])
        self.assertEqual(w.inventory(archived/'sources'),original)
        self.assertTrue((archived/'compliance-brief.md').exists())
        self.assertTrue(w.p.validate(self.out)['all_seven_run_ids_match'])
        scope=w.c.load(self.out/'snapshots/01-scope.json')
        self.assertEqual(scope['state']['supersedes_run_id'],first['run_id'])
        self.assertEqual(scope['state']['review_date'],'2026-08-26')
        self.assertEqual(second['publication_status'],'blocked')
    def test_bad_rows_reach_snapshots_and_drafts_even_when_no_valid_rows(self):
        import csv
        from html import escape
        source=next(s for s in w.c.load(self.manifest)['sources'] if s['name']=='SYSTEMS')
        response=self.responses[(source['url'],None)]
        _,meta,_,_=w.c.inspect(source,'original',response)
        headers=meta['headers']
        def row(cells): return '<tr>'+''.join('<td>'+escape(v)+'</td>' for v in cells)+'</tr>'
        valid=[list(r['values'][h] for h in headers) for r in meta['rows']]
        blank=list(valid[0]);blank[headers.index('system_id')]=''
        malformed=valid[0][:-1]
        for keep_valid in (True,False):
            with self.subTest(valid_rows=keep_valid):
                response['body']=('<table>'+row(headers)+''.join(row(v) for v in (valid if keep_valid else [])+[blank,malformed])+'</table>').encode()
                result=self.execute()
                self.assertTrue(result['final_files_agree_with_stage06'])
                second=w.c.load(self.out/'snapshots/02-source-capture.json')
                fourth=w.c.load(self.out/'snapshots/04-evidence-reconciliation.json')
                sixth=w.c.load(self.out/'snapshots/06-actions-and-approvals.json')
                self.assertEqual(second['status'],'partial')
                source_record=next(s for s in second['state']['sources'] if s['source_name']=='SYSTEMS')
                self.assertEqual(source_record['requested_content_available'],keep_valid)
                self.assertEqual(len([r for r in second['unresolved'] if r['id'].startswith('UNRESOLVED-ROW-')]),2)
                gaps=[r for r in fourth['state']['evidence_gaps'] if r['id'].startswith('GAP-ROW-')]
                self.assertEqual(len(gaps),2)
                self.assertEqual([x['row_issue']['cells'] for x in gaps],[blank,malformed])
                self.assertEqual(gaps[0]['owner'],valid[0][headers.index('owner')])
                self.assertEqual(gaps[1]['owner'],'Source owner')
                self.assertEqual(len(fourth['state']['system_facts']),len(valid) if keep_valid else 0)
                with (self.out/'impact-register.csv').open(encoding='utf-8',newline='') as stream:
                    register={r['impact_id']:r for r in csv.DictReader(stream)}
                brief=(self.out/'compliance-brief.md').read_text(encoding='utf-8')
                for gap in gaps:
                    self.assertIn(gap['id'],{x['id'] for x in sixth['state']['escalations']})
                    self.assertEqual(register[gap['id']]['state'],'unresolved')
                    self.assertEqual(register[gap['id']]['system_id'],'ALL')
                    self.assertIn(gap['id'],brief)
                    self.assertIn(gap['row_issue']['reason'],brief)
    def test_missing_and_damaged_outputs_detected_and_rebuilt_fresh(self):
        self.execute();(self.out/'impact-register.csv').unlink()
        source=self.out/'sources/SOURCE-SYSTEMS-original.response';source.write_bytes(b'damaged retained bytes')
        report=w.inspect(self.out);self.assertFalse(report['valid']);self.assertIn('impact-register.csv',report['missing_files'])
        result=self.execute(reason='Recovery test: missing final file and damaged evidence')
        self.assertEqual(len(self.calls),34);self.assertFalse(result['prior_bundle_valid'])
        archive=Path(result['history_path'])
        self.assertEqual((archive/'sources/SOURCE-SYSTEMS-original.response').read_bytes(),b'damaged retained bytes')
        self.assertFalse((archive/'impact-register.csv').exists())
        self.assertTrue(w.p.validate(self.out)['final_files_agree_with_stage06'])
        (self.out/'snapshots/03-authority-and-timing.json').unlink()
        (self.out/'action-calendar.ics').write_bytes(b'damaged calendar')
        report=w.inspect(self.out)
        self.assertTrue(any(x['path']=='action-calendar.ics' for x in report['issues']))
        self.assertIn('snapshots/03-authority-and-timing.json',report['missing_files'])
        repaired=self.execute(reason='Recovery test: missing snapshot and damaged final file')
        self.assertEqual(len(self.calls),51)
        self.assertFalse((Path(repaired['history_path'])/'snapshots/03-authority-and-timing.json').exists())
        self.assertTrue(w.p.validate(self.out)['schemas_valid'])
    def test_stage_failure_keeps_previous_and_candidate_then_fresh_retry(self):
        first=self.execute();before=w.inventory(self.out/'snapshots')
        def fail(stage):
            if stage=='impacts-and-actions': raise RuntimeError('Injected local stage failure')
        with self.assertRaises(RuntimeError): self.execute(stage_hook=fail)
        self.assertEqual(w.inventory(self.out/'snapshots'),before)
        journals=[w.c.load(x) for x in (self.out/'workflow-attempts').glob('*/journal.json')]
        failed=next(x for x in journals if x['status']=='failed')
        self.assertEqual(failed['failure']['stage'],'impacts-and-actions')
        self.assertTrue((self.out/'workflow-attempts'/failed['run_id']/'bundle/snapshots/04-evidence-reconciliation.json').exists())
        retry=self.execute();self.assertEqual(len(self.calls),51);self.assertEqual(retry['supersedes_run_id'],first['run_id'])
    def test_interrupted_promotion_restores_archived_previous_and_preserves_observed(self):
        self.execute();before=w.inventory(self.out/'snapshots')
        def fail(index): raise RuntimeError('Injected promotion interruption')
        with self.assertRaises(RuntimeError): self.execute(promotion_hook=fail)
        self.assertEqual(w.inventory(self.out/'snapshots'),before)
        self.assertTrue(list((self.out/'workflow-attempts').glob('*/recovery-observed-*')))
        self.assertTrue(w.p.validate(self.out)['artifact_hashes_valid'])
        self.execute();self.assertEqual(len(self.calls),51)
    def test_pending_journal_and_stale_lock_recovery_without_reusing_capture(self):
        first=self.execute();attempt=self.out/'workflow-attempts'/'interrupted-test';attempt.mkdir()
        w.atomic(attempt/'journal.json',dict(status='running',phase='capture',run_id='test-interruption'))
        w.atomic(self.out/'.workflow.lock',dict(pid=99999999))
        with patch.object(w,'pid_alive',return_value=False): second=self.execute()
        self.assertEqual(w.c.load(attempt/'journal.json')['status'],'failed')
        self.assertNotEqual(first['run_id'],second['run_id']);self.assertEqual(len(self.calls),34)
        self.assertTrue(list((self.out/'workflow-attempts').glob('stale-lock-*/lock.json')))
    def test_active_lock_and_unsafe_output_refused(self):
        self.assertTrue(w.pid_alive(os.getpid()))
        self.out.mkdir();w.atomic(self.out/'.workflow.lock',dict(pid=os.getpid()))
        with self.assertRaises(ValueError): self.execute()
        self.assertEqual(self.calls,[])
        with self.assertRaises(ValueError): w.run(self.manifest,ROOT,transport=self.transport)

if __name__=='__main__': unittest.main()
