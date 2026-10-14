"""Stages 03-04: verify and reconcile retained capture; no network or approvals."""
import argparse
import re
from datetime import date, timedelta
from pathlib import Path
import sys
from jsonschema import Draft202012Validator, FormatChecker
sys.path.insert(0, str(Path(__file__).resolve().parent))
import capture_sources as c

FILES = ['01-scope.json', '02-source-capture.json', '03-authority-and-timing.json', '04-evidence-reconciliation.json']

def norm(text):
    text=re.sub(r'(?m)^(AMENDED|NEW)\s*$', '', text)
    text=' '.join(re.sub(r'[▼►][BM]\d*', '', text).split())
    return re.sub(r'\s+([,;])',r'\1',text)

def article(text, number):
    start = text.rfind('\nArticle '+str(number)+'\n')
    if start < 0: raise ValueError('Article not located: '+str(number))
    end = re.search(r'\nArticle \d+\n|\nANNEX I\n', text[start+1:])
    return text[start:start+1+end.start()] if end else text[start:]

def paragraphs(text):
    matches = list(re.finditer(r'\n([1-7])\.\s+', text))
    result = {m.group(1): norm(text[m.end():matches[i+1].start() if i+1<len(matches) else len(text)].split('CHAPTER V')[0]) for i,m in enumerate(matches)}
    if set(result)!=set('1234567'): raise ValueError('All seven Article 50 paragraphs required')
    return result

def records(value):
    found = {}
    def visit(v):
        if isinstance(v,dict):
            if {'id','summary','evidence_ids'}<=v.keys():
                if v['id'] in found and found[v['id']]!=v: raise ValueError('Conflicting duplicate record')
                found[v['id']]=v
            for item in v.values(): visit(item)
        elif isinstance(v,list):
            for item in v: visit(item)
    visit(value)
    return found

