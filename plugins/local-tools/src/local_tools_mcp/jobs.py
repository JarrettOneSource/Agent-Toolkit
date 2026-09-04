from __future__ import annotations

import datetime as dt
import json
import os
import signal
import subprocess
import threading
import time
import uuid
from collections import deque
from pathlib import Path
from typing import TextIO

from .json_types import JsonObject

DEFAULT_JOB_ROOT = Path.home() / ".codex" / "local-tools" / "jobs"


JOB_ROOT = Path(os.environ.get("LOCAL_TOOLS_MCP_JOB_ROOT", str(DEFAULT_JOB_ROOT))).expanduser()


STATE_FILE = JOB_ROOT / "jobs.json"


TERMINAL_STATUSES = {"completed", "failed", "timed_out", "cancelled", "exited_unknown", "start_failed"}


LOCK = threading.RLock()


JOB_CONDITION = threading.Condition(LOCK)


FILE_LOCK = threading.RLock()


JOBS: dict[str, JsonObject] = {}


PROCESSES: dict[str, subprocess.Popen[str]] = {}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def ensure_storage() -> None:
    JOB_ROOT.mkdir(parents=True, exist_ok=True)


def load_jobs() -> None:
    ensure_storage()
    if not STATE_FILE.exists():
        return
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if isinstance(data, dict):
        jobs = data.get("jobs")
        if isinstance(jobs, dict):
            with LOCK:
                JOBS.update({str(key): value for key, value in jobs.items() if isinstance(value, dict)})


def save_jobs() -> None:
    ensure_storage()
    tmp_path = STATE_FILE.with_suffix(".json.tmp")
    with LOCK:
        payload = {"updated_at": utc_now(), "jobs": JOBS}
        tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        tmp_path.replace(STATE_FILE)


def process_exists(pid: int | None) -> bool:
    if not pid or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def job_paths(job_id: str) -> dict[str, str]:
    job_dir = JOB_ROOT / job_id
    return {
        "job_dir": str(job_dir),
        "stdout_path": str(job_dir / "stdout.log"),
        "stderr_path": str(job_dir / "stderr.log"),
        "combined_path": str(job_dir / "combined.log"),
        "events_path": str(job_dir / "events.jsonl"),
    }


def write_combined(job_id: str, stream_name: str, line: str) -> None:
    timestamp = utc_now()
    with LOCK:
        metadata = JOBS.get(job_id)
        if metadata is not None:
            paths = {
                "combined_path": metadata["combined_path"],
                "events_path": metadata["events_path"],
            }
        else:
            return

    clean_line = line.rstrip("\n")
    combined_line = f"{timestamp} {stream_name}: {clean_line}\n"
    event_line = json.dumps(
        {"timestamp": timestamp, "job_id": job_id, "stream": stream_name, "line": clean_line},
        separators=(",", ":"),
    )
    with FILE_LOCK:
        with open(paths["combined_path"], "a", encoding="utf-8", errors="replace") as combined:
            combined.write(combined_line)
        with open(paths["events_path"], "a", encoding="utf-8", errors="replace") as events:
            events.write(event_line + "\n")

    with LOCK:
        metadata = JOBS.get(job_id)
        if metadata is not None:
            metadata["last_output_at"] = timestamp
            metadata["output_line_count"] = int(metadata.get("output_line_count") or 0) + 1
            JOB_CONDITION.notify_all()


def stream_reader(job_id: str, stream_name: str, stream: TextIO, output_path: str) -> None:
    try:
        with open(output_path, "a", encoding="utf-8", errors="replace") as output:
            for line in iter(stream.readline, ""):
                output.write(line)
                output.flush()
                write_combined(job_id, stream_name, line)
    finally:
        try:
            stream.close()
        except OSError:
            pass


def terminate_process_group(pid: int, *, grace_seconds: float) -> None:
    try:
        pgid = os.getpgid(pid)
    except ProcessLookupError:
        return

    try:
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        return

    deadline = time.monotonic() + grace_seconds
    while time.monotonic() < deadline:
        if not process_exists(pid):
            return
        time.sleep(0.1)

    try:
        os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:
        return


def finalize_job(
    job_id: str,
    exit_code: int | None,
    *,
    timed_out: bool = False,
    cancelled: bool = False,
) -> None:
    finished_at = utc_now()
    with LOCK:
        metadata = JOBS.get(job_id)
        if metadata is None:
            return

        prior_status = metadata.get("status")
        if timed_out or prior_status == "timeout_requested":
            status = "timed_out"
        elif cancelled or prior_status == "cancel_requested":
            status = "cancelled"
        elif exit_code == 0:
            status = "completed"
        else:
            status = "failed"

        metadata.update(
            {
                "status": status,
                "exit_code": exit_code,
                "finished_at": finished_at,
                "updated_at": finished_at,
            }
        )
        PROCESSES.pop(job_id, None)
        save_jobs()
        JOB_CONDITION.notify_all()


