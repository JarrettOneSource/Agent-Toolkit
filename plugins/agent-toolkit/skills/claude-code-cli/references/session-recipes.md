# Claude Code CLI

Use Claude Code as a stateful agent, not an opaque subprocess. Choose interactive, print, or background mode deliberately; keep the working directory and session identity explicit; and treat permissions, output capture, and completion as part of the command.

Use `--model fable` for Claude sessions unless the user requests another model. Pass the alias directly; do not resolve or pin it to a model slug.

## Verify The Installed CLI

When flags are uncertain, check only the relevant help; check authentication when needed:

```bash
claude --version
claude --help
claude agents --help
claude auth status --text
```

Prefer the installed CLI help and Anthropic's current CLI reference over remembered syntax.

## Choose The Session Mode

- Use `claude --model fable` for a live interactive session.
- Use `claude --model fable -p` for a scripted turn that prints its result and exits.
- Use `--resume <session>` to continue a specific conversation by ID or name.
- Use `--fork-session` with `--resume` when the next turn should branch without modifying the original conversation.
- Use `--bg` for a persistent background session and `claude agents` to inspect active sessions.

Run Claude from the repository it should treat as its project:

```bash
cd /abs/path/to/repo
claude --model fable
```

Claude Code has no `-C` equivalent. Use `cd` for the primary project and `--add-dir` only for additional directories Claude must access.

## Command Patterns

Start an interactive session with an opening prompt:

```bash
cd /abs/path/to/repo
claude --model fable -n auth-refactor "Inspect the authentication flow and propose the narrowest safe change."
```

Run one non-interactive turn:

```bash
cd /abs/path/to/repo
claude --model fable -p "Inspect the current branch and return review findings first, with file references."
```

Capture a JSON result and the session ID:

```bash
run_dir=/tmp/claude-runs/review
mkdir -p "$run_dir"

cd /abs/path/to/repo
claude --model fable -p \
  --output-format json \
  "Review the current branch and return findings first." \
  >"$run_dir/result.json"

jq -r '.session_id' "$run_dir/result.json" >"$run_dir/session_id"
jq -r '.result' "$run_dir/result.json"
```

Resume the exact session:

```bash
cd /abs/path/to/repo
claude --model fable -p \
  --resume "$(tr -d '\n' </tmp/claude-runs/review/session_id)" \
  "I changed the implementation. Re-check the actual files."
```

Fork a session for a tangent:

```bash
cd /abs/path/to/repo
claude --model fable -p \
  --resume <session-id> \
  --fork-session \
  "Explore the alternate design without changing the original conversation."
```

Use `--continue` only when the most recent conversation in the current directory is unambiguous. Prefer an explicit session ID when multiple runs may overlap.

## Structured And Streaming Output

Use the output format that matches the caller:

- `text`: human-readable final response.
- `json`: one result object containing `result`, `session_id`, and metadata.
- `stream-json`: newline-delimited events for real-time consumers.

For streamed output:

```bash
mkdir -p /tmp/claude-runs/test-debug
cd /abs/path/to/repo
claude --model fable -p \
  --output-format stream-json \
  --verbose \
  "Inspect the test failures and identify the root cause." \
  > /tmp/claude-runs/test-debug/events.jsonl
```

Trust the process exit and final result event as completion signals. Do not busy-poll the transcript or process list.

## Background Sessions

Start a background session when the work should survive the launching terminal:

```bash
cd /abs/path/to/repo
claude --model fable --bg -n dependency-audit "Audit dependencies and report actionable findings."
```

Inspect sessions non-interactively:

```bash
claude agents --cwd /abs/path/to/repo --json
```

Use `claude agents` interactively to monitor or dispatch sessions. Verify `claude --help` before using lifecycle commands such as `attach`, `logs`, `stop`, or `respawn`, because this surface changes across releases.

## Permissions And Isolation

- Keep normal permission handling for interactive work.
- For automation, grant only the tools the task requires with `--allowedTools` or a suitable `--permission-mode`.
- Use `--dangerously-skip-permissions` only when the environment is externally sandboxed or the user explicitly requests that risk.
- Use one output directory per scripted job. Never mix JSON, session IDs, or logs from concurrent runs.
- Use `--no-session-persistence` only when the conversation must not be resumable.
- Use `--bare` for reproducible automation that should not load local hooks, plugins, memory, or project instructions. Do not use it when those customizations are part of the task.

## Prompting

Give Claude a concrete role and scope:

- State the repository and intended outcome.
- Point it to actual files or commands when known.
- Say whether the task is review, diagnosis, implementation, or planning.
- Ask for findings first for reviews.
- On follow-up turns, resume the same session and describe only what changed or what to inspect next.

Avoid broad prompts such as "review everything" when the relevant branch, module, failure, or decision can be named.
