# Solomon Dark Ghidra workflow

Read this reference before using Ghidra for a Solomon Dark parity task.

## Canonical environment and identity

Static analysis runs on the Windows side of the shared workspace.

| Item | Canonical value |
| --- | --- |
| Ghidra installation | `C:\Users\User\Documents\GitHub\ghidra_12.0.3_PUBLIC` |
| Source project root | `C:\Users\User\Documents\GitHub\SB Modding\Solomon Dark\Decompiled Game\ghidra_project` |
| Project | `SolomonDark` (`SolomonDark.gpr`) |
| Program | `SolomonDark.exe` |
| Retail binary source | `C:\Users\User\Documents\GitHub\SB Modding\Solomon Dark\SolomonDarkAbandonware\SolomonDark.exe` |
| Replica pool | `C:\Users\User\Documents\GitHub\SB Modding\Solomon Dark\Decompiled Game\ghidra_project_replicas` |
| Wrapper | existing Mod Loader checkout, read-only: `scripts\Invoke-GhidraHeadless.ps1` |
| Scripts | existing Mod Loader checkout, read-only: `tools\ghidra-scripts\` |
| Preferred image base | `0x00400000` |
| Retail image | 0.72.5, 4,723,200 bytes, SHA-256 `03a834566ce70fd8088f4cf9ee6693157130d8aec28c092cb814d6221231f1e3` |
| Layout/address catalog | existing Mod Loader checkout, read-only: `config\binary-layout.ini` |

The empty `.gpr` launcher file is not the analyzed data by itself; the sibling
`SolomonDark.rep` directory is part of the project. Never copy only the `.gpr`.

Mod Loader is only an execution dependency here. Do not edit, branch, update,
commit, push, validate, or publish its checkout. Record the tool revision or
file hashes used, then place every durable finding or maintained artifact in
Website.

## When Ghidra owns the question

Use Ghidra when the missing fact is instruction/static-data truth:

- constructor, destructor, owner, caller/callee, or update/render order;
- xrefs to a string, global, table, vtable, registry row, or asset record;
- object-field offsets and their readers/writers;
- exact constants, branches, float operations, RNG calls, and authored arrays;
- factory membership, RTTI/vtable siblings, and virtual overrides.

Use stock observation for appearance and externally visible timing. Use the
live-memory skill for dynamic pointers, runtime state, watches, and ASLR
mapping. Reconcile those evidence classes; do not ask a decompiler to prove a
pixel result or use one runtime sample to replace a complete static table.

## Required invocation path

The source project is a normal writable Ghidra project and locks under
concurrency. Never invoke `analyzeHeadless.bat` directly on it. Always use
`Invoke-GhidraHeadless.ps1`; it leases a replica, refreshes it when necessary,
and invokes Ghidra with `-readOnly -noanalysis`.

From the existing Mod Loader checkout in Windows PowerShell:

```powershell
$SourceProject = 'C:\Users\User\Documents\GitHub\SB Modding\Solomon Dark\Decompiled Game\ghidra_project'
$ReplicaPool = 'C:\Users\User\Documents\GitHub\SB Modding\Solomon Dark\Decompiled Game\ghidra_project_replicas'

.\scripts\Invoke-GhidraHeadless.ps1 `
  -ProjectRoot $SourceProject `
  -ReplicaRoot $ReplicaPool `
  -ScriptPath .\tools\ghidra-scripts\decompile_targets.py `
  -ScriptArguments 0x00548B00
```

From WSL, the wrapper and an existing post-script may come from the read-only
Mod Loader checkout, while `-ProjectRoot` and `-ReplicaRoot` must remain the
original Windows paths above. For example, with the shell currently at that
tool checkout root:

```bash
re_tool_root="$PWD"
powershell.exe -NoProfile -ExecutionPolicy Bypass \
  -File "$(wslpath -w "$re_tool_root/scripts/Invoke-GhidraHeadless.ps1")" \
  -ProjectRoot 'C:\Users\User\Documents\GitHub\SB Modding\Solomon Dark\Decompiled Game\ghidra_project' \
  -ReplicaRoot 'C:\Users\User\Documents\GitHub\SB Modding\Solomon Dark\Decompiled Game\ghidra_project_replicas' \
  -ScriptPath "$(wslpath -w "$re_tool_root/tools/ghidra-scripts/decompile_targets.py")" \
  -ScriptArguments 0x00548B00
