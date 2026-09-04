# Local Tools

An optional, dependency-free stdio MCP server for commands and background jobs on the machine running the server. Requires Python 3.11+ and a POSIX host: Linux, macOS, or WSL.

## Install

After adding the Agent Toolkit marketplace:

```sh
codex plugin add local-tools@agent-toolkit
```

For Claude Code:

```sh
claude plugin install local-tools@agent-toolkit
```

The plugin runs its bundled Python source without a separate package installation. Installing it enables the MCP server and its loopback dashboard. The main `agent-toolkit` plugin does not enable Local Tools.

## Tools

| Tool | Behavior |
| --- | --- |
| `run_shell` | Run a command and wait for exit or timeout. |
| `start_job` | Start a background command and return its job ID. |
| `wait_job` | Wait for a job, optionally cancelling it on timeout. Defaults to one hour. |
| `status_job` | Read current job status and recent output. |
| `tail_job` | Read recent or cursor-based stdout, stderr, or combined output. |
| `cancel_job` | Terminate a job's process group. |
| `list_jobs` | List recorded jobs, optionally filtered by status. |
| `sleep` | Pause for the requested duration. |
| `await_instruction` | Wait for a dashboard instruction. Requires native Codex thread metadata. |
| `monitor` | Start a job and, when supported, deliver one final callback to its Codex thread. |

Shell tools accept `command`, optional `cwd`, `shell`, and environment values. The working directory defaults to the current user's home and the shell to `/bin/bash`. Commands execute with the MCP process's local permissions; logs contain their actual output.

Sleep, wait, timeout, and runtime limits are at most 604800 seconds. `await_instruction` has no server-side timeout. The bundled configuration sets client tool timeouts to one week and keeps Codex tools directly exposed instead of wrapping long waits in code-mode background cells. Client or administrator policy can impose shorter limits. [Configuration research](https://github.com/JarrettOneSource/Agent-Toolkit/blob/main/docs/distribution-research.md#local-tools-mcp-packaging-follow-up).

## Instruction dashboard

The dashboard normally starts at `http://127.0.0.1:8765/`. Each pending instruction call has a card with its Codex thread ID, title when available, optional comment, and response form. Times use the host's timezone, including daylight-saving time. Cancelling a pending MCP call removes its card.

If the preferred port is occupied, the server chooses an available port. The active URL is written to `~/.codex/local-tools/await_instruction.url`. Multiple MCP processes share the dashboard, and a surviving process can take over if the listener exits.

| Environment variable | Purpose |
| --- | --- |
| `LOCAL_TOOLS_MCP_JOB_ROOT` | Job state and logs; defaults to `~/.codex/local-tools/jobs`. |
| `LOCAL_TOOLS_MCP_AWAIT_ROOT` | Pending instruction state; defaults to a sibling of the job directory. |
| `LOCAL_TOOLS_MCP_AWAIT_HOST` | Bind IP; defaults to `127.0.0.1`. |
| `LOCAL_TOOLS_MCP_AWAIT_PORT` | Preferred port; defaults to `8765`. Use `0` for an available port. |
| `LOCAL_TOOLS_MCP_AWAIT_URL_FILE` | Destination for the active dashboard URL. |
| `LOCAL_TOOLS_MCP_AWAIT_OPEN_BROWSER` | Set to `1` to open the dashboard for a wait. The plugin uses `0`. |
| `LOCAL_TOOLS_MCP_CODEX_BIN` | Codex executable for callbacks; defaults to `codex` on `PATH`. |

The dashboard has no account login. Its forms control waiting agents, so retain the loopback binding unless you intend to grant access to another network.

For a continuous workflow, ask Codex to keep calling `await_instruction`, execute each instruction returned, and call it again until you cancel. Ordinary shell tools also work in MCP clients that do not provide Codex metadata.

## Monitor callbacks

Use `monitor` when the agent will end its turn immediately after the tool returns. Its final callback queues the next turn through `codex queue`, which requires a Codex CLI with that command and native thread metadata on the request.

Use `start_job` followed by `wait_job` when the agent needs to remain active. Calling `wait_job` or `cancel_job` on a monitor takes manual ownership and suppresses a callback that has not already been queued. Read-only status and log requests do not suppress it. A callback already accepted by Codex cannot be retracted; status reports that condition.

Callbacks contain the job ID, final status, finish timestamp, and bounded new output. `tail_lines` defaults to 20 and is capped at 200 for monitors. Callbacks have a 12000-character limit; complete logs remain available through `tail_job`.

## Standalone use

From a checkout, run the MCP server directly:

```sh
python3 plugins/local-tools/scripts/run.py
```

Or install it into your chosen Python environment:

```sh
python3 -m pip install ./plugins/local-tools
```

This provides `local-tools-mcp` and `local-tools-mcp-dashboard`. The second command runs only the dashboard and can be placed under a process supervisor for an always-on page.

For a standalone Codex registration, set `command` to the installed executable and configure a long `tool_timeout_sec`. Register a single copy of this server.

## Development

From the Agent Toolkit repository root:

```sh
PYTHONPATH=plugins/local-tools/src python3 -m unittest discover -s plugins/local-tools/tests
```

Responsibilities are separated into job lifecycle and storage (`jobs.py`), callback delivery (`monitoring.py`), input validation (`validation.py`), wire schemas (`protocol.py`), MCP dispatch (`server.py`), and the dashboard (`await_instruction.py`).
