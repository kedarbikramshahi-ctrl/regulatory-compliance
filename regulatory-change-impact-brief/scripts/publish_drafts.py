"""Stage 07: local review-only drafts and detached request bindings. No network."""
import argparse
import csv
import io
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import uuid4
from jsonschema import Draft202012Validator, FormatChecker
sys.path.insert(0,str(Path(__file__).resolve().parent))
import analyze_impacts as a
c=a.c
FILES=a.FILES+['07-publication-validation.json']
ARTIFACTS=['impact-register.csv','compliance-brief.md','action-calendar.ics']
HEADER=['impact_id','system_id','rule_ref','state','evidence_ids','reason','owner','proposed_action','proposed_due_date','approval_status',
        'run_id','review_date','action_ids','action_date_pairs','date_reason','resolution_need','scope']

def inputs(directory):
    snapshots=[c.load(directory/'snapshots'/f) for f in a.FILES]
    upstream={}
    for value in snapshots: upstream.update(a.r.records(value))
    return snapshots,upstream

def publication_state(snapshots):
    # Every authority limitation remains visible; technical consistency cannot clear it.
    return 'blocked' if snapshots[2]['state']['authority_blockers'] else 'validated'

def dated_actions(sixth,blocked):
    # Keep existing calendar review proposals useful while withholding dependent conclusions.
    return [x for x in sixth['state']['proposed_actions'] if x['proposed_due_date']
            and (not blocked or x.get('source_action_id'))]

def register_rows(snapshots,upstream):
    fifth,sixth=snapshots[4:6]; rows=[]
    for impact in fifth['state']['impacts']:
        linked=[x for x in sixth['state']['proposed_actions'] if impact['id'] in x['impact_ids']]
        dates=sorted({x['proposed_due_date'] for x in linked if x['proposed_due_date']})
        # Multiple proposals are not one deadline. Exact action/date pairs remain in the brief/ICS.
        due=dates[0] if len(linked)==1 and len(dates)==1 else ''
        date_reason='One linked existing calendar proposal; pending approval' if due else (
            'Multiple linked actions; no single impact deadline assigned. See exact action/date pairs' if dates else 'No disclosed date for a new proposal')
        rows.append(dict(impact_id=impact['id'],system_id=impact['system_id'],rule_ref=impact['rule_ref'],state=impact['state'],
            evidence_ids=';'.join(impact['evidence_ids']),reason=impact['reason'],owner=impact['owner'] or '',
            proposed_action='\n'.join(x['id']+': '+x['proposed_action'] for x in linked),proposed_due_date=due,approval_status='pending',
            run_id=fifth['run_id'],review_date=c.REVIEW_DATE,action_ids=';'.join(x['id'] for x in linked),
            action_date_pairs=';'.join(x['id']+'='+(x['proposed_due_date'] or 'undated') for x in linked),date_reason=date_reason,
            resolution_need=impact['resolution_need'],scope=impact['scope']))
    for record,state in [(x,'unresolved') for x in fifth['state']['unresolved_items']]+[(x,'conflicting') for x in fifth['state']['conflicts']]:
        systems=set()
        for ref in record['evidence_ids']:
            values=upstream.get(ref,{}).get('values',{})
            if values.get('system_id'): systems.add(values['system_id'])
        rows.append(dict(impact_id=record['id'],system_id=';'.join(sorted(systems)) or 'ALL',
            rule_ref='Internal POLICY' if record['id']=='GAP-POLICY' else 'Authority review' if record['id'].startswith('BLOCK-') else 'Evidence reconciliation',
            state=state,evidence_ids=';'.join(record['evidence_ids']),reason=record['summary'],owner=record.get('owner') or '',
            proposed_action='',proposed_due_date='',approval_status='pending',run_id=fifth['run_id'],review_date=c.REVIEW_DATE,action_ids='',action_date_pairs='',
            date_reason='No separate dated proposal for this issue; review underlying system/action records',
            resolution_need=record.get('resolution_need','Human review required'),scope='Unresolved source issue, not a compliance finding'))
    if len({x['impact_id'] for x in rows})!=len(rows): raise ValueError('Duplicate register row ID')
    return rows

def render_csv(rows):
    out=io.StringIO(newline=''); writer=csv.DictWriter(out,fieldnames=HEADER,lineterminator='\r\n');writer.writeheader();writer.writerows(rows)
    return out.getvalue().encode('utf-8')

