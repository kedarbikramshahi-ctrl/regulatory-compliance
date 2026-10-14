"""Focused review-only stage 05/06 tests; captured inputs are copied, never live substitutes."""
import copy
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'regulatory-change-impact-brief/scripts'))
import analyze_impacts as a

class ImpactTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.out=Path(self.temp.name)/'bundle';self.out.mkdir()
        shutil.copytree(ROOT/'deliverables/sources',self.out/'sources');(self.out/'snapshots').mkdir()
        for f in a.FILES[:4]: shutil.copy2(ROOT/'deliverables/snapshots'/f,self.out/'snapshots'/f)
        shutil.copy2(ROOT/'deliverables/source-manifest.json',self.out/'source-manifest.json')
        self.third,self.fourth,self.versions=a.basis(self.out)
    def tearDown(self): self.temp.cleanup()
    def test_all_systems_scoped_outcomes_policy_and_conflicts(self):
        state=a.analyze(self.third,self.fourth)
        self.assertEqual(len(state['impacts']),80)
        self.assertEqual(len({x['system_id'] for x in state['impacts']}),8)
        ids={x['id']:x for x in state['impacts']}
        self.assertEqual(ids['IMPACT-AI-004-50-1']['state'],'supported-impact')
        self.assertIn('not a finding of legal breach',ids['IMPACT-AI-004-50-1']['reason'])
        self.assertEqual(ids['IMPACT-AI-007-50-1']['state'],'conflicting')
        self.assertEqual(ids['IMPACT-AI-003-50-2']['state'],'conflicting')
        self.assertEqual(ids['IMPACT-AI-006-50-4-text']['state'],'supported-no-impact')
        self.assertTrue(all(x['state']=='unresolved' for x in state['impacts'] if x['rule_ref']=='Internal POLICY'))
        self.assertTrue(all(x['approval_status']=='pending' for x in state['impacts']))
    def test_authority_block_and_role_changes_do_not_reuse_conclusions(self):
        changed=copy.deepcopy(self.third);changed['status']='blocked'
        self.assertTrue(all(x['state']=='unresolved' for x in a.analyze(changed,self.fourth)['impacts']))
        changed=copy.deepcopy(self.fourth);changed['state']['system_facts'][0]['values']['provider_role']='unknown'
        state=a.analyze(self.third,changed)
        self.assertEqual(next(x for x in state['impacts'] if x['id']=='IMPACT-AI-001-50-2')['state'],'unresolved')
    def test_stable_ids_under_reordering(self):
        changed=copy.deepcopy(self.fourth)
        for field in ('system_facts','incident_evidence','calendar_records'): changed['state'][field].reverse()
        first=a.analyze(self.third,self.fourth);second=a.analyze(self.third,changed)
        self.assertEqual(first,second)
    def test_no_invented_dates_approvals_or_sent_requests(self):
        fifth={'state':a.analyze(self.third,self.fourth)}
        state=a.actions(fifth,self.fourth,'test-run',self.versions)
        calendar={x['values']['action_id']:x['values'] for x in self.fourth['state']['calendar_records']}
        for action in state['proposed_actions']:
            self.assertEqual(action['approval_status'],'pending')
            self.assertEqual(action['execution_status'],'not-executed')
            if 'source_action_id' in action: self.assertEqual(action['proposed_due_date'],calendar[action['source_action_id']]['due_date'])
            else: self.assertIsNone(action['proposed_due_date'])
        self.assertEqual(len([x for x in state['review_requests'] if x['id'].startswith('REQUEST-SYSTEM-')]),8)
        self.assertTrue(all(x['delivery_status']=='not-sent' and x['feedback_status']=='not-received' for x in state['review_requests']))
        self.assertEqual(state['feedback'],[])
        shared=next(x for x in state['proposed_actions'] if x.get('source_action_id')=='ACT-008')
        self.assertEqual(len({x.split('-')[2] for x in shared['impact_ids']}),8)
        changed=copy.deepcopy(self.fourth);changed['state']['calendar_records'][0]['values']['due_date']='not-a-date'
        actions=a.actions(fifth,changed,'test-run',self.versions)['proposed_actions']
        self.assertIsNone(next(x for x in actions if x.get('source_action_id')=='ACT-001')['proposed_due_date'])
    def test_unknown_output_requires_clarification_without_no_impact(self):
        for output in ('unrecognised-output-kind', '', None):
            with self.subTest(output=output):
                changed=copy.deepcopy(self.fourth)
                fact=next(x for x in changed['state']['system_facts'] if x['values']['system_id']=='AI-003')
                fact['values']['output_type']=output
                before=copy.deepcopy(changed)
                impacts=a.analyze(self.third,changed)['impacts']
                affected=[x for x in impacts if x['system_id']=='AI-003' and x['id'].removeprefix('IMPACT-AI-003-') in a.OUTPUT_DEPENDENT_RULES]
                self.assertEqual(len(affected),7)
                for impact in affected:
                    self.assertEqual(impact['state'],'unresolved')
                    self.assertIn('must clarify',impact['reason'])
                    self.assertEqual(impact['reported_facts']['output_type'],output)
                    self.assertEqual(impact['approval_status'],'pending')
                self.assertEqual(changed,before)

    def test_unknown_reviewer_remains_unassigned_pending_and_unsent(self):
        fifth={'state':a.analyze(self.third,self.fourth)}
        for reviewer in ('unrecognised-reviewer', '', None):
            with self.subTest(reviewer=reviewer):
                changed=copy.deepcopy(self.fourth)
                row=next(x for x in changed['state']['calendar_records'] if x['values']['action_id']=='ACT-001')
                row['values']['approval_required']=reviewer
                before=copy.deepcopy(changed)
                state=a.actions(fifth,changed,'test-run',self.versions)
                action=next(x for x in state['proposed_actions'] if x.get('source_action_id')=='ACT-001')
                request=next(x for x in state['review_requests'] if x.get('subject_action')==action['id'])
                approval=next(x for x in state['approval_requirements'] if x['id']=='APPROVAL-'+action['id'])
                for record in (action,request,approval):
                    self.assertEqual(record['state'],'unresolved')
                    self.assertEqual(record['reported_approval_required'],reviewer)
                    self.assertEqual(record['reviewer_status'],'unresolved')
                    self.assertIn('no reviewer assigned',record['resolution_need'])
                self.assertIsNone(request['required_reviewer'])
                self.assertIsNone(approval['required_reviewer'])
                self.assertIn('Clarify',request['question'])
                self.assertEqual(approval['status'],'pending')
                self.assertEqual(action['approval_status'],'pending')
                self.assertEqual(request['delivery_status'],'not-sent')
                self.assertEqual(state['feedback'],[])
                self.assertEqual(changed,before)

    def test_schema_chain_replay_and_tampering(self):
        self.assertTrue(a.build(self.out)['semantic_replay_valid'])
        path=self.out/'snapshots'/a.FILES[5];baseline=path.read_bytes()
        mutations=[lambda v:v.update(status='complete'),lambda v:v['state']['proposed_actions'][0].update(proposed_due_date='2026-09-01'),
            lambda v:v['state']['approval_requirements'][0].update(status='approved'),
            lambda v:v['state']['review_requests'][0].update(delivery_status='sent'),
            lambda v:v['state']['proposed_actions'][0]['evidence_ids'].append('UNKNOWN'),
            lambda v:v['predecessor'].update(sha256='sha256:'+'0'*64)]
        for mutate in mutations:
            value=a.c.load(path);mutate(value);a.c.save(path,value)
            with self.assertRaises(ValueError): a.validate(self.out)
            path.write_bytes(baseline)
        with self.assertRaises(ValueError): a.build(self.out)
        self.assertFalse((self.out/'snapshots/07-publication-validation.json').exists())

if __name__=='__main__': unittest.main()
