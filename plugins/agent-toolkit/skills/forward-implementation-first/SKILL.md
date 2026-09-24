---
name: forward-implementation-first
description: Unblock authorized pipeline work stalled by administrative markers, or prevent needless replay of already-valid stages.
---

# Forward Implementation First

Build the requested capability and verify its output. Use this skill when
bookkeeping is displacing that work, rather than for every multi-stage task.

## Distinguish paperwork from a real contract

Identify what a blocking marker actually protects. A missing dashboard row or
presence-only receipt does not by itself invalidate a correct result. Existing
authorization covers proportionate repairs to such administrative dependencies.

Preserve substantive requirements: input and revision identity, artifact
integrity, locks that protect live writers, reproducibility, frozen experiment
partitions, required signatures, product output formats, and actual runtime
evidence. A hash can identify the correct artifact without proving its behavior.
Do not bypass one of these requirements by calling it bookkeeping.

## Continue from the valid work

When a stage is blocked only by administrative state, inspect its inputs,
existing output, and downstream contract. Repair the stale record or run the
authorized stage directly if that is the smaller complete solution. Validate
the result before advancing. Use atomic publication when the output contract
requires it, within the user's existing publication authority.

Replay only work affected by changed inputs, a changed target revision,
malformed or incompatible output, or a demonstrated failure. Do not restart a
valid campaign to regenerate a missing marker or after a wait timeout. Preserve
valid earlier output and the evidence supporting it.

## Verify the result

Choose checks that address the affected behavior: schema, counts and joins,
identity conservation, complete output, representative samples, or resource
measurements. Follow the project's acceptance criteria; this skill creates no
universal checklist or numerical gate. An execution record supports a claim
only when it connects the command, inputs, result, and expected behavior.

Do not infer success from a file's presence. Finish the required implementation
and validation, then report the observed result and remaining dependencies.
Administrative incompleteness must not conceal missing behavioral evidence.

## Coordinate execution

Avoid overlapping jobs that compete for the same saturated resource, writer,
port, or experiment state. Independent work may proceed when isolation and the
user's delegation policy allow it. Keep one owner for publication and experiment
state. Verify a worker's output before consuming it, and use completed work when
its dependency is reached without waiting for unrelated workers. Scheduling and
model tiers belong to the runtime or the user's chosen execution profile.

Read [examples/failure-modes.md](examples/failure-modes.md) only when a concrete
pipeline failure needs an example. Stop when the requested result and its
required checks are complete.

If the user needs a scheduling profile and no runtime owns it, use
[examples/execution-profile.md](examples/execution-profile.md) as an optional
starting point. Its single-machine example is not a default policy.
