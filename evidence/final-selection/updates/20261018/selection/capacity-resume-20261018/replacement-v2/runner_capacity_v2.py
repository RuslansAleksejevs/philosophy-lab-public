"""Two separately recorded replacements, each once at attempt-002; never retries or substitutes a model.

This is a versioned static derivative of frozen Dispatcher.run_one. Command,
allowlisted environment, native inspection, classification and teardown remain
calls to the frozen implementation. Importing/testing does not launch Codex.
"""
from pathlib import Path
import argparse
import fcntl
import json
import os
import sys
import threading
import time
from resolver_v2 import JOBS, ROOT, RUN, runner, load_ready, load_attempt_resolution, require

now, safe_error, save_new = runner.now, runner.safe_error, runner.save_new
check_inputs, command, digest = runner.check_inputs, runner.command, runner.digest
actual_quota, known_transport = runner.actual_quota, runner.known_transport
strict_json, visible_event = runner.strict_json, runner.visible_event
teardown, inspect_native, regular = runner.teardown, runner.inspect_native, runner.regular
classify, FAILED = runner.classify, runner.FAILED


class ReplacementDispatcher(runner.Dispatcher):
    def __init__(self, run_dir, root, ready):
        super().__init__(run_dir, root)
        self.ready = ready

    def event(self, record):
        with self.lock:
            location = self.run_dir / 'capacity-resume-20261018' / 'replacement-v2' / 'dispatch.jsonl'
            with location.open('a') as out:
                out.write(json.dumps({'at': now(), **record}, ensure_ascii=False) + '\n')
                out.flush(); os.fsync(out.fileno())

    def run_one(self, job):
        if job != self.ready["job"]:
            raise ValueError("Only exact assigned replacement job allowed")
        if self.ready["attempt"].exists():
            return {"job_id": job["id"], "status": "SKIPPED_EXISTING_002_NO_RETRY"}
        if self.stopped():
            return {"job_id": job["id"], "status": "NOT_STARTED_STOP"}
        attempt = self.run_dir / "results" / job["id"] / "attempt-002"
        sid, process, thread = None, None, None
        started, monotonic = now(), time.monotonic()
        stderr, errors, usage, fatal = [], [], [], []
        metadata = {"job_id": job["id"], "started_at": started, "prompt_sha256": job["prompt_sha256"], "schema_sha256": job["schema_sha256"],
                    "requested_model": job["model"], "requested_effort": job["effort"], "requested_service_tier": job["service_tier"],
                    "physical_attempt": 2, "replacement_ready_event_id": self.ready["ready_event_id"],
                    "failed_attempt_event_id": self.ready["failed_attempt"]["event_id"]}
        try:
            prompt, schema = check_inputs(job, self.root)
            attempt.mkdir(parents=True, exist_ok=False)
            argv = command(job, attempt, self.root)
            metadata.update(argv=argv, argv_sha256=digest(json.dumps(argv, separators=(",", ":")).encode()), auth="Forced ChatGPT subscription; environment allowlist; no API keys")
            save_new(attempt / "launch.json", metadata)
            if self.stopped():
                save_new(attempt / "not-launched.json", {**metadata, "status": "NOT_STARTED_STOP"})
                return {"job_id": job["id"], "status": "NOT_STARTED_STOP"}
            process = self.launch_process(argv)
            if process is None:
                save_new(attempt / "not-launched.json", {**metadata, "status": "NOT_STARTED_STOP"})
                return {"job_id": job["id"], "status": "NOT_STARTED_STOP"}
            self.event({"event": "job.started", "job_id": job["id"]})
            def abort(reason):
                fatal.append(safe_error(reason))
                try:
                    self.fail_stop(reason, job["id"])
                finally:
                    if process.poll() is None:
                        process.terminate()
            def drain_stderr():
                try:
                    for line in process.stderr:
                        safe = safe_error(line); stderr.append(safe)
                        if actual_quota(safe):
                            abort("ACTUAL_QUOTA: " + safe)
                        elif "retrying sampling request" in safe.lower() and not known_transport(safe):
                            abort("UNKNOWN_INTERNAL_RETRY: " + safe)
                except BaseException as exc:
                    abort("STDERR_CAPTURE_FAILURE: " + safe_error(exc))
            thread = threading.Thread(target=drain_stderr, daemon=True)
            thread.start()
            process.stdin.write(prompt.decode()); process.stdin.close()
            completed = False
            with (attempt / "visible-events.jsonl").open("x") as out:
                for line in process.stdout:
                    try:
                        event = strict_json(line)
                        visible = visible_event(event)
                    except (ValueError, TypeError, AttributeError):
                        abort("Malformed stdout event; body excluded"); continue
                    if visible is None:
                        continue
                    out.write(json.dumps(visible, ensure_ascii=False) + "\n"); out.flush()
                    if visible.get("unexpected"):
                        abort("Unexpected tool/event; body excluded")
                    if visible["type"] == "thread.started":
                        if sid is not None:
                            abort("Multiple thread.started events")
                        sid = visible["thread_id"]; self.register_session(sid)
                        self.event({"event": "job.session", "job_id": job["id"], "session_id": sid})
                    if visible["type"] in {"error", "turn.failed"}:
                        errors.append(visible["message"])
                        if actual_quota(visible["message"]) or not known_transport(visible["message"]):
                            abort(visible["message"])
                    if visible["type"] == "turn.completed":
                        if completed:
                            abort("Multiple completed turns")
                        completed = True; usage.append(visible.get("usage", {}))
                out.flush(); os.fsync(out.fileno())
            exit_code, forced = teardown(process, thread)
            if forced:
                raise ValueError("Child required forced termination after output closed")
            save_new(attempt / "stderr.json", {"lines": stderr, "exit_code": exit_code})
            if fatal:
                raise ValueError("Stopped after unsafe/unknown event: " + "; ".join(fatal))
            if not sid or (exit_code != 0 and not errors and not any(known_transport(x) for x in stderr)):
                raise ValueError("Unclassified CLI exit or missing identity")
            check_inputs(job, self.root)
            proof, visible, finals = inspect_native(sid, prompt.decode(), job, self.root)
            save_new(attempt / "native-check.json", proof)
            save_new(attempt / "native-visible.json", {"session_id": sid, "records": visible})
            if proof["isolation_failures"]:
                raise ValueError("; ".join(proof["isolation_failures"]))
            final_file = attempt / "final.txt"
            raw_final = regular(final_file, self.root).read_text() if final_file.exists() else ""
            status, flags, value = classify(finals, stderr, raw_final, schema, errors, completed, exit_code, job)
            if value is not None:
                save_new(attempt / "response.json", value)
            receipt = {**metadata, "status": status, "completed_at": now(), "elapsed_seconds": time.monotonic() - monotonic,
                       "session_id": sid, "quality_flags": flags, "usage_observed": usage, "cli_exit_code": exit_code,
                       "internal_sampling_retry_count": sum("retrying sampling request" in x.lower() for x in stderr),
                       "visible_final_count": len(finals), "model_call_count": "Unknown; CLI sessions and observed internal retries are separate.",
                       "outputs": {str(p.relative_to(self.root)): digest(regular(p, self.root).read_bytes()) for p in sorted(attempt.iterdir()) if p.is_file()},
                       "archive_boundary": "Local only; canonical output event and receipt required before dependent reading."}
            save_new(attempt / "receipt.json", receipt)
            self.event({"event": "job.finished", "job_id": job["id"], "status": status, "session_id": sid})
            return {"job_id": job["id"], "status": status, "session_id": sid}
        except BaseException as exc:
            stop_error = None
            try:
                self.fail_stop(exc, job["id"])
            except BaseException as failure:
                stop_error = safe_error(failure)
            process_state = {"process_stopped": process is None, "stderr_drained": thread is None}
            if process is not None:
                try:
                    code, killed = teardown(process, thread, terminate=True)
                    process_state = {"process_stopped": True, "stderr_drained": True, "exit_code": code, "forced_kill": killed}
                except BaseException as failure:
                    process_state = {"process_stopped": process.poll() is not None, "stderr_drained": thread is None or not thread.is_alive(), "error": safe_error(failure)}
            attempt.mkdir(parents=True, exist_ok=True)
            failure = {**metadata, "status": FAILED, "ended_at": now(), "elapsed_seconds": time.monotonic() - monotonic,
                       "session_id": sid, "error": safe_error(exc), "automatic_retry": False, "process_state": process_state,
                       "stop_record_error": stop_error}
            if not (attempt / "stderr.json").exists():
                save_new(attempt / "stderr.json", {"lines": list(stderr), "error_messages": errors, "complete": process_state["stderr_drained"]})
            save_new(attempt / "failure.json", failure)
            return {"job_id": job["id"], "status": FAILED, "session_id": sid, "error": safe_error(exc), "process_state": process_state}



