"""Generate only temporary copies to guard current workflow status and human boundaries."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'regulatory-change-impact-brief/scripts'))
import publish_drafts as p

class WorkflowStatusTests(unittest.TestCase):
    def test_generated_decisions_describe_implemented_workflow_and_pending_review(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'bundle';out.mkdir()
            shutil.copytree(ROOT/'deliverables/sources',out/'sources')
            (out/'snapshots').mkdir()
            for name in p.FILES[:2]:
                shutil.copy2(ROOT/'deliverables/snapshots'/name,out/'snapshots'/name)
            shutil.copy2(ROOT/'deliverables/source-manifest.json',out/'source-manifest.json')
            p.a.r.build(out)
            p.a.build(out)
            p.build(out)
            snapshots=[p.c.load(out/'snapshots'/name) for name in p.FILES]
            for snapshot in snapshots[2:]:
                with self.subTest(stage=snapshot['sequence']):
                    effect=snapshot['decisions'][0]['downstream_effect']
                    for safeguard in ('POLICY', 'unresolved', 'legal interpretation', 'approvals pending', 'publication blocked'):
                        self.assertIn(safeguard,effect)
                    # Catch obsolete implementation claims anywhere in generated records.
                    text=json.dumps(snapshot).lower()
                    self.assertNotRegex(text,r'(?:stages?\s*0?[5-7](?:[-–]0?[5-7])?|final (?:artifacts|deliverables)|(?:full )?workflow/recovery)[^.]*?(?:unimplemented|not implemented|remain required)')
                    self.assertNotIn('not a completed compliance assessment or fresh full run',text)
            self.assertIn('Stages 05-07 use',snapshots[2]['decisions'][0]['downstream_effect'])
            self.assertIn('Stage 07 generates and validates',snapshots[4]['decisions'][0]['downstream_effect'])
            final=snapshots[6]['decisions'][0]['downstream_effect']
            for capability in ('fresh retrieval','all seven stages','run history','journalled recovery'):
                self.assertIn(capability,final)
            fourth=snapshots[3]['state'];sixth=snapshots[5]['state'];seventh=snapshots[6]['state']
            self.assertEqual(fourth['policy_status'],'unresolved')
            self.assertEqual(fourth['interpretation_status'],'human review pending')
            self.assertTrue(all(x['status']=='pending' for x in sixth['approval_requirements']))
            self.assertTrue(all(x['delivery_status']=='not-sent' for x in sixth['review_requests']))
            self.assertEqual(seventh['publication_status'],'blocked')
            self.assertEqual(seventh['human_approval'],'pending')
            self.assertFalse(seventh['external_publication'])
            self.assertTrue(p.validate(out)['all_seven_run_ids_match'])

if __name__=='__main__': unittest.main()
