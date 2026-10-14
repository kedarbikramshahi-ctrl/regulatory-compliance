"""Continue captured stages 01-04 into review-only impacts and proposed actions."""
import argparse
import sys
from datetime import date
from pathlib import Path
from uuid import uuid4
from jsonschema import Draft202012Validator, FormatChecker
sys.path.insert(0,str(Path(__file__).resolve().parent))
import reconcile_evidence as r
c=r.c
FILES=r.FILES+['05-impact-analysis.json','06-actions-and-approvals.json']
KNOWN_OUTPUT_TYPES={'direct_interaction','text','synthetic_image','synthetic_audio_video','classification'}
OUTPUT_DEPENDENT_RULES={'50-1','50-2','50-3','50-4-image','50-4-text','50-5','111-4'}

def analyze(third,fourth):
    impacts=[]
    rules=r.records(third)
    authority_blocked=third['status']=='blocked'
    for fact in sorted(fourth['state']['system_facts'],key=lambda x:x['id']):
        v=fact['values']; sid=v['system_id']
        evidence=sorted([x for x in fourth['state']['incident_evidence'] if x['values']['system_id']==sid],key=lambda x:x['id'])
        basis=[fact['id']]+[x['id'] for x in evidence]
        output=v['output_type']; role=v['provider_role']
        # These are bounded register-based screening observations, never compliance determinations.
        cases=[
            ('50-1','RULE-50-1','Direct-interaction provider notice',
             'supported-no-impact' if role=='no' and output!='direct_interaction' else 'unresolved',
             'Provider role is reported no and output is not direct interaction.' if role=='no' and output!='direct_interaction' else 'Verify provider responsibility, direct interaction and the obviousness/other exceptions; deployer=yes alone does not establish provider duty.'),
            ('50-2','RULE-50-2','Provider machine-readable marking',
             'supported-no-impact' if role=='no' else 'unresolved',
             'Register reports provider=no; this is bounded actor-role screening, not verification of vendor marking.' if role=='no' else 'Provider role and synthetic generation facts require confirmation; visible notice is not machine-readable marking.'),
            ('50-3','RULE-50-3','Emotion recognition/biometric categorisation', 'unresolved',
             'Classification, assessment use and human adjudication do not establish emotion recognition or biometric categorisation; verify actual functionality.'),
            ('50-4-image','RULE-50-4','Deployer deep-fake disclosure',
             'unresolved' if output in {'synthetic_image','synthetic_audio_video'} else 'supported-no-impact',
             'Synthetic output alone does not establish the deep-fake definition; verify real-person/event resemblance and specific exceptions.' if output in {'synthetic_image','synthetic_audio_video'} else 'The captured output description does not report image/audio/video generation; bounded screening only.'),
            ('50-4-text','RULE-50-4','Public-interest text disclosure',
             'supported-no-impact' if output=='text' and v['exposed_group'] in {'staff','applicants'} else 'unresolved',
             'Recorded use is internal staff notes or individual applicant replies, not reported public-interest publication; reassess if actual publication differs.' if output=='text' and v['exposed_group'] in {'staff','applicants'} else 'Verify text generation, publication, public-interest purpose and substantive editorial responsibility; human_review labels alone do not establish exemption.'),
            ('50-5','RULE-50-5','Notice timing, clarity and accessibility','unresolved',
             'Verify first-interaction/exposure timing, clarity and accessibility only after applicable paragraph/actor scope is established.'),
            ('50-6','RULE-50-6','Other obligations preserved','unresolved',
             'Article 50 screening does not settle Chapter III or other transparency obligations; Legal must confirm review boundary.'),
            ('50-7','RULE-50-7','Codes-of-practice context','supported-no-impact',
             'Captured paragraph addresses Commission code mechanisms; no standalone company conformity finding is made from that paragraph.'),
            ('111-4','TIMING-50-2-TRANSITION','Conditional provider transition','unresolved',
             'Do not grant a blanket delay: provider/synthetic-output facts and pre-2026-08-02 placing-on-market date must be established.'),
            ('POLICY','GAP-POLICY','Internal policy controls','unresolved',
             'POLICY is inaccessible; no requirements, exceptions or controls can be inferred.')]
        for key,rule,title,state,reason in cases:
            refs=basis+[rule] if rule in rules or rule=='GAP-POLICY' else basis
            if key in {'50-1','50-5'} and output=='direct_interaction':
                if v['evidence_status']=='conflicting' or any(x['values']['evidence_state']=='conflicting' for x in evidence):
                    state='conflicting'; reason='Opposing notice claims remain unresolved; preserve register and incident statements without choosing a winner.'
                elif v['current_notice']=='no':
                    state='supported-impact'; reason='Registers support a notice-remediation review need; this is not a finding of legal breach or established provider liability.'
            if key=='50-2' and any(x['values']['evidence_state']=='conflicting' for x in evidence) and isinstance(output,str) and output.startswith('synthetic'):
                state='conflicting'; reason='Visible-label and exported-metadata claims differ in subject; provenance concern needs investigation, not inference of provider liability.'
            if output not in KNOWN_OUTPUT_TYPES and key in OUTPUT_DEPENDENT_RULES:
                state='unresolved'; reason=f'Unrecognized output_type {output!r}; system owner must clarify the actual output/function before paragraph-specific screening.'
            if authority_blocked and key!='POLICY':
                state='unresolved'; reason='Required authority is blocked; dependent formal screening outcome withheld. '+reason
            impacts.append(c.record('IMPACT-'+sid+'-'+key,title+': '+reason,refs,state=state,system_id=sid,
                rule_ref='Internal POLICY' if key=='POLICY' else rule,owner=v.get('owner') or None,
                reason=reason,scope='Provisional register-based review preparation; no compliance or final applicability conclusion',
                reported_facts=v,reported_evidence=[x['values'] for x in evidence],
                resolution_need='Legal confirms scope/interpretation; system owner verifies facts and supporting artifacts',approval_status='pending'))
    return dict(review_date=c.REVIEW_DATE,impacts=impacts,unaffected_items=[],conflicts=fourth['state']['conflicts'],
        unresolved_items=fourth['state']['evidence_gaps']+third['state']['authority_blockers'],
        scope_limitation='All screening outcomes remain subject to missing POLICY, uncaptured supporting artifacts and human interpretation')

