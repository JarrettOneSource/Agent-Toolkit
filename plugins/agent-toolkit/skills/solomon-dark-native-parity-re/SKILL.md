---
name: solomon-dark-native-parity-re
description: Recover and port complete stock Solomon Dark systems into Website /game, or fix native-parity defects. Excludes ML training.
---

# Solomon Dark Native Parity RE

Recover the complete stock system that owns the reported behavior, document its
contract, and port it through verified browser acceptance. A parity report
defines a system investigation, including its siblings, authored data, scenes,
branches, timing, presentation, authority, and teardown. Fix the shared cause
and every affected member. Research-only requests stop at the requested evidence.

## Find the task and report evidence first

Use an explicitly supplied report file or folder directly. Otherwise, when the
chat lacks task details or supporting evidence, first check
`/home/user/solomon-darker-bug-reports/` before repository exploration or asking
the user for those materials. Read `README.md` and `STATUS.md`, then the matching
dated folder's `report.txt`, `source.json` and relevant `attachments/`. Match by
the requested report ID, title, symptom or Discord link, and include related
follow-ups such as later save files. The Windows mirror is
`/mnt/c/Users/User/Documents/Solomon Darker Bug Reports/`.

The current chat controls the task; archive status and old acceptance receipts
provide context rather than overriding a new report or assigning unrelated work.
If no matching report exists, continue with the supplied task and normal RE
workflow. If the task itself is still ambiguous, surface that after checking the
index instead of guessing a folder. When chat already supplies the needed brief
and evidence, use it directly without repeating intake.

For needed Discord intake or a requested archive refresh, use
[`discord-report-archive`](../discord-report-archive/SKILL.md). Preserve original
archive files as retained evidence; put experiments and extracted working copies
in task scratch so cleanup cannot remove the user's reports.

## Fleet Terminal ownership

When using Fleet Terminal, check the active item for an existing claim, then
claim it before starting work by writing your actual session ID(s) into its
shared task/status record. Include the coordinating session and any worker
sessions assigned to that item so other agents can see who owns it. Coordinate
overlapping work with an existing owner. Keep the claim current when sessions
change or work is handed off, and mark it released or completed when ownership
ends.

## Workspace boundaries

- `Website/` is the sole maintained Git root and parity authority. Durable RE
  docs, extracted data, assets, tools, implementation, tests, and publication
  belong there.
- The existing Mod Loader checkout may be read or executed as an RE instrument.
  Never edit it, create or maintain its task branches/worktrees, or use its tests
  as a Website acceptance gate.
- Run every automated Website check, validation build, and browser acceptance
  on the Mac mini. Windows/WSL may provide clean-stock and binary/runtime RE.
- Preserve dirty/shared checkouts and other tasks. Use an isolated Website
  worktree when needed. Reuse verified findings unless new evidence conflicts.

Read the Website instructions and authoritative handoff. For an investigation,
read `Website/docs/Game Native Parity RE/README.md`, its relevant system entry,
and affected source/tests. A documentation-only edit or status request needs
only the relevant material; it does not reopen completed system work by itself.

## Route by the work being performed

- Before new native recovery or parity implementation, read
  [system-recovery.md](references/system-recovery.md). It defines the membership
  inventory, evidence classes, full table extraction, and ledger-before-code
  contract. Enumerate membership before implementation; give every row a
  supported final disposition before delivery.
- Before Ghidra work, read
  [solomon-ghidra-workflow.md](references/solomon-ghidra-workflow.md). Use the
  existing read-only replica wrapper and explicit canonical project/replica
  paths; never bypass live project locks or import another task-local project.
- For injected runtime inspection, use `solomon-dark-live-memory-re`; injected
  observations support diagnosis and do not replace clean-stock evidence.
- Before any validation command, read
  [mac-validation.md](references/mac-validation.md). It owns exact-tree transfer,
  toolchain, process isolation, the canonical gate, and browser acceptance.
- Before authorized publication or post-push cleanup, read
  [publication-and-cleanup.md](references/publication-and-cleanup.md).

Load a reference when entering its workflow. Do not read every procedure before
a small edit or rerun unchanged checks merely because the skill is loaded.

## Evidence and acceptance

Extract every authored row and variant the recovered system consumes. Do not
substitute guessed constants, symptom patches, or inferred geometry for
available native data. An approximation needs a named browser constraint,
ledger disposition, and a disclosed visible difference.

Record new findings in the relevant Website system ledger before using them
to justify implementation. When shared evidence falsifies an assumption, remove
that assumption across all affected members. Reopen a completed system only
when a new report, change, or conflicting observation warrants it.

The completion gate includes per-member evidence, the exact candidate's Mac
`/opt/homebrew/bin/bash ./scripts/validate.sh`, and a real Mac browser journey
through the affected scenes. A test count, screenshot, or build alone does not
prove parity. Keep missing evidence explicit and continue authorized work that
can resolve it.

Honor publication authority already supplied in the session. Push, deployment,
and live behavior require their own evidence. After a verified authorized push,
complete task-owned branch/worktree/process/file cleanup, including residual
files beneath removed worktrees. Preserve tracked evidence or specifically
requested artifacts; do not touch shared work or maintain Mod Loader.

Finish at the requested verified boundary and report the recovered behavior,
coverage, Mac/browser evidence, platform limits, publication state, and cleanup.
ML policy training and checkpoint evaluation belong to `solomon-dark-ml-training`.
