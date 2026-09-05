---
name: recursive-planning
description: Plan and execute substantial multi-step work with explicit acceptance criteria, scoped verification, and a final review. Use when a task has dependencies or spans sessions; keep planning proportional and stop when the requested outcome is verified.
---

# Recursive Planning

Carry the requested work through to a verified result. Keep the plan useful for execution and bounded by the user's objective.

## Define the outcome

- Identify the requested behavior, explicit exclusions, and evidence needed for acceptance.
- Inspect enough of the affected system to choose the next concrete step. Add investigation tasks for unresolved dependencies; do not require exhaustive exploration before implementation.
- Build a task list whose items produce reviewable results. Use as many items as the dependencies need, without a preferred count or a task for every incidental edit.
- Use available task tracking. Create a persistent goal only when the user or host instructions authorize it, and reuse a goal only when it tracks this objective. Bookkeeping must not block otherwise valid work.

## Execute and adapt

- Complete one coherent slice, verify it, then advance. Keep status accurate: splitting a task does not complete its unfinished work.
- Add findings that are necessary for the requested outcome. Put unrelated or disproportionate improvements on a follow-up list rather than making them new acceptance requirements.
- Replan when evidence changes the approach. Preserve completed work and do not rerun unchanged stages merely to refresh progress markers.
- Give concise updates about findings, decisions, and blockers. Resolve routine choices from existing context and authorization; ask only for a missing decision or access that materially affects the next step. Continue independent work while waiting.

## Review and stop

Review the final diff, affected callers, tests, docs, and configuration. Fix residual defects that prevent the requested outcome or invalidate its verification.

Repeat the relevant checks after those fixes. Broaden the review only when a failure or new risk warrants it; do not restart a whole-project sweep simply because the current list is complete.

Finish when the acceptance criteria are met, the required checks pass, and no known issue prevents delivery of the requested result. Report useful follow-ups separately. If required work is externally blocked, state what is incomplete and what would unblock it; do not label blocked work or its goal complete.

The final response should state the result, the evidence actually obtained, and any material limitation. Completing a task does not require exhausting every possible improvement to the project.
