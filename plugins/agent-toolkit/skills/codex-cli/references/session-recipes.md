# Codex CLI

## Overview

Use Codex as another agent, not as an opaque subprocess. Choose interactive versus non-interactive mode deliberately, record explicit thread ids, and treat waiting, logging, and parallel session hygiene as part of the workflow.

## Workflow

1. Verify the local CLI surface if there is any doubt about flags or subcommands.
   - `codex --help`
   - `codex exec --help`
   - `codex resume --help`
   - `codex fork --help`
   - `codex exec resume --help`
2. Choose the session mode deliberately.
   - New scripted turn: `codex exec`
   - Resume a scripted thread: `codex exec resume`
   - New live interactive chat: `codex [OPTIONS] [PROMPT]`
   - Resume a live interactive chat: `codex resume`
   - Branch a live interactive chat: `codex fork`
   - Branch a scripted thread: `codex exec fork`
3. Prefer explicit UUID thread ids over `--last` when more than one Codex session may exist.
   - `codex exec --json` emits `thread.started` with the thread UUID.
   - `codex resume` accepts a UUID or thread name.
   - `codex fork` documents UUID input, so record the UUID if branching may matter later.
4. Prefer `codex exec` and `codex exec resume` for agent-to-agent orchestration.
   - They block until the turn completes.
   - They can emit machine-readable JSON.
   - They can be backgrounded safely when parallel work is useful.
5. Use top-level `codex resume` and `codex fork` only when a live TUI is actually useful.
   - Use `codex exec fork <thread-id>` for a scripted branch. Capture its new
     UUID separately from the source thread.
6. Keep each run isolated.
   - Use a separate run directory per Codex job.
   - Store `events.jsonl`, `last.txt`, `pid`, and `thread_id` separately for each job.
   - Do not mix logs from multiple Codex processes into one file.

## Command Patterns

Adapt these examples to the installed CLI and requested permissions.

New scripted thread:

```bash
codex exec \
  -C /abs/path/to/repo \
  -s workspace-write \
  --json \
  -o /tmp/codex-runs/review/last.txt \
  "Inspect the repo, then review the implementation and return findings first with file references."
```

Resume a scripted thread:

```bash
cd /abs/path/to/repo
codex exec resume \
  --json \
  -o /tmp/codex-runs/review-followup/last.txt \
  019d59a2-28db-7ec0-b4fd-240e7cb49317 \
  "I changed the implementation. Re-check the actual files and either sign off or return findings first."
```

Important nuance:

- `codex exec` accepts `-C`.
- `codex exec resume` does not accept `-C` in the current CLI surface, so `cd` into the target repo first.

Fork a scripted thread:

```bash
cd /abs/path/to/repo
codex exec fork --json "$thread_id" "Explore the alternative within the agreed scope."
```

New live interactive chat:

```bash
codex -C /abs/path/to/repo
```

New live interactive chat with an opening prompt:

```bash
codex -C /abs/path/to/repo "Inspect the current branch and propose the narrowest safe fix."
```

Resume a live interactive chat:

```bash
codex resume 019d59a2-28db-7ec0-b4fd-240e7cb49317
```

Fork a live interactive chat:

```bash
codex fork 019d59a2-28db-7ec0-b4fd-240e7cb49317
```

## Waiting And Completion

Do not poll aggressively.

- Foreground `codex exec` and `codex exec resume` already wait until Codex finishes. If you need the result before doing the next step, just run the command in the foreground and let the shell block.
- Only background a Codex process when you have useful work to do in parallel.
- When a Codex job is backgrounded, prefer `wait` when you are ready for the result.
- If you need periodic status checks while doing other work, sleep between checks. Use coarse intervals like 15 to 60 seconds, not tight loops.

Blocking run with no polling:

```bash
codex exec -C /abs/path/to/repo --json -o /tmp/run/last.txt "Review the diff."
```

Background run with explicit wait:

