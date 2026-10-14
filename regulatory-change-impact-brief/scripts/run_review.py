"""One fresh read-only run, seven boundaries, verified drafts, history and recovery."""
import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
from uuid import uuid4
sys.path.insert(0,str(Path(__file__).resolve().parent))
import publish_drafts as p
c=p.c
CONTROL={'history','workflow-attempts','.workflow.lock'}

def atomic(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(path.name+'.tmp-'+uuid4().hex)
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    os.replace(temporary,path)

def child(root,name):
    root=root.resolve();result=root/name
    if not result.resolve().is_relative_to(root) or result.is_symlink(): raise ValueError('Unsafe local path')
    return result

def inventory(path):
    if path.is_symlink(): raise ValueError('Links cannot be archived/promoted')
    if path.is_file(): return {'':c.digest(path.read_bytes())}
    result={}
    for entry in sorted(path.rglob('*')):
        if entry.is_symlink() or not entry.resolve().is_relative_to(path.resolve()): raise ValueError('Linked/escaping evidence is not copied')
        if entry.is_file(): result[entry.relative_to(path).as_posix()]=c.digest(entry.read_bytes())
    return result

def payload(output):
    return sorted(x.name for x in output.iterdir() if x.name not in CONTROL)

def inspect(output):
    identities=set();missing=[name for name in ['snapshots/'+x for x in p.FILES]+p.ARTIFACTS if not (output/name).exists()]
    issues=[dict(path=name,error='Missing required output') for name in missing]
    parsed={}
    validator=p.Draft202012Validator(c.load(c.ROOT/'snapshot.schema.json'),format_checker=p.FormatChecker())
    for name in p.FILES:
        try:
            snapshot=c.load(output/'snapshots'/name);rid=snapshot['run_id']
            if isinstance(rid,str) and re.fullmatch(r'[A-Za-z0-9_-]{1,100}',rid): identities.add(rid)
            validator.validate(snapshot)
            parsed[name]=snapshot
        except Exception as exc:
            issues.append(dict(path='snapshots/'+name,error='Unreadable/invalid snapshot: '+getattr(exc,'message',str(exc))))
    def check_hash(path,expected,basis):
        try:
            target=child(output,path)
            if not target.is_file(): raise ValueError('Referenced file is missing')
            if c.digest(target.read_bytes())!=expected: raise ValueError('Referenced hash mismatch')
        except (OSError,ValueError,TypeError) as exc: issues.append(dict(path=str(path),basis=basis,error=str(exc)))
    for name,snapshot in parsed.items():
        pred=snapshot.get('predecessor')
        if isinstance(pred,dict): check_hash(pred['path'],pred['sha256'],'predecessor of '+name)
    for source in parsed.get(p.FILES[1],{}).get('state',{}).get('sources',[]):
        for ref,hash_key in [('local_reference','content_hash'),('diagnostic_reference','diagnostic_hash'),('extract_reference','extract_hash')]:
            if source.get(ref): check_hash(source[ref],source.get(hash_key),source.get('id','Source capture'))
    for artifact in parsed.get(p.FILES[6],{}).get('state',{}).get('artifacts',[]):
        check_hash(artifact['path'],artifact['sha256'],artifact['id'])
    if len(identities)>1: issues.append(dict(path='snapshots/',error='Multiple run IDs found',run_ids=sorted(identities)))
    try:
        validation=p.validate(output);valid=True;error=None
    except Exception as exc:
        valid=False;validation=None;error=type(exc).__name__+': '+str(exc)
    return dict(inspected_at=c.now(),run_id=next(iter(identities)) if len(identities)==1 else None,
        observed_run_ids=sorted(identities),valid=valid and not issues,validation=validation,error=error,missing_files=missing,issues=issues,
        available_inventory={name:inventory(child(output,name)) for name in payload(output)})

def copy_entry(source,target):
    if target.exists(): raise ValueError('Refusing to overwrite retained history')
    if source.is_dir(): shutil.copytree(source,target)
    else: shutil.copy2(source,target)
    if inventory(source)!=inventory(target): raise ValueError('Archive copy verification failed')

def archive(output,previous,attempt_id):
    label=previous['run_id'] or 'unidentified-'+attempt_id
    base=child(output,'history')/label
    base.mkdir(parents=True,exist_ok=True)
    # Existing development/history occurrences are retained; never merge different evidence.
    names=list(previous['available_inventory'])
    destination=base if not any((base/name).exists() for name in names+['archive-record.json']) else base/('preserved-'+attempt_id)
    destination.mkdir(parents=True,exist_ok=True)
    for name in names:
        copy_entry(child(output,name),child(destination,name))
        if inventory(child(destination,name))!=previous['available_inventory'][name]:
            raise ValueError('Current payload changed during archive; inspect retained copies before retry')
    atomic(destination/'archive-record.json',dict(archived_at=c.now(),attempt_id=attempt_id,prior_inspection=previous,
        note='Only available bytes retained; pre-existing missing/corrupt evidence not recreated'))
    return destination

def restore_interrupted(output,attempt,journal):
    # Recovery preserves the observed mixed/current payload before restoring verified old bytes.
    archived=Path(journal['archive_path']) if journal.get('archive_path') else None
    if archived and not archived.resolve().is_relative_to((output/'history').resolve()): raise ValueError('Unsafe recovery archive')
    previous=journal['prior_inspection']['available_inventory'] if journal.get('prior_inspection') else {}
    for name,expected in previous.items():
        if inventory(child(archived,name))!=expected: raise ValueError('Recovery archive missing/damaged: '+name)
    observed=attempt/('recovery-observed-'+uuid4().hex);observed.mkdir()
    atomic(observed/'observed-inventory.json',{n:inventory(child(output,n)) for n in payload(output)})
    for name in payload(output):
        source=child(output,name);target=child(observed,name);source.rename(target)
    for name in previous: copy_entry(child(archived,name),child(output,name))
    journal.update(status='failed',phase='recovered-interruption',finished_at=c.now(),
        failure=dict(stage='promotion',error='Interrupted promotion recovered',resolution_need='Retry with fresh required source attempts',owner='Learner'),
        recovered_observed_path=str(observed))
    atomic(attempt/'journal.json',journal)

def recover(output):
    for path in sorted((output/'workflow-attempts').glob('*/journal.json')):
        value=c.load(path)
        if value.get('status')!='running': continue
        if value.get('phase') in {'promoting','recovering'}:
            value['phase']='recovering';atomic(path,value)
            restore_interrupted(output,path.parent,value)
        else:
            value.update(status='failed',finished_at=c.now(),failure=dict(stage=value.get('phase'),error='Interrupted earlier attempt',
                owner='Learner',resolution_need='Retained candidate is not reused; retry with fresh source attempts'))
            atomic(path,value)

def pid_alive(pid):
    if not isinstance(pid,int) or pid<=0: return False
    if os.name=='nt':
        import ctypes
        from ctypes import wintypes
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
        kernel.OpenProcess.restype=wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)]
        kernel.CloseHandle.argtypes=[wintypes.HANDLE]
        handle=kernel.OpenProcess(0x1000,False,pid)
        if not handle:
            if ctypes.get_last_error()==5: raise ValueError('Cannot establish lock owner state; inspect manually')
            return False
        code=wintypes.DWORD()
        try:
            if not kernel.GetExitCodeProcess(handle,ctypes.byref(code)): raise ValueError('Cannot check lock process')
            return code.value==259
        finally: kernel.CloseHandle(handle)
    try: os.kill(pid,0);return True
    except ProcessLookupError: return False

