"""Validate explicitly supplied feedback against immutable drafts; never apply decisions."""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from jsonschema import FormatChecker
sys.path.insert(0,str(Path(__file__).resolve().parent))
import publish_drafts as p
c=p.c
OUTCOMES={'approve','reject','request-changes','comment'}
HASH=re.compile(r'^sha256:[0-9a-f]{64}$')


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)


def response_digest(value):
    return c.digest(canonical(value).encode('utf-8'))


def parse(data):
    def pairs(items):
        value={}
        for key,item in items:
            if key in value: raise ValueError('Duplicate JSON key: '+key)
            value[key]=item
        return value
    return json.loads(data.decode('utf-8-sig'),object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Invalid JSON constant: '+value)))


def text(value):
    return isinstance(value,str) and bool(value.strip())


def timestamp(value):
    if not isinstance(value,str) or not FormatChecker().conforms(value,'date-time'):
        raise ValueError('Expected RFC 3339 timestamp with timezone')
    return datetime.fromisoformat(value.replace('Z','+00:00'))


def indexed(value,key):
    if not isinstance(value,list) or any(not isinstance(x,dict) or not text(x.get(key)) for x in value):
        raise ValueError('Expected list of records with '+key)
    result={x[key]:x for x in value}
    if len(result)!=len(value): raise ValueError('Duplicate '+key)
    return result


def same_records(actual,expected,key):
    return canonical(indexed(actual,key))==canonical(indexed(expected,key))


def check_response(response,request,binding,seventh,attestation,trust_error,synthetic):
    issues=[];binding_issues=[];identity_issues=[]
    if not isinstance(response,dict):
        return dict(state='unresolved',binding_status='unresolved',verification_status='unresolved',
                    issues=['Response is not a JSON object'],response=response)
    for field in ('response_id','request_id','run_id','response_time','outcome'):
        if not text(response.get(field)): issues.append('Missing/invalid '+field)
    if not isinstance(response.get('outcome'),str) or response['outcome'] not in OUTCOMES: issues.append('Unknown outcome; clarify without applying a decision')
    for field in ('reasons','conditions'):
        value=response.get(field)
        if not isinstance(value,list) or any(not text(x) for x in value) or (field=='reasons' and not value):
            issues.append('Missing/invalid '+field+'; expected text list (conditions may be empty)')
    reviewer=response.get('reviewer')
    if not isinstance(reviewer,dict) or any(not text(reviewer.get(k)) for k in ('identity_id','display_name','role')):
        identity_issues.append('Reviewer identity_id, display_name and role are required; a name is not authentication')
    else:
        if request and reviewer['role']!=request.get('required_reviewer'):
            identity_issues.append('Reviewer role does not match the required reviewer; no substitute assignment')
    evidence=response.get('verification_channel_evidence')
    if not isinstance(evidence,dict) or not text(evidence.get('channel')) or not text(evidence.get('locator')):
        identity_issues.append('Missing verification-channel evidence; self-declared verified flags are not trusted')
    try:
        when=timestamp(response.get('response_time'))
        if when>datetime.now(timezone.utc): issues.append('Response time is in the future')
        if seventh and when<timestamp(seventh['created_at']): binding_issues.append('Response predates the final draft boundary')
    except (ValueError,TypeError): issues.append('Invalid response_time; use RFC 3339 with timezone')
    if not request or not binding:
        binding_issues.append('Unknown/missing request ID or detached Stage 07 binding')
    else:
        if response.get('run_id')!=binding['run_id']: binding_issues.append('Run ID mismatch/stale response')
        subject=response.get('subject')
        expected=dict(system_id=request['subject_system'],impact_ids=request['subject_impacts'],action_id=request['subject_action'])
        try:
            if not isinstance(subject,dict) or set(subject)!=set(expected): raise ValueError()
            ids=subject['impact_ids']
            if not isinstance(ids,list) or any(not text(x) for x in ids) or len(ids)!=len(set(ids)): raise ValueError()
            normalized=dict(subject,impact_ids=sorted(ids))
            if canonical(normalized)!=canonical(dict(expected,impact_ids=sorted(expected['impact_ids']))): raise ValueError()
        except (ValueError,TypeError): binding_issues.append('Subject system/impacts/action mismatch or missing')
        for field,key,expected_value in [('source_versions','source_id',request['source_versions']),('drafts','path',binding['drafts'])]:
            try:
                if not same_records(response.get(field),expected_value,key): raise ValueError()
                if field=='drafts' and any(not HASH.fullmatch(x.get('sha256','')) for x in response[field]): raise ValueError()
            except (ValueError,TypeError): binding_issues.append(field+' mismatch, stale hashes, missing records or duplicate identifiers')
        if not text(request.get('required_reviewer')):
            identity_issues.append('Required reviewer is unresolved in Stage 06; human clarification required')
    if trust_error:
        identity_issues.append(trust_error)
    elif not isinstance(attestation,dict):
        identity_issues.append('No unique pinned facilitator attestation for this response')
    else:
        for field in ('response_id','request_id','run_id','reviewer'):
            if canonical(attestation.get(field))!=canonical(response.get(field)):
                identity_issues.append('Attestation '+field+' mismatch')
        if attestation.get('response_sha256')!=response_digest(response):
            identity_issues.append('Attestation does not bind the exact response content')
        verified_by=attestation.get('verified_by')
        if not isinstance(verified_by,dict) or not text(verified_by.get('identity_id')) or verified_by.get('role')!='Facilitator':
            identity_issues.append('Facilitator verifier identity/role missing')
        if attestation.get('channel')!='facilitator-verified': identity_issues.append('Unsupported verification channel')
        receipts=attestation.get('verification_evidence')
        if not isinstance(receipts,list) or not receipts or any(not isinstance(x,dict) or not text(x.get('locator')) for x in receipts):
            identity_issues.append('Attestation verification-channel evidence missing')
        if isinstance(evidence,dict) and evidence.get('locator') not in [x.get('locator') for x in (receipts if isinstance(receipts,list) else []) if isinstance(x,dict)]:
            identity_issues.append('Response verification locator not corroborated by attestation')
        if isinstance(evidence,dict) and evidence.get('channel')!=attestation.get('channel'):
            identity_issues.append('Response verification channel mismatch')
        try:
            verified=timestamp(attestation.get('verified_at'))
            if verified<timestamp(response.get('response_time')) or verified>datetime.now(timezone.utc):
                identity_issues.append('Attestation time predates response or is in the future')
        except (ValueError,TypeError): identity_issues.append('Invalid attestation verification time')
    issues+=binding_issues+identity_issues
    return dict(response_id=response.get('response_id'),request_id=response.get('request_id'),
        state='unresolved' if issues else ('test-only' if synthetic else 'validated-for-human-review'),
        binding_status='unresolved' if binding_issues else 'matched',
        verification_status='unresolved' if identity_issues else 'human-pinned-attestation-matched',
        issues=issues,response=response,verification_attestation=attestation,expected_binding=binding,
        authentication_note='Offline matching of a separately human-confirmed attestation hash; no independent login, signature or channel authentication',
        delivery_note='No delivery inferred; Stage 06 request remains '+(request or {}).get('delivery_status','unknown'),
        decisions_applied=False)


def intake(response_file,bundle,report_root=None,verification_file=None,trusted_verification_sha256=None):
    bundle=Path(bundle).resolve();response_file=Path(response_file).resolve()
    report_root=Path(report_root or c.ROOT/'feedback-reports').resolve()
    forbidden=[bundle,(c.ROOT/'interviews').resolve(),(c.ROOT/'.git').resolve(),c.PACKAGE.resolve()]
    if any(report_root==x or x in report_root.parents for x in forbidden):
        raise ValueError('Feedback reports must be separate from bundle, interviews, Git and Skill evidence')
    report=dict(format_version=1,intake_id='feedback-'+uuid4().hex,created_at=c.now(),bundle_path=str(bundle),
        state='unresolved',responses=[],issues=[],synthetic=False,decisions_applied=False,
        safeguards=dict(approvals_changed=False,publication_changed=False,requests_sent=False,external_systems_changed=False),
        trust_boundary='Only an explicitly supplied, separately human-confirmed facilitator attestation hash can match verification evidence; file names and verified flags are not authentication')
    raw=None;verification_raw=None;data=None;verification=None
    try:
        raw=response_file.read_bytes();data=parse(raw)
        if not isinstance(data,dict) or type(data.get('format_version')) is not int or data.get('format_version')!=1 or not isinstance(data.get('responses'),list) or not data['responses']:
            raise ValueError('Expected format_version 1 and a nonempty responses list')
        if 'synthetic' in data and not isinstance(data['synthetic'],bool): raise ValueError('synthetic must be boolean')
        report['synthetic']=data.get('synthetic',False)
    except (OSError,ValueError,UnicodeError) as error: report['issues'].append('Response file unavailable/invalid: '+str(error))
    trust_error='No independently supplied pinned facilitator attestation; response remains unverified'
    if verification_file:
        try:
            verification_raw=Path(verification_file).read_bytes();verification=parse(verification_raw)
            if not isinstance(trusted_verification_sha256,str) or not HASH.fullmatch(trusted_verification_sha256):
                raise ValueError('Explicit trusted-verification SHA-256 pin required from separately confirmed facilitator channel')
            if c.digest(verification_raw)!=trusted_verification_sha256: raise ValueError('Verification file hash does not match trusted pin')
            if not isinstance(verification,dict) or type(verification.get('format_version')) is not int or verification.get('format_version')!=1: raise ValueError('Invalid attestation format')
            if raw is None or verification.get('response_file_sha256')!=c.digest(raw): raise ValueError('Attestation response-file hash mismatch')
            attestations=indexed(verification.get('attestations'),'response_id')
            trust_error=None
        except (OSError,ValueError,UnicodeError) as error: trust_error='Unverified attestation: '+str(error)
    try:
        result=p.validate(bundle);report['bundle_validation']=result
        sixth=c.load(bundle/'snapshots'/p.FILES[5]);seventh=c.load(bundle/'snapshots'/p.FILES[6])
        if sixth['run_id']!=result['run_id'] or seventh['run_id']!=result['run_id']:
            raise ValueError('Bundle changed during intake')
        report['bundle_basis']={name:c.digest((bundle/name).read_bytes()) for name in
            ['snapshots/'+p.FILES[5],'snapshots/'+p.FILES[6],*p.ARTIFACTS]}
        requests=indexed(sixth['state']['review_requests'],'request_id')
        bindings=indexed(seventh['state']['review_request_bindings'],'request_id')
    except Exception as error:
        report['issues'].append('Bundle unavailable/invalid; bindings cannot be trusted: '+str(error))
        requests={};bindings={};seventh=None
    if isinstance(data,dict) and isinstance(data.get('responses'),list):
        counts={}
        for response in data['responses']:
            if isinstance(response,dict) and text(response.get('response_id')):
                counts[response['response_id']]=counts.get(response['response_id'],0)+1
        for response in data['responses']:
            rid=response.get('request_id') if isinstance(response,dict) else None
            rid=rid if isinstance(rid,str) else None
            aid=response.get('response_id') if isinstance(response,dict) else None
            attestation=attestations.get(aid) if not trust_error and isinstance(aid,str) else None
            entry=check_response(response,requests.get(rid),bindings.get(rid),seventh,attestation,trust_error,report['synthetic'])
            if isinstance(aid,str) and counts.get(aid,0)>1: entry['issues'].append('Duplicate response_id; clarify without choosing a response')
            if report['issues'] or entry['issues']: entry['state']='unresolved'
            report['responses'].append(entry)
    for name,expected in report.get('bundle_basis',{}).items():
        try:
            if c.digest((bundle/name).read_bytes())!=expected: raise ValueError('Hash changed')
        except (OSError,ValueError):
            report['issues'].append('Bundle changed during intake: '+name)
    if report['issues']:
        for entry in report['responses']: entry['state']='unresolved'
    if report['responses'] and not report['issues'] and all(x['state']!='unresolved' for x in report['responses']):
        report['state']='test-only' if report['synthetic'] else 'validated-for-human-review'
    report['resolution_need']='Human must confirm provenance and consider any decision separately; no approvals or legal interpretations applied'
    receipt=report_root/report['intake_id'];receipt.mkdir(parents=True,exist_ok=False)
    for name,content in [('response-input.json',raw),('verification-input.json',verification_raw)]:
        if content is not None:
            with (receipt/name).open('xb') as stream: stream.write(content)
    report['inputs']=dict(response=dict(original_path=str(response_file),sha256=c.digest(raw) if raw is not None else None,
        preserved_path='response-input.json' if raw is not None else None),
        verification=dict(original_path=str(verification_file) if verification_file else None,
            sha256=c.digest(verification_raw) if verification_raw is not None else None,
            preserved_path='verification-input.json' if verification_raw is not None else None,
            trusted_pin=trusted_verification_sha256))
    report['report_path']=str(receipt/'validation-report.json')
    with (receipt/'validation-report.json').open('x',encoding='utf-8') as stream:
        json.dump(report,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--responses',type=Path,required=True)
    parser.add_argument('--bundle',type=Path,default=c.ROOT/'deliverables')
    parser.add_argument('--report-root',type=Path,default=c.ROOT/'feedback-reports')
    parser.add_argument('--verification',type=Path)
    parser.add_argument('--trusted-verification-sha256')
    args=parser.parse_args()
    try:
        result=intake(args.responses,args.bundle,args.report_root,args.verification,args.trusted_verification_sha256)
        print(json.dumps(dict(state=result['state'],report_path=result['report_path'],decisions_applied=False),indent=2))
        return 0 if result['state']=='validated-for-human-review' else 2
    except Exception as error:
        print(json.dumps(dict(state='failed',error=str(error),decisions_applied=False)),file=__import__('sys').stderr)
        return 1

if __name__=='__main__': raise SystemExit(main())