def actions(fifth,fourth,run_id,source_versions):
    proposed=[]; requests=[]; approvals=[]
    def add(action,reviewer,question):
        proposed.append(action)
        rid='REQUEST-'+action['id']
        requests.append(c.record(rid,'Unsent review request: '+question,action['evidence_ids']+[action['id']],
            request_id=rid,subject_system=action['system_id'],subject_impacts=action['impact_ids'],subject_action=action['id'],
            run_id=run_id,source_versions=source_versions,required_reviewer=reviewer,question=question,
            delivery_status='not-sent',feedback_status='not-received',final_draft_binding='deferred to stage 07'))
        approvals.append(c.record('APPROVAL-'+action['id'],'Human decision required before '+action['summary'],
            [action['id'],rid],status='pending',required_reviewer=reviewer,run_id=run_id))
    impacts=fifth['state']['impacts']
    for impact in impacts:
        if impact['state']=='supported-no-impact': continue
        aid='PROPOSED-'+impact['id']
        add(c.record(aid,'Verify and resolve '+impact['rule_ref']+' review scope', [impact['id']],
            system_id=impact['system_id'],impact_ids=[impact['id']],owner=impact['owner'],
            proposed_action='Collect supporting facts and seek paragraph-specific Legal review: '+impact['reason'],
            proposed_due_date=None,date_reason='No date disclosed for this proposed action; do not invent or borrow an unrelated deadline',
            approval_status='pending',execution_status='not-executed',
            dependencies=['Authorized POLICY access'] if impact['rule_ref']=='Internal POLICY' else ['Owner supplies referenced evidence','Legal confirms paragraph scope before implementation'],
            operational_effect='Evidence collection and potential draft control changes only; activation remains with Operations'),
            'Legal','Does the cited paragraph apply to this actor/output, and what facts or exception decisions are still needed?')
    for row in sorted(fourth['state']['calendar_records'],key=lambda x:x['id']):
        v=row['values']; sid=v['system_id']; linked=[x['id'] for x in impacts if (sid=='ALL' or x['system_id']==sid) and x['state']!='supported-no-impact']
        due=v['due_date']
        try:
            if date.fromisoformat(due).isoformat()!=due: raise ValueError('Noncanonical date')
        except ValueError: due=None
        reviewer={'legal':'Legal','operations':'Operations'}.get(v['approval_required'])
        add(c.record('PROPOSED-CALENDAR-'+v['action_id'],'Review existing calendar proposal: '+v['action'],[row['id']]+linked,
            system_id=sid,impact_ids=linked,source_action_id=v['action_id'],owner=v.get('owner') or None,
            proposed_action=v['action'],proposed_due_date=due,reported_due_date=v['due_date'],
            date_reason='Exact existing CALENDAR proposal; not approved or changed' if due else 'Source date invalid or missing; verify with Operations',
            reported_status=v['status'],source_version=v['source_version'],approval_status='pending',execution_status='not-executed',
            dependencies=['Verify source proposal and actual approval','Resolve linked evidence gaps'],operational_effect='No calendar write or activation'),
            reviewer,'Is this source proposal still appropriate, and what date/conditions can be approved?' if reviewer else 'Clarify the unrecognized approval_required value before assigning a reviewer or considering approval of this source proposal.')
        if reviewer is None:
            for record in (proposed[-1],requests[-1],approvals[-1]):
                record.update(state='unresolved',reported_approval_required=v['approval_required'],
                    reviewer_status='unresolved',resolution_need='Clarify the source reviewer value with the source owner; no reviewer assigned')
    for sid in sorted({x['system_id'] for x in impacts}):
        ids=[x['id'] for x in impacts if x['system_id']==sid]
        rid='REQUEST-SYSTEM-'+sid
        requests.append(c.record(rid,'Unsent Legal review of all scoped outcomes for '+sid,ids,request_id=rid,
            subject_system=sid,subject_impacts=ids,subject_action=None,run_id=run_id,source_versions=source_versions,
            required_reviewer='Legal',question='Confirm or revise every paragraph-specific screening outcome, including bounded no-impact findings, actor roles, exceptions and transition eligibility.',
            delivery_status='not-sent',feedback_status='not-received',final_draft_binding='deferred to stage 07'))
    return dict(review_date=c.REVIEW_DATE,proposed_actions=proposed,approval_requirements=approvals,
        escalations=fifth['state']['unresolved_items'],review_requests=requests,feedback=[],policy_status='unresolved',
        legal_decisions_applied=False,operations_activation=False)