def acquire(output):
    lock=output/'.workflow.lock'
    if lock.exists():
        value=c.load(lock)
        if not isinstance(value.get('pid'),int) or isinstance(value.get('pid'),bool) or value['pid']<=0:
            raise ValueError('Lock owner is unknown; preserve lock and inspect manually')
        if pid_alive(value.get('pid')): raise ValueError('Another workflow owns the lock; do not run concurrently')
        retained=output/'workflow-attempts'/('stale-lock-'+uuid4().hex)
        retained.mkdir(parents=True);lock.rename(retained/'lock.json')
    with lock.open('x',encoding='utf-8') as stream: json.dump(dict(pid=os.getpid(),created_at=c.now()),stream)
    return lock

def promote(output,bundle,attempt,journal,hook=None):
    displaced=attempt/'displaced-current';displaced.mkdir()
    journal.update(phase='promoting',candidate_inventory={x.name:inventory(x) for x in bundle.iterdir()})
    atomic(attempt/'journal.json',journal)
    for name in payload(output): child(output,name).rename(child(displaced,name))
    for index,entry in enumerate(sorted(bundle.iterdir())):
        entry.rename(child(output,entry.name))
        if hook: hook(index)
    p.validate(output)  # Inspect actual canonical files, never the prior validation report.
    journal.update(status='finished',phase='promoted',finished_at=c.now())
    atomic(attempt/'journal.json',journal)