```bash
run_dir=/tmp/codex-runs/$(date +%Y%m%d-%H%M%S)-review
mkdir -p "$run_dir"

codex exec \
  -C /abs/path/to/repo \
  -s workspace-write \
  --json \
  -o "$run_dir/last.txt" \
  "Review the implementation and return findings first." \
  >"$run_dir/events.jsonl" 2>&1 &

pid=$!
printf '%s\n' "$pid" >"$run_dir/pid"

wait "$pid"
status=$?
printf '%s\n' "$status" >"$run_dir/exit_status"
```

Background run with coarse sleep intervals instead of busy polling:

```bash
while kill -0 "$pid" 2>/dev/null; do
  sleep 30
done

wait "$pid"
status=$?
```

Capture the thread id from JSON output:

```bash
for _ in $(seq 1 30); do
  thread_id=$(rg -o '"thread_id":"[^"]+"' "$run_dir/events.jsonl" 2>/dev/null | head -n1 | cut -d'"' -f4)
  [ -n "$thread_id" ] && break
  sleep 1
done

printf '%s\n' "$thread_id" >"$run_dir/thread_id"
```

Completion signals worth trusting:

- Process exit from `codex exec` or `codex exec resume`
- `turn.completed` in `events.jsonl`
- `item.completed` containing the final `agent_message`
- The `last.txt` file written by `-o`

Do not keep re-running `ps`, `tail`, or `rg` every second. Launch the job, do other work, then `wait` or sleep for a reasonable interval before checking.

## Parallel Runs

When running more than one Codex session at the same time, use one run directory per job and avoid ambiguous resume behavior.

Parallel example:

```bash
base=/tmp/codex-runs/$(date +%Y%m%d-%H%M%S)
mkdir -p "$base/review" "$base/plan"

codex exec \
  -C /repo/app \
  --json \
  -o "$base/review/last.txt" \
  "Review the current branch and list findings first." \
  >"$base/review/events.jsonl" 2>&1 &
review_pid=$!
printf '%s\n' "$review_pid" >"$base/review/pid"

codex exec \
  -C /repo/app \
  --json \
  -o "$base/plan/last.txt" \
  "Inspect the repo and propose a stepwise implementation plan." \
  >"$base/plan/events.jsonl" 2>&1 &
plan_pid=$!
printf '%s\n' "$plan_pid" >"$base/plan/pid"

wait "$review_pid"
wait "$plan_pid"
```

Parallel hygiene rules:

- Do not use `--last` if more than one relevant session may exist.
- Record each job's thread UUID as soon as it appears.
- Keep prompts narrow so each thread has a distinct purpose.
- Resume the exact UUID you intend, not "whatever was newest."
- Use `--ephemeral` only when you intentionally do not want to resume that job later.

## How To Prompt Codex

Be specific and keep the scope narrow.

- State the repo or working directory Codex should inspect.
- Tell Codex whether you want review, implementation, debugging, or plan critique.
- Ask for findings first when you want a review.
- Ask Codex to inspect actual files and commands, not just restate the prompt.
- On follow-ups, resume the same thread id and only ask for the next pass you need.

Useful prompt patterns:

Initial review:

```text
Inspect the actual repository state and review the implementation. Return findings first, ordered by severity, with file references. If the approach is sound, say so explicitly.
```

Implementation pass:

```text
Inspect the repo, implement the narrowest safe fix, run the relevant checks, and summarize what changed plus anything that still needs manual verification.
```

Follow-up on the same thread:

```text
I changed the implementation. Re-check the actual files and either sign off or return the remaining findings first.
```

## Practical Notes

- `codex exec --json` is the easiest way to capture a thread UUID programmatically because it emits `thread.started` immediately.
- Codex persists sessions by default under `~/.codex/sessions/...`; that is useful for recovery, but direct UUID capture from JSON is cleaner.
- Use `-s read-only` for audit-only runs and `-s workspace-write` when Codex should edit files.
- Use `--skip-git-repo-check` only when you intentionally run outside a Git repository.
- Use `--dangerously-bypass-approvals-and-sandbox` only when the environment is already externally sandboxed or the user explicitly wants that behavior.
- If you are unsure whether a flag still exists, re-run local help and adapt. Do not trust memory over the installed CLI.