def escape(text):
    return str(text).replace('\\','\\\\').replace('\r\n','\n').replace('\r','\n').replace('\n','\\n').replace(';','\\;').replace(',','\\,')

def fold(line):
    lines=[];current=''
    for char in line:
        if len((current+char).encode('utf-8'))>75:
            lines.append(current);current=' '+char
        else: current+=char
    lines.append(current)
    return '\r\n'.join(lines)

def calendar(snapshots):
    sixth=snapshots[5]; blocked=publication_state(snapshots)=='blocked'
    stamp=datetime.fromisoformat(sixth['created_at']).astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    lines=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//Quillhaven Project B//Review-only proposals//EN','CALSCALE:GREGORIAN',
           'X-WR-CALNAME:Project B tentative review proposals']
    for action in dated_actions(sixth,blocked):
        due=date.fromisoformat(action['proposed_due_date']).strftime('%Y%m%d')
        desc='Action: '+action['id']+'\nSystem: '+action['system_id']+'\nResponsible role: '+(action['owner'] or 'unresolved')
        desc+='\nRun: '+sixth['run_id']+'\nReview date: '+c.REVIEW_DATE+'\nSource/decision basis: '+';'.join(action['evidence_ids'])
        desc+='\nImpacts: '+';'.join(action['impact_ids'])+'\nApproval status: pending\nSource proposal only; no approved deadline or activation.'
        lines+=['BEGIN:VEVENT','UID:'+action['id']+'@project-b.quillhaven.invalid','DTSTAMP:'+stamp,
                'DTSTART;VALUE=DATE:'+due,'SUMMARY:'+escape(action['proposed_action']),
                'DESCRIPTION:'+escape(desc),'STATUS:TENTATIVE','END:VEVENT']
    lines.append('END:VCALENDAR')
    return ('\r\n'.join(fold(x) for x in lines)+'\r\n').encode('utf-8')

def md(text):
    return str(text).replace('\\','\\\\').replace('|','\\|').replace('\r','').replace('\n','<br>')