def snapshot(directory,sequence,state,upstream):
    previous=c.load(directory/'snapshots'/FILES[sequence-2]); path=FILES[sequence-2]
    value=c.snapshot(previous['run_id'],sequence,state,[],consumed=sorted(upstream),
        predecessor=dict(snapshot_id=previous['snapshot_id'],path='snapshots/'+path,sha256=c.digest((directory/'snapshots'/path).read_bytes())),status='partial')
    value.update(stage='impact-analysis' if sequence==5 else 'actions-and-approvals',snapshot_id=previous['run_id']+'-'+str(sequence)+'-'+uuid4().hex)
    value['unresolved']=state['unresolved_items'] if sequence==5 else state['escalations']
    value['decisions']=[c.record('DECISION-MILESTONE3-'+str(sequence),'Use bounded screening and unsent human requests',sorted(upstream),
        concern='Missing evidence, authority limitations and unverified approvals',options=['Infer compliance and dates','Preserve scoped proposals for human review'],
        chosen_behavior='Preserve scoped proposals',rationale='Register claims do not establish compliance; source dates are proposals only',
        tradeoffs=['More unresolved review work; no invented decisions or deadlines'],downstream_effect='Stage 07 generates and validates the CSV, compliance brief and tentative calendar, binding unsent review requests to exact draft paths and hashes; POLICY remains unresolved, legal interpretation and approvals pending, and publication blocked while required evidence is missing')]
    value['produced_record_ids']=sorted(r.records(value))
    return value