def watcher(
    job_id: str, proc: subprocess.Popen[str], threads: list[threading.Thread], max_runtime: float | None
) -> None:
    timed_out = False
    try:
        if max_runtime is None:
            exit_code = proc.wait()
        else:
            try:
                exit_code = proc.wait(timeout=max_runtime)
            except subprocess.TimeoutExpired:
                timed_out = True
                terminate_process_group(proc.pid, grace_seconds=5.0)
                exit_code = proc.wait()
    except (OSError, subprocess.SubprocessError) as exc:
        with LOCK:
            JOBS[job_id]["error"] = str(exc)
            save_jobs()
        terminate_process_group(proc.pid, grace_seconds=5.0)
        exit_code = proc.wait()

    for thread in threads:
        thread.join(timeout=2.0)

    with LOCK:
        cancelled = JOBS.get(job_id, {}).get("status") == "cancel_requested"
    finalize_job(job_id, exit_code, timed_out=timed_out, cancelled=cancelled)


def start_process_job(
    *,
    command: str,
    cwd: str,
    shell: str,
    env_update: dict[str, str] | None,
    kind: str,
    max_runtime_seconds: float | None,
    origin: JsonObject | None = None,
) -> JsonObject:
    ensure_storage()
    job_id = f"job_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:10]}"
    paths = job_paths(job_id)
    Path(paths["job_dir"]).mkdir(parents=True, exist_ok=False)
    for key in ("stdout_path", "stderr_path", "combined_path", "events_path"):
        Path(paths[key]).touch()

    now = utc_now()
    metadata: JsonObject = {
        "job_id": job_id,
        "kind": kind,
        "command": command,
        "cwd": cwd,
        "shell": shell,
        "status": "starting",
        "pid": None,
        "pgid": None,
        "exit_code": None,
        "created_at": now,
        "started_at": None,
        "finished_at": None,
        "updated_at": now,
        "last_output_at": None,
        "output_line_count": 0,
        "max_runtime_seconds": max_runtime_seconds,
        "origin": origin,
        **paths,
    }

    with LOCK:
        JOBS[job_id] = metadata
        save_jobs()

    child_env = os.environ.copy()
    if env_update:
        child_env.update(env_update)

    try:
        proc = subprocess.Popen(
            [shell, "-lc", command],
            cwd=cwd,
            env=child_env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            start_new_session=True,
        )
    except Exception as exc:
        finished_at = utc_now()
        with LOCK:
            metadata.update(
                {
                    "status": "start_failed",
                    "error": str(exc),
                    "finished_at": finished_at,
                    "updated_at": finished_at,
                }
            )
            save_jobs()
        return metadata.copy()

    try:
        pgid = os.getpgid(proc.pid)
    except ProcessLookupError:
        pgid = None

    with LOCK:
        metadata.update(
            {
                "status": "running",
                "pid": proc.pid,
                "pgid": pgid,
                "started_at": utc_now(),
                "updated_at": utc_now(),
            }
        )
        PROCESSES[job_id] = proc
        save_jobs()

    threads = [
        threading.Thread(
            target=stream_reader,
            args=(job_id, "stdout", proc.stdout, paths["stdout_path"]),
            daemon=True,
        ),
        threading.Thread(
            target=stream_reader,
            args=(job_id, "stderr", proc.stderr, paths["stderr_path"]),
            daemon=True,
        ),
    ]
    for thread in threads:
        thread.start()

    threading.Thread(target=watcher, args=(job_id, proc, threads, max_runtime_seconds), daemon=True).start()
    return metadata.copy()


def refresh_job(job_id: str) -> JsonObject:
    with LOCK:
        if job_id not in JOBS:
            raise ValueError(f"unknown job_id: {job_id}")
        metadata = JOBS[job_id]
        status = metadata.get("status")
        pid = metadata.get("pid")
        proc = PROCESSES.get(job_id)

    if status in TERMINAL_STATUSES:
        return job_payload(job_id)

    if proc is not None and proc.poll() is None:
        return job_payload(job_id)

    if proc is not None and proc.poll() is not None:
        time.sleep(0.05)
        return job_payload(job_id)

    if isinstance(pid, int) and process_exists(pid):
        return job_payload(job_id)

    with LOCK:
        metadata = JOBS[job_id]
        if metadata.get("status") not in TERMINAL_STATUSES:
            now = utc_now()
            metadata.update({"status": "exited_unknown", "finished_at": now, "updated_at": now})
            save_jobs()
            JOB_CONDITION.notify_all()
    return job_payload(job_id)