def brief(snapshots,rows):
    fifth,sixth=snapshots[4:6]; pub=publication_state(snapshots); blocked=pub=='blocked'
    events={x['id'] for x in dated_actions(sixth,blocked)}
    counts={s:sum(x['state']==s for x in fifth['state']['impacts']) for s in ('supported-impact','supported-no-impact','conflicting','unresolved')}
    policy_attempts=[x for x in snapshots[1]['state']['sources'] if x['source_name']=='POLICY']
    policy_description='; '.join(x['mode']+' HTTP '+str(x.get('http_status','no response'))+' ('+x['retrieval_status']+')' for x in policy_attempts)
    lines=['# Quillhaven Academy regulatory review draft','',
        'Run ID: '+sixth['run_id'],'Assigned review date: '+c.REVIEW_DATE,'Recipients: Legal and Operations',
        'Draft/run status: partial. Authority/publication gate: '+pub+'. All approvals pending; all requests unsent.',
        '', 'This package contains provisional register-based review preparation. Supported impact means a review need, not a legal breach; bounded no-impact observations are not whole-system compliance.',
        'No company system, policy, incident, production calendar or approved deadline has been changed. No request has been sent and no reviewer response has been received.',
        '', '## Source quality and limits','',
        'POLICY remains unresolved: '+policy_description+'. No policy controls are inferred. Supporting artifacts named in the EVIDENCE register were not independently inspected.',
        'Authority limitations and actor, exception, provenance and transition questions remain for Legal. Later retrieval does not prove exhaustive historical coverage. Source dates are distinct from the assigned review date.',
        'Dependent formal conclusions are withheld. Existing calendar proposals can still support limited scheduling discussion; they remain tentative and require their disclosed reviewers. Other evidence collection may proceed without inventing POLICY requirements.',
        '', '| Source attempt | Actual retrieval time | Result | Version/basis | Evidence reference |', '|---|---|---|---|---|']
    for s in snapshots[1]['state']['sources']:
        metadata=s['version_metadata'] or {}
        version={k:v for k,v in metadata.items() if k not in {'rows','headers','identifiers'}}
        lines.append('| '+ ' | '.join(md(x) for x in [s['id'],s['retrieved_at'],s['retrieval_status'],__import__('json').dumps(version,ensure_ascii=False),s['local_reference'] or 'No requested content'])+' |')
    lines+=['','## Supported observations and unresolved scope','',
        'Scoped outcomes: '+', '.join(s+'='+str(n) for s,n in counts.items())+'. These are not violation counts.',
        '', '| Record | System | Rule basis | State | Reason | Evidence |', '|---|---|---|---|---|---|']
    for row in rows:
        lines.append('| '+' | '.join(md(row[x]) for x in ['impact_id','system_id','rule_ref','state','reason','evidence_ids'])+' |')
    lines+=['','## Proposed actions and dates','',
        'Undated actions are omitted from the calendar. No date is invented for them. Existing calendar proposals retain their own dates; dates are not borrowed for newly proposed actions. Multiple action dates are not collapsed into one deadline.',
        '', '| Action | System | Responsible owner | Proposed action | Proposed date | Approval | Calendar | Basis |', '|---|---|---|---|---|---|---|---|']
    for action in sixth['state']['proposed_actions']:
        lines.append('| '+' | '.join(md(x) for x in [action['id'],action['system_id'],action['owner'] or 'Owner unresolved',action['proposed_action'],
            action['proposed_due_date'] or 'Undated: '+action['date_reason'],'pending','Tentative proposal' if action['id'] in events else 'Omitted: undated or authority-dependent',
            ';'.join(action['evidence_ids'])])+' |')
    lines+=['','## Decisions requested from Legal and Operations','',
        'The detached bindings are in snapshots/07-publication-validation.json, state.review_request_bindings. Each binding identifies this final draft and the other two artifact paths and exact SHA-256 hashes. This brief deliberately contains no hash of itself.',
        'Request source versions, hashes and retrieval times remain in each immutable Stage 06 request. Proposed coordinator owners are not evidence of reviewer approval.',
        '', '| Request | Required reviewer | System / impacts / action | Question | Evidence | Delivery / feedback |', '|---|---|---|---|---|---|']
    for req in sixth['state']['review_requests']:
        subjects=req['subject_system']+' / '+';'.join(req['subject_impacts'])+' / '+(req['subject_action'] or 'No individual action')
        lines.append('| '+' | '.join(md(x) for x in [req['id'],req['required_reviewer'],subjects,req['question'],';'.join(req['evidence_ids']),'not-sent / not-received'])+' |')
    lines+=['','## Remaining human work','',
        'Obtain authorized POLICY content; verify supporting artifacts, actor/function facts, exceptions, transition eligibility and historical authority completeness. Legal retains interpretation; Operations retains activation and approved dates.',
        'Actual retrieval times and run/retry history are separate from the assigned date. See workflow-result.json and workflow-attempts/ for end-to-end execution status where available. Verified feedback handling, coding-session capture and facilitator/submission access still need separate verification.']
    return ('\n'.join(lines)+'\n').encode('utf-8')

def expected_artifacts(snapshots,upstream):
    rows=register_rows(snapshots,upstream)
    return dict(zip(ARTIFACTS,[render_csv(rows),brief(snapshots,rows),calendar(snapshots)]))

def check_ics(data):
    text=data.decode('utf-8')
    if not text.endswith('\r\n') or '\n' in text.replace('\r\n',''): raise ValueError('Calendar requires CRLF')
    physical=text.split('\r\n')[:-1]
    if any(len(x.encode('utf-8'))>75 for x in physical): raise ValueError('Calendar line exceeds 75 octets')
    logical=re.sub(r'\r\n[ \t]','',text).split('\r\n')[:-1]
    if logical[0]!='BEGIN:VCALENDAR' or logical[-1]!='END:VCALENDAR' or 'VERSION:2.0' not in logical or not any(x.startswith('PRODID:') for x in logical): raise ValueError('Invalid calendar wrapper')
    events=[];current=None
    for line in logical:
        if line=='BEGIN:VEVENT':
            if current is not None: raise ValueError('Nested event')
            current={}
        elif line=='END:VEVENT':
            if current is None: raise ValueError('Unmatched event')
            for field in ('UID','DTSTAMP','DTSTART;VALUE=DATE','SUMMARY','DESCRIPTION','STATUS'):
                if not current.get(field): raise ValueError('Missing event '+field)
            if current['STATUS']!='TENTATIVE': raise ValueError('Only tentative events allowed')
            datetime.strptime(current['DTSTAMP'],'%Y%m%dT%H%M%SZ');datetime.strptime(current['DTSTART;VALUE=DATE'],'%Y%m%d')
            events.append(current);current=None
        elif current is not None:
            key,sep,value=line.partition(':')
            if not sep or key in current: raise ValueError('Invalid/duplicate event property')
            current[key]=value
    if current is not None or len({x['UID'] for x in events})!=len(events): raise ValueError('Unclosed event/duplicate UID')
    return events

