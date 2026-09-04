from __future__ import annotations

import json
import sys
import threading
import time

from . import jobs as job_store
from . import monitoring, protocol, validation
from .await_instruction import AwaitInstructionCancelled, start_instruction_dashboard, wait_for_instruction
from .json_types import JsonObject, JsonValue

SERVER_VERSION = "0.8.0"


WRITE_LOCK = threading.Lock()


IN_FLIGHT_LOCK = threading.Lock()


IN_FLIGHT_AWAITS: dict[str | int, threading.Event] = {}


def write_message(message: JsonObject) -> None:
    with WRITE_LOCK:
        sys.stdout.write(json.dumps(message, separators=(",", ":")) + "\n")
        sys.stdout.flush()


def await_instruction_tool(
    arguments: JsonValue,
    request_meta: JsonValue,
    cancellation_event: threading.Event | None = None,
) -> JsonObject:
    args = validation.parse_arguments(arguments)
    unknown_arguments = sorted(set(args) - {"comment"})
    if unknown_arguments:
        raise ValueError(f"await_instruction does not accept arguments: {', '.join(unknown_arguments)}")
    comment = args.get("comment")
    if comment is not None:
        if not isinstance(comment, str):
            raise ValueError("comment must be a string")
        comment = comment.strip() or None
    if comment is not None and len(comment) > 2000:
        raise ValueError("comment must be at most 2000 characters")
    if not isinstance(request_meta, dict):
        raise ValueError("Codex thread ID is unavailable from MCP request metadata")
    thread_id = request_meta.get("threadId")
    if not isinstance(thread_id, str) or not thread_id.strip():
        raise ValueError("Codex thread ID is unavailable from MCP request metadata")
    payload = wait_for_instruction(thread_id, comment, cancellation_event)
    return protocol.tool_result(payload["instruction"], payload)


def request_id(value: JsonValue) -> str | int | None:
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        return None
    return value


def register_await_request(request: JsonObject) -> tuple[str | int, threading.Event] | None:
    params = request.get("params")
    if not isinstance(params, dict) or params.get("name") != "await_instruction":
        return None
    parsed_request_id = request_id(request.get("id"))
    if parsed_request_id is None:
        return None
    cancellation_event = threading.Event()
    with IN_FLIGHT_LOCK:
        IN_FLIGHT_AWAITS[parsed_request_id] = cancellation_event
    return parsed_request_id, cancellation_event


def cancel_await_request(params: JsonValue) -> None:
    if not isinstance(params, dict):
        return
    cancelled_request_id = request_id(params.get("requestId"))
    if cancelled_request_id is None:
        return
    with IN_FLIGHT_LOCK:
        cancellation_event = IN_FLIGHT_AWAITS.get(cancelled_request_id)
        if cancellation_event is not None:
            cancellation_event.set()


def finish_await_request(
    in_flight_await: tuple[str | int, threading.Event],
) -> bool:
    parsed_request_id, cancellation_event = in_flight_await
    with IN_FLIGHT_LOCK:
        if IN_FLIGHT_AWAITS.get(parsed_request_id) is not cancellation_event:
            return False
        del IN_FLIGHT_AWAITS[parsed_request_id]
        return not cancellation_event.is_set()


def sleep_tool(arguments: JsonValue) -> JsonObject:
    args = validation.parse_arguments(arguments)
    seconds = validation.parse_seconds(
        args.get("seconds"), default=validation.DEFAULT_SLEEP_SECONDS, field="seconds"
    )
    assert seconds is not None
    started_at = job_store.utc_now()

    deadline = time.monotonic() + seconds
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(remaining, 60.0))

    finished_at = job_store.utc_now()
    text = f"Slept synchronously for {seconds:g} seconds."
    return protocol.tool_result(
        text,
        {
            "slept_seconds": seconds,
            "started_at": started_at,
            "finished_at": finished_at,
            "max_sleep_seconds": validation.MAX_SECONDS,
        },
    )


def start_job_tool(arguments: JsonValue) -> JsonObject:
    args = validation.parse_arguments(arguments)
    parsed = validation.parse_command_tool_args(args)
    max_runtime = validation.parse_seconds(
        args.get("max_runtime_seconds"),
        field="max_runtime_seconds",
        allow_none=True,
    )
    tail_lines = validation.parse_int(args.get("tail_lines"), default=20, field="tail_lines")
    metadata = job_store.start_process_job(kind="job", max_runtime_seconds=max_runtime, **parsed)
    payload = job_store.collect_tails(metadata["job_id"], tail_lines)
    text = f"Started job {metadata['job_id']} with status {payload['job']['status']}."
    return protocol.tool_result(text, payload)


