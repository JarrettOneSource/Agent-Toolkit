from __future__ import annotations

import math
from pathlib import Path

from .json_types import JsonObject, JsonValue

MAX_SECONDS = 7 * 24 * 60 * 60


DEFAULT_SLEEP_SECONDS = 30.0


DEFAULT_WAIT_JOB_SECONDS = 60 * 60


DEFAULT_CWD = str(Path.home())


DEFAULT_SHELL = "/bin/bash"


DEFAULT_MONITOR_TAIL_LINES = 20


MAX_MONITOR_TAIL_LINES = 200


def parse_arguments(arguments: JsonValue) -> JsonObject:
    if arguments is None:
        return {}
    if not isinstance(arguments, dict):
        raise ValueError("arguments must be an object")
    return arguments


def parse_seconds(
    value: JsonValue,
    *,
    default: float | None = None,
    field: str = "seconds",
    allow_none: bool = False,
) -> float | None:
    if value is None:
        if allow_none:
            return None
        if default is None:
            raise ValueError(f"{field} is required")
        return float(default)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a number")
    seconds = float(value)
    if not math.isfinite(seconds) or seconds < 0:
        raise ValueError(f"{field} must be finite and non-negative")
    if seconds > MAX_SECONDS:
        raise ValueError(f"{field} must be <= {MAX_SECONDS}")
    return seconds


def parse_int(value: JsonValue, *, default: int, field: str, minimum: int = 0, maximum: int = 1000) -> int:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field} must be an integer")
    if value < minimum or value > maximum:
        raise ValueError(f"{field} must be between {minimum} and {maximum}")
    return value


def parse_string(value: JsonValue, *, default: str | None = None, field: str) -> str:
    if value is None:
        if default is None:
            raise ValueError(f"{field} is required")
        return default
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a non-empty string")
    return value


def parse_bool(value: JsonValue, *, default: bool, field: str) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise ValueError(f"{field} must be a boolean")
    return value


def parse_env(value: JsonValue) -> dict[str, str] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError("env must be an object")
    env: dict[str, str] = {}
    for key, raw in value.items():
        if not isinstance(key, str) or not key:
            raise ValueError("env keys must be non-empty strings")
        if isinstance(raw, bool) or raw is None:
            raise ValueError("env values must be strings or numbers")
        if not isinstance(raw, (str, int, float)):
            raise ValueError("env values must be strings or numbers")
        env[key] = str(raw)
    return env


def resolve_cwd(value: JsonValue) -> str:
    cwd = parse_string(value, default=DEFAULT_CWD, field="cwd")
    path = Path(cwd).expanduser()
    if not path.is_absolute():
        path = Path(DEFAULT_CWD) / path
    path = path.resolve()
    if not path.exists():
        raise ValueError(f"cwd does not exist: {path}")
    if not path.is_dir():
        raise ValueError(f"cwd is not a directory: {path}")
    return str(path)


def parse_job_id(arguments: JsonObject) -> str:
    return parse_string(arguments.get("job_id"), field="job_id")


def parse_command_tool_args(arguments: JsonValue) -> JsonObject:
    args = parse_arguments(arguments)
    return {
        "command": parse_string(args.get("command"), field="command"),
        "cwd": resolve_cwd(args.get("cwd")),
        "shell": parse_string(args.get("shell"), default=DEFAULT_SHELL, field="shell"),
        "env_update": parse_env(args.get("env")),
    }
