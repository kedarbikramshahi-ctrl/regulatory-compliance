"""Synthetic response fixtures test mechanics only, never live-source evidence."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('capture',ROOT/'regulatory-change-impact-brief/scripts/capture_sources.py')
capture=importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)

class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out=Path(self.temp.name)/'deliverables'
        self.manifest=ROOT/'regulatory-change-impact-brief/references/sources.json'
        self.sources=capture.load(self.manifest)['sources']
        self.calls=[]
    def response(self,url,headers):
        self.calls.append((url,headers))
        source=next((s for s in self.sources if s['url']==url),None)
        status=200
        if url.startswith('https://api.notion.com'):
            status=401; text='{"status":401,"code":"unauthorized"}'
        elif 'publications.europa.eu' in url:
            celex=url.rsplit('/',1)[1]
            if 'xml;notice' in headers.get('Accept',''):
                text='<NOTICE><WORK><URI><IDENTIFIER>'+celex+'</IDENTIFIER></URI></WORK></NOTICE>'
            elif celex=='02024R1689-20260727':
                text='<title>Consolidated</title><p>02024R1689 — EN — 27.07.2026 — 001.001 Article 50</p>'
            else:
                title='2024/1689' if celex=='32024R1689' else '2026/1744'
                date='12.7.2024' if celex=='32024R1689' else '24.7.2026'
                text='<p>REGULATION (EU) '+title+' '+date+' Article 50</p>'
        elif source['name']=='POLICY': text='<title>Notion</title><p>JavaScript required</p>'
        elif source['name'] in ('OJ','AMEND','CONSOLIDATED'): status=202; text=''
        elif source['name'] in ('SYSTEMS','EVIDENCE','CALENDAR'):
            columns={'SYSTEMS':['system_id','system_name','record_version'],
                     'EVIDENCE':['record_id','system_id','evidence_state'],
                     'CALENDAR':['action_id','system_id','source_version']}[source['name']]
            values=['SYNTHETIC-'+str(i) for i in range(3)]
            text='<title>Synthetic table</title><table><tr>'+''.join('<th>'+c+'</th>' for c in columns)+'</tr><tr>'+''.join('<td>'+v+'</td>' for v in values)+'</tr></table>'
        else:
            title={'LAW':'Article 50','TIME':'Timeline for the Implementation','FAQ':'Transparency obligations under Article 50'}[source['name']]
            text='<title>'+title+'</title><p>'+('Synthetic testing content. '*80)+'</p>'
        return dict(status=status,content_type='text/html',body=text.encode(),final_url=url,redirects=[])
    def build(self): return capture.build(self.manifest,self.out,self.response)
    def test_only_two_valid_snapshots_and_all_fresh_attempts(self):
        result=self.build()
        self.assertEqual(result['attempt_count'],17)
        self.assertEqual(len(self.calls),17)
        self.assertEqual(result['stages_validated'],[1,2])
        self.assertEqual(len(list((self.out/'snapshots').iterdir())),2)
        second=capture.load(self.out/'snapshots/02-source-capture.json')
        self.assertEqual(second['status'],'partial')
        policy=[s for s in second['state']['sources'] if s['source_name']=='POLICY']
        self.assertTrue(all(s['local_reference'] is None and s['content_hash'] is None for s in policy))
        self.assertEqual(policy[1]['http_status'],401)
        self.assertTrue(policy[1]['diagnostic_reference'])
    def test_repeated_runs_are_fresh_and_preserved(self):
        first=self.build(); second=self.build()
        self.assertEqual(len(self.calls),34)
        self.assertNotEqual(first['run_id'],second['run_id'])
        self.assertTrue((self.out/'history'/first['run_id']/'snapshots/02-source-capture.json').is_file())
        scope=capture.load(self.out/'snapshots/01-scope.json')
        self.assertEqual(scope['state']['supersedes_run_id'],first['run_id'])
        self.assertEqual(scope['state']['as_of'],'2026-08-26T00:00:00Z')
    def test_evidence_tamper_is_detected(self):
        self.build()
        path=next((self.out/'sources').glob('*.response'))
        path.write_bytes(b'altered')
        with self.assertRaisesRegex(ValueError,'hash'): capture.validate(self.out)
    def test_predecessor_tamper_is_detected(self):
        self.build()
        path=self.out/'snapshots/01-scope.json'
        path.write_bytes(path.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'Predecessor'): capture.validate(self.out)
    def test_wrong_date_rejected_before_requests(self):
        data=capture.load(self.manifest); data['review_date']='2026-10-11'
        path=Path(self.temp.name)/'manifest.json'; capture.save(path,data)
        with self.assertRaises(ValueError): capture.build(path,self.out,self.response)
        self.assertEqual(self.calls,[])
    def test_wrong_identity_and_landing_pages_rejected(self):
        source=next(s for s in self.sources if s['name']=='OJ')
        for body,mode in [('<title>Official Journal</title>','original'),
                         ('<NOTICE><WORK><URI><IDENTIFIER>WRONG</IDENTIFIER></URI></WORK></NOTICE>','cellar-metadata')]:
            response=dict(status=200,body=body.encode())
            self.assertEqual(capture.inspect(source,mode,response)[0],'invalid')
    def test_reordered_headers_and_extra_columns_keep_values(self):
        source=next(s for s in self.sources if s['name']=='SYSTEMS')
        body='<table><tr><th>record_version</th><th>extra</th><th>system_name</th><th>system_id</th></tr><tr><td>v1</td><td>x</td><td>Synthetic</td><td>T-1</td></tr></table>'
        state,meta,locators,_=capture.inspect(source,'original',dict(status=200,body=body.encode()))
        self.assertEqual(state,'retrieved')
        self.assertEqual(meta['rows'][0]['values']['system_id'],'T-1')
        self.assertEqual(meta['observed_versions'],['v1'])
        self.assertTrue(locators)
    def test_network_failure_preserved_and_never_synthesized(self):
        source=self.sources[0]
        def failure(url,headers): raise TimeoutError('Synthetic timeout')
        rec=capture.capture(source,'original',source['url'],{},Path(self.temp.name),failure)
        self.assertEqual(rec['retrieval_status'],'unavailable')
        self.assertIsNone(rec['content_hash'])
        self.assertIn('technical_error',rec)
        self.assertGreaterEqual(rec['completed_at'],rec['started_at'])
    def test_bad_rows_retained_with_cells_locators_and_no_inferred_identity(self):
        columns={'SYSTEMS':['system_id','system_name','record_version'],
                 'EVIDENCE':['record_id','system_id','evidence_state'],
                 'CALENDAR':['action_id','system_id','source_version']}
        def row(cells): return '<tr>'+''.join('<td>'+v+'</td>' for v in cells)+'</tr>'
        for name, headers in columns.items():
            source=next(s for s in self.sources if s['name']==name)
            bad=[['TOO','SHORT'],['TOO','MANY','CELLS','HERE'],['   ','value','version']]
            for valid in ([],[['TEST-ID','value','version']]):
                with self.subTest(source=name,valid=bool(valid)):
                    body=('<table>'+row(headers)+''.join(row(v) for v in valid+bad)+'</table>').encode()
                    state,meta,locators,_=capture.inspect(source,'original',dict(status=200,body=body))
                    self.assertEqual(state,'retrieved' if valid else 'unverified')
                    self.assertEqual(len(meta['rows']),len(valid))
                    self.assertEqual([x['cells'] for x in meta['row_issues']],[[v.strip() for v in cells] for cells in bad])
                    self.assertEqual(meta['record_quality'],'partial')
                    self.assertEqual(len({x['locator'] for x in meta['row_issues']}),3)
                    for problem in meta['row_issues']:
                        self.assertIn(problem['locator'],locators)
                        self.assertTrue(problem['owner']);self.assertTrue(problem['resolution_need'])
                        self.assertNotIn('values',problem)
    def test_credentials_and_unapproved_redirect_hosts_rejected(self):
        for url in ['https://user:password@docs.google.com/x','https://docs.google.com/x?api_key=secret','https://unapproved.example/x']:
            with self.assertRaises(ValueError): capture.check_url(url)
    def test_empty_grid_slots_and_unrelated_tables_are_not_missing_records(self):
        source=next(s for s in self.sources if s['name']=='SYSTEMS')
        body=('<table><tr><th>1</th><th>system_id</th><th>system_name</th><th>record_version</th></tr>'
              '<tr><td>2</td><td>TEST-1</td><td>Test</td><td>v1</td></tr>'
              '<tr><td>3</td><td></td><td></td><td></td></tr>'
              '<tr><td></td><td></td><td></td><td></td></tr></table>'
              '<table><tr><td>Unrelated navigation</td></tr></table>').encode()
        state,meta,_,_=capture.inspect(source,'original',dict(status=200,body=body))
        self.assertEqual(state,'retrieved');self.assertEqual(len(meta['rows']),1)
        self.assertNotIn('row_issues',meta)

if __name__=='__main__': unittest.main()
