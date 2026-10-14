"""Final-draft tests on disposable copies of actual captured inputs."""
import copy
import csv
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'regulatory-change-impact-brief/scripts'))
import publish_drafts as p

class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.out=Path(self.temp.name)/'bundle';self.out.mkdir()
        shutil.copytree(ROOT/'deliverables/sources',self.out/'sources');(self.out/'snapshots').mkdir()
        for name in p.a.FILES: shutil.copy2(ROOT/'deliverables/snapshots'/name,self.out/'snapshots'/name)
        shutil.copy2(ROOT/'deliverables/source-manifest.json',self.out/'source-manifest.json')
        self.snapshots,self.upstream=p.inputs(self.out)
    def tearDown(self): self.temp.cleanup()
    def test_seven_run_ids_schema_hashes_requests_and_stage06_agreement(self):
        result=p.build(self.out)
        self.assertTrue(result['all_seven_run_ids_match']);self.assertTrue(result['final_files_agree_with_stage06'])
        self.assertEqual(result['publication_status'],'blocked')
        seventh=p.c.load(self.out/'snapshots'/p.FILES[6])
        self.assertEqual(len(seventh['state']['review_request_bindings']),70)
        for binding in seventh['state']['review_request_bindings']:
            self.assertEqual(binding['approval_status'],'pending');self.assertEqual(binding['delivery_status'],'not-sent')
            self.assertEqual(len(binding['drafts']),3)
        brief=(self.out/'compliance-brief.md').read_text(encoding='utf-8')
        self.assertIn('state.review_request_bindings',brief)
        self.assertNotIn(p.c.digest((self.out/'compliance-brief.md').read_bytes()),brief)
    def test_csv_scope_ids_evidence_and_unborrowed_dates(self):
        rows=p.register_rows(self.snapshots,self.upstream)
        parsed=list(csv.DictReader(io.StringIO(p.render_csv(rows).decode('utf-8'),newline='')))
        self.assertEqual(rows,parsed);self.assertEqual(len(rows),105)
        self.assertEqual(len({x['system_id'] for x in rows if x['impact_id'].startswith('IMPACT-')}),8)
        self.assertTrue(all(x['approval_status']=='pending' for x in rows))
        row=next(x for x in rows if x['impact_id']=='IMPACT-AI-001-50-1')
        self.assertEqual(row['proposed_due_date'],'')
        self.assertIn('PROPOSED-CALENDAR-ACT-008=2026-10-02',row['action_date_pairs'])
        self.assertIn('undated',row['action_date_pairs'])
        self.assertTrue(any(x['impact_id']=='GAP-POLICY' for x in rows))
    def test_calendar_actual_proposals_stable_uids_and_no_undated_events(self):
        data=p.calendar(self.snapshots);events=p.check_ics(data)
        expected=p.dated_actions(self.snapshots[5],True)
        self.assertEqual(len(events),8)
        for event,action in zip(events,expected):
            self.assertEqual(event['UID'],action['id']+'@project-b.quillhaven.invalid')
            self.assertEqual(event['DTSTART;VALUE=DATE'],action['proposed_due_date'].replace('-',''))
            self.assertIn(action['id'],event['DESCRIPTION']);self.assertIn(action['owner'],event['DESCRIPTION'])
            self.assertEqual(event['STATUS'],'TENTATIVE');self.assertNotIn('DTEND',event)
        self.assertEqual(p.calendar(self.snapshots),data)
    def test_empty_calendar_and_utf8_folding_escaping(self):
        changed=copy.deepcopy(self.snapshots)
        for action in changed[5]['state']['proposed_actions']: action['proposed_due_date']=None
        self.assertEqual(p.check_ics(p.calendar(changed)),[])
        sample=copy.deepcopy(self.snapshots)
        sample[5]['state']['proposed_actions'][-1]['proposed_action']='Review café, records; '+('語'*90)+'\nSecond line\\notes'
        data=p.calendar(sample);events=p.check_ics(data)
        self.assertIn('\\,',events[-1]['SUMMARY']);self.assertIn('\\;',events[-1]['SUMMARY']);self.assertIn('\\n',events[-1]['SUMMARY'])
        self.assertTrue(all(len(x)<=75 for x in data.split(b'\r\n')))
    def test_changed_file_rehash_cannot_hide_stage06_disagreement(self):
        p.build(self.out)
        path=self.out/'impact-register.csv';path.write_bytes(path.read_bytes().replace(b'pending',b'approved',1))
        seventh=p.c.load(self.out/'snapshots'/p.FILES[6])
        for artifact in seventh['state']['artifacts']:
            if artifact['path']=='impact-register.csv': artifact['sha256']=p.c.digest(path.read_bytes())
        for binding in seventh['state']['review_request_bindings']:
            for draft in binding['drafts']:
                if draft['path']=='impact-register.csv': draft['sha256']=p.c.digest(path.read_bytes())
        p.c.save(self.out/'snapshots'/p.FILES[6],seventh)
        with self.assertRaisesRegex(ValueError,'disagrees'): p.validate(self.out)
    def test_binding_and_run_tampering_missing_files_and_no_overwrite(self):
        p.build(self.out);path=self.out/'snapshots'/p.FILES[6];original=path.read_bytes()
        for mutate in [lambda v:v.update(run_id='other-run'),lambda v:v['state']['review_request_bindings'][0]['drafts'][0].update(sha256='sha256:'+'0'*64),
                       lambda v:v['state'].update(publication_status='validated'),lambda v:v['state']['review_request_bindings'][0].update(delivery_status='sent')]:
            value=p.c.load(path);mutate(value);p.c.save(path,value)
            with self.assertRaises(ValueError): p.validate(self.out)
            path.write_bytes(original)
        with self.assertRaises(ValueError): p.build(self.out)
        (self.out/'action-calendar.ics').unlink()
        with self.assertRaises(FileNotFoundError): p.validate(self.out)

if __name__=='__main__': unittest.main()
