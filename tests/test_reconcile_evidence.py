"""Focused continuation tests. Copies of captured evidence are test inputs, not new live reads."""
import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'regulatory-change-impact-brief/scripts'))
import reconcile_evidence as r

class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.out=Path(self.temp.name)/'bundle'
        self.out.mkdir()
        shutil.copytree(ROOT/'deliverables/sources',self.out/'sources')
        (self.out/'snapshots').mkdir()
        for name in r.FILES[:2]: shutil.copy2(ROOT/'deliverables/snapshots'/name,self.out/'snapshots'/name)
        shutil.copy2(ROOT/'deliverables/source-manifest.json',self.out/'source-manifest.json')
    def tearDown(self): self.temp.cleanup()
    def stages(self):
        r.build(self.out)
        return [r.c.load(self.out/'snapshots'/f) for f in r.FILES[2:]]
    def test_identity_paragraphs_timing_and_chain(self):
        third,fourth=self.stages()
        self.assertEqual(third['status'],'partial')
        self.assertTrue(all(x['comparison_verified'] for x in third['state']['binding_rules']))
        timing={x['id']:x for x in third['state']['timing_rules']}
        self.assertEqual(timing['TIMING-OJ-ENTRY']['calculated_entry_into_force'],'2024-08-01')
        self.assertEqual(timing['TIMING-AMEND-ENTRY']['calculated_entry_into_force'],'2026-07-27')
        self.assertEqual(timing['TIMING-50-2-TRANSITION']['company_eligibility'],'unresolved')
        self.assertTrue(all(x['comparison_with_captured_binding_basis'] for x in third['state']['guidance_context'] if x['id'].startswith('GUIDANCE-')))
        self.assertTrue(r.validate(self.out)['semantic_replay_valid'])
        self.assertEqual(len(fourth['state']['system_links']),8)
        self.assertEqual(len(fourth['state']['incident_evidence']),10)
        self.assertEqual(len(fourth['state']['calendar_records']),8)
        self.assertFalse(list((self.out/'snapshots').glob('0[5-7]-*.json')))
    def test_policy_support_and_exception_not_approved(self):
        _,fourth=self.stages(); state=fourth['state']
        self.assertEqual(state['policy_controls'],[])
        self.assertFalse(state['approvals_applied'])
        ids={x['id'] for x in state['evidence_gaps']}
        self.assertIn('GAP-POLICY',ids)
        self.assertIn('GAP-EXCEPTION-EVIDENCE-REC-010',ids)
        self.assertEqual(sum(x.startswith('GAP-SUPPORT-') for x in ids),10)
        rec=next(x for x in state['incident_evidence'] if x['id']=='EVIDENCE-REC-004')
        self.assertEqual(rec['values']['evidence_state'],'complete')
        self.assertIn('no AI notice',rec['values']['notes'])
        conflicts={x['id'] for x in state['conflicts']}
        self.assertIn('ISSUE-EVIDENCE-REC-008',conflicts)
        self.assertIn('ISSUE-EVIDENCE-REC-003',conflicts)
        self.assertTrue(all(x['approval_status']=='unverified' for x in state['calendar_records']))
    def test_paragraph_layout_and_changed_rule_detection(self):
        text='\nArticle 50\n'+''.join('\n'+str(n)+'. '+str(n)+' text' for n in range(1,8))
        self.assertEqual(r.paragraphs(text)['4'],'4 text')
        self.assertEqual(r.paragraphs(text.replace('. ','.\n'))['4'],'4 text')
        review=r.Review(self.out); original=review.text
        review.text=lambda name: original(name).replace('Providers shall ensure','Providers may ignore',1) if name=='CONSOLIDATED' else original(name)
        state=review.authority()
        self.assertIn('BLOCK-50-1',{x['id'] for x in state['authority_blockers']})
    def test_row_order_extras_duplicates_and_orphans(self):
        review=r.Review(self.out); original=review.rows
        def rows(name):
            source,values=original(name)
            values=[dict(row,values=dict(row['values'],unrelated='retained')) for row in reversed(values)]
            if name=='SYSTEMS':
                values.append(dict(values[0],values=dict(values[0]['values'],owner='Opposing owner')))
            if name=='EVIDENCE': values[0]['values']['system_id']='UNKNOWN-SYSTEM'
            return source,values
        third=r.snapshot(review,3,review.authority(),review.second)
        baseline=review.reconcile(third)
        review.rows=rows
        changed=review.reconcile(third)
        self.assertEqual({x['values']['system_id'] for x in baseline['system_facts']},{x['values']['system_id'] for x in changed['system_facts']})
        self.assertTrue(any(x['id'].startswith('CONFLICT-ID-') for x in changed['conflicts']))
        self.assertTrue(any(x['id'].startswith('GAP-ORPHAN-') for x in changed['evidence_gaps']))
        self.assertTrue(all(x['values']['unrelated']=='retained' for x in changed['calendar_records']))
    def test_invalid_fields_remain_unresolved(self):
        review=r.Review(self.out); original=review.rows
        def rows(name):
            source,values=original(name)
            if name=='SYSTEMS': values[0]['values'].update(owner='',evidence_updated_at='2026-99-12',provider_role='renamed')
            return source,values
        review.rows=rows
        state=review.reconcile({'state':{}})
        self.assertTrue(any('missing' in x['summary'] and 'invalid' in x['summary'] for x in state['evidence_gaps']))
    def test_missing_fields_and_unavailable_authority_remain_visible(self):
        review=r.Review(self.out); original=review.source
        def source(name):
            if name=='AMEND': raise ValueError('AMEND unavailable')
            return original(name)
        review.source=source
        self.assertIn('BLOCK-AUTHORITY',{x['id'] for x in review.authority()['authority_blockers']})
        original_rows=review.rows
        def rows(name):
            if name=='SYSTEMS': raise ValueError('Missing/ambiguous required fields: SYSTEMS')
            return original_rows(name)
        review.rows=rows
        state=review.reconcile({'state':{}})
        self.assertIn('GAP-SYSTEMS',{x['id'] for x in state['evidence_gaps']})
        self.assertEqual(state['system_facts'],[])
    def test_tampering_and_unsupported_completion_rejected(self):
        self.stages()
        path=self.out/'snapshots'/r.FILES[3]
        baseline=path.read_bytes()
        for mutate in [lambda v:v.update(status='complete'),lambda v:v['state'].update(review_date='2026-10-11'),
                       lambda v:v['state']['system_facts'][0]['evidence_ids'].append('UNKNOWN'),
                       lambda v:v['predecessor'].update(sha256='sha256:'+'0'*64),
                       lambda v:v['state']['calendar_records'][0]['values'].update(due_date='2020-01-01')]:
            v=r.c.load(path); mutate(v); r.c.save(path,v)
            with self.assertRaises(ValueError): r.validate(self.out)
            path.write_bytes(baseline)
    def test_no_overwrite_and_source_tamper(self):
        self.stages()
        with self.assertRaises(ValueError): r.build(self.out)
        source=r.c.load(self.out/'snapshots'/r.FILES[1])['state']['sources'][2]
        path=self.out/source['local_reference']; path.write_bytes(path.read_bytes()+b'tamper')
        with self.assertRaises(ValueError): r.validate(self.out)

if __name__=='__main__': unittest.main()
