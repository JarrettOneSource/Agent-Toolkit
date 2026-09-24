# Publication and Cleanup

## 7. Publish and Clean Up Task Scaffolding

When the user authorizes a push to `main`:

1. fetch immediately before publication; if `origin/main` moved, rebase the
   focused commit and repeat the complete Mac validation/browser acceptance;
2. push normally as a fast-forward—never force-push;
3. fetch again and prove task `HEAD`, local `origin/main`, and
   `git ls-remote origin refs/heads/main` are the same Website commit;
4. only after that proof, clean up the task's scaffolding on both machines.

Cleanup is part of completion, not an optional courtesy:

- confirm each task worktree is clean and its branch tip is an ancestor of the
  verified remote `main`;
- stop task-owned servers, browsers, game processes, tunnels, and listeners by
  exact PID/path; never kill another task's process;
- remove every task-owned Mac acceptance worktree and local task worktree
  through the Website repository's `git worktree remove` (without `--force` for
  a clean worktree), then delete the merged local task branch with
  `git branch -d`. The complete former worktree paths must be absent afterward:
  no source copy, dependency, build output, hidden file, evidence file, or temp
  file may remain under them. If a clean removal leaves a task-owned residual,
  verify the exact path contains no foreign or uncommitted user data, then
  delete that residual directory and all of its files;
- delete a remote task branch only when this workflow created it and the user's
  cleanup/publication authorization covers it;
- remove task-owned patches, bundles, temporary databases, build outputs,
  scratch Ghidra logs/scripts, screenshots, copied captures, and temp
  directories from local and Mac storage, using trash/recoverable deletion when
  practical. Evidence is disposable after its result has been recorded: delete
  untracked logs, screenshots, videos, captures, traces, manifests, and receipts
  even when the completion report cites their measurements or hashes. Retain
  only repository-tracked artifacts or a named artifact the user explicitly
  asked to preserve;
- run `git worktree list`, `git branch --list`, process/listener checks, and
  exact-path filesystem checks afterward, and report any retained artifact and
  why it remains.

After a verified push, retaining a task worktree or any file beneath its former
path is a cleanup failure. If the user explicitly asks to preserve a named
artifact, move it to the agreed non-worktree destination before removing the
worktree and report that destination.

Do not preserve evidence by default or treat a hash/path mentioned in a ledger
or completion receipt as retention authorization. Record the conclusion and
provenance, then delete the underlying task-owned evidence unless it is tracked
in Website or the user explicitly requested that exact artifact be kept.

Do not clean, reset, switch, remove, or otherwise maintain the Mod Loader
checkout during publication cleanup. Stop only task-owned RE processes and
remove only task-owned temporary outputs created outside it.

Never reset, clean, remove, prune, or delete a dirty/shared primary checkout,
another agent's worktree or branch, the canonical Ghidra source project, or an
unrelated artifact. If the user did not authorize push, retain the focused task
worktree and report its path instead of deleting unfinished work.


## Completion Receipt

Report concisely:

- the recovered causal model and important nearby discoveries;
- the system membership inventory with per-member dispositions;
- every `blocked-by-platform` member surfaced as a predicted visible
  difference the user may notice;
- stock executable/capture provenance and key addresses or records;
- documents updated;
- implementation and regression coverage;
- exact validation and browser evidence;
- explicit unknowns, each platform-justified;
- commit, push, and deployment state as separate facts;
- post-push cleanup state: removed task branches/worktrees/processes/files and
  proof that every former worktree path is absent, plus every explicitly
  retained artifact at its non-worktree destination. The expected default is
  that no untracked task evidence remains.

Do not claim completion while a required evidence, document, implementation,
or validation gate remains unfinished, or while any inventory row lacks a
disposition.