def predecessor(root,run_dir,ready,events,get_object):
    jid=ready['job']['id']
    if jid==JOBS[0]:
        require(not (run_dir/'results'/JOBS[1]/'attempt-002').exists(),'Second replacement started before first was accepted')
        return None
    resolved=load_attempt_resolution(root,run_dir,root/ready['plan']['predecessor_map_receipt'],events,get_object)
    require(resolved['logical_job_id']==JOBS[0] and resolved['input_event_id']==ready['input_event_id'] and resolved['plan']['authorization']==ready['plan']['authorization'],'First replacement map/resume differs')
    return resolved


def ordinary_prerequisites(root,run_dir,input_event_id,events):
    indexed={e['id']:e for e in events};_,jobs=runner.gate(run_dir,root)
    require(len(jobs)==110,'Original110 scope changed')
    for job in jobs:
        if job['id'] in JOBS:continue
        lane=run_dir/'results'/job['id']
        receipt=strict_json(regular(lane/'ARCHIVE_RECEIPT.json',root).read_bytes())
        local=strict_json(regular(lane/'attempt-001/receipt.json',root).read_bytes())
        event=indexed.get(receipt.get('event_id'),{})
        require(receipt.get('status')=='REVIEW_ARCHIVED' and local.get('status')==runner.COMPLETE and receipt.get('input_event_id')==input_event_id,'All other108 reviews must already be accepted')
        require(event.get('kind')=='research.selection.review.completed' and event.get('run_id')==run_dir.name and event['payload']['job_id']==job['id'] and event['session_id']==local['session_id']==receipt['session_id'],'Other review has no actual acceptance')
    return jobs


