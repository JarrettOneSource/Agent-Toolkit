# Execution profile

Scheduling is data, not doctrine. The invariants in `SKILL.md` (single writer,
trust-but-verify, no busywork, no waiting on the whole wave) hold under any
scheduler. Scheduling policy is a property of your environment, so it is not
in the skill at all. This file is an optional starting point that the skill
never loads on its own: copy what fits into your own rules or config.

## Example profile: single developer machine

An example, not a default. It assumes one box, no external scheduler, and
heavy processes that fight over CPU, memory, and ports.

- Run one heavy process at a time: compiler, full test suite, large data job,
  benchmark, or long scan.
- Keep parallel workers on light, nonoverlapping implementation and
  focused-test lanes.
- With an authorized pool of size N and useful bounded backlog, keep up to N
  cheap-model lanes filled. Refill a completed lane with the next independent
  light task without waiting for the whole wave.

## Writing your own

If your runtime already has an orchestrator, scheduler, workflow engine, or
capacity model, you need no profile. At most, state the precedence:

- Name the system that owns scheduling and concurrency.
- State the caps it enforces, so the agent does not negotiate with them.
- Keep the invariants from `SKILL.md`; they are the part that transfers.

Things that belong in a profile, not in the skill: worker counts, model tiers
per lane, wave sizes, retry policy, which processes count as heavy, and which
lanes may touch which directories.
