import copy
import tempfile
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker, ValidationError
import review

class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.data = review.read_json(review.ROOT/'sample-data/review.json')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
    def generate(self):
        return review.build(review.ROOT/'sample-data/review.json', Path(self.temp.name))
    def test_missing_and_conflicting_evidence(self):
        gaps, conflicts = review.analyze(self.data)
        self.assertEqual(len(gaps), 2)
        self.assertEqual(len(conflicts), 1)
    def test_complete_consistent_evidence(self):
        self.data['records'][1]['notice_enabled'] = True
        self.data['evidence'] = [dict(id='E-'+kind, system_id='DEMO-001', kind=kind,
                                    status='available', content='Fictional content')
                                 for kind in self.data['required_evidence']]
        self.assertEqual(review.analyze(self.data), ([], []))
    def test_seven_stages_pending_approvals_and_preserved_runs(self):
        first, second = self.generate(), self.generate()
        self.assertNotEqual(first, second)
        self.assertEqual(review.validate_run(first)['snapshots_validated'], 7)
        actions = review.read_json(first/'06-actions-and-approvals.json')['state']
        self.assertTrue(all(a['status']=='pending' for a in actions['approval_requirements']))
        self.assertTrue(all(a['approved_date'] is None and not a['activation_allowed'] for a in actions['proposed_actions']))
        report = (first/'review-report.md').read_text(encoding='utf-8')
        for action in actions['proposed_actions']:
            self.assertIn(action['id'], report)
            self.assertIn(action['summary'], report)
    def test_schema_rejects_missing_fields_and_bad_dates(self):
        directory = self.generate()
        snap = review.read_json(directory/'01-scope.json')
        validator = Draft202012Validator(review.read_json(review.ROOT/'snapshot.schema.json'), format_checker=FormatChecker())
        invalid = copy.deepcopy(snap)
        del invalid['run_id']
        with self.assertRaises(ValidationError): validator.validate(invalid)
        invalid = copy.deepcopy(snap)
        invalid['created_at'] = 'yesterday'
        with self.assertRaises(ValidationError): validator.validate(invalid)
    def test_predecessor_tampering(self):
        directory = self.generate()
        with (directory/'01-scope.json').open('a', encoding='utf-8') as handle: handle.write(' ')
        with self.assertRaisesRegex(ValueError, 'Predecessor'): review.validate_run(directory)
    def test_report_tampering(self):
        directory = self.generate()
        (directory/'review-report.md').write_text('Changed', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Artifact hash'): review.validate_run(directory)
    def test_publication_and_reference_controls(self):
        directory = self.generate()
        path = directory/'07-publication-validation.json'
        snap = review.read_json(path)
        snap['state']['publication_status'] = 'validated'
        review.write_json(path, snap)
        with self.assertRaisesRegex(ValueError, 'Final publication'): review.validate_run(directory)
        snap['state']['publication_status'] = 'blocked'
        snap['unresolved'][0]['evidence_ids'] = ['DOES-NOT-EXIST']
        review.write_json(path, snap)
        with self.assertRaisesRegex(ValueError, 'Evidence reference'): review.validate_run(directory)
    def test_reject_real_data_and_duplicate_ids(self):
        self.data['fictional'] = False
        with self.assertRaises(ValueError): review.analyze(self.data)
        self.data['fictional'] = True
        self.data['records'][1]['id'] = self.data['records'][0]['id']
        with self.assertRaises(ValueError): review.analyze(self.data)

if __name__ == '__main__': unittest.main()
