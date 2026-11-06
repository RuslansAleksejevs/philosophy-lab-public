#!/usr/bin/env python3
"""Prepare/install/control the explicitly authorized local launchd collector."""
import argparse
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys

from research_archive import _safe_path

LABEL='org.philosophylab.collector'


def plist(root):
    interpreter=Path('/opt/homebrew/bin/python3')
    if not interpreter.is_file(): interpreter=Path(sys.executable)
    return {'Label':LABEL,'ProgramArguments':[str(interpreter),'-B',str(root/'scripts/collector.py'),'--root',str(root),'watch'],
            'WorkingDirectory':str(root),'RunAtLoad':True,'KeepAlive':True,'ThrottleInterval':30,
            'ProcessType':'Background','Umask':0o077,
            'StandardOutPath':str(root/'collector/runtime/service-out.log'),
            'StandardErrorPath':str(root/'collector/runtime/service-error.log')}


def main():
    p=argparse.ArgumentParser(); p.add_argument('command',choices=['prepare','install','start','stop','status'])
    args=p.parse_args(); root=Path(__file__).resolve().parents[1]; os.umask(0o077)
    staged=_safe_path(root/'collector'/ (LABEL+'.plist'))
    target=Path.home()/'Library/LaunchAgents'/(LABEL+'.plist'); domain='gui/'+str(os.getuid()); service=domain+'/'+LABEL
    if args.command=='prepare':
        staged.write_bytes(plistlib.dumps(plist(root),sort_keys=True)); os.chmod(staged,0o600)
        print(staged); return 0
    if args.command=='install':
        expected=plistlib.dumps(plist(root),sort_keys=True)
        if staged.read_bytes()!=expected: raise ValueError('staged launchd configuration differs from current project')
        _safe_path(target)
        if target.exists() and target.read_bytes()!=expected:
            raise ValueError('existing launch agent differs; preserve/review it before replacing')
        if not target.exists():
            target.parent.mkdir(exist_ok=True,parents=True)
            with target.open('xb') as f: f.write(expected); f.flush(); os.fsync(f.fileno())
            os.chmod(target,0o600)
        loaded=subprocess.run(['/bin/launchctl','print',service],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
        if not loaded: subprocess.run(['/bin/launchctl','bootstrap',domain,str(target)],check=True)
        print('Installed and loaded '+service); return 0
    if args.command=='start':
        expected=plistlib.dumps(plist(root),sort_keys=True)
        _safe_path(target)
        if not target.exists() or target.read_bytes()!=expected:
            raise ValueError('install exact reviewed service configuration before starting')
        loaded=subprocess.run(['/bin/launchctl','print',service],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
        if not loaded: subprocess.run(['/bin/launchctl','bootstrap',domain,str(target)],check=True)
        subprocess.run(['/bin/launchctl','kickstart',service],check=True); return 0
    if args.command=='stop':
        subprocess.run(['/bin/launchctl','bootout',service],check=True)
        from collector import atomic_json, now
        atomic_json(root/'collector/runtime/status.json',{'status':'STOPPED','checked_at':now(),'interval_seconds':10})
        print('Unloaded; installed login configuration remains.'); return 0
    loaded=subprocess.run(['/bin/launchctl','print',service],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
    from collector import status
    try: report=status(root)
    except (OSError,ValueError,KeyError) as exc: report={'status':'UNKNOWN','error_type':type(exc).__name__}
    service_healthy=loaded and report.get('fresh',False) and report.get('status')=='RUNNING'
    from collector import coverage_summary
    coverage_healthy=report.get('coverage_healthy',coverage_summary(report.get('sessions'))['coverage_healthy'])
    healthy=bool(service_healthy and coverage_healthy is True)
    print(json.dumps({'loaded':loaded,'service_healthy':service_healthy,'coverage_healthy':coverage_healthy,
                      'healthy':healthy,'collector':report},ensure_ascii=False,indent=2))
    return 0 if healthy else 1


if __name__=='__main__':
    sys.exit(main())