def run_shell_tool(arguments: JsonValue) -> JsonObject:
    args = validation.parse_arguments(arguments)
    parsed = validation.parse_command_tool_args(args)
    timeout = validation.parse_seconds(
        args.get("timeout_seconds"), default=validation.MAX_SECONDS, field="timeout_seconds"
    )
    tail_lines = validation.parse_int(args.get("tail_lines"), default=80, field="tail_lines")
    assert timeout is not None
    metadata = job_store.start_process_job(kind="run_shell", max_runtime_seconds=None, **parsed)
    payload = job_store.wait_for_job(
        metadata["job_id"],
        timeout_seconds=timeout,
        cancel_on_timeout=True,
        tail_lines=tail_lines,
    )
    job = payload["job"]
    text = f"Job {job['job_id']} finished with status {job['status']} and exit code {job.get('exit_code')}."
    return protocol.tool_result(text, payload)


def wait_job_tool(arguments: JsonValue) -> JsonObject:
    args = validation.parse_arguments(arguments)
    job_id = validation.parse_job_id(args)
    timeout = validation.parse_seconds(
        args.get("timeout_seconds"),
        default=validation.DEFAULT_WAIT_JOB_SECONDS,
        field="timeout_seconds",
    )
    cancel_on_timeout = validation.parse_bool(
        args.get("cancel_on_timeout"), default=False, field="cancel_on_timeout"
    )
    tail_lines = validation.parse_int(args.get("tail_lines"), default=80, field="tail_lines")
    assert timeout is not None
    callback_suppressed = monitoring.suppress_monitor_notification(job_id, suppressed_by="wait_job")
    payload = job_store.wait_for_job(
        job_id,
        timeout_seconds=timeout,
        cancel_on_timeout=cancel_on_timeout,
        tail_lines=tail_lines,
    )
    job = payload["job"]
    if payload["wait_timed_out"]:
        text = f"Timed out waiting for job {job_id}; current status is {job['status']}."
    else:
        text = f"Job {job_id} finished with status {job['status']} and exit code {job.get('exit_code')}."
    if callback_suppressed:
        text += " Automatic monitor callback was suppressed because wait_job took manual ownership."
    elif job.get("kind") == "monitor" and int((job.get("notification") or {}).get("messages_queued") or 0):
        text += " A monitor callback was already queued and may still arrive; treat it as stale."
    return protocol.tool_result(text, payload)


def status_job_tool(arguments: JsonValue) -> JsonObject:
    args = validation.parse_arguments(arguments)
    job_id = validation.parse_job_id(args)
    tail_lines = validation.parse_int(args.get("tail_lines"), default=20, field="tail_lines")
    payload = job_store.collect_tails(job_id, tail_lines)
    job = payload["job"]
    return protocol.tool_result(f"Job {job_id} status is {job['status']}.", payload)


def tail_job_tool(arguments: JsonValue) -> JsonObject:
    args = validation.parse_arguments(arguments)
    job_id = validation.parse_job_id(args)
    stream = validation.parse_string(args.get("stream"), default="combined", field="stream")
    if stream not in {"combined", "stdout", "stderr"}:
        raise ValueError("stream must be one of: combined, stdout, stderr")
    lines = validation.parse_int(args.get("lines"), default=80, field="lines")
    since_line_raw = args.get("since_line")
    since_line = None
    if since_line_raw is not None:
        since_line = validation.parse_int(since_line_raw, default=0, field="since_line", maximum=10**12)
    metadata = job_store.refresh_job(job_id)
    path = metadata[f"{stream}_path"]
    payload = {
        "job": metadata,
        "stream": stream,
        "output": job_store.read_lines(path, lines=lines, since_line=since_line),
    }
    return protocol.tool_result(
        f"Read {len(payload['output']['lines'])} {stream} lines for job {job_id}.", payload
    )


def cancel_job_tool(arguments: JsonValue) -> JsonObject:
    args = validation.parse_arguments(arguments)
    job_id = validation.parse_job_id(args)
    grace_seconds = validation.parse_seconds(args.get("grace_seconds"), default=5.0, field="grace_seconds")
    tail_lines = validation.parse_int(args.get("tail_lines"), default=20, field="tail_lines")
    assert grace_seconds is not None
    callback_suppressed = monitoring.suppress_monitor_notification(job_id, suppressed_by="cancel_job")
    job_store.cancel_job_internal(job_id, grace_seconds=grace_seconds)
    payload = job_store.collect_tails(job_id, tail_lines)
    text = f"Cancelled job {job_id}; status is {payload['job']['status']}."
    if callback_suppressed:
        text += " Automatic monitor callback was suppressed because cancel_job took manual ownership."
    elif payload["job"].get("kind") == "monitor" and int(
        (payload["job"].get("notification") or {}).get("messages_queued") or 0
    ):
        text += " A monitor callback was already queued and may still arrive; treat it as stale."
    return protocol.tool_result(text, payload)