def bindings(sixth,artifacts):
    return [c.record('BINDING-'+req['id'],'Detached binding for unsent request '+req['id'],[req['id']],
        request_id=req['id'],run_id=sixth['run_id'],subject_system=req['subject_system'],subject_impacts=req['subject_impacts'],
        subject_action=req['subject_action'],required_reviewer=req['required_reviewer'],source_versions=req['source_versions'],
        delivery_status='not-sent',approval_status='pending',drafts=[dict(path=x['path'],sha256=x['sha256']) for x in artifacts])
        for req in sixth['state']['review_requests']]

def validate(directory, in_progress=False):
    a.validate(directory,allow_later=True)
    snapshots,upstream=inputs(directory); seventh=c.load(directory/'snapshots'/FILES[6]); ids={x['run_id'] for x in snapshots+[seventh]}
    if len(ids)!=1: raise ValueError('All seven snapshots must share the same run_id')
    Draft202012Validator(c.load(c.ROOT/'snapshot.schema.json'),format_checker=FormatChecker()).validate(seventh)
    sixth=snapshots[5]
    if seventh['stage']!='publication-validation' or seventh['sequence']!=7: raise ValueError('Stage 07 identity mismatch')
    if seventh['predecessor']!=dict(snapshot_id=sixth['snapshot_id'],path='snapshots/'+FILES[5],sha256=c.digest((directory/'snapshots'/FILES[5]).read_bytes())): raise ValueError('Predecessor mismatch')
    expected=expected_artifacts(snapshots,upstream)
    artifacts=[]
    for name in ARTIFACTS:
        data=(directory/name).read_bytes()
        if data!=expected[name]: raise ValueError('Final file disagrees with Stage 06/evidence: '+name)
        artifacts.append(dict(id='ARTIFACT-'+name,path=name,sha256=c.digest(data),validation_status='valid'))
    if seventh['state']['artifacts']!=artifacts: raise ValueError('Artifact path/hash mismatch')
    if seventh['state']['review_request_bindings']!=bindings(sixth,artifacts): raise ValueError('Request binding mismatch')
    pub=publication_state(snapshots)
    if seventh['state']['publication_status']!=pub or seventh['status']!=('blocked' if pub=='blocked' else 'partial'): raise ValueError('Authority/publication gate mismatch')
    if seventh['state']['review_date']!=c.REVIEW_DATE or seventh['state']['human_approval']!='pending' or seventh['state']['external_publication'] is not False: raise ValueError('Safeguard mismatch')
    checks=seventh['state']['validation_checks']
    if {x['id'] for x in checks}!=set(CHECKS) or (not in_progress and any(x.get('result')!='passed' for x in checks)): raise ValueError('Validation check inventory/result mismatch')
    current=a.r.records(seventh)
    artifact_ids={x['id'] for x in artifacts}
    if set(seventh['produced_record_ids'])!=set(current)|artifact_ids or not set(seventh['consumed_record_ids'])<=set(upstream): raise ValueError('Record inventory mismatch')
    for record in current.values():
        if not set(record['evidence_ids'])<=set(upstream)|set(current)|artifact_ids: raise ValueError('Unknown Stage 07 evidence reference')
    check_ics((directory/'action-calendar.ics').read_bytes())
    rows=list(csv.DictReader(io.StringIO((directory/'impact-register.csv').read_text(encoding='utf-8'),newline='')))
    if not rows or list(rows[0])!=HEADER: raise ValueError('CSV header mismatch')
    return dict(run_id=sixth['run_id'],stages_validated=[1,2,3,4,5,6,7],all_seven_run_ids_match=True,
        schemas_valid=True,predecessor_hashes_valid=True,evidence_references_valid=True,artifact_hashes_valid=True,
        request_bindings_valid=True,final_files_agree_with_stage06=True,calendar_valid=True,
        publication_status=pub,assessment_complete=False)