class Review:
    def __init__(self, directory):
        self.directory=directory
        c.validate(directory,allow_later=True)
        self.scope=c.load(directory/'snapshots'/FILES[0])
        self.second=c.load(directory/'snapshots'/FILES[1])
        self.sources=self.second['state']['sources']
        self.claims={}
        self.blockers=[]
        self.source_cache={}
        self.text_cache={}

    def source(self,name):
        if name in self.source_cache: return self.source_cache[name]
        sources=[s for s in self.sources if s['source_name']==name and s['requested_content_available'] and s['mode']!='cellar-metadata']
        if len(sources)!=1: raise ValueError('One usable requested document required: '+name)
        s=sources[0]
        manifest=next(x for x in c.load(self.directory/'source-manifest.json')['sources'] if x['name']==name)
        state,metadata,_,_=c.inspect(manifest,s['mode'],dict(body=(self.directory/s['local_reference']).read_bytes(),status=s['http_status']))
        if state!='retrieved' or metadata!=s['version_metadata']:
            raise ValueError('Document identity/version no longer matches captured bytes: '+name)
        self.source_cache[name]=s
        return s

    def text(self,name):
        if name in self.text_cache: return self.text_cache[name]
        s=self.source(name)
        self.text_cache[name]='\n'.join(c.Document((self.directory/s['local_reference']).read_text(encoding='utf-8',errors='replace')).visible)
        return self.text_cache[name]

    def claim(self,name,label,quote):
        offset=self.text(name).find(quote)
        if offset<0 or not quote: raise ValueError('Claim not in source: '+label)
        rid='CLAIM-'+name+'-'+label
        self.claims[rid]=c.record(rid,'Captured passage: '+name+' '+label,[self.source(name)['id']],quote=quote,
            locator=dict(format='newline-joined visible HTML text',start=offset,end=offset+len(quote),section=label),
            source_hash=self.source(name)['content_hash'])
        return rid

    def block(self,rid,summary,basis,need):
        self.blockers.append(c.record(rid,summary,basis,owner='Legal',status='unresolved',resolution_need=need))

    def authority(self):
        binding,timing,guidance=[],[],[]
        try:
            original=paragraphs(article(self.text('OJ'),50))
            revised=paragraphs(article(self.text('CONSOLIDATED'),50))
            refs=[self.claim(n,'Article-50',article(self.text(n),50)) for n in ('OJ','CONSOLIDATED')]
            am=self.text('AMEND')
            start=am.find('in Article 50, paragraph 7 is replaced by the following:')
            end=am.find('\n(21)\n',start)
            if start<0 or end<0: raise ValueError('Article 1(20) replacement not located')
            replacement=am[start:end]
            replacement_ref=self.claim('AMEND','Article-1-20',replacement)
            expected=norm(replacement.split('‘7. ',1)[1].split('’',1)[0])
            for n in '1234567':
                verified=original[n]==revised[n] if n!='7' else expected==revised[n] and original[n]!=revised[n]
                basis=refs+([replacement_ref] if n=='7' else [])
                binding.append(c.record('RULE-50-'+n,'Article 50('+n+') text comparison '+('matches' if verified else 'unresolved'),basis,
                    rule_ref='2024/1689 Article 50('+n+')',original_text=original[n],reviewed_text=revised[n],
                    comparison_verified=verified,amended=n=='7',owner='Legal',approval_status='pending',
                    actor_scope='As stated in source text; company applicability not decided'))
                if not verified: self.block('BLOCK-50-'+n,'Paragraph comparison failed',basis,'Legal must reconcile the original and amended texts')
            for name,number in [('OJ',113),('AMEND',4),('CONSOLIDATED',113),('CONSOLIDATED',111)]:
                self.claim(name,'Article-'+str(number),article(self.text(name),number))
            for name,published,interval,number,formula in [('OJ','2024-07-12',20,113,'twentieth day following'),('AMEND','2026-07-24',3,4,'third day following')]:
                clause=article(self.text(name),number)
                pub='12.7.2024' if name=='OJ' else '24.7.2026'
                if formula not in clause or pub not in self.text(name) or self.source(name)['version_metadata']['publication_date']!=pub:
                    raise ValueError('Publication/entry formula not corroborated: '+name)
                effective=(date.fromisoformat(published)+timedelta(days=interval)).isoformat()
                timing.append(c.record('TIMING-'+name+'-ENTRY','Publication date plus stated entry interval',
                    ['CLAIM-'+name+'-Article-'+str(number)],publication_date=published,interval_days=interval,
                    calculated_entry_into_force=effective,before_review_date=effective<=c.REVIEW_DATE,
                    owner='Legal',rationale='Source-based calendar arithmetic, not a company compliance conclusion'))
            for name in ('OJ','CONSOLIDATED'):
                if 'It shall apply from 2 August 2026.' not in article(self.text(name),113): raise ValueError('General application date changed')
            transition='Providers of AI systems, including general-purpose AI systems, generating synthetic audio, image, video or text content, that have been placed on the market before 2 August 2026 shall take the necessary steps in order to comply with Article 50(2) by 2 December 2026.'
            if transition not in norm(article(self.text('CONSOLIDATED'),111)) or transition not in norm(am): raise ValueError('Transition not corroborated')
            for label,marker,endmarker in [('Article-1-39','Article 111 is amended as follows:','\n(40)\n'),('Article-1-40','in Article 113, the third paragraph is amended as follows:','\n(41)\n')]:
                start=am.find(marker); end=am.find(endmarker,start)
                if start<0 or end<0: raise ValueError('Operative amendment not found: '+label)
                self.claim('AMEND',label,am[start:end])
            timing.extend([
                c.record('TIMING-50-GENERAL','General application date retained; distinguish conditional transition',
                    ['CLAIM-OJ-Article-113','CLAIM-CONSOLIDATED-Article-113','CLAIM-AMEND-Article-1-40'],
                    application_date='2026-08-02',before_review_date=True,owner='Legal',
                    rationale='Article 50 is in Chapter IV; high-risk Chapter III dates are separate'),
                c.record('TIMING-50-2-TRANSITION','Conditional provider transition, not a blanket Article 50 delay',
                    ['CLAIM-CONSOLIDATED-Article-111','CLAIM-AMEND-Article-1-39'],deadline='2026-12-02',
                    rule_ref='2024/1689 Article 111(4)',conditions=['provider of synthetic-content AI system','placed on market before 2026-08-02'],
                    company_eligibility='unresolved',owner='Legal',resolution_need='Verify actor role and placed-on-market date')])
            timing.append(c.record('TIMING-113-OTHER-BASES','Amended Article 113 exception dates remain separate from Chapter IV transparency timing',
                ['CLAIM-CONSOLIDATED-Article-113','CLAIM-AMEND-Article-1-40'],owner='Legal',
                observed_dates=dict(new_prohibition_points='2026-12-02',chapter_III_annex_III='2027-12-02',
                    chapter_III_annex_I='2028-08-02',articles_102_to_110='2026-07-27'),
                company_applicability='not determined',rationale='Preserve distinct dated bases; do not apply high-risk delays to all Article 50 duties'))
            for phrase in ('2 December 2027','2 August 2028','27 July 2026','2 December 2026'):
                if phrase not in article(self.text('CONSOLIDATED'),113) or phrase not in self.claims['CLAIM-AMEND-Article-1-40']['quote']:
                    raise ValueError('Article 113 exception date not corroborated: '+phrase)
            header=self.text('CONSOLIDATED').split('CHAPTER I')[0]
            header_ref=self.claim('CONSOLIDATED','Header',header)
            if '27.07.2026 — 001.001' not in header or '2026/1744' not in header or 'has no legal effect' not in header: raise ValueError('Consolidation identity/disclaimer changed')
            guidance.append(c.record('CONSOLIDATION-CONTEXT','27 July 2026 revision 001.001 names amendment 2026/1744; documentation only',
                [header_ref],version_date='2026-07-27',authority='documentation; no legal effect',owner='Legal',
                suitability='Pre-review comparison aid; original acts retained'))
        except (ValueError,KeyError,IndexError) as error:
            self.block('BLOCK-AUTHORITY',str(error),[s['id'] for s in self.sources if s['source_name'] in {'OJ','AMEND','CONSOLIDATED'}],
                'Verify identity/version/operative clauses before dependent conclusions')
        for name in ('LAW','TIME','FAQ'):
            try:
                ref=self.claim(name,'Context',self.text(name))
                context=self.text(name)
                agrees=None
                if name=='LAW' and binding:
                    law_paragraphs=paragraphs(context.split('Relevant recitals')[0])
                    agrees=all(law_paragraphs[n]==r['reviewed_text'] for n,r in zip('1234567',binding))
                if name in {'TIME','FAQ'}:
                    agrees=all(phrase in context for phrase in ('2 August 2026','2 December 2026')) if name=='FAQ' else all(phrase in context for phrase in ('02 Aug 2026','02 Dec 2026','before 02 Aug 2026'))
                guidance.append(c.record('GUIDANCE-'+name,'Official '+name+' context; advisory only',[ref],
                    version_metadata=self.source(name)['version_metadata'],owner='Legal',authority='advisory',
                    suitability='Declared basis only; historical completeness unverified',overrides_binding_text=False,
                    comparison_with_captured_binding_basis=agrees))
                if agrees is False: self.block('BLOCK-CONTEXT-'+name,'Context does not match tested binding-text/date basis',[ref],'Legal must reconcile context; do not override operative acts')
            except ValueError as error: self.block('BLOCK-'+name,str(error),[],'Check contextual document')
        self.block('BLOCK-HISTORICAL','Later retrieval does not prove exhaustive legal history as of 2026-08-26',
            [r['id'] for r in binding],'Legal must confirm authoritative completeness and applicability')
        return dict(review_date=c.REVIEW_DATE,binding_rules=binding,timing_rules=timing,guidance_context=guidance,
            authority_blockers=self.blockers,source_claims=list(self.claims.values()),legal_approval='pending',dependent_formal_conclusions='withheld')

    def rows(self,name):
        required={'SYSTEMS':'system_id system_name use_case owner provider_role deployer_role exposed_group output_type current_notice human_review evidence_status evidence_updated_at record_version',
            'EVIDENCE':'record_id system_id record_type reported_at owner status evidence_ref evidence_state notes',
            'CALENDAR':'action_id system_id action owner due_date status approval_required source_version'}[name].split()
        s=self.source(name)
        manifest=next(x for x in c.load(self.directory/'source-manifest.json')['sources'] if x['name']==name)
        state,metadata,_,_=c.inspect(manifest,s['mode'],dict(body=(self.directory/s['local_reference']).read_bytes(),status=s['http_status']))
        if state!='retrieved' or metadata!=s['version_metadata']: raise ValueError('Table metadata does not match raw source: '+name)
        if any(metadata['headers'].count(x)!=1 for x in required): raise ValueError('Missing/ambiguous required fields: '+name)
        return s,metadata['rows']

    def reconcile(self,third):
        facts,incidents,calendar,conflicts,gaps=[],[],[],[],[]
        def issue(rid,summary,basis,owner,need,**extra):
            return c.record(rid,summary,basis,owner=owner or None,resolution_need=need,status='unresolved',**extra)
        gaps.append(issue('GAP-POLICY','POLICY unavailable; no internal controls inferred',
            [s['id'] for s in self.sources if s['source_name']=='POLICY'],'Facilitator/source owner','Provide authorized POLICY content and version'))
        for name,key,collection in [('SYSTEMS','system_id',facts),('EVIDENCE','record_id',incidents),('CALENDAR','action_id',calendar)]:
            try:
                s,rows=self.rows(name)
                counts={}
                for row in rows: counts[row['values'][key]]=counts.get(row['values'][key],0)+1
                for row in rows:
                    v=row['values']; base=name+'-'+v[key]; duplicate=counts[v[key]]>1
                    rid=base+('-'+c.digest(str(sorted(v.items())).encode())[7:19] if duplicate else '')
                    if any(r['id']==rid for r in collection):
                        gaps.append(issue('GAP-DUPLICATE-'+rid,'Identical duplicate identity retained in raw source',[rid],v.get('owner'),'Resolve duplicate rows'))
                        continue
                    r=c.record(rid,'Captured '+name+' record '+v[key],[s['id']],values=v,locator=row['locator'],owner=v.get('owner') or None,
                        source_versions=s['version_metadata']['observed_versions'],claim_level='Register statement, not inspected supporting artifact')
                    collection.append(r)
                    if duplicate: conflicts.append(issue('CONFLICT-ID-'+rid,'Duplicate business identity '+v[key],[rid],r['owner'],'Reconcile source identity'))
                    invalid=[]
                    if not v.get('owner'): invalid.append('owner missing')
                    for field in ('evidence_updated_at','reported_at','due_date'):
                        if field in v:
                            try: date.fromisoformat(v[field])
                            except ValueError: invalid.append(field+' missing/invalid')
                            else:
                                if field!='due_date' and v[field]>c.REVIEW_DATE: invalid.append(field+' after review date')
                    for field in ('provider_role','deployer_role'):
                        if field in v and v[field] not in {'yes','no'}: invalid.append(field+' unresolved: '+v[field])
                    if invalid: gaps.append(issue('GAP-FIELDS-'+rid,'; '.join(invalid),[rid],r['owner'],'Confirm facts/field meaning with source owner'))
                    field='evidence_status' if name=='SYSTEMS' else 'evidence_state'
                    if name!='CALENDAR' and v.get(field)!='complete':
                        target=conflicts if v.get(field)=='conflicting' else gaps
                        target.append(issue('ISSUE-'+rid,name+' reports '+field+'='+str(v.get(field)),[rid],r['owner'],
                            'Supply/reconcile facts; no compliance determination',reported_state=v.get(field),reported_notes=v.get('notes')))
                    if name=='EVIDENCE':
                        gaps.append(issue('GAP-SUPPORT-'+rid,'Supporting artifact '+(v.get('evidence_ref') or '(missing)')+' not separately captured',
                            [rid],r['owner'],'Obtain authorized supporting evidence; complete/closed does not mean compliant'))
                        if v['record_type']=='exception_request': gaps.append(issue('GAP-EXCEPTION-'+rid,'Exception request is not verified Legal approval',
                            [rid],'Legal','Verify criteria, actual approval, scope and expiry',reported_status=v['status'],reported_notes=v['notes']))
                    if name=='CALENDAR': r.update(date_role='source-proposed; not legal date or verified approved deadline',approval_status='unverified',approval_required=v['approval_required'])
            except (ValueError,KeyError) as error:
                gaps.append(issue('GAP-'+name,str(error),[s['id'] for s in self.sources if s['source_name']==name],'Source owner','Restore unambiguous fields; no renamed-field guesses'))
        ids={r['values']['system_id'] for r in facts}
        links=[]
        for sid in sorted(ids):
            sr=[r for r in facts if r['values']['system_id']==sid]
            er=[r for r in incidents if r['values']['system_id']==sid]
            cr=[r for r in calendar if r['values']['system_id'] in {sid,'ALL'}]
            links.append(c.record('JOIN-'+sid,'Records linked by exact system_id '+sid,[r['id'] for r in sr+er+cr],system_id=sid,
                system_records=[r['id'] for r in sr],evidence_records=[r['id'] for r in er],calendar_records=[r['id'] for r in cr],
                owner=sr[0]['owner'],rationale='Different statuses describe different subjects; complete evidence does not establish a notice or compliance'))
            if not er: gaps.append(issue('GAP-NO-EVIDENCE-'+sid,'No linked EVIDENCE row',[r['id'] for r in sr],sr[0]['owner'],'Provide supporting evidence'))
            if any(r['values']['provider_role'] in {'yes','unknown'} for r in sr):
                basis=[r['id'] for r in sr]
                if 'TIMING-50-2-TRANSITION' in records(third): basis+=['TIMING-50-2-TRANSITION']
                gaps.append(issue('GAP-TRANSITION-'+sid,'Placed-on-market date not disclosed; transition eligibility unresolved',basis,sr[0]['owner'],
                    'Verify actor role, synthetic-output facts and placed-on-market date with Legal'))
        for r in incidents+calendar:
            sid=r['values']['system_id']
            if sid not in ids and not (r in calendar and sid=='ALL'): gaps.append(issue('GAP-ORPHAN-'+r['id'],'Unknown linked system '+sid,[r['id']],r['owner'],'Reconcile system identity'))
        return dict(review_date=c.REVIEW_DATE,system_facts=facts,policy_controls=[],incident_evidence=incidents,calendar_records=calendar,
            system_links=links,conflicts=conflicts,evidence_gaps=gaps,policy_status='unresolved',approvals_applied=False,interpretation_status='human review pending')