def prerequisites(root,run_dir,ready,events,get_object):
    """Other108 accepted; both plans ready; M12 then M13 with canonical map."""
    jobs=ordinary_prerequisites(root,run_dir,ready['input_event_id'],events)
    sessions={}
    for job in jobs:
        for attempt in (run_dir/'results'/job['id']).glob('attempt-*'):
            require(attempt.name in ({'attempt-001','attempt-002'} if job['id'] in JOBS else {'attempt-001'}),'Unexpected physical attempt')
            for name in ('receipt.json','failure.json'):
                if (attempt/name).exists():
                    sid=strict_json(regular(attempt/name,root).read_bytes()).get('session_id')
                    if sid:
                        require(sid not in sessions or sessions[sid]==attempt,'Prior SID reused')
                        sessions[sid]=attempt
    for jid in JOBS:
        companion=load_ready(root,run_dir,run_dir/'capacity-resume-20261018/replacement-v2'/jid/'READY_RECEIPT.json',events,get_object)
        require(companion['job']['id']==jid and companion['plan']['authorization']==ready['plan']['authorization'],'Two ready plans must share the same current resume')
    predecessor(root,run_dir,ready,events,get_object)
    return sessions


def execute(root, run_dir, ready_receipt, archive, *, check_only=False):
    root, run_dir = Path(root).resolve(), Path(run_dir).resolve()
    # Same lock as frozen runner; never run beside its scheduling or another replacement.
    with (run_dir / 'dispatch.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        events = list(archive.events())
        ready = load_ready(root, run_dir, ready_receipt, events, archive.get)
        sessions = prerequisites(root, run_dir, ready, events, archive.get)
        job_id = ready["job"]["id"]
        if ready['attempt'].exists():
            return {'job_id': job_id, 'status': 'SKIPPED_EXISTING_002_NO_RETRY'}
        require(not (run_dir / 'results' / job_id / 'ARCHIVE_RECEIPT.json').exists(), 'Logical review already accepted')
        prompt, _ = check_inputs(ready['job'], root)
        proof, visible, finals = inspect_native(ready['failed_attempt']['session_id'], prompt.decode(), ready['job'], root)
        expected = strict_json((root / ready['failure_inspection']['path']).read_bytes())['native_proof']
        require(proof == expected and not proof['isolation_failures'] and not finals and not any(x['role'] == 'assistant' for x in visible), 'Failure native proof no longer supports empty-output replacement')
        worker = ReplacementDispatcher(run_dir, root, ready)
        for sid in sessions: worker.register_session(sid)
        require(not worker.stopped(), 'Stop marker preserved; no replacement launch permitted')
        if check_only:
            return {'job_id': job_id, 'status': 'REPLACEMENT_CHECK_ONLY_NO_MODEL_CALLS', 'attempt': 2}
        return worker.run_one(ready['job'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ready-receipt', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--run-dir', type=Path, default=RUN)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    sys.path.insert(0, str(args.root / 'scripts'))
    from research_archive import Archive
    result = execute(args.root, args.run_dir, args.ready_receipt, Archive(args.root / 'research/archive'), check_only=args.check_only)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__': main()
