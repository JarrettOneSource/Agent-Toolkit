from __future__ import annotations

import json
import os
import subprocess
import threading
import time
from collections import deque
from typing import Any

from . import jobs as job_store
from . import protocol, validation

MONITOR_NOTIFICATION_MAX_CHARS = 12_000


MONITOR_NOTIFICATION_RETRY_DELAYS = (0.0, 0.5, 2.0)


MONITOR_DELIVERY_LOCK = threading.Lock()


def capture_monitor_origin(request_meta: Any) -> dict[str, str | None]:
    thread_id = None
    if isinstance(request_meta, dict):
        raw_thread_id = request_meta.get("threadId")
        if isinstance(raw_thread_id, str) and raw_thread_id.strip():
            thread_id = raw_thread_id.strip()

    tmux_pane = (os.environ.get("TMUX_PANE") or "").strip() or None
    tmux_value = (os.environ.get("TMUX") or "").strip()
    tmux_socket = tmux_value.split(",", 1)[0].strip() if tmux_value else None
    return {
        "thread_id": thread_id,
        "tmux_pane": tmux_pane,
        "tmux_socket": tmux_socket or None,
    }


def update_monitor_notification(job_id: str, **changes: Any) -> None:
    with job_store.JOB_CONDITION:
        metadata = job_store.JOBS.get(job_id)
        if metadata is None:
            return
        notification = dict(metadata.get("notification") or {})
        notification.update(changes)
        metadata["notification"] = notification
        metadata["updated_at"] = job_store.utc_now()
        job_store.save_jobs()
        job_store.JOB_CONDITION.notify_all()


def initialize_monitor_notification(
    job_id: str,
    origin: dict[str, str | None],
    *,
    tail_lines: int,
) -> None:
    enabled = bool(origin.get("thread_id"))
    update_monitor_notification(
        job_id,
        enabled=enabled,
        state="pending" if enabled else "disabled",
        next_line=0,
        messages_queued=0,
        tail_lines=tail_lines,
        last_queued_at=None,
        last_error=None if enabled else "Codex thread ID is unavailable from MCP request metadata",
        suppressed_at=None,
        suppressed_by=None,
    )


def suppress_monitor_notification(job_id: str, *, suppressed_by: str) -> bool:
    with MONITOR_DELIVERY_LOCK:
        with job_store.JOB_CONDITION:
            metadata = job_store.JOBS.get(job_id)
            if metadata is None or metadata.get("kind") != "monitor":
                return False
            notification = dict(metadata.get("notification") or {})
            if not notification.get("enabled") or notification.get("state") not in {"pending", "active"}:
                return False
            now = job_store.utc_now()
            notification.update(
                {
                    "state": "suppressed",
                    "suppressed_at": now,
                    "suppressed_by": suppressed_by,
                }
            )
            metadata["notification"] = notification
            metadata["updated_at"] = now
            job_store.save_jobs()
            job_store.JOB_CONDITION.notify_all()
            return True


def read_monitor_event_lines(
    path: str,
    *,
    start_line: int,
    end_line: int,
    max_lines: int,
) -> tuple[str, int, int]:
    selected: deque[str] = deque(maxlen=max_lines)
    try:
        with job_store.FILE_LOCK:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                for index, raw_line in enumerate(handle):
                    if index < start_line:
                        continue
                    if index >= end_line:
                        break
                    try:
                        event = json.loads(raw_line)
                    except json.JSONDecodeError:
                        selected.append(raw_line.rstrip("\n").replace("\x00", "�"))
                        continue
                    text = str(event.get("line") or "").replace("\x00", "�")
                    if event.get("stream") == "stderr":
                        text = f"[stderr] {text}"
                    selected.append(text)
    except OSError:
        return "", max(end_line - start_line, 0), 0

    omitted_lines = max(end_line - start_line - len(selected), 0)
    body = "\n".join(selected)
    omitted_chars = 0
    if len(body) > MONITOR_NOTIFICATION_MAX_CHARS:
        omitted_chars = len(body) - MONITOR_NOTIFICATION_MAX_CHARS
        body = body[-MONITOR_NOTIFICATION_MAX_CHARS:]
    return body, omitted_lines, omitted_chars


