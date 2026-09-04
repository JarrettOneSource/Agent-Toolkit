from __future__ import annotations

from typing import Any

from . import validation


def success(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def tool_result(text: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": text}], "structuredContent": payload}


def tool_schema(
    name: str,
    description: str,
    properties: dict[str, Any],
    *,
    required: list[str] | None = None,
) -> dict[str, Any]:
    schema: dict[str, Any] = {
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
    }
    if required:
        schema["required"] = required
    return {"name": name, "description": description, "inputSchema": schema}


COMMAND_PROPERTIES = {
    "command": {"type": "string", "description": "Shell command to run."},
    "cwd": {"type": "string", "default": validation.DEFAULT_CWD, "description": "Working directory."},
    "shell": {
        "type": "string",
        "default": validation.DEFAULT_SHELL,
        "description": "Shell executable used with -lc.",
    },
    "env": {
        "type": "object",
        "additionalProperties": {"type": ["string", "number"]},
        "description": "Extra environment variables for the child process.",
    },
}


TOOLS = [
    tool_schema(
        "await_instruction",
        (
            "When the user invokes this as a persistent workflow, create or maintain a persistent goal to "
            "repeatedly call await_instruction, execute each instruction it returns, and call await_instruction "
            "again. Do not mark that goal complete unless the user cancels it. Optionally pass a comment describing "
            "what the agent is waiting on; it is shown on the dashboard. The tool blocks until the dashboard "
            "returns an instruction and receives its Codex thread ID automatically."
        ),
        {
            "comment": {
                "type": "string",
                "maxLength": 2000,
                "description": "Optional agent message displayed on this thread's waiting card.",
            }
        },
    ),
    tool_schema(
        "sleep",
        "Sleep synchronously for a requested number of seconds, then return a short completion message. Maximum sleep is one week.",
        {
            "seconds": {
                "type": "number",
                "minimum": 0,
                "maximum": validation.MAX_SECONDS,
                "default": validation.DEFAULT_SLEEP_SECONDS,
                "description": "Seconds to sleep before returning.",
            }
        },
    ),
    tool_schema(
        "run_shell",
        "Run a shell command, block until it exits or times out, and return exit status plus log tails. Maximum timeout is one week.",
        {
            **COMMAND_PROPERTIES,
            "timeout_seconds": {
                "type": "number",
                "minimum": 0,
                "maximum": validation.MAX_SECONDS,
                "default": validation.MAX_SECONDS,
            },
            "tail_lines": {"type": "integer", "minimum": 0, "maximum": 1000, "default": 80},
        },
        required=["command"],
    ),
    tool_schema(
        "start_job",
        "Start a shell command in the background and return a job id plus log paths.",
        {
            **COMMAND_PROPERTIES,
            "max_runtime_seconds": {
                "type": "number",
                "minimum": 0,
                "maximum": validation.MAX_SECONDS,
                "description": "Optional runtime cap. If reached, the process group is terminated.",
            },
            "tail_lines": {"type": "integer", "minimum": 0, "maximum": 1000, "default": 20},
        },
        required=["command"],
    ),
    tool_schema(
        "wait_job",
        (
            "Block until a background job exits, or until this wait call times out. The default wait is one hour; "
            "agents should use it unless they have a specific reason to choose a different timeout. Maximum wait "
            "is one week. Calling wait_job on a monitor takes manual ownership and suppresses its pending automatic "
            "callback; use start_job rather than monitor when you intend to wait in the same turn."
        ),
        {
            "job_id": {"type": "string"},
            "timeout_seconds": {
                "type": "number",
                "minimum": 0,
                "maximum": validation.MAX_SECONDS,
                "default": validation.DEFAULT_WAIT_JOB_SECONDS,
                "description": "Wait before yielding. Override the one-hour default only for a specific reason.",
            },
            "cancel_on_timeout": {"type": "boolean", "default": False},
            "tail_lines": {"type": "integer", "minimum": 0, "maximum": 1000, "default": 80},
        },
        required=["job_id"],
    ),
    tool_schema(
        "status_job",
        "Return status, metadata, and recent output for a job. This read-only check does not suppress monitor callbacks.",
        {
            "job_id": {"type": "string"},
            "tail_lines": {"type": "integer", "minimum": 0, "maximum": 1000, "default": 20},
        },
        required=["job_id"],
    ),
    tool_schema(
        "tail_job",
        "Read recent or cursor-based output lines from a job log. This read-only check does not suppress monitor callbacks.",
        {
            "job_id": {"type": "string"},
            "stream": {"type": "string", "enum": ["combined", "stdout", "stderr"], "default": "combined"},
            "lines": {"type": "integer", "minimum": 0, "maximum": 1000, "default": 80},
            "since_line": {
                "type": "integer",
                "minimum": 0,
                "description": "Optional zero-based cursor. Returns lines from this offset instead of tailing.",
            },
        },
        required=["job_id"],
    ),
    tool_schema(
        "cancel_job",
        "Terminate a running job's process group. Cancelling a monitor takes manual ownership and suppresses its pending callback.",
        {
            "job_id": {"type": "string"},
            "grace_seconds": {
                "type": "number",
                "minimum": 0,
                "maximum": validation.MAX_SECONDS,
                "default": 5,
            },
            "tail_lines": {"type": "integer", "minimum": 0, "maximum": 1000, "default": 20},
        },
        required=["job_id"],
    ),
    tool_schema(
        "list_jobs",
        "List known local-tools jobs from newest to oldest.",
        {
            "limit": {"type": "integer", "minimum": 1, "maximum": 500, "default": 20},
            "status": {"type": "string", "description": "Optional exact status filter."},
        },
    ),
    tool_schema(
        "monitor",
        (
            "Use monitor only when you will end the current turn immediately. It starts a background command and "
            "posts exactly one final-status callback to the originating Codex thread after the job exits. Do not "
            "poll or wait on a monitor while staying in the same turn. If you need to stay active, use start_job "
            "followed by wait_job instead. Calling wait_job or cancel_job on a monitor takes manual ownership and "
            "suppresses any callback not already queued. tail_lines bounds both the initial response and final callback."
        ),
        {
            **COMMAND_PROPERTIES,
            "max_runtime_seconds": {
                "type": "number",
                "minimum": 0,
                "maximum": validation.MAX_SECONDS,
                "description": "Optional runtime cap. If reached, the process group is terminated.",
            },
            "startup_wait_seconds": {
                "type": "number",
                "minimum": 0,
                "maximum": 60,
                "default": 1,
                "description": "Briefly wait for initial output or early failure before returning.",
            },
            "tail_lines": {
                "type": "integer",
                "minimum": 0,
                "maximum": validation.MAX_MONITOR_TAIL_LINES,
                "default": validation.DEFAULT_MONITOR_TAIL_LINES,
                "description": "Maximum output lines included in both the initial response and final callback.",
            },
        },
        required=["command"],
    ),
]