def snapshot(review,sequence,state,previous):
    path=FILES[sequence-2]
    v=c.snapshot(review.scope['run_id'],sequence,state,[],consumed=list(records(previous)),
        predecessor=dict(snapshot_id=previous['snapshot_id'],path='snapshots/'+path,sha256=c.digest((review.directory/'snapshots'/path).read_bytes())),
        status='blocked' if sequence==3 and any(r['id']!='BLOCK-HISTORICAL' for r in review.blockers) else 'partial')
    v['stage']='authority-and-timing' if sequence==3 else 'evidence-reconciliation'
    v['snapshot_id'] += '-'+__import__('uuid').uuid4().hex
    if sequence==4:
        v['consumed_record_ids'] += [s['id'] for s in review.sources]
    v['unresolved']=state['authority_blockers'] if sequence==3 else state['evidence_gaps']+state['conflicts']
    v['decisions']=[c.record('DECISION-STAGE-'+str(sequence),'Preserve claims and withhold formal conclusions/approvals',previous['produced_record_ids'],
        concern='Missing evidence and interpretation authority',options=['Infer or collapse claims','Preserve opposing claims and unresolved scope'],
        chosen_behavior='Preserve',rationale='Legal and Operations retain decisions; POLICY cannot be inferred',
        tradeoffs=['Useful bounded preparation; no complete compliance conclusion'],downstream_effect='Stages 05-07 use these authority and evidence records for bounded impact screening, proposed actions and validated local drafts; POLICY remains unresolved, legal interpretation and approvals pending, and publication blocked while required evidence is missing')]
    v['produced_record_ids']=list(records(v))
    return v

