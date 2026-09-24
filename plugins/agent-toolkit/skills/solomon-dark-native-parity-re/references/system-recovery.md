# System Recovery

## Core Rule: The System Is the Unit of Work

A reported issue is never the work item. It is evidence that one native system
is not fully mirrored. The work item is that entire system, closed end to end
in this pass. You are done only when a user inspecting ANY other member,
variant, scene, or branch of the same system finds behavior the ledger already
proves correct — not merely the member they reported.

Do not tune the visible symptom with a CSS nudge, one-off delay, scene
exception, guessed constant, or compatibility shim.

Locate a native evidence thread: a function, field, vtable slot, registry
record, asset, state transition, or reproducible event. Pull it until the
whole owning system is recovered:

- upstream construction, ownership, initialization, inputs, and state writers;
- downstream update, render, audio, collision, replication, and destruction;
- lateral siblings sharing a factory, registry, vtable, bundle, scene,
  authored data table, or state machine;
- clocks, transition thresholds, coordinate spaces, ordering, randomness,
  authority, and lifetime boundaries.

### Declare the boundary, then enumerate the membership

Before any web code, write a system boundary declaration in the ledger: name
the native system, then enumerate its complete membership as a checkable
inventory —

- every xref of every recovered shared function;
- every row of every authored data table any member indexes;
- every class, variant, style, and scene that consumes the system;
- every state branch, setting gate, and degraded/fallback path;
- every asset, registry record, and audio/bundle resource it touches.

Before completion, give every member exactly one final recorded disposition: `exact-ported`,
`verified-already-at-parity`, `out-of-system` (with the reason), or
`blocked-by-platform` (with the named browser constraint). `not-yet-extracted`
is not a final disposition, and a silent or missing row prevents completion.
During investigation, record unresolved evidence and `recovered-pending-port`
members honestly. A recovered member can enter implementation once its native
contract is established; it must not be called `exact-ported` before validation.

### Extract the truth whenever the truth is extractable

If native truth exists — in instructions, static data tables, assets, registry
records, or reproducible runtime state — and the web system consumes that kind
of truth, extract all of it: every table row, every variant, every sibling
class, not only the members visible in the reported scene. Tedium, table size,
and session length are never reasons to approximate; spending that budget is
exactly what this skill exists for.

An approximation is legal only when the browser platform cannot represent the
native mechanism. It must then name the platform constraint in the ledger and
be surfaced in the completion receipt as a predicted visible difference.

### A falsified assumption dies everywhere at once

When evidence proves a shared assumption or approximation wrong for one
member, treat it as wrong for every member that shares it. Replace the
assumption class across the whole membership in the same pass. Never correct
the observed member while siblings keep the refuted path.

### A secondary report is a process failure

If a new issue lands in a system the ledger already covers, do not patch the
new symptom. Reopen the entry, state plainly which rule above the earlier pass
skipped, then close the entire system under these rules.

### Canonical failure — do not repeat it

