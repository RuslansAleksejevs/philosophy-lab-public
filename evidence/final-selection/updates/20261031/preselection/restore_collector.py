"""Restore the pre-existing service at the final writer's explicit gate."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, re, subprocess, sys, time

D = Path(__file__).resolve().parent
R = D.parents[1]
target = D / 'COLLECTOR_RESTART_OBSERVATION.json'
assert (D / 'COLLECTOR_RESTORE_GATE.json').exists()
assert not target.exists() and not (D / 'FINAL_RECEIPT.json').exists()
intent = json.loads((D / 'COLLECTOR_TEMPORARY_STOP_INTENT.json').read_text())
installed = Path.home() / 'Library/LaunchAgents/org.philosophylab.collector.plist'
installed_sha = hashlib.sha256(installed.read_bytes()).hexdigest()
assert installed_sha == intent['installed_plist_sha256']
command = [sys.executable, '-B', str(R / 'scripts/collector_service.py'), 'start']
started = subprocess.run(command, cwd=R, capture_output=True, text=True)
if started.returncode:
    raise RuntimeError('Existing collector start failed: ' + started.stderr[:500])
service = 'gui/' + str(os.getuid()) + '/org.philosophylab.collector'
pid = None
deadline = time.monotonic() + 10
while time.monotonic() < deadline:
    checked = subprocess.run(['/bin/launchctl', 'print', service], capture_output=True, text=True)
    match = re.search(r'^\s*pid\s*=\s*(\d+)\s*$', checked.stdout, re.M)
    if checked.returncode == 0 and match:
        pid = int(match.group(1))
        break
    time.sleep(0.25)
assert pid and checked.returncode == 0, 'Collector PID not observed; final receipt remains gated.'
state = re.search(r'^\s*state\s*=\s*(\S+)\s*$', checked.stdout, re.M)
data = {
    'observed_at': datetime.now(timezone.utc).isoformat(),
    'start_command': command,
    'start_exit_code': started.returncode,
    'service_loaded': True,
    'observed_pid': pid,
    'observed_launchd_state': state.group(1) if state else None,
    'installed_plist_sha256': installed_sha,
    'installed_configuration_unchanged': True,
    'catchup_verified': False,
    'old_gaps_repaired': False,
    'boundary': 'Existing service loaded with an observed process. It may await the final canonical writer. This is not evidence that collection caught up or that older gaps were repaired.'
}
temporary = D / 'COLLECTOR_RESTART_OBSERVATION.pending.json'
with temporary.open('x') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')
    f.flush()
    os.fsync(f.fileno())
assert not target.exists()
os.replace(temporary, target)
print(json.dumps({'status': 'EXISTING_COLLECTOR_RESTARTED', 'pid': pid, 'catchup_verified': False}))