CHECKS=['CHECK-SEVEN-RUN-IDS','CHECK-SCHEMAS-CHAIN-REFERENCES','CHECK-CSV-STAGE06',
        'CHECK-BRIEF-STAGE06','CHECK-ICS-STAGE06','CHECK-EXACT-HASHES-BINDINGS','CHECK-HUMAN-SAFEGUARDS']

def build(directory):
    # Refuse all replacements; prior artifacts/evidence remain intact if a partial attempt needs inspection.
    if any((directory/x).exists() for x in ARTIFACTS+['snapshots/'+FILES[6]]): raise ValueError('Existing final artifacts/Stage 07 not overwritten; validate or inspect retained failure')
    a.validate(directory)
    snapshots,upstream=inputs(directory); sixth=snapshots[5]
    expected=expected_artifacts(snapshots,upstream)
    for name,data in expected.items(): (directory/name).write_bytes(data)
    check_ics(expected['action-calendar.ics'])
    artifacts=[dict(id='ARTIFACT-'+name,path=name,sha256=c.digest((directory/name).read_bytes()),validation_status='valid') for name in ARTIFACTS]
    state=dict(artifacts=artifacts,validation_checks=[],publication_status=publication_state(snapshots),review_date=c.REVIEW_DATE,
        review_request_bindings=bindings(sixth,artifacts),human_approval='pending',external_publication=False,
        draft_scope='Partial review-only preparation; dependent formal conclusions withheld',
        unresolved_scope=snapshots[4]['state']['unresolved_items']+snapshots[4]['state']['conflicts'])
    for identifier in CHECKS:
        state['validation_checks'].append(c.record(identifier,'Current bundle check: '+identifier,sorted(upstream),result='not-run'))
    value=c.snapshot(sixth['run_id'],7,state,[],consumed=sorted(upstream),
        predecessor=dict(snapshot_id=sixth['snapshot_id'],path='snapshots/'+FILES[5],sha256=c.digest((directory/'snapshots'/FILES[5]).read_bytes())),
        status='blocked' if state['publication_status']=='blocked' else 'partial')
    value.update(stage='publication-validation',snapshot_id=sixth['run_id']+'-7-'+uuid4().hex,unresolved=state['unresolved_scope'])
    value['decisions']=[c.record('DECISION-STAGE07','Produce a limited review draft while preserving unresolved authority and POLICY',sorted(upstream),
        concern='Draft consistency must not imply legal approval',options=['Defer all preparation','Preserve bounded drafts and exact bindings with blocked authority gate'],
        chosen_behavior='Bounded drafts; dependent formal conclusions withheld',rationale='Existing calendar proposals and factual review remain useful; missing authority/POLICY cannot be inferred',
        tradeoffs=['Useful local review package; not a completed compliance assessment'],downstream_effect='The one-command workflow implements fresh retrieval, all seven stages, run history and journalled recovery; validated drafts remain review-only, POLICY unresolved, legal interpretation and approvals pending, requests unsent, and publication blocked while required evidence is missing')]
    value['produced_record_ids']=sorted(set(a.r.records(value))|{x['id'] for x in artifacts})
    c.save(directory/'snapshots'/FILES[6],value)
    try:
        result=validate(directory,in_progress=True)
    except Exception:
        value['status']='failed';value['state']['publication_status']='failed'
        for check in value['state']['validation_checks']: check['result']='failed'
        c.save(directory/'snapshots'/FILES[6],value)
        raise
    for check in value['state']['validation_checks']: check['result']='passed'
    c.save(directory/'snapshots'/FILES[6],value)
    result=validate(directory);c.save(directory/'stage-7-validation.json',result);return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=c.ROOT/'deliverables');p.add_argument('--validate',action='store_true');args=p.parse_args()
    try: result=validate(args.output) if args.validate else build(args.output)
    except Exception as error:
        c.save(args.output/('stage-7-failure-'+uuid4().hex+'.json'),dict(created_at=c.now(),stage='07',error=str(error),owner='Learner',
            resolution_need='Inspect preserved partial outputs; do not overwrite history or invent recovery'))
        raise
    print(__import__('json').dumps(result,indent=2))

if __name__=='__main__': main()
