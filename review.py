"""Fictional compliance-review demonstration; no legal decisions or approvals."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent
STAGES = ['scope', 'source-capture', 'authority-and-timing', 'evidence-reconciliation',
          'impact-analysis', 'actions-and-approvals', 'publication-validation']


def fingerprint(path):
    return 'sha256:' + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def record(identifier, summary, evidence_ids=(), **extra):
    return dict(id=identifier, summary=summary, evidence_ids=list(evidence_ids), **extra)


def analyze(data):
    """Exact checks on structured sample fields; never infer legal compliance."""
    if data.get('fictional') is not True:
        raise ValueError('This MVP accepts explicitly fictional examples only.')
    system = data['system_id']
    records = data['records'] + data['evidence']
    ids = [r['id'] for r in records]
    if len(ids) != len(set(ids)) or any(not isinstance(i, str) or not i for i in ids):
        raise ValueError('Input record IDs must be unique nonempty strings.')
    if any(r['system_id'] != system for r in records):
        raise ValueError('This single-system demo cannot mix system IDs.')
    gaps, conflicts = [], []
    for index, kind in enumerate(data['required_evidence'], 1):
        matches = [r for r in data['evidence'] if r['kind'] == kind]
        valid = any(r.get('status') == 'available' and r.get('content') for r in matches)
        if not valid:
            gaps.append(record('GAP-' + str(index), 'Missing or incomplete evidence: ' + kind,
                               [r['id'] for r in matches], owner='Demo system owner'))
    values = [(r['id'], r['notice_enabled']) for r in data['records']
              if 'notice_enabled' in r]
    if any(not isinstance(v, bool) for _, v in values):
        raise ValueError('notice_enabled must be true or false.')
    if len({v for _, v in values}) > 1:
        conflicts.append(record('CONFLICT-1', 'Records disagree about notice_enabled.',
                                [i for i, _ in values], claims=dict(values), owner='Demo system owner'))
    return gaps, conflicts


def safe_artifact(directory, relative):
    path = (directory / relative).resolve()
    if not path.is_relative_to(directory.resolve()):
        raise ValueError('Artifact path escapes the run directory.')
    return path


def validate_run(directory, schema_path=ROOT / 'snapshot.schema.json'):
    """Check the schema, hashes, record references, and demo decision controls."""
    directory = Path(directory)
    schema = read_json(schema_path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    paths = sorted(directory.glob('[0-9][0-9]-*.json'))
    if len(paths) != 7:
        raise ValueError('Expected exactly seven stage snapshots.')
    snapshots = [read_json(p) for p in paths]
    known, previous, run_id = set(), None, snapshots[0]['run_id']
    for index, (path, snap) in enumerate(zip(paths, snapshots), 1):
        validator.validate(snap)
        if snap['sequence'] != index or snap['stage'] != STAGES[index - 1]:
            raise ValueError('Stages are out of order.')
        if snap['run_id'] != run_id or not snap['state'].get('fictional'):
            raise ValueError('Run identity or fictional label is inconsistent.')
        if not set(snap['consumed_record_ids']).issubset(known):
            raise ValueError('Consumed record does not exist in an earlier stage.')
        if previous:
            expected = dict(snapshot_id=previous['snapshot_id'], path=paths[index-2].name,
                            sha256=fingerprint(paths[index-2]))
            if snap['predecessor'] != expected:
                raise ValueError('Predecessor ID, path, or hash does not match.')
        produced = set(snap['produced_record_ids'])
        if produced & known:
            raise ValueError('Produced IDs must be new within a run.')
        visible = known | produced
        found = set()
        def inspect(value):
            if isinstance(value, dict):
                if 'id' in value:
                    found.add(value['id'])
                if 'evidence_ids' in value and not set(value['evidence_ids']).issubset(visible):
                    raise ValueError('Evidence reference does not exist.')
                for child in value.values():
                    inspect(child)
            elif isinstance(value, list):
                for child in value:
                    inspect(child)
        inspect(snap)
        if not produced.issubset(found):
            raise ValueError('A produced ID has no saved record.')
        known |= produced
        previous = snap
    approvals = snapshots[5]['state']['approval_requirements']
    if any(a['status'] != 'pending' for a in approvals):
        raise ValueError('The fictional demo cannot approve decisions.')
    if snapshots[6]['state']['publication_status'] != 'blocked':
        raise ValueError('Final publication must remain blocked pending human review.')
    for artifact in snapshots[6]['state']['artifacts']:
        target = safe_artifact(directory, artifact['path'])
        if fingerprint(target) != artifact['sha256']:
            raise ValueError('Artifact hash does not match: ' + artifact['path'])
    return {'snapshots_validated': 7, 'schema_valid': True,
            'references_and_hashes_valid': True, 'human_approvals': 'pending',
            'final_publication': 'blocked'}


def build(input_path, output_root):
    data = read_json(input_path)
    gaps, conflicts = analyze(data)
    run_id = 'demo-' + uuid4().hex[:12]
    directory = Path(output_root) / run_id
    directory.mkdir(parents=True, exist_ok=False)
    # Preserve the exact input used so later changes do not alter this run's evidence.
    (directory / 'input.json').write_bytes(Path(input_path).read_bytes())
    now = datetime.now(timezone.utc).isoformat()
    source = record('SOURCE-001', 'Fictional input bundle; not a legal authority.',
                    source_role='other', authority='unknown', locator='input.json',
                    retrieved_at=now, retrieval_status='retrieved', content_type='application/json',
                    version_metadata={'fictional': True}, content_hash=fingerprint(directory/'input.json'),
                    local_reference='input.json')
    change = record(data['change']['id'], data['change']['summary'], ['SOURCE-001'])
    legal = record('LEGAL-QUESTION', 'Legal must determine applicability; no binding law supplied.',
                   [change['id']], owner='Legal')
    issues = [legal] + gaps + conflicts
    facts = [record(r['id'], json.dumps(r, sort_keys=True), ['SOURCE-001']) for r in data['records']]
    evidence = [record(r['id'], json.dumps(r, sort_keys=True), ['SOURCE-001']) for r in data['evidence']]
    impacts = [record('IMPACT-' + str(i), issue['summary'], [issue['id']],
                      state='conflicting' if issue in conflicts else 'unresolved')
               for i, issue in enumerate(issues, 1)]
    actions = [record('ACTION-' + str(i), 'Review and resolve: ' + issue['summary'],
                      [issue['id']], owner=issue.get('owner'), proposed_date=data.get('proposed_date'),
                      approved_date=None, approval_status='pending', activation_allowed=False)
               for i, issue in enumerate(issues, 1)]
    approvals = [record('APPROVAL-LEGAL', 'Final interpretation requires Legal review.',
                        [legal['id']], owner='Legal', status='pending'),
                 record('APPROVAL-OPS', 'Activation and approved deadlines require Operations review.',
                        [a['id'] for a in actions], owner='Operations', status='pending')]
    states = [
        dict(as_of=now, review_type='fictional demonstration', systems_in_scope=[data['system_id']],
             audiences=['Legal', 'Operations'], approval_gates=['Legal interpretation', 'Operations activation and dates'],
             scope_record=record('SCOPE-001', 'One fictional system and proposed change.')),
        dict(sources=[source], example_change=change),
        dict(binding_rules=[], timing_rules=[], guidance_context=[], authority_blockers=[legal]),
        dict(system_facts=facts, policy_controls=evidence, incident_evidence=[], conflicts=conflicts, evidence_gaps=gaps),
        dict(impacts=impacts, unaffected_items=[], conflicts=conflicts, unresolved_items=issues),
        dict(proposed_actions=actions, approval_requirements=approvals, escalations=[legal]),
    ]
    produced = [['SCOPE-001'], [source['id'], change['id']], [legal['id']],
                [r['id'] for r in facts+evidence+gaps+conflicts], [r['id'] for r in impacts],
                [r['id'] for r in actions+approvals]]
    known, previous, previous_path = [], None, None
    def save(index, state, new_ids):
        nonlocal previous, previous_path
        decision = record('DECISION-' + str(index), 'Preserve draft status and human authority.',
                          rationale='Synthetic evidence cannot establish legal compliance.',
                          tradeoffs=['Human review remains necessary.'])
        snap = dict(schema_version='regulatory-compliance-stage-snapshot/2',
                    snapshot_id=run_id + '-stage-' + str(index), run_id=run_id,
                    stage=STAGES[index-1], sequence=index, created_at=now,
                    status='complete' if index <= 2 else 'blocked' if index in (3,6,7) else 'partial',
                    predecessor=None if previous is None else dict(snapshot_id=previous['snapshot_id'],
                        path=previous_path.name, sha256=fingerprint(previous_path)),
                    consumed_record_ids=list(known), produced_record_ids=new_ids+[decision['id']],
                    state=dict(state, fictional=True), unresolved=[] if index <= 2 else ([legal] if index == 3 else issues),
                    decisions=[decision])
        path = directory / (str(index).zfill(2) + '-' + STAGES[index-1] + '.json')
        write_json(path, snap)
        known.extend(snap['produced_record_ids'])
        previous, previous_path = snap, path
    for index, state in enumerate(states, 1):
        save(index, state, produced[index-1])
    lines = ['# Fictional regulatory change review — DRAFT', '',
             'Training example only. No real law was reviewed. No legal conclusion, compliance approval,',
             'activation authorization, or approved deadline is issued.', '',
             'Run: ' + run_id, 'System: ' + data['system_id'],
             'Example change: ' + data['change']['title'], '',
             '## Evidence issues', '']
    for issue in issues:
        lines.append('- ' + issue['id'] + ': ' + issue['summary'] + ' Evidence: ' + ', '.join(issue['evidence_ids']))
        if 'claims' in issue:
            lines.append('  Competing claims: ' + json.dumps(issue['claims'], sort_keys=True))
    lines += ['', '## Impact register', '', '| ID | Finding | State | Evidence |', '|---|---|---|---|']
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    for impact in impacts:
        lines.append('| ' + ' | '.join(cell(v) for v in [impact['id'], impact['summary'], impact['state'], ', '.join(impact['evidence_ids'])]) + ' |')
    lines += ['', '## Draft action calendar', '', '| ID | Task | Owner | Proposed date | Approved date | Approval |', '|---|---|---|---|---|---|']
    for action in actions:
        lines.append('| ' + ' | '.join(cell(v) for v in [action['id'], action['summary'], action['owner'], action['proposed_date'] or 'Unknown', 'None', 'Pending']) + ' |')
    lines += ['', '## Legal and Operations review', '',
              '- Legal: resolve applicability and interpretation; no binding legal source has been supplied.',
              '- Operations: review owners, dependencies, activation, and proposed dates. All approvals are pending.',
              '- Final publication and activation remain blocked. File validity is not compliance approval.', '',
              '## Source and history', '', 'Exact fictional input: [input.json](input.json).',
              'Every run is saved separately; previous runs are never overwritten.',
              'Cross-run comparison and live register updates are not implemented.', '']
    report = directory / 'review-report.md'
    report.write_text('\n'.join(lines), encoding='utf-8')
    artifacts = [dict(id='ARTIFACT-REPORT', path=report.name, sha256=fingerprint(report), validation_status='valid'),
                 dict(id='ARTIFACT-INPUT', path='input.json', sha256=fingerprint(directory/'input.json'), validation_status='valid')]
    check = record('CHECK-001', 'Draft artifacts exist and were fingerprinted; full run validation is recorded separately.')
    save(7, dict(artifacts=artifacts, validation_checks=[check], publication_status='blocked'),
         [a['id'] for a in artifacts]+[check['id']])
    result = validate_run(directory)
    write_json(directory / 'validation-results.json', result)
    return directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT/'sample-data/review.json')
    parser.add_argument('--output', type=Path, default=ROOT/'outputs')
    parser.add_argument('--validate', type=Path, help='Validate an existing run instead of generating one.')
    args = parser.parse_args()
    if args.validate:
        print(json.dumps(validate_run(args.validate), indent=2))
    else:
        directory = build(args.input, args.output)
        print('Created and validated seven snapshots: ' + str(directory))
        print('Read review-report.md. Final publication is BLOCKED; approvals are PENDING.')


if __name__ == '__main__':
    main()