def run(manifest,output,reason='Fresh source retrieval and full review-only recomputation',transport=None,stage_hook=None,promotion_hook=None):
    output=output.resolve()
    if output==c.ROOT or output in c.ROOT.parents or output.name in {'.git','.agents','.codex'}: raise ValueError('Output must be a dedicated bundle directory')
    output.mkdir(parents=True,exist_ok=True)
    lock=acquire(output)
    attempt=None;journal=None
    try:
        recover(output)
        previous=inspect(output) if payload(output) else None
        rid='live-'+uuid4().hex
        attempt=output/'workflow-attempts'/rid;attempt.mkdir(parents=True)
        journal=dict(run_id=rid,status='running',phase='archive',started_at=c.now(),reason=reason,prior_inspection=previous)
        atomic(attempt/'journal.json',journal)
        archived=archive(output,previous,rid) if previous else None
        journal.update(archive_path=str(archived) if archived else None,phase='capture')
        atomic(attempt/'journal.json',journal)
        bundle=attempt/'bundle'
        c.build(manifest,bundle,transport=transport or c.fetch,run_id=rid,supersedes_run_id=previous['run_id'] if previous else None,
            change_reason=reason+('; prior bundle invalid: '+previous['error'] if previous and not previous['valid'] else ''),workflow=True)
        for phase,build in [('authority-and-evidence',p.a.r.build),('impacts-and-actions',p.a.build),('final-drafts',p.build)]:
            journal['phase']=phase;atomic(attempt/'journal.json',journal)
            if stage_hook: stage_hook(phase)
            build(bundle)
        validation=p.validate(bundle)
        result=dict(**validation,workflow_status='finished',source_attempt_count=len(c.load(bundle/'attempts.json')),
            supersedes_run_id=previous['run_id'] if previous else None,prior_bundle_valid=previous['valid'] if previous else None,
            history_path=str(archived) if archived else None,attempt_path=str(attempt),finished_at=c.now())
        atomic(bundle/'workflow-result.json',result)
        promote(output,bundle,attempt,journal,promotion_hook)
        p.validate(output)
        return result
    except BaseException as exc:
        if attempt and journal:
            phase=journal['phase']
            if phase=='promoting':
                try:
                    journal['phase']='recovering';atomic(attempt/'journal.json',journal)
                    restore_interrupted(output,attempt,journal)
                except Exception as recovery_error:
                    journal.update(status='running',phase='recovering',recovery_error=str(recovery_error))
                    atomic(attempt/'journal.json',journal)
            if journal.get('phase')!='recovering':
                journal.update(status='failed',finished_at=c.now(),failure=dict(stage=phase,error=type(exc).__name__+': '+str(exc),
                    owner='Learner',resolution_need='Inspect retained candidate/archive and retry the command with fresh source attempts'))
                atomic(attempt/'journal.json',journal)
        raise
    finally:
        # Release only this process's lock; keep malformed/changed lock evidence for investigation.
        if lock.exists() and c.load(lock).get('pid')==os.getpid(): lock.unlink()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,default=c.PACKAGE/'references/sources.json')
    parser.add_argument('--output',type=Path,default=c.ROOT/'deliverables')
    parser.add_argument('--reason',default='Fresh source retrieval and full review-only recomputation')
    parser.add_argument('--validate',action='store_true')
    args=parser.parse_args()
    try: result=p.validate(args.output) if args.validate else run(args.manifest,args.output,args.reason)
    except Exception as exc:
        failure=dict(created_at=c.now(),stage='workflow',error=type(exc).__name__+': '+str(exc),owner='Learner',
            resolution_need='Inspect workflow-attempts journals and retained files; retry only with fresh source retrieval')
        if args.output.exists():
            try: atomic(args.output/'workflow-attempts'/('failure-'+uuid4().hex)/'failure.json',failure)
            except OSError as persistence_error: failure['failure_record_write_error']=str(persistence_error)
        print(json.dumps(failure,indent=2));return 1
    print(json.dumps(result,indent=2));return 0

if __name__=='__main__': raise SystemExit(main())
