---
name: codex-cli
description: Start, resume, fork, or monitor local Codex CLI sessions and capture thread IDs and results.
---

# Codex CLI

Choose a session mode and keep its directory, permissions, and thread identity
explicit. Use the installed CLI's relevant help when syntax is uncertain.

- `codex exec` runs a scripted turn; `codex exec resume` continues one and
  `codex exec fork` branches it into a new thread.
- `codex`, `codex resume`, and `codex fork` provide interactive sessions.
- `codex exec --json` emits the thread UUID in `thread.started`.
- Save the exact UUID for continuation; avoid `--last` when sessions overlap.

Read [session-recipes.md](references/session-recipes.md) for the selected mode,
JSON capture, or concurrent-job commands. Treat its flags as examples to verify
against local help when needed, rather than a reason to change current policy.

Each job needs a concrete outcome, allowed side effects, and its own output
directory. Use read-only access for a review; preserve the user's model, effort,
delegation, and sandbox choices. Do not create a child agent merely because
this skill is available, and do not bypass approvals to avoid a prompt.

Use process exit, terminal events, and the final result to distinguish success,
failure, and incomplete work. A log file or a quiet process is insufficient.
Parse the thread ID from existing events; do not repeatedly scan session caches.

When using local job tools, use `start_job` followed by `wait_job` if staying
active. Use `monitor` only when ending the turn immediately for its callback.
A wait timeout observes the same running job; report requested status and
continue waiting rather than launching a duplicate. When shell execution has
already yielded a process session, continue that exact session.
