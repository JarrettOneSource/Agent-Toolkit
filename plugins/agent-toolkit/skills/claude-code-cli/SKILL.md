---
name: claude-code-cli
description: Start, resume, fork, or monitor Claude Code CLI sessions and capture their results.
---

# Claude Code CLI

Use the installed CLI and its relevant `--help` output as the command authority.
Check version, flags, or authentication when uncertain; a known print command
does not require checking every subcommand first.

Use `--model fable` unless the user chose another model. Pass the alias directly.
Run from the intended repository; use `--add-dir` for additional directories.
Keep the task role, allowed side effects, and expected result explicit.

- `-p` runs one scripted turn. Omit it only for an intended interactive session.
- `--resume <session-id>` continues a particular conversation.
- `--fork-session` with `--resume` branches a conversation.
- Choose text, JSON, or streamed JSON for the required output. Save the session
  ID and isolate each job's output directory.

Read [session-recipes.md](references/session-recipes.md) for the selected mode,
structured output, background-session commands, or permission options. Verify
version-sensitive flags against local help before using an unfamiliar recipe.

For advice, keep the subprocess read-only unless changes were requested. Honor
the user's current delegation, model, effort, and permission constraints.
Do not bypass permissions just to avoid a prompt. Use one exact session ID
instead of an ambiguous latest-session shortcut when jobs may overlap.

Trust process exit and the final result as completion evidence. Use `start_job`
and `wait_job` when remaining active; use `monitor` only when ending the turn
immediately for its callback. A wait timeout is an observation timeout, not
permission to restart the process. Report requested status before waiting again.
