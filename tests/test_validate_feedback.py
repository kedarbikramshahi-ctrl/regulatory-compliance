"""SYNTHETIC reviewer responses/attestations only; never actual review evidence."""
import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'regulatory-change-impact-brief/scripts'))
import validate_feedback as f

class FeedbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace=tempfile.TemporaryDirectory()
        cls.bundle=Path(cls.workspace.name)/'bundle';cls.bundle.mkdir()
        for name in ('sources','snapshots'): shutil.copytree(ROOT/'deliverables'/name,cls.bundle/name)
        for name in ('source-manifest.json',*f.p.ARTIFACTS): shutil.copy2(ROOT/'deliverables'/name,cls.bundle/name)
        cls.baseline={str(x.relative_to(cls.bundle)):f.c.digest(x.read_bytes()) for x in cls.bundle.rglob('*') if x.is_file()}
    @classmethod
    def tearDownClass(cls): cls.workspace.cleanup()
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.directory=Path(self.temp.name)
        self.request=f.c.load(self.bundle/'snapshots'/f.p.FILES[5])['state']['review_requests'][0]
        self.binding=f.c.load(self.bundle/'snapshots'/f.p.FILES[6])['state']['review_request_bindings'][0]
        self.response=dict(response_id='SYNTHETIC-RESPONSE-001',request_id=self.request['request_id'],
            reviewer=dict(identity_id='synthetic-reviewer',display_name='SYNTHETIC TEST REVIEWER',role=self.request['required_reviewer']),
            run_id=self.request['run_id'],subject=dict(system_id=self.request['subject_system'],
                impact_ids=self.request['subject_impacts'],action_id=self.request['subject_action']),
            source_versions=copy.deepcopy(self.request['source_versions']),drafts=copy.deepcopy(self.binding['drafts']),
            response_time=datetime.now(timezone.utc).isoformat(),outcome='approve',
            reasons=['SYNTHETIC fixture reason; not a legal decision'],conditions=['SYNTHETIC fixture condition'],
            verification_channel_evidence=dict(channel='facilitator-verified',locator='synthetic://fixture/receipt'))
        self.input=self.directory/'responses.json';self.verification=self.directory/'verification.json'
    def tearDown(self):
        self.assertEqual(self.baseline,{str(x.relative_to(self.bundle)):f.c.digest(x.read_bytes()) for x in self.bundle.rglob('*') if x.is_file()})
        self.temp.cleanup()
    def prepare(self):
        payload=dict(format_version=1,synthetic=True,responses=[self.response])
        self.input.write_text(json.dumps(payload),encoding='utf-8')
        attestation=dict(response_id=self.response['response_id'],request_id=self.response['request_id'],run_id=self.response['run_id'],
            reviewer=self.response['reviewer'],response_sha256=f.response_digest(self.response),channel='facilitator-verified',
            verified_by=dict(identity_id='synthetic-facilitator',role='Facilitator'),
            verified_at=datetime.now(timezone.utc).isoformat(),verification_evidence=[dict(locator='synthetic://fixture/receipt')])
        self.verification.write_text(json.dumps(dict(format_version=1,response_file_sha256=f.c.digest(self.input.read_bytes()),
            attestations=[attestation])),encoding='utf-8')
        return f.c.digest(self.verification.read_bytes())
    def intake(self,pin=None,verification=True):
        return f.intake(self.input,self.bundle,self.directory/'reports',self.verification if verification else None,pin)
    def test_matching_synthetic_receipt_preserved_without_applying_approval(self):
        pin=self.prepare();report=self.intake(pin)
        self.assertEqual(report['state'],'test-only')
        entry=report['responses'][0]
        self.assertEqual(entry['binding_status'],'matched');self.assertEqual(entry['verification_status'],'human-pinned-attestation-matched')
        self.assertFalse(entry['decisions_applied']);self.assertFalse(report['decisions_applied'])
        self.assertEqual(entry['response'],self.response)
        self.assertEqual(entry['expected_binding'],self.binding)
        self.assertEqual(report['bundle_basis']['snapshots/'+f.p.FILES[6]],f.c.digest((self.bundle/'snapshots'/f.p.FILES[6]).read_bytes()))
        receipt=Path(report['report_path']).parent
        self.assertEqual((receipt/'response-input.json').read_bytes(),self.input.read_bytes())
        self.assertEqual((receipt/'verification-input.json').read_bytes(),self.verification.read_bytes())
        self.assertTrue(all(value is False for value in report['safeguards'].values()))
        self.assertIn('not-sent',entry['delivery_note'])
        self.assertEqual(f.parse((receipt/'validation-report.json').read_bytes())['state'],'test-only')
    def test_name_verified_flag_and_unpinned_attestation_do_not_authenticate(self):
        self.response['verified']=True;self.prepare()
        for verification in (False,True):
            with self.subTest(verification=verification):
                result=self.intake(verification=verification)
                self.assertEqual(result['state'],'unresolved')
                self.assertEqual(result['responses'][0]['verification_status'],'unresolved')
    def test_wrong_pin_and_changed_response_rejected(self):
        pin=self.prepare()
        self.assertEqual(self.intake('sha256:'+'0'*64)['state'],'unresolved')
        payload=f.parse(self.input.read_bytes());payload['responses'][0]['conditions']=['Changed after attestation']
        self.input.write_text(json.dumps(payload),encoding='utf-8')
        self.assertEqual(self.intake(pin)['state'],'unresolved')
    def test_all_binding_fields_and_duplicate_paths_rejected(self):
        mutations=[lambda x:x.update(request_id='unknown'),lambda x:x.update(run_id='stale-run'),
            lambda x:x['subject'].update(system_id='OTHER'),lambda x:x['subject'].update(action_id='OTHER'),
            lambda x:x['subject'].update(impact_ids=['OTHER']),lambda x:x['source_versions'][0].update(retrieved_at='stale'),
            lambda x:x['source_versions'][0].update(content_hash='sha256:'+'0'*64),
            lambda x:x['source_versions'][0].update(version_metadata={'changed':True}),
            lambda x:x['drafts'][0].update(path='OTHER.csv'),lambda x:x['drafts'][0].update(sha256='sha256:'+'0'*64),
            lambda x:x['drafts'].pop(),lambda x:x['drafts'].append(copy.deepcopy(x['drafts'][0])),
            lambda x:x['source_versions'].append(copy.deepcopy(x['source_versions'][0]))]
        baseline=copy.deepcopy(self.response)
        for mutate in mutations:
            self.response=copy.deepcopy(baseline);mutate(self.response);pin=self.prepare()
            with self.subTest(response=self.response['request_id']):
                result=self.intake(pin);self.assertEqual(result['state'],'unresolved')
                self.assertEqual(result['responses'][0]['binding_status'],'unresolved')
    def test_wrong_reviewer_identity_role_or_channel_not_accepted(self):
        pin=self.prepare();payload=f.parse(self.verification.read_bytes());baseline=copy.deepcopy(payload)
        for key,value in [('identity_id','imposter'),('display_name','other'),('role','Operations')]:
            payload=copy.deepcopy(baseline);payload['attestations'][0]['reviewer'][key]=value
            self.verification.write_text(json.dumps(payload),encoding='utf-8')
            self.assertEqual(self.intake(f.c.digest(self.verification.read_bytes()))['state'],'unresolved')
        self.response['reviewer']['role']='unassigned';pin=self.prepare()
        self.assertEqual(self.intake(pin)['state'],'unresolved')
        self.response['verification_channel_evidence']['channel']='self-declared';pin=self.prepare()
        self.assertEqual(self.intake(pin)['state'],'unresolved')
    def test_missing_fields_invalid_values_and_times_are_unresolved(self):
        baseline=copy.deepcopy(self.response)
        for field in ('reviewer','response_time','reasons','conditions','verification_channel_evidence','drafts','source_versions','subject'):
            self.response=copy.deepcopy(baseline);self.response.pop(field)
            self.input.write_text(json.dumps(dict(format_version=1,synthetic=True,responses=[self.response])),encoding='utf-8')
            self.assertEqual(self.intake(verification=False)['state'],'unresolved')
        for field,value in [('outcome',[]),('response_time','2026-10-12'),('response_time','1900-01-01T00:00:00Z'),
                            ('response_time','2999-01-01T00:00:00Z'),('conditions','not a list'),('reviewer',[])]:
            self.response=copy.deepcopy(baseline);self.response[field]=value
            self.input.write_text(json.dumps(dict(format_version=1,synthetic=True,responses=[self.response])),encoding='utf-8')
            self.assertEqual(self.intake(verification=False)['state'],'unresolved')
    def test_ambiguous_responses_and_attestations_are_unresolved(self):
        pin=self.prepare();payload=f.parse(self.input.read_bytes());payload['responses'].append(copy.deepcopy(self.response))
        self.input.write_text(json.dumps(payload),encoding='utf-8');result=self.intake(verification=False)
        self.assertTrue(all(x['state']=='unresolved' for x in result['responses']))
        pin=self.prepare();payload=f.parse(self.verification.read_bytes());payload['attestations'].append(copy.deepcopy(payload['attestations'][0]))
        self.verification.write_text(json.dumps(payload),encoding='utf-8')
        self.assertEqual(self.intake(f.c.digest(self.verification.read_bytes()))['state'],'unresolved')
    def test_malformed_or_missing_file_reported_and_original_bytes_preserved(self):
        for raw in (b'{invalid',b'{"format_version":1,"format_version":1}',b'[]',b'\xff'):
            self.input.write_bytes(raw);result=self.intake(verification=False)
            self.assertEqual(result['state'],'unresolved')
            self.assertEqual((Path(result['report_path']).parent/'response-input.json').read_bytes(),raw)
        self.input.unlink();result=self.intake(verification=False)
        self.assertEqual(result['state'],'unresolved');self.assertIsNone(result['inputs']['response']['sha256'])
    def test_invalid_bundle_and_stale_actual_draft_detected(self):
        pin=self.prepare();path=self.bundle/'compliance-brief.md';before=path.read_bytes()
        try:
            path.write_bytes(before+b'tamper')
            result=self.intake(pin);self.assertEqual(result['state'],'unresolved')
            self.assertTrue(any('Bundle unavailable/invalid' in x for x in result['issues']))
        finally: path.write_bytes(before)
    def test_repeated_intakes_never_overwrite_and_protected_output_refused(self):
        pin=self.prepare();one=self.intake(pin);bytes_before=Path(one['report_path']).read_bytes();two=self.intake(pin)
        self.assertNotEqual(one['report_path'],two['report_path'])
        self.assertEqual(Path(one['report_path']).read_bytes(),bytes_before)
        with self.assertRaises(ValueError): f.intake(self.input,self.bundle,self.bundle/'feedback',self.verification,pin)
    def test_attestation_missing_or_changed_proof_fields_stays_unverified(self):
        self.prepare();baseline=f.parse(self.verification.read_bytes())
        mutations=[lambda x:x.pop('reviewer'),lambda x:x.update(response_sha256='sha256:'+'0'*64),
            lambda x:x.update(request_id='OTHER'),lambda x:x.update(run_id='OTHER'),
            lambda x:x.update(channel='self-declared'),lambda x:x.update(verified_by={'identity_id':'x','role':'Reviewer'}),
            lambda x:x.update(verified_at='1900-01-01T00:00:00Z'),lambda x:x.update(verified_at='2999-01-01T00:00:00Z'),
            lambda x:x.update(verification_evidence=[]),lambda x:x.update(verification_evidence=7)]
        for mutate in mutations:
            payload=copy.deepcopy(baseline);mutate(payload['attestations'][0])
            self.verification.write_text(json.dumps(payload),encoding='utf-8')
            result=self.intake(f.c.digest(self.verification.read_bytes()))
            self.assertEqual(result['state'],'unresolved');self.assertEqual(result['responses'][0]['verification_status'],'unresolved')
    def test_binding_record_order_can_change_without_guessing_values(self):
        self.response['drafts'].reverse();self.response['source_versions'].reverse()
        pin=self.prepare();result=self.intake(pin)
        self.assertEqual(result['state'],'test-only');self.assertEqual(result['responses'][0]['binding_status'],'matched')
    def test_cli_reports_unresolved_with_nonzero_exit(self):
        self.prepare()
        result=subprocess.run([sys.executable,'-B',str(ROOT/'regulatory-change-impact-brief/scripts/validate_feedback.py'),
            '--responses',str(self.input),'--bundle',str(self.bundle),'--report-root',str(self.directory/'cli')],capture_output=True,text=True)
        self.assertEqual(result.returncode,2);self.assertEqual(json.loads(result.stdout)['state'],'unresolved')

if __name__=='__main__': unittest.main()