def job_payload(job_id: str) -> JsonObject:
    with LOCK:
        if job_id not in JOBS:
            raise ValueError(f"unknown job_id: {job_id}")
        return dict(JOBS[job_id])


def read_lines(path: str, *, lines: int, since_line: int | None = None) -> JsonObject:
    if lines < 0:
        raise ValueError("lines must be non-negative")
    p = Path(path)
    if not p.exists():
        return {"path": path, "lines": [], "start_line": 0, "next_line": 0, "total_lines": 0}

    if since_line is not None:
        if since_line < 0:
            raise ValueError("since_line must be non-negative")
        selected: list[str] = []
        total = 0
        with p.open("r", encoding="utf-8", errors="replace") as handle:
            for index, line in enumerate(handle):
                total = index + 1
                if index >= since_line and len(selected) < lines:
                    selected.append(line.rstrip("\n"))
        return {
            "path": path,
            "lines": selected,
            "start_line": since_line,
            "next_line": since_line + len(selected),
            "total_lines": total,
            "truncated": total > since_line + len(selected),
        }

    queue: deque[str] = deque(maxlen=lines)
    total = 0
    with p.open("r", encoding="utf-8", errors="replace") as handle:
        for total, line in enumerate(handle, start=1):
            if lines:
                queue.append(line.rstrip("\n"))
    start_line = max(total - len(queue), 0)
    return {
        "path": path,
        "lines": list(queue),
        "start_line": start_line,
        "next_line": total,
        "total_lines": total,
        "truncated": start_line > 0,
    }


def collect_tails(job_id: str, tail_lines: int) -> JsonObject:
    metadata = refresh_job(job_id)
    return {
        "job": metadata,
        "combined_tail": read_lines(metadata["combined_path"], lines=tail_lines),
        "stdout_tail": read_lines(metadata["stdout_path"], lines=tail_lines),
        "stderr_tail": read_lines(metadata["stderr_path"], lines=tail_lines),
    }


def collect_monitor_tail(job_id: str, tail_lines: int) -> JsonObject:
    metadata = refresh_job(job_id)
    return {
        "job": metadata,
        "combined_tail": read_lines(metadata["combined_path"], lines=tail_lines),
    }


def wait_for_job(
    job_id: str,
    *,
    timeout_seconds: float,
    cancel_on_timeout: bool,
    tail_lines: int,
) -> JsonObject:
    deadline = time.monotonic() + timeout_seconds
    wait_timed_out = False

    while True:
        metadata = refresh_job(job_id)
        if metadata.get("status") in TERMINAL_STATUSES:
            break

        remaining = deadline - time.monotonic()
        if remaining <= 0:
            wait_timed_out = True
            if cancel_on_timeout:
                cancel_job_internal(job_id, grace_seconds=5.0, reason="timeout")
            break

        proc = PROCESSES.get(job_id)
        if proc is not None:
            try:
                proc.wait(timeout=min(remaining, 1.0))
            except subprocess.TimeoutExpired:
                pass
        else:
            time.sleep(min(remaining, 1.0))

    payload = collect_tails(job_id, tail_lines)
    payload["wait_timed_out"] = wait_timed_out
    payload["cancelled_on_timeout"] = bool(wait_timed_out and cancel_on_timeout)
    return payload


def cancel_job_internal(job_id: str, *, grace_seconds: float, reason: str = "cancel") -> JsonObject:
    metadata = refresh_job(job_id)
    if metadata.get("status") in TERMINAL_STATUSES:
        return metadata

    requested_status = "timeout_requested" if reason == "timeout" else "cancel_requested"
    with LOCK:
        JOBS[job_id]["status"] = requested_status
        JOBS[job_id]["updated_at"] = utc_now()
        save_jobs()

    proc = PROCESSES.get(job_id)
    if proc is not None and proc.poll() is None:
        terminate_process_group(proc.pid, grace_seconds=grace_seconds)
        try:
            proc.wait(timeout=max(grace_seconds, 0.1) + 1.0)
        except subprocess.TimeoutExpired:
            pass
        for _ in range(40):
            metadata = refresh_job(job_id)
            if metadata.get("status") in TERMINAL_STATUSES:
                return metadata
            time.sleep(0.05)
        return refresh_job(job_id)

    pid = metadata.get("pid")
    if isinstance(pid, int) and process_exists(pid):
        terminate_process_group(pid, grace_seconds=grace_seconds)

    with LOCK:
        if JOBS[job_id].get("status") not in TERMINAL_STATUSES:
            now = utc_now()
            JOBS[job_id].update({"status": "cancelled", "finished_at": now, "updated_at": now})
            save_jobs()
            JOB_CONDITION.notify_all()
    return job_payload(job_id)
