# Mac Validation

## 6. Prove the Result on the Mac Mini Only

Windows/WSL owns Ghidra, clean-stock observation, debugger work, and native
runtime probes because the retail executable is Windows-only. Those are RE
evidence, not permission to run Website tests locally. After Website source
edits begin, do not run focused tests, lint, formatting checks, type checks,
production builds used as gates, canonical validation, or Playwright acceptance
on Windows/WSL or another machine.

Run every validation command against the exact candidate tree on the Mac mini:

- focused unit/contract tests for constants, state transitions, ordering, and
  lifecycle;
- per-member coverage: every enumerated member with its own data row, branch,
  or code path gets its own assertion or visual check — validating only the
  reported member proves nothing about the system;
- the Website's only supported full gate, `./scripts/validate.sh`;
- a real Playwright journey through the affected `/game` scenes with page and
  console errors captured;
- mechanic-specific evidence such as pixels, animation frames, positions,
  collision outcomes, audio `play()` events/current time, or replicated state;
- a stock-versus-web comparison using matching inputs, viewport, scene phase,
  and timing where feasible.

Use SSH alias `mac-mini`. Discover the live source/worktree paths rather than
assuming an old acceptance directory; the stable source checkout is normally
under `/Users/jarrett/Projects/Solomon Dark/`, and task-owned acceptance
worktrees belong under `/Users/jarrett/codex-acceptance/`. Before running:

1. fetch current `origin/main` on both machines and rebase the focused task;
2. materialize a clean detached Mac worktree at that exact base, then transfer
   the focused commit/patch;
3. prove the local and Mac changed-file manifests are byte-identical;
4. inspect Mac processes for ownership and conflicting ports/profiles. There is
   no fixed parallel-workflow ceiling. Isolate task-owned ports, browser
   profiles, audio/temp paths, and evidence so concurrent workflows cannot
   contaminate receipts, and never stop another task's process;
5. expose the pinned toolchain with
   `PATH=/Users/jarrett/.local/bin:/Users/jarrett/.dotnet:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin`
   and run the repository-supported commands from the Mac worktree;
6. run browser acceptance against the built candidate on Mac Chrome, capture
   page/console/failed-response arrays, and stop only task-owned processes.

Run the complete gate as `/opt/homebrew/bin/bash ./scripts/validate.sh` from the
Mac Website root. Windows-only native probes, including read-only use of Mod
Loader tooling, may still establish missing stock facts, but Mod Loader tests
are not part of this skill's validation or publication contract and do not
replace the Mac Website receipt.

Do not call configuration, a build, or a screenshot alone proof of behavioral
parity. Clean up only processes and temporary artifacts owned by the task.

If the user explicitly requests commit, push, release, or deployment, verify the
exact tree and perform that separate publication step. Do not infer those
permissions from a request to RE or implement. A push is not a deployment; a
production claim requires live routes, services, browser behavior, and rollback
readiness. Never restart an occupied production runtime without authorization.
