---
name: solomon-dark-live-memory-re
description: "Inspect Solomon Dark runtime state through the existing loader's Lua APIs, traces, and write watches."
---

# Solomon Dark Live Memory RE

Use this skill to treat the repo's Lua runtime as the first-line live reverse-engineering surface.
Prefer it over attaching WinDbg when the job is to inspect runtime state, compare objects, validate offsets, or trace a narrow code path without full single-stepping.

## Quick Start

Work from the workspace root that contains `Mod Loader/`.
Most repo docs assume `cwd` is `Mod Loader/`; either `cd "Mod Loader"` first or prefix paths with `Mod Loader/`.

For a live probe, first check the existing game and loader state. Start a task-owned game only when needed for the authorized diagnostic; do not disrupt an unrelated session.

Before using Lua exec:
- Ensure the game is running through the loader with Lua enabled.
- Ensure at least one Lua mod is loaded. The named-pipe executor uses the first loaded Lua mod state; if none are loaded it fails.
- Prefer enabling `sample.lua.ui_sandbox_lab` when you need a repeatable probe harness.

Primary entry points:
- One-off Lua: `python tools/lua-exec.py "<lua code>"`
- PowerShell bridge: `powershell.exe -NoProfile -File scripts/Invoke-LuaExec.ps1 -Code "<lua code>"`
- Settled render investigation helper: `python tools/live_bot_render_debug.py`
- UI and gameplay probe harness: `mods/lua_ui_sandbox_lab`

Read [references/lua-tooling-reference.md](references/lua-tooling-reference.md) when you need the full API inventory, example snippets, or current runtime limits.

## Working Order

Use the tools in this order unless there is a reason to skip ahead:

1. Start from semantic state.
   Query `sd.world.get_scene()`, `sd.world.get_state()`, `sd.player.get_state()`, `sd.bots.get_state(id)`, `sd.ui.get_snapshot()`, or `sd.hub.*` first.
   These APIs already expose recovered structure and live addresses, which is cheaper and safer than blind memory reads.

2. Pivot from semantic state into `sd.debug`.
   Use addresses returned by the semantic APIs as anchors for pointer-chain walks, snapshots, diffs, struct dumps, vtable dumps, traces, or write watches.
   The debug layer accepts either already-readable runtime addresses or original game-image addresses that can be rebased through the configured image base.

3. Use seam metadata to label what you see.
   Cross-check addresses and offsets against:
   - `Mod Loader/docs/lua-memory-tooling.md`
   - `Mod Loader/SolomonDarkModLoader/src/gameplay_seams.h`
   - `Mod Loader/SolomonDarkModLoader/src/gameplay_seams.cpp`
   - `Mod Loader/SolomonDarkModLoader/src/mod_loader_gameplay/public_api.inl`
   - `Mod Loader/SolomonDarkModLoader/src/lua_engine_bindings_gameplay.cpp`

4. Use Ghidra to explain unknowns, then return to Lua.
   Use Ghidra to identify symbols, object layouts, and likely call sites.
   Use Lua exec to verify those findings against a live scene immediately.

5. Escalate to WinDbg only for debugger-class problems.
   Stay in Lua for state comparison, pointer chasing, write-watch validation, trace-hit capture, and live object inspection.
   Escalate for single-step debugging, full native call stacks, crash-time analysis, or code paths that are unsafe to patch with the loader's trace hooks.

## High-Value Workflows

### Compare stock state against synthetic or remote-like state

Use `sd.player.get_state()` and `sd.bots.get_state(id)` to compare actor state, render descriptors, visual lanes, runtime handles, and scene ownership before reading raw memory.

### Chase a recovered object layout

Use `sd.debug.resolve_ptr_chain`, `dump_ptr_chain`, `resolve_object_ptr_chain`, `dump_struct`, and `dump_vtable` to walk from a known gameplay object to a live child object and verify its shape.

### Prove who writes a field

Use `sd.debug.watch_write` or `watch_write_ptr_field`, trigger the behavior in-game, then inspect `sd.debug.get_write_hits()`.
Prefer this for "who changed this byte/pointer/window" questions.

### Prove who consumes an object

Use `sd.debug.trace_function` on a narrow stock accessor or builder, reproduce the behavior, and inspect `sd.debug.get_trace_hits()`.
Prefer this for "which function reads this object" questions.

### Diff two live objects or windows

Use `snapshot`, `snapshot_ptr_field`, `snapshot_ptr_chain`, and `diff` when comparing player vs bot, before vs after, or scene A vs scene B.

### Stabilize a reproduction harness

Prefer the settled helpers already in the repo:
- `tools/live_bot_render_debug.py` for current bot/render investigations
- `mods/lua_ui_sandbox_lab` for repeatable UI and gameplay-entry setups

## Safety Rules

- Treat `sd.debug.call_thiscall_u32` and `sd.debug.call_cdecl_u32_u32` as last-resort tools. They are useful for narrow known signatures, not as a general calling interface.
- Treat page-guard write watches and invasive traces as opt-in diagnostics. They can destabilize runs if overused.
- When Lua exec reports that the engine is busy, wait briefly and retry only within the diagnostic's bound. Persistent contention calls for inspecting the owner; do not spin or terminate another task. The server uses a non-blocking Lua-engine lock.
- Keep Lua results compact. Return tables or key-value data that can be inspected, not megabyte-scale dumps.
- Prefer existing typed helpers over ad hoc raw writes. Keep any new maintained helper Website-owned; do not edit the Mod Loader checkout.

## Extension Guidance

The Mod Loader checkout is read-only tooling. Keep new maintained probes or helpers in Website-owned tooling and invoke existing loader APIs. For authorized extensions, prefer:
- Typed enumerators like actor, region, puppet, or live-object listings
- Layout-aware dumpers backed by named seam metadata
- Trace and write-watch enrichers that decode object identity, scene context, slot ids, and type ids
- Small helpers that return structured, inspectable state through Lua exec

Avoid extending the system with:
- Broad arbitrary native-call APIs
- Large raw dump surfaces that belong in external tools
- Duplicate helpers that re-expose data already available through `sd.player`, `sd.world`, `sd.bots`, or `sd.ui`