def monitor_status_text(metadata: dict[str, Any]) -> str:
    status = str(metadata.get("status") or "unknown")
    exit_code = metadata.get("exit_code")
    if isinstance(exit_code, int):
        return f"Status: {status} (exit code {exit_code})."
    return f"Status: {status}."


def format_monitor_notification(
    metadata: dict[str, Any],
    *,
    start_line: int,
    end_line: int,
    tail_lines: int,
) -> str:
    body, omitted_lines, omitted_chars = read_monitor_event_lines(
        metadata["events_path"],
        start_line=start_line,
        end_line=end_line,
        max_lines=tail_lines,
    )
    response = [monitor_status_text(metadata)]
    finished_at = metadata.get("finished_at")
    if isinstance(finished_at, str) and finished_at:
        response.append(f"Finished at: {finished_at}.")
    if omitted_lines:
        response.append(f"[... {omitted_lines} earlier output lines omitted ...]")
    if omitted_chars:
        response.append(f"[... {omitted_chars} earlier output characters omitted ...]")
    if body:
        response.append(body)
    return f"[Local Tools] Job ID: {metadata['job_id']}\n" + "\n".join(response)


def queue_codex_message(thread_id: str, message: str) -> None:
    codex_bin = (os.environ.get("LOCAL_TOOLS_MCP_CODEX_BIN") or "codex").strip()
    if not codex_bin:
        raise RuntimeError("LOCAL_TOOLS_MCP_CODEX_BIN is empty")
    try:
        result = subprocess.run(
            [codex_bin, "queue", "--thread", thread_id, "--message", message],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError(f"could not run codex queue: {exc}") from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        if len(detail) > 1000:
            detail = f"{detail[:999]}…"
        suffix = f": {detail}" if detail else ""
        raise RuntimeError(f"codex queue exited with code {result.returncode}{suffix}")


def deliver_monitor_notification(
    metadata: dict[str, Any],
    message: str,
    *,
    next_line: int,
) -> bool:
    origin = metadata.get("origin") or {}
    thread_id = origin.get("thread_id") if isinstance(origin, dict) else None
    if not isinstance(thread_id, str) or not thread_id:
        update_monitor_notification(
            metadata["job_id"],
            enabled=False,
            state="disabled",
            last_error="Codex thread ID is unavailable from MCP request metadata",
        )
        return False

    with MONITOR_DELIVERY_LOCK:
        with job_store.LOCK:
            current = job_store.JOBS.get(metadata["job_id"], {})
            notification = current.get("notification") or {}
            if notification.get("state") != "active":
                return False

        last_error = ""
        for delay in MONITOR_NOTIFICATION_RETRY_DELAYS:
            if delay:
                time.sleep(delay)
            try:
                queue_codex_message(thread_id, message)
            except RuntimeError as exc:
                last_error = str(exc)
                continue

            with job_store.LOCK:
                current = job_store.JOBS.get(metadata["job_id"], {})
                notification = current.get("notification") or {}
                messages_queued = int(notification.get("messages_queued") or 0) + 1
            update_monitor_notification(
                metadata["job_id"],
                state="finished",
                next_line=next_line,
                messages_queued=messages_queued,
                last_queued_at=job_store.utc_now(),
                last_error=None,
            )
            return True

        update_monitor_notification(
            metadata["job_id"],
            state="failed",
            last_error=last_error or "codex queue failed",
        )
    return False


def monitor_notification_worker(job_id: str, initial_line: int, tail_lines: int) -> None:
    with job_store.JOB_CONDITION:
        while True:
            metadata = job_store.JOBS.get(job_id)
            if metadata is None:
                return
            notification = metadata.get("notification") or {}
            if notification.get("state") != "active":
                return
            if metadata.get("status") in job_store.TERMINAL_STATUSES:
                snapshot = dict(metadata)
                end_line = int(metadata.get("output_line_count") or 0)
                break
            job_store.JOB_CONDITION.wait()

    message = format_monitor_notification(
        snapshot,
        start_line=initial_line,
        end_line=end_line,
        tail_lines=tail_lines,
    )
    deliver_monitor_notification(
        snapshot,
        message,
        next_line=end_line,
    )


def start_monitor_notification_worker(job_id: str, initial_line: int, tail_lines: int) -> None:
    update_monitor_notification(job_id, state="active", next_line=initial_line)
    threading.Thread(
        target=monitor_notification_worker,
        args=(job_id, initial_line, tail_lines),
        name=f"monitor-notification-{job_id}",
        daemon=True,
    ).start()


def monitor_tool(arguments: Any, request_meta: Any = None) -> dict[str, Any]:
    args = validation.parse_arguments(arguments)
    parsed = validation.parse_command_tool_args(args)
    max_runtime = validation.parse_seconds(
        args.get("max_runtime_seconds"),
        field="max_runtime_seconds",
        allow_none=True,
    )
    startup_wait = validation.parse_seconds(
        args.get("startup_wait_seconds"),
        default=1.0,
        field="startup_wait_seconds",
    )
    tail_lines = validation.parse_int(
        args.get("tail_lines"),
        default=validation.DEFAULT_MONITOR_TAIL_LINES,
        field="tail_lines",
        maximum=validation.MAX_MONITOR_TAIL_LINES,
    )
    assert startup_wait is not None
    origin = capture_monitor_origin(request_meta)
    metadata = job_store.start_process_job(
        kind="monitor",
        max_runtime_seconds=max_runtime,
        origin=origin,
        **parsed,
    )
    initialize_monitor_notification(metadata["job_id"], origin, tail_lines=tail_lines)

    deadline = time.monotonic() + min(startup_wait, 60.0)
    while time.monotonic() < deadline:
        payload = job_store.collect_monitor_tail(metadata["job_id"], tail_lines)
        if (
            payload["combined_tail"]["total_lines"] > 0
            or payload["job"]["status"] in job_store.TERMINAL_STATUSES
        ):
            break
        time.sleep(0.1)

    payload = job_store.collect_monitor_tail(metadata["job_id"], tail_lines)
    notification = payload["job"].get("notification") or {}
    if notification.get("enabled"):
        if payload["job"]["status"] in job_store.TERMINAL_STATUSES:
            update_monitor_notification(
                metadata["job_id"],
                state="returned",
                next_line=payload["combined_tail"]["total_lines"],
            )
        else:
            start_monitor_notification_worker(
                metadata["job_id"],
                payload["combined_tail"]["total_lines"],
                tail_lines,
            )
        payload = job_store.collect_monitor_tail(metadata["job_id"], tail_lines)
    text = f"Started monitor job {metadata['job_id']} with status {payload['job']['status']}. "
    if not notification.get("enabled"):
        text += (
            "Automatic callbacks are unavailable because this request had no Codex thread ID. "
            "Use wait_job once when you are ready to block for the result. "
        )
    elif payload["job"]["status"] in job_store.TERMINAL_STATUSES:
        text += "The final status and startup output are in this response; no callback is needed. "
    else:
        text += (
            "Local Tools will invoke the originating agent once, after the job finishes. End this turn now; "
            "do not poll this monitor with wait_job, status_job, or tail_job. If you need to stay in the current "
            "turn, use start_job followed by wait_job instead. "
        )
    text += "Calling wait_job or cancel_job takes manual ownership and suppresses any callback not already queued."
    return protocol.tool_result(text, payload)