def validate(directory, allow_later=False):
    c.validate(directory,allow_later=True)
    validator=Draft202012Validator(c.load(c.ROOT/'snapshot.schema.json'),format_checker=FormatChecker())
    upstream={}; run_id=None
    for i,name in enumerate(FILES):
        v=c.load(directory/'snapshots'/name); validator.validate(v)
        if i==0: run_id=v['run_id']
        if v['run_id']!=run_id or v['sequence']!=i+1: raise ValueError('Run/stage mismatch')
        if i:
            prior=c.load(directory/'snapshots'/FILES[i-1])
            if v['predecessor']!=dict(snapshot_id=prior['snapshot_id'],path='snapshots/'+FILES[i-1],sha256=c.digest((directory/'snapshots'/FILES[i-1]).read_bytes())): raise ValueError('Predecessor mismatch')
        current=records(v)
        if set(v['produced_record_ids'])!=set(current): raise ValueError('Produced record mismatch')
        if not set(v['consumed_record_ids'])<=set(upstream): raise ValueError('Unknown consumed reference')
        for r in current.values():
            if not set(r['evidence_ids'])<=set(upstream)|set(current): raise ValueError('Unknown evidence reference')
        if i>=2 and v['state']['review_date']!=c.REVIEW_DATE: raise ValueError('Assigned date changed')
        upstream.update(current)
    review=Review(directory)
    third=c.load(directory/'snapshots'/FILES[2]); fourth=c.load(directory/'snapshots'/FILES[3])
    if third['state']!=review.authority(): raise ValueError('Authority does not match captured evidence')
    if fourth['state']!=review.reconcile(third): raise ValueError('Reconciliation does not match captured evidence')
    expected_status='blocked' if any(r['id']!='BLOCK-HISTORICAL' for r in review.blockers) else 'partial'
    if third['status']!=expected_status or fourth['status']!='partial': raise ValueError('Unsupported completion status')
    if not allow_later and list((directory/'snapshots').glob('0[5-7]-*.json')): raise ValueError('Milestone 2 stops at stage 04')
    return dict(run_id=run_id,stages_validated=[1,2,3,4],schema_valid=True,predecessor_hashes_valid=True,
        evidence_references_valid=True,semantic_replay_valid=True,stage03_status=third['status'],stage04_status=fourth['status'],assessment_complete=False)

def build(directory):
    if any((directory/'snapshots'/f).exists() for f in FILES[2:]): raise ValueError('Existing stages not replaced; validate or use a newly authorized capture run')
    review=Review(directory)
    third=snapshot(review,3,review.authority(),review.second)
    c.save(directory/'snapshots'/FILES[2],third)
    fourth=snapshot(review,4,review.reconcile(third),third)
    c.save(directory/'snapshots'/FILES[3],fourth)
    result=validate(directory); c.save(directory/'milestone-2-validation.json',result)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--output',type=Path,default=c.ROOT/'deliverables'); p.add_argument('--validate',action='store_true'); args=p.parse_args()
    try: result=validate(args.output) if args.validate else build(args.output)
    except Exception as error:
        c.save(args.output/'milestone-2-failure.json',dict(created_at=c.now(),stage='03-04 continuation',error=str(error),owner='Learner',resolution_need='Inspect retained boundary outputs; repair or authorize a fresh capture run'))
        raise
    print(__import__('json').dumps(result,indent=2))

if __name__=='__main__': main()
