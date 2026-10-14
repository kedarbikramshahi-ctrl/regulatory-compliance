"""Milestone 1: fresh read-only source capture and snapshots 01-02 only."""
import argparse
import hashlib
import json
import re
import shutil
import ssl
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from uuid import uuid4

from jsonschema import Draft202012Validator, FormatChecker
import rfc3339_validator  # Fail explicitly if required format support is missing.

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parents[1]
REVIEW_DATE = '2026-08-26'
NAMES = {'POLICY','SYSTEMS','EVIDENCE','CALENDAR','LAW','OJ','AMEND','CONSOLIDATED','TIME','FAQ'}
ALLOWED_HOSTS = {'private-pecorino-70e.notion.site','docs.google.com',
                'ai-act-service-desk.ec.europa.eu','eur-lex.europa.eu',
                'digital-strategy.ec.europa.eu','publications.europa.eu','api.notion.com'}


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def record(identifier, summary, evidence_ids=(), **extra):
    return dict(id=identifier, summary=summary, evidence_ids=list(evidence_ids), **extra)


def check_url(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in ('http','https') or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError('Source URL or redirect is outside the allowed public hosts.')
    if parsed.username or parsed.password:
        raise ValueError('Credentials must not appear in source URLs.')
    if any(re.search(r'token|password|secret|api.?key', key, re.I)
           for key, _ in urllib.parse.parse_qsl(parsed.query)):
        raise ValueError('Secret-like URL parameters are not permitted.')


class PublicRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self):
        super().__init__()
        self.chain = []
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        self.chain.append(dict(status=code, url=newurl))
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url, headers, timeout=20):
    """GET only: no cookies, credentials, challenge solving, or unverified TLS."""
    check_url(url)
    redirect = PublicRedirect()
    opener = urllib.request.build_opener(redirect, urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    request = urllib.request.Request(url, headers=dict(headers, **{'Cache-Control':'no-cache','Pragma':'no-cache'}), method='GET')
    try:
        response = opener.open(request, timeout=timeout)
    except urllib.error.HTTPError as error:
        response = error  # Preserve error body as diagnostic evidence, never policy content.
    with response:
        body = response.read(16*1024*1024+1)
        if len(body) > 16*1024*1024:
            raise ValueError('Response exceeds the documented 16 MiB limit.')
        return dict(status=response.code, content_type=response.headers.get('Content-Type','unknown'),
                    body=body, final_url=response.geturl(), redirects=redirect.chain)


class Document(HTMLParser):
    """Keep visible source passages and table cells; do not execute scripts."""
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.visible = []
        self.rows = []
        self.row_tables = []
        self.table_stack = []
        self.table_count = 0
        self.row_table = None
        self.row = None
        self.cell = None
        self.in_title = False
        self.title = []
        self.feed(html)
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'):
            self.skip += 1
        if tag == 'title': self.in_title = True
        if tag == 'table':
            self.table_count += 1
            self.table_stack.append(self.table_count)
        if tag == 'tr':
            self.row = []
            self.row_table = self.table_stack[-1] if self.table_stack else None
        if tag in ('td','th') and self.row is not None: self.cell = []
    def handle_endtag(self, tag):
        if tag in ('script','style'): self.skip = max(0,self.skip-1)
        if tag == 'title': self.in_title = False
        if tag in ('td','th') and self.cell is not None:
            self.row.append(' '.join(' '.join(self.cell).split()))
            self.cell = None
        if tag == 'tr' and self.row is not None:
            self.rows.append(self.row)
            self.row_tables.append(self.row_table)
            self.row = None
        if tag == 'table' and self.table_stack: self.table_stack.pop()
    def handle_data(self, data):
        if self.skip: return
        if self.in_title: self.title.append(data)
        if data.strip(): self.visible.append(' '.join(data.split()))
        if self.cell is not None: self.cell.append(data)
    @property
    def text(self): return ' '.join(self.visible)


def inspect(source, mode, response):
    body = response['body']
    text = body.decode('utf-8', errors='replace')
    doc = Document(text)
    plain = doc.text
    metadata = dict(title=' '.join(doc.title), historical_suitability='unverified')
    locators = []
    if response['status'] in (401,403):
        return 'unavailable', None, [], 'Authentication/access required; no credential retry.'
    if response['status'] != 200 or not body:
        return 'unavailable', None, [], 'No usable document returned (HTTP '+str(response['status'])+').' 
    if re.search(r'not a robot|verify that you|checking your browser', plain, re.I):
        return 'invalid', None, [], 'Robot/challenge page; stopped without bypass.'
    name = source['name']
    if name == 'POLICY':
        return 'unverified', None, [], 'Policy title/body/version not verified; shell or unauthorized API is not policy evidence.'
    if mode == 'cellar-metadata':
        try: tree = ET.fromstring(text)
        except ET.ParseError: return 'invalid', None, [], 'Cellar metadata is not valid XML.'
        work = tree.find('WORK')
        identities = set()
        if work is not None:
            for uri in [work.find('URI')] + list(work.findall('SAMEAS/URI')):
                if uri is not None: identities.add(uri.findtext('IDENTIFIER',''))
        if source['cellar_id'] not in identities:
            return 'invalid', None, [], 'Cellar work identity does not match requested CELEX.'
        metadata.update(title='Cellar metadata for CELEX '+source['cellar_id'],
                        celex=source['cellar_id'], identifiers=sorted(identities),
                        document_role='metadata only, not legal text')
        return 'retrieved', metadata, ['XML /NOTICE/WORK/URI and /NOTICE/WORK/SAMEAS'], 'Verified CELEX mapping; metadata is not a legal-text capture.'
    if name in ('SYSTEMS','EVIDENCE','CALENDAR'):
        needed = {'SYSTEMS':{'system_id','system_name','record_version'},
                  'EVIDENCE':{'record_id','system_id','evidence_state'},
                  'CALENDAR':{'action_id','system_id','source_version'}}[name]
        for index,row in enumerate(doc.rows):
            clean = [cell.strip() for cell in row]
            if needed.issubset(set(clean)):
                headers = clean
                header_set = [h for h in headers if h in needed]
                if len(header_set) != len(set(header_set)):
                    return 'unverified', metadata, [], 'Ambiguous duplicate required table header.'
                rows, row_issues = [], []
                for n, values in enumerate(doc.rows[index+1:],index+2):
                    if doc.row_tables[n-1] != doc.row_tables[index]: continue
                    # Empty spreadsheet grid slots are not business records. Google
                    # renders their row number in the leading header-labelled "1" cell.
                    if len(values) == len(headers):
                        content = values[1:] if headers[0]=='1' and values[0].isdigit() else values
                        if not any(value.strip() for value in content): continue
                    locator = 'HTML table row '+str(n)
                    id_field = 'record_id' if name=='EVIDENCE' else 'action_id' if name=='CALENDAR' else 'system_id'
                    reason = None
                    if len(values) != len(headers):
                        reason = 'Cell count does not match header count; field alignment unresolved'
                    elif not values[headers.index(id_field)].strip():
                        reason = 'Missing required '+id_field+'; business identity unresolved'
                    if reason:
                        owner = (values[headers.index('owner')] if len(values)==len(headers) and headers.count('owner')==1 else '') or 'Source owner'
                        row_issues.append(dict(locator=locator, cells=values, headers=headers,
                            reason=reason, owner=owner,
                            resolution_need='Correct or explain the source row; no field alignment or business ID inferred'))
                        continue
                    rows.append(dict(locator=locator, values=dict(zip(headers,values))))
                versions = sorted({r['values'].get('record_version') or r['values'].get('source_version') for r in rows} - {None,''})
                metadata.update(headers=headers,rows=rows,observed_versions=versions,
                                historical_suitability='provisional source labels only; row dates and meanings need stage 03/04 review')
                if row_issues:
                    metadata.update(row_issues=row_issues, record_quality='partial')
                locators = ['HTML header row '+str(index+1)]+[r['locator'] for r in rows+row_issues]
                if not rows: return 'unverified', metadata, locators, 'Expected headers present but no records verified; row issues retained.'
                return 'retrieved', metadata, locators, ('Readable disclosed register; unresolved row issues retained; record quality partial.' if row_issues else 'Readable disclosed register; revisions preserved, not certified historical completeness.')
        return 'unverified', metadata, [], 'Expected register headers not verified; JavaScript shell is not table content.'
    if name in ('OJ','AMEND','CONSOLIDATED'):
        expected = '2024/1689' if name=='OJ' else '2026/1744' if name=='AMEND' else '02024R1689'
        if expected not in plain or not re.search(r'Article\s*50',plain):
            return 'invalid', None, [], 'Requested act identity/Article 50 content not verified; landing pages do not count.'
        if name=='CONSOLIDATED':
            match = re.search(r'02024R1689\s*[—–-]\s*EN\s*[—–-]\s*(\d{2}\.\d{2}\.\d{4})\s*[—–-]\s*([\d.]+)',plain)
            if not match or match.group(1)!='27.07.2026':
                return 'unverified', metadata, [], 'Requested consolidation date/revision not verified.'
            metadata.update(celex=source['cellar_id'],version_date=match.group(1),revision=match.group(2),
                            document_role='documentation consolidation; not an authentic OJ act')
        else:
            date = '12.7.2024' if name=='OJ' else '24.7.2026'
            if date not in plain or 'REGULATION' not in plain.upper():
                return 'unverified', metadata, [], 'Publication identity/date not verified.'
            metadata.update(celex=source['cellar_id'],publication_date=date,document_role='original OJ rendition')
        metadata['historical_suitability']='identified pre-review version; full authority/timing reconciliation deferred to stage 03'
        return 'retrieved', metadata, ['Document header/version','Article 50 (or amendment references)'], 'Identity/version verified; no legal interpretation or signature verification.'
    expected = {'LAW':'Article 50','TIME':'Timeline for the Implementation','FAQ':'Transparency obligations under Article 50'}[name]
    if expected.lower() not in ' '.join(doc.title).lower() or len(plain)<1000:
        return 'invalid', None, [], 'Expected official page identity/body not verified.'
    if name=='LAW':
        basis=re.search(r'(?:as at|as of)\s+(\d{1,2}\s+\w+\s+\d{4})',plain)
        metadata['declared_text_basis']=basis.group(1) if basis else None
    if name=='FAQ':
        update=re.search(r'Last update\s+(\d{1,2}\s+\w+\s+\d{4})',plain)
        metadata['last_update']=update.group(1) if update else None
    metadata['historical_suitability']='context only; version/date suitability not a legal applicability decision'
    return 'retrieved', metadata, ['HTML title','Visible text passages'], 'Official context page retrieved; not substituted for primary authority.'


def attempts_for(source):
    attempts = [('original',source['url'],{})]
    if source['name']=='POLICY':
        attempts.append(('policy-api','https://api.notion.com/v1/pages/3ba0b700-541e-81f0-9998-d48f3b1c2856',{'Notion-Version':'2026-03-11'}))
    if source.get('cellar_id'):
        url='https://publications.europa.eu/resource/celex/'+source['cellar_id']
        attempts += [('cellar-metadata',url,{'Accept':'application/xml;notice=tree','Accept-Language':'eng'}),
                     ('cellar-content',url,{'Accept':'application/xhtml+xml','Accept-Language':'eng'})]
    return attempts


def capture(source, mode, url, headers, directory, transport=fetch):
    identifier='SOURCE-'+source['name']+'-'+mode
    start=now()
    rec=record(identifier,'Source attempt: '+source['name']+' '+mode,
               source_name=source['name'],source_role=source['source_role'],authority=source['authority'],
               locator=url,original_locator=source['url'],request_headers=headers,started_at=start,
               retrieved_at=start,retrieval_status='unavailable',content_type='unknown',
               version_metadata=None,content_hash=None,local_reference=None,mode=mode,
               diagnostic_reference=None,diagnostic_hash=None,requested_content_available=False)
    try:
        response=transport(url,headers)
        rec['response_received_at']=now()
        rec.update(http_status=response['status'],final_url=response['final_url'],redirects=response['redirects'],
                   content_type=response['content_type'])
        raw=response['body']
        if raw:
            path=Path('sources')/(identifier+'.response')
            (directory/path).parent.mkdir(parents=True,exist_ok=True)
            (directory/path).write_bytes(raw)
            rec.update(diagnostic_reference=path.as_posix(),diagnostic_hash=digest(raw))
        state,metadata,locators,reason=inspect(source,mode,response)
        rec.update(retrieval_status=state,version_metadata=metadata,locators=locators,summary=reason,
                   requested_content_available=state=='retrieved')
        if state=='retrieved':
            rec.update(local_reference=rec['diagnostic_reference'],content_hash=rec['diagnostic_hash'])
            doc=Document(raw.decode('utf-8',errors='replace'))
            extract=Path('sources')/(identifier+'.extract.json')
            save(directory/extract,dict(source_id=identifier,raw_reference=rec['local_reference'],
                 raw_hash=rec['content_hash'],metadata=metadata,locators=locators,
                 visible_text=doc.visible if mode!='cellar-metadata' else []))
            rec.update(extract_reference=extract.as_posix(),extract_hash=digest((directory/extract).read_bytes()))
        else:
            rec['resolution_need']='Authorized policy access' if source['name']=='POLICY' else 'Verify returned document/access route'
    except Exception as error:
        rec.update(summary='Attempt failed: '+type(error).__name__,technical_error=str(error),
                   resolution_need='Check network/access and retry with fresh attempts')
    rec['completed_at']=now()
    rec['retrieved_at']=rec.get('response_received_at',rec['completed_at'])
    rec['transport_limitation']='HTTP redirect observed' if rec.get('final_url','').startswith('http:') else None
    return rec


def snapshot(run_id, sequence, state, produced, consumed=(), predecessor=None, unresolved=(), status='complete'):
    return dict(schema_version='regulatory-compliance-stage-snapshot/2',snapshot_id=run_id+'-'+str(sequence),
                run_id=run_id,stage='scope' if sequence==1 else 'source-capture',sequence=sequence,
                created_at=now(),status=status,predecessor=predecessor,consumed_record_ids=list(consumed),
                produced_record_ids=produced,state=state,unresolved=list(unresolved),decisions=[])


def validate(directory, schema_path=ROOT/'snapshot.schema.json', allow_later=False):
    validator=Draft202012Validator(load(schema_path),format_checker=FormatChecker())
    paths=[directory/'snapshots/01-scope.json',directory/'snapshots/02-source-capture.json']
    first,second=[load(p) for p in paths]
    for value in (first,second): validator.validate(value)
    if first['state']['as_of']!='2026-08-26T00:00:00Z' or second['run_id']!=first['run_id']:
        raise ValueError('Review date/run identity mismatch.')
    if second['predecessor']!=dict(snapshot_id=first['snapshot_id'],path='snapshots/01-scope.json',sha256=digest(paths[0].read_bytes())):
        raise ValueError('Predecessor mismatch.')
    if not set(second['consumed_record_ids']).issubset(first['produced_record_ids']):
        raise ValueError('Unknown upstream record.')
    sources=second['state']['sources']
    if {s['source_name'] for s in sources}!=NAMES:
        raise ValueError('All ten disclosed sources must have attempts.')
    if len({s['id'] for s in sources})!=len(sources): raise ValueError('Duplicate attempt IDs.')
    for source in sources:
        for ref_key,hash_key in [('local_reference','content_hash'),('diagnostic_reference','diagnostic_hash'),('extract_reference','extract_hash')]:
            if source.get(ref_key):
                path=(directory/source[ref_key]).resolve()
                if not path.is_relative_to(directory.resolve()): raise ValueError('Evidence path escapes output.')
                if digest(path.read_bytes())!=source[hash_key]: raise ValueError('Evidence hash mismatch.')
        if source['requested_content_available'] and (not source['local_reference'] or not source['content_hash']):
            raise ValueError('Successful capture needs actual evidence.')
        if not source['requested_content_available'] and (source['content_hash'] or source['local_reference']):
            raise ValueError('Failed response cannot masquerade as requested evidence.')
    expected={s['id'] for s in sources}|{r['id'] for r in second['unresolved']}|{d['id'] for d in second['decisions']}
    if set(second['produced_record_ids'])!=expected: raise ValueError('Produced records mismatch.')
    if not allow_later and list(directory.joinpath('snapshots').glob('0[3-7]-*.json')): raise ValueError('Milestone 1 must stop at stage 02.')
    return dict(run_id=first['run_id'],schema_valid=True,evidence_hashes_valid=True,
                stages_validated=[1,2],attempt_count=len(sources),source_capture_status=second['status'],
                assessment_complete=False)


def build(manifest_path, output, transport=fetch, run_id=None, supersedes_run_id=None, change_reason=None, workflow=False):
    manifest=load(manifest_path)
    if manifest['review_date']!=REVIEW_DATE or {s['name'] for s in manifest['sources']}!=NAMES or len(manifest['sources'])!=10:
        raise ValueError('Manifest must contain the fixed date and exactly ten disclosed sources.')
    for source in manifest['sources']: check_url(source['url'])
    output=output.resolve()
    run_id=run_id or 'live-'+uuid4().hex
    if not re.fullmatch(r'live-[0-9a-f]{32}',run_id): raise ValueError('Invalid new run ID.')
    staging=output.parent/('.'+output.name+'-staging')/run_id
    staging.mkdir(parents=True,exist_ok=False)
    prior=supersedes_run_id
    if (output/'snapshots/01-scope.json').exists(): prior=load(output/'snapshots/01-scope.json')['run_id']
    if list((output/'snapshots').glob('0[3-7]-*.json')):
        raise ValueError('Refusing to replace a later-stage bundle with milestone 1.')
    scope=record('SCOPE','All Quillhaven Academy AI systems in the disclosed SYSTEMS register; individual IDs captured in stage 02.')
    first=snapshot(run_id,1,dict(as_of='2026-08-26T00:00:00Z',review_date=REVIEW_DATE,
        as_of_convention='UTC midnight serialization of assigned date, not a claim about event times',
        review_type='Article 50 live review workflow' if workflow else 'Article 50 live source-access milestone 1',systems_in_scope=['All systems in disclosed SYSTEMS register'],
        audiences=['Legal','Operations'],approval_gates=['Legal interpretation','Operations activation and approved dates'],
        scope_record=scope,supersedes_run_id=prior,change_reason=change_reason or 'Fresh source capture; milestone 1 only'),['SCOPE'])
    save(staging/'snapshots/01-scope.json',first)
    save(staging/'source-manifest.json',manifest)
    sources=[]
    for source in manifest['sources']:
        for mode,url,headers in attempts_for(source):
            sources.append(capture(source,mode,url,headers,staging,transport))
            save(staging/'attempts.json',sources)  # Durable attempt boundary.
    unresolved=[]
    for source in sources:
        for index, problem in enumerate((source.get('version_metadata') or {}).get('row_issues', []), 1):
            unresolved.append(record('UNRESOLVED-ROW-'+source['id']+'-'+str(index),
                source['source_name']+' '+problem['locator']+': '+problem['reason'], [source['id']],
                owner=problem['owner'], resolution_need=problem['resolution_need'], row_issue=problem))
    for name in sorted(NAMES):
        actual=[s for s in sources if s['source_name']==name and s['mode']!='cellar-metadata' and s['requested_content_available']]
        if not actual:
            ids=[s['id'] for s in sources if s['source_name']==name]
            unresolved.append(record('UNRESOLVED-'+name,name+' requested content is not available or not verified.',ids,
                owner='Facilitator/source owner',resolution_need='Authorized access or suitable verified source response'))
    second=snapshot(run_id,2,dict(sources=sources,review_date=REVIEW_DATE,
        downstream_stages_implemented=workflow),[s['id'] for s in sources]+[u['id'] for u in unresolved],['SCOPE'],
        dict(snapshot_id=first['snapshot_id'],path='snapshots/01-scope.json',sha256=digest((staging/'snapshots/01-scope.json').read_bytes())),
        unresolved,status='partial' if unresolved else 'complete')
    decision=record('CAPTURE-DECISION','Retain original failures alongside public Cellar alternatives; keep missing policy unresolved.',
        [s['id'] for s in sources],concern='Source completeness and provenance',options=['Abort all capture','Preserve useful evidence with gaps'],
        chosen_behavior='Prepare bounded downstream drafts' if workflow else 'Capture only; no downstream review',rationale='Missing source content must remain visible without inventing evidence.',
        tradeoffs=['Useful available evidence is retained; assessment remains incomplete.'],downstream_effect='Stages 03-07 may proceed with unresolved scope; no legal approvals' if workflow else 'No stages 03-07 or legal conclusions')
    second['decisions']=[decision]
    second['produced_record_ids'].append(decision['id'])
    save(staging/'snapshots/02-source-capture.json',second)
    result=validate(staging)
    save(staging/'capture-validation.json',result)
    output.mkdir(parents=True,exist_ok=True)
    if prior and (output/'snapshots/01-scope.json').exists():
        history=output/'history'/prior
        history.mkdir(parents=True,exist_ok=False)
        for name in ['sources','snapshots','source-manifest.json','attempts.json','capture-validation.json']:
            if (output/name).exists(): shutil.move(str(output/name),str(history/name))
    for name in ['sources','snapshots','source-manifest.json','attempts.json','capture-validation.json']:
        if (staging/name).exists(): shutil.move(str(staging/name),str(output/name))
    staging.rmdir()
    return validate(output)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,default=PACKAGE/'references/sources.json')
    parser.add_argument('--output',type=Path,default=ROOT/'deliverables')
    parser.add_argument('--validate',action='store_true')
    args=parser.parse_args()
    result=validate(args.output.resolve()) if args.validate else build(args.manifest,args.output)
    print(json.dumps(result,indent=2))
    print('Milestone 1 only. No legal conclusions, approvals, or final review package.')


if __name__=='__main__': main()