def list_jobs_tool(arguments: JsonValue) -> JsonObject:
    args = validation.parse_arguments(arguments)
    limit = validation.parse_int(args.get("limit"), default=20, field="limit", minimum=1, maximum=500)
    status_filter = args.get("status")
    if status_filter is not None and not isinstance(status_filter, str):
        raise ValueError("status must be a string")
    with job_store.LOCK:
        jobs = [dict(job) for job in job_store.JOBS.values()]
    for job in jobs:
        try:
            job_store.refresh_job(job["job_id"])
        except ValueError:
            pass
    with job_store.LOCK:
        jobs = [dict(job) for job in job_store.JOBS.values()]
    if status_filter:
        jobs = [job for job in jobs if job.get("status") == status_filter]
    jobs.sort(key=lambda job: str(job.get("created_at") or ""), reverse=True)
    payload = {"jobs": jobs[:limit], "count": len(jobs), "limit": limit}
    return protocol.tool_result(f"Listed {len(payload['jobs'])} jobs.", payload)


TOOL_HANDLERS = {
    "await_instruction": await_instruction_tool,
    "sleep": sleep_tool,
    "run_shell": run_shell_tool,
    "start_job": start_job_tool,
    "wait_job": wait_job_tool,
    "status_job": status_job_tool,
    "tail_job": tail_job_tool,
    "cancel_job": cancel_job_tool,
    "list_jobs": list_jobs_tool,
    "monitor": monitoring.monitor_tool,
}


def call_tool(
    request_id: JsonValue, params: JsonValue, cancellation_event: threading.Event | None
) -> JsonObject | None:
    if not isinstance(params, dict):
        return protocol.error(request_id, -32602, "params must be an object")
    name = params.get("name")
    if not isinstance(name, str):
        return protocol.error(request_id, -32602, "tool name is required")
    handler = TOOL_HANDLERS.get(name)
    if handler is None:
        return protocol.error(request_id, -32601, f"unknown tool: {name}")
    try:
        if name == "await_instruction":
            result = await_instruction_tool(
                params.get("arguments"),
                params.get("_meta"),
                cancellation_event,
            )
        elif name == "monitor":
            result = monitoring.monitor_tool(
                params.get("arguments"),
                params.get("_meta"),
            )
        else:
            result = handler(params.get("arguments"))
        return protocol.success(request_id, result)
    except ValueError as exc:
        return protocol.error(request_id, -32602, str(exc))
    except AwaitInstructionCancelled:
        return None


def handle_request(
    request: JsonObject,
    cancellation_event: threading.Event | None = None,
) -> JsonObject | None:
    request_id = request.get("id")
    method = request.get("method")
    params = request.get("params") or {}

    if not isinstance(method, str):
        return protocol.error(request_id, -32600, "method is required")

    if method == "notifications/cancelled":
        cancel_await_request(params)
        return None

    if method.startswith("notifications/"):
        return None

    if method == "initialize":
        protocol_version = "2024-11-05"
        if isinstance(params, dict) and isinstance(params.get("protocolVersion"), str):
            protocol_version = params["protocolVersion"]
        return protocol.success(
            request_id,
            {
                "protocolVersion": protocol_version,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "local-tools", "version": SERVER_VERSION},
                "instructions": (
                    "When the user invokes await_instruction as a persistent workflow, create or maintain a "
                    "persistent goal to repeatedly call it, execute each returned instruction, and call it "
                    "again. Never mark that goal complete unless the user cancels it. await_instruction takes "
                    "an optional comment shown on the dashboard and receives the native Codex thread ID from "
                    "MCP request metadata. Use monitor only when you will end the current turn immediately; it posts "
                    "one final callback that invokes the agent after the job exits. Never poll or wait on a monitor "
                    "in the same turn. Use start_job followed by wait_job when you need to remain active. Calling "
                    "wait_job or cancel_job on a monitor takes manual ownership and suppresses its pending callback. "
                    "Treat messages beginning with [Local Tools] as terminal job callbacks."
                ),
            },
        )

    if method == "ping":
        return protocol.success(request_id, {})

    if method == "tools/list":
        return protocol.success(request_id, {"tools": protocol.TOOLS})

    if method == "resources/list":
        return protocol.success(request_id, {"resources": []})

    if method == "prompts/list":
        return protocol.success(request_id, {"prompts": []})

    if method == "tools/call":
        return call_tool(request_id, params, cancellation_event)

    return protocol.error(request_id, -32601, f"unknown method: {method}")


def handle_and_write_request(
    request: JsonObject,
    in_flight_await: tuple[str | int, threading.Event] | None = None,
) -> None:
    should_write_response = True
    try:
        response = handle_request(
            request,
            in_flight_await[1] if in_flight_await is not None else None,
        )
    finally:
        if in_flight_await is not None:
            should_write_response = finish_await_request(in_flight_await)
    if response is not None and should_write_response:
        write_message(response)


def main() -> int:
    job_store.load_jobs()
    start_instruction_dashboard()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError as exc:
            write_message(protocol.error(None, -32700, f"parse error: {exc}"))
            continue
        if not isinstance(request, dict):
            write_message(protocol.error(None, -32600, "request must be an object"))
            continue

        if request.get("method") == "tools/call":
            in_flight_await = register_await_request(request)
            threading.Thread(
                target=handle_and_write_request,
                args=(request, in_flight_await),
                name=f"mcp-tool-request-{request.get('id', 'unknown')}",
            ).start()
        else:
            handle_and_write_request(request)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
