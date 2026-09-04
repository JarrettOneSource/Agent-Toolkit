---
name: "recursive-planning"
description: "Autonomous planning and execution for large multi-step tasks. Uses Codex goal tracking when available, decomposes the task into a full TODO list in the harness, executes every item, then re-scans and builds a new TODO list for residuals. Repeats until the task is fully complete. Does not stop or ask for input mid-execution. Final output is a completion report."
---

# Recursive Planning

When this skill is active, you are an execution engine. Your job is to decompose the task into work items, execute every one of them, and keep going until the task is fully done. Do not stop to summarize, ask questions, or report intermediate progress. See the work through to completion.

## Goal Tracking

At the start of a recursive-planning run, use Codex's goal functionality when it is available: create a goal that matches the user's objective before decomposition begins. If a goal already exists, continue under that goal instead of creating a duplicate. During residual sweeps, compare the remaining work against the active goal. Mark the goal complete only after the final sweep finds no actionable residual work, or after all remaining blockers are genuinely outside the environment.

## Phase 1 — Decompose

Before writing any code or making any changes, build the full TODO list.

1. Read, search, and investigate everything relevant to the task.
2. Create a task list in the harness using the task tools. Every item must be:
   - Concrete and scoped to a specific file, function, module, endpoint, test, or artifact.
   - Independently completable — finishing it produces a visible result.
   - Verifiable — there is a clear way to confirm it is done.
3. If there are unknowns, create investigation tasks for them. Do not bury unknowns inside broader items.
4. Prefer many precise items over few vague ones. A 30-item plan is better than a 5-item plan with hidden complexity.

Bad items: "Refactor auth", "Fix issues", "Update tests"
Good items: "Extract token refresh logic from `src/auth/session.ts:handleRefresh` into a standalone function", "Add test for expired-token path in `tests/auth.test.ts`", "Update OpenAPI spec for the new `/v2/verify` response shape"

## Phase 2 — Execute

Work the list from top to bottom.

- Mark each task `in_progress` when you start it. Mark it `completed` when done.
- Keep only one task `in_progress` at a time.
- If a task turns out to be larger than expected, mark it completed and add narrower replacement tasks for the remaining work. Do not leave tasks half-done.
- If you discover new work that must be done, add it as new tasks immediately. Do not defer.
- Do not stop to report progress. Do not ask the user questions. Do not summarize what you just did. Just keep executing.

## Phase 3 — Residual Sweep

When every task is marked completed, you are not done yet.

1. Re-scan the codebase, tests, docs, logs, and any artifacts you touched.
2. Look for anything still broken, incomplete, inconsistent, untested, or TODO-marked.
3. Build a new task list in the harness for every residual issue found.
4. Immediately begin executing this new list. Same rules as Phase 2.

This sweep is mandatory. Skip it and the task is not done.

## Phase 4 — Repeat Or Finish

After executing the residual task list, run Phase 3 again.

Keep cycling through Phase 3 → Phase 4 until one of these is true:
- The residual sweep finds zero new issues.
- The only remaining items are things that genuinely cannot be resolved in this environment (missing credentials, external service dependencies, runtime-only behaviors).

When you reach that point, the task is done.

## Final Output

Your final message to the user should be a short completion report:
- State that the task is done.
- List the major things that were accomplished.
- If anything remains unresolvable, state exactly what and why.

Do not give this report until all phases are complete. Do not give intermediate reports.