The Boneyard directional-shadow work burned three user-report cycles on one
system. Pass one recovered the shared projector correctly but substituted
alpha-derived convex hulls for the authored caster outline tables ("not yet
extracted") and shipped. The user then saw canopy-wide Tree shadow wedges;
pass two extracted the Tree table at `0x0081B910` — pure static data available
all along — for Tree only, keeping the now-refuted hulls on every sibling
caster. A third report cycle extracted Gravestone, Fencepost, Monument, and
Building. Under these rules, pass one drains every caster's authored table and
the second and third reports never happen.

### Discovery passes

Run two passes before coding:

1. **Causal trace** — follow the reported behavior from input or scene entry to
   its owner, state transitions, outputs, and teardown.
2. **Membership sweep** — build the inventory above from xrefs, callers,
   callees, neighboring vtable slots, authored tables, registry records,
   alternate state branches, shared assets, sibling objects, and other scenes
   using the same system.

Do not stop at a one-hop caller or callee while ownership remains ambiguous.
Expand the investigation whenever a nearby discovery could change the causal
model, and record durable nearby findings even when they lie outside the
immediate web change.

The RE pass is ready for implementation when membership is enumerated, every
authored table the system consumes is fully extracted, and the recovered model
predicts every member's behavior. Record which recovered members still need
porting and validation. Final dispositions are the delivery gate, not a demand
to have implemented the system before coding starts. Keep platform constraints
explicit; unresolved extractable facts still require investigation.

## 1. Establish the Exact Workspace

1. Find the `Website/` Git root inside the outer Solomon Dark workbench. The
   outer directory is not a repository, and Mod Loader is not a task repository.
2. Read the Website `AGENTS.md` and authoritative handoff before acting. Read
   Mod Loader instructions only when required to invoke existing RE tooling
   safely; they do not expand the maintained scope.
3. Inspect branch, status, worktrees, remotes, and current `origin/main` for
   Website. Preserve user and concurrent-agent changes everywhere.
4. Use an isolated clean Website worktree from current `origin/main` when the
   shared checkout is dirty or concurrent. Never create, switch, update, or
   modify a Mod Loader branch/worktree for a parity task.
5. Verify the exact stock executable, build identity, capture source, process,
   and image base used for evidence. Never reuse a stale PID, runtime address,
   ASLR delta, or deployment claim.

Read these sources before starting a new investigation:

- `Website/docs/Game Native Parity RE/README.md` and the relevant system file —
  the sole authoritative parity ledger;
- relevant current web implementation and tests;
- stock assets, data files, captures, and existing Ghidra evidence;
- existing Mod Loader reports or catalogs only when useful as read-only
  historical evidence. Re-verify material facts and never update those files.

Search first. Distinguish confirmed prior findings from assumptions and open
questions; do not redo settled work without a conflicting observation.

### Canonical Ghidra environment

Before any Ghidra action, read
[references/solomon-ghidra-workflow.md](solomon-ghidra-workflow.md).
It owns the exact Windows installation/project locations, binary identity,
replica-pool invocation, script selection, address conventions, output
provenance, and stale-lock rules. The essential boundary is:

- canonical analyzed source project: outer workspace
  `Decompiled Game/ghidra_project/SolomonDark.gpr`;
- invocation provider: the existing Mod Loader checkout's
  `scripts/Invoke-GhidraHeadless.ps1` and `tools/ghidra-scripts/`, used
  read-only;
- concurrency owner: outer-workspace
  `Decompiled Game/ghidra_project_replicas/`;
- target: retail `SolomonDark.exe` 0.72.5 at preferred image base
  `0x00400000`.

Always pass the original Windows `-ProjectRoot` and `-ReplicaRoot` explicitly
when invoking from WSL or an isolated Website worktree. Record the exact Mod
Loader tool revision or file hashes used as provenance, but do not change that
checkout. Do not call
`analyzeHeadless.bat` directly against the canonical project, do not create a
second imported project in a task worktree, and do not clear replica locks
until live process inspection proves their owners are gone.

## 2. Define the Parity Question

Turn the user's mechanic or report into observable questions without asking for
details that can be discovered locally. Capture:

- the stock behavior to reproduce and the web behavior that differs;
- the scenes, actors, inputs, phases, and boundary conditions involved;
- what must be visually, behaviorally, or audibly measurable;
- which nearby systems may share ownership;
- which facts would falsify the leading explanation.

Reproduce both stock and web behavior when feasible before editing code. For a
reported issue, capture enough to make the symptom and its trigger concrete,
record the result and provenance in the Website ledger, then delete the
untracked capture or receipt during task cleanup.

## 3. Recover the Native System

Use multiple evidence classes where practical:

1. **Existing durable evidence** — Website ledger entries, stock captures,
   address maps, tests, and read-only historical Mod Loader reports/catalogs
   when useful.
2. **Clean stock observation** — launch the unmodified executable directly with
   every mod disabled, as required by the parity ledger. Capture exact inputs,
   timing, frames, pixels, and audio where relevant.
3. **Static content** — stock data, atlases, bundles, audio, scripts, and object
   registries.
4. **Static binary analysis** — use `$ghidra-binary-analysis` and the
   Solomon-specific workflow linked above for callers, callees, xrefs,
   constructors, layouts, vtables, constants, authored tables, and algorithms.
5. **Runtime investigation** — use `$solomon-dark-live-memory-re` for semantic
   state, pointer chains, watches, and traces when it can resolve an unknown.
   Treat loader-injected observations as supporting diagnostics, not clean-stock
   parity evidence; verify material conclusions through clean observation,
   static instructions, or a clearly labeled debugger run.
6. **Web instrumentation** — use Playwright and focused logging to determine
   which recovered contract the current port violates.

Do not treat decompiler names, one frame, one runtime sample, or visual
similarity as sufficient proof. Record function addresses, field offsets,
registry indices, asset records, call relationships, measurements, and
provenance in the Website ledger or a justified Website-tracked catalog. A
recorded capture path is provenance, not authorization to retain the disposable
capture. Label direct observation, instruction-derived facts, decompiler
interpretation, and inference separately.

Recover every applicable dimension before implementation:

- owner and lifetime;
- state representation and transition graph;
- every authored data table the system consumes, drained in full — all rows,
  variants, and styles, including members absent from the reported scene;
- producer/consumer call paths;
- fixed ticks, wall-clock timing, thresholds, and recurrence;
- geometry, transforms, coordinate systems, and camera relationship;
- painter, hit-test, collision, and traversal order;
- assets, audio channels, gain, pitch, and stream semantics;
- input, random selection, multiplayer authority, and replication;
- scene entry, exit, reset, interruption, and teardown.

## 4. Update the Living RE Documents Before Code

Read [references/re-ledger-template.md](re-ledger-template.md) before
writing the first entry. Update documents iteratively as the thread expands,
not as an afterthought.

Always update the relevant system file under
`Website/docs/Game Native Parity RE/` before using a finding to justify web
code. Create a new numbered system file and index entry only when the finding
belongs to a genuinely separate system. Update
`Website/docs/game-runtime-architecture.md` only when runtime ownership or
topology changes.

Website owns every durable output from this workflow. Put reusable native facts,
machine-consumable catalogs, extracted data, maintained RE helpers, and parity
receipts in an appropriate Website-owned path. Never update Mod Loader docs,
reports, catalogs, configuration, scripts, tests, or other files. Prefer its
existing RE tools read-only; keep one-off probes and raw logs task-owned and
temporary unless they become a justified Website artifact.

Record:

- the reported smell and parity question;
- exact evidence and provenance;
- native owner, state, calls, constants, and lifecycle;
- upstream, downstream, and sibling findings;
- confidence per conclusion and explicit unknowns;
- implementation consequence and validation contract.

Keep recovered facts distinct from web approximations and browser constraints.
Document nearby discoveries even when no web code consumes them yet.

## 5. Implement the Recovered Model

The system boundary is the scope. Inside it, implement everything the
recovered contract requires: porting the entire enumerated membership is the
default, not scope creep, and shipping the mechanism for only the reported
member while siblings keep a weaker path is a skill violation. Outside the
boundary, touch nothing — broad recovery does not authorize unrelated
refactors or speculative web features.

1. Add a focused failing regression or contract test before the behavior change
   when feasible.
2. Put ownership in the deepest cohesive web module that represents the native
   system. Make the reported fix emerge from shared rules.
3. Preserve externally visible stock behavior, not incidental executable debt.
   Use clear interfaces, authoritative simulation state, and separate
   presentation modules where appropriate.
4. Use recovered fixed-tick and lifecycle semantics instead of browser-frame
   guesses or arbitrary timers.
5. Use exact stock assets, constants, and extracted data everywhere the system
   consumes them. An approximation may exist only under a named platform
   constraint per the core rule — never in place of extractable native data.
6. Remove superseded symptom patches and stale tests in the touched scope.
7. Re-scan the recovered subsystem after implementation. If the web design
   exposes a missing native fact, return to RE and update the ledger first.

Do not change stock behavior or the Mod Loader merely to make the web port
easier. If maintained RE tooling is genuinely required, keep it cohesive and
Website-owned; invoke the existing Mod Loader wrapper read-only when needed.