```

This explicit split matters when implementation lives in an isolated Website
worktree: allowing the wrapper to infer `ProjectRoot` from that worktree points
it at a nonexistent outer workspace. Do not create a Mod Loader task worktree
to solve that path mismatch.

Prepare the four-slot pool once when missing:

```powershell
.\scripts\Invoke-GhidraHeadless.ps1 `
  -ProjectRoot $SourceProject `
  -ReplicaRoot $ReplicaPool `
  -PreparePool `
  -ReplicaCount 4
```

Use `-RefreshReplica` only after the canonical analyzed project changes. Use
`-ClearReplicaLocks` only after checking Windows processes and proving no live
Ghidra/wrapper process owns a slot; a lock is not stale merely because another
agent is quiet.

## Script selection

| Need | Script |
| --- | --- |
| Strings, RTTI, UI text, parser tokens | `search_terms_refs.py` |
| Exact function(s) by preferred address/name | `decompile_targets.py` |
| Every function referencing a global/table/vtable/string | `refs_to_addr_decompile.py` |
| Candidate users of an object-field offset | `find_offset_accesses.py`, then `find_reads_from_offset.py` / `find_writes_to_offset.py` |
| Raw instructions for a complete function | `dump_function_instructions.py` |
| Instruction window around one or more addresses | `dump_insns_around.py` |
| Arrays, float clusters, scalars | `dump_array.py`, `dump_values.py`, `dump_floats_at.py` |
| RTTI/vtable and virtual slot ownership | `find_vtable.py`, `vtable_slot_lookup.py`, `dump_vtable_around.py` |
| Call-site pushed/register arguments | `trace_call_arguments.py` |
| Symbols or references in a global range | `list_symbols_range.py`, `refs_in_range.py` |
| Durable bundle/audio/class registries | the relevant `catalog_*.py` or `trace_bundle_*.py` script |

`dump_insns_around.py` requires the window sizes before the addresses:

```powershell
.\scripts\Invoke-GhidraHeadless.ps1 `
  -ProjectRoot $SourceProject `
  -ReplicaRoot $ReplicaPool `
  -ScriptPath .\tools\ghidra-scripts\dump_insns_around.py `
  -ScriptArguments 12, 12, 0x00548B00, 0x00525800
```

Do not pass addresses alone to that script.

## Address and evidence discipline

- Ghidra addresses are preferred-image addresses based at `0x00400000`.
  Runtime addresses require an explicit process image base/ASLR conversion;
  never mix the two silently.
- Confirm `SolomonDark.exe` identity before relying on old addresses. Record
  project/program names, executable SHA-256, command/script/arguments, and
  every material address in the RE report.
- Check raw instructions whenever decompiler types, pointer arithmetic,
  float precision, branch strictness, or a tiny wrapper could change the
  conclusion.
- Start from an owner/string/global, expand through callers/callees/xrefs, then
  sweep factories, neighboring vtable slots, registry rows, and authored data.
- A one-function decompile is a lead, not membership closure. Drain every table
  and sibling path consumed by the recovered system.
- Prefer the existing Mod Loader probes without modifying them. If a new probe
  is essential, make it task-owned and temporary or maintain it in a cohesive
  Website-owned path, then pass its explicit Windows path to the read-only
  wrapper.
- Store raw logs only in a task-owned temporary directory. Promote durable facts
  and machine-consumable artifacts only into Website, then remove scratch
  scripts/logs after the verified push.
- Never add or update Mod Loader docs, reports, catalogs, configuration, scripts,
  tests, or other files under this skill.