def basis(directory):
    third=c.load(directory/'snapshots'/FILES[2]); fourth=c.load(directory/'snapshots'/FILES[3])
    versions=[dict(source_id=s['id'],retrieved_at=s['retrieved_at'],version_metadata=s['version_metadata'],content_hash=s['content_hash'])
        for s in c.load(directory/'snapshots'/FILES[1])['state']['sources']]
    return third,fourth,versions

def validate(directory, allow_later=False):
    r.validate(directory,allow_later=True)
    upstream={}; validator=Draft202012Validator(c.load(c.ROOT/'snapshot.schema.json'),format_checker=FormatChecker())
    for index,name in enumerate(FILES):
        value=c.load(directory/'snapshots'/name); validator.validate(value)
        current=r.records(value)
        if value['sequence']!=index+1 or value['run_id']!=c.load(directory/'snapshots'/FILES[0])['run_id']: raise ValueError('Stage/run mismatch')
        if set(value['produced_record_ids'])!=set(current) or not set(value['consumed_record_ids'])<=set(upstream): raise ValueError('Record inventory mismatch')
        for record in current.values():
            if not set(record['evidence_ids'])<=set(upstream)|set(current): raise ValueError('Unknown evidence reference')
        if index>=4:
            prev=c.load(directory/'snapshots'/FILES[index-1])
            if value['predecessor']!=dict(snapshot_id=prev['snapshot_id'],path='snapshots/'+FILES[index-1],sha256=c.digest((directory/'snapshots'/FILES[index-1]).read_bytes())): raise ValueError('Predecessor mismatch')
            if value['status']!='partial': raise ValueError('Unsupported completion status')
        upstream.update(current)
    third,fourth,versions=basis(directory); fifth=c.load(directory/'snapshots'/FILES[4]); sixth=c.load(directory/'snapshots'/FILES[5])
    if fifth['state']!=analyze(third,fourth): raise ValueError('Impact state does not match evidence')
    if sixth['state']!=actions(fifth,fourth,fifth['run_id'],versions): raise ValueError('Action/request state does not match evidence')
    if not allow_later and (directory/'snapshots/07-publication-validation.json').exists(): raise ValueError('Milestone 3 stops at stage 06')
    return dict(run_id=fifth['run_id'],stages_validated=[1,2,3,4,5,6],schema_valid=True,evidence_references_valid=True,
        predecessor_hashes_valid=True,semantic_replay_valid=True,assessment_complete=False,stage05_status='partial',stage06_status='partial')

def build(directory):
    r.validate(directory)
    if any((directory/'snapshots'/f).exists() for f in FILES[4:]): raise ValueError('Existing stages not overwritten')
    third,fourth,versions=basis(directory); upstream={}
    for name in FILES[:4]: upstream.update(r.records(c.load(directory/'snapshots'/name)))
    fifth=snapshot(directory,5,analyze(third,fourth),upstream); c.save(directory/'snapshots'/FILES[4],fifth)
    upstream.update(r.records(fifth))
    sixth=snapshot(directory,6,actions(fifth,fourth,fifth['run_id'],versions),upstream); c.save(directory/'snapshots'/FILES[5],sixth)
    result=validate(directory); c.save(directory/'milestone-3-validation.json',result); return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=c.ROOT/'deliverables');p.add_argument('--validate',action='store_true');args=p.parse_args()
    try: result=validate(args.output) if args.validate else build(args.output)
    except Exception as error:
        c.save(args.output/'milestone-3-failure.json',dict(created_at=c.now(),stage='05-06',error=str(error),owner='Learner',resolution_need='Inspect retained boundaries; no overwrite or fabricated recovery'))
        raise
    print(__import__('json').dumps(result,indent=2))

if __name__=='__main__': main()
