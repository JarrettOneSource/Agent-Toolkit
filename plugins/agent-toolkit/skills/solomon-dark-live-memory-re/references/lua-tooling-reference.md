# Solomon Dark Lua Tooling Reference

This reference is the detailed map for the repo's live Lua reverse-engineering surface.
Read it when you need the full API inventory, example workflows, or the key source files that define the runtime contracts.

## Entry Points

Run these from `Mod Loader/`, or prefix paths with `Mod Loader/` from the workspace root.

- `python tools/lua-exec.py "<lua code>"`
- `powershell.exe -NoProfile -File scripts/Invoke-LuaExec.ps1 -Code "<lua code>"`
- `python tools/live_bot_render_debug.py`

Relevant repo docs and source:
- `docs/lua-memory-tooling.md`
- `README.md`
- `SolomonDarkModLoader/src/lua_exec_pipe.cpp`
- `SolomonDarkModLoader/src/lua_engine_bindings_debug.cpp`
- `SolomonDarkModLoader/src/lua_engine_bindings_debug/functions.inl`
- `SolomonDarkModLoader/src/lua_engine_bindings_gameplay.cpp`
- `SolomonDarkModLoader/src/mod_loader_gameplay/public_api.inl`
- `SolomonDarkModLoader/src/gameplay_seams.h`
- `SolomonDarkModLoader/src/gameplay_seams.cpp`

Address handling rule:
- Most `sd.debug` helpers accept either a readable runtime address or an original game-image address.
- If the address is not currently readable, the loader attempts to rebase it through the configured image base before failing.

## Preconditions

- Launch the game through `SolomonDarkModLauncher` so the loader is injected.
- Keep Lua enabled in the staged runtime flags.
- Load at least one Lua mod. The named-pipe executor runs against the first loaded Lua mod state and fails if no Lua mod state exists.
- Prefer `sample.lua.ui_sandbox_lab` when you need a repeatable live harness.

## Semantic Runtime APIs

Start with these before raw memory work:

- `sd.player.get_state()`
- `sd.world.get_state()`
- `sd.world.get_scene()`
- `sd.bots.get_state(id)`
- `sd.ui.get_snapshot()`
- `sd.ui.find_element(...)`
- `sd.ui.find_action(...)`
- `sd.ui.get_action_dispatch(...)`
- `sd.ui.activate_action(...)`
- `sd.hub.start_testrun()`

Use them to obtain:
- Stable scene kind and name
- Live actor, world, arena, region, progression, equip, and render addresses
- Current visual lane object addresses, holder kinds, vtable pointers, and type ids
- High-level UI action ids and dispatch state

## `sd.debug` API Inventory

### Scalar reads

- `sd.debug.read_u8(address)`
- `sd.debug.read_u16(address)`
- `sd.debug.read_u32(address)`
- `sd.debug.read_i8(address)`
- `sd.debug.read_i16(address)`
- `sd.debug.read_i32(address)`
- `sd.debug.read_float(address)`
- `sd.debug.read_ptr(address)`
- `sd.debug.read_ptr_field(ptr_address, offset)`
- `sd.debug.read_field_u8(ptr_address, offset)`
- `sd.debug.read_field_u32(ptr_address, offset)`
- `sd.debug.read_field_float(ptr_address, offset)`

### Scalar writes

- `sd.debug.write_u8(address, value)`
- `sd.debug.write_i8(address, value)`
- `sd.debug.write_u16(address, value)`
- `sd.debug.write_i16(address, value)`
- `sd.debug.write_u32(address, value)`
- `sd.debug.write_i32(address, value)`
- `sd.debug.write_float(address, value)`
- `sd.debug.write_ptr(address, value)`
- `sd.debug.write_field_u8(ptr_address, offset, value)`
- `sd.debug.write_field_u32(ptr_address, offset, value)`
- `sd.debug.write_field_float(ptr_address, offset, value)`

### Pointer-chain helpers

- `sd.debug.resolve_ptr_chain(ptr_slot_address, {off0, off1, ...})`
- `sd.debug.resolve_object_ptr_chain(base_address, {off0, off1, ...})`
- `sd.debug.dump_ptr_chain(ptr_slot_address, {off0, off1, ...})`
- `sd.debug.dump_object_ptr_chain(base_address, {off0, off1, ...})`
- `sd.debug.snapshot_ptr_chain(name, ptr_slot_address, {off0, off1, ...}, size)`
- `sd.debug.snapshot_object_ptr_chain(name, base_address, {off0, off1, ...}, size)`

### Watches and diffs

- `sd.debug.watch(name, address, size)`
- `sd.debug.watch_ptr_field(ptr_slot_address, offset, size, name)`
- `sd.debug.watch_write(name, address, size)`
- `sd.debug.watch_write_ptr_field(ptr_slot_address, offset, size, name)`
- `sd.debug.list_watches()`
- `sd.debug.unwatch(name)`
- `sd.debug.snapshot(name, address, size)`
- `sd.debug.snapshot_ptr_field(name, ptr_slot_address, offset, size)`
- `sd.debug.snapshot_nested_ptr_field(name, ptr_slot_address, outer_offset, inner_offset, size)`
- `sd.debug.snapshot_double_nested_ptr_field(name, ptr_slot_address, outer_offset, middle_offset, inner_offset, size)`
- `sd.debug.diff(name_a, name_b)`

### Function tracing

- `sd.debug.trace_function(address, name[, patch_size])`
- `sd.debug.untrace_function(address)`
- `sd.debug.list_traces()`
- `sd.debug.get_trace_hits([name])`
- `sd.debug.clear_trace_hits([name])`

Trace hits currently capture:
- Requested and resolved address
- Thread id
- `eax`, `ecx`, `edx`, `ebx`, `esi`, `edi`, `ebp`
- `esp_before_pushad`
- `eflags`
- `ret`
- `arg0`, `arg1`, `arg2`

### Write-watch history

- `sd.debug.get_write_hits([name])`
- `sd.debug.clear_write_hits([name])`

Write hits currently capture:
- Requested and resolved address
- Base, value, and exact access address
- Thread id
- `eip`, `esp`, `ebp`, `eax`, `ecx`, `edx`
- `ret`
- `arg0`, `arg1`, `arg2`
- Before and after bytes

### Struct and object helpers

- `sd.debug.dump_struct(address, field_defs)`
- `sd.debug.dump_vtable(object_or_vtable_address, count[, treat_as_object])`

### Raw bytes and search

- `sd.debug.read_bytes(address, count)`
- `sd.debug.read_string(address, max_len)`
- `sd.debug.search_bytes(start_addr, end_addr, "AA BB ?? CC")`
- `sd.debug.copy_bytes(src_addr, dst_addr, count)`

### Narrow native call shims

- `sd.debug.call_thiscall_u32(function_address, this_ptr, arg0)`
- `sd.debug.call_cdecl_u32_u32(function_address, arg0, arg1)`

### Gameplay helper exposed through `sd.debug`

- `sd.debug.switch_region(region_index)`

## Common Live Workflows

### 1. Start from scene and player state

```lua
local scene = sd.world.get_scene()
local world = sd.world.get_state()
local player = sd.player.get_state()
print(sd.inspect(scene))
print(sd.inspect(world))
print(sd.inspect(player))
```

Use these tables to obtain the actor, world, arena, region, progression, equip, and visual-lane addresses that anchor the rest of the investigation.

### 2. Compare stock player vs bot render state

```lua
local player = sd.player.get_state()
local bot = sd.bots.get_state(BOT_ID)
print(string.format("player attach object = 0x%X", player.attachment_visual_lane.current_object_address or 0))
print(string.format("bot attach object    = 0x%X", bot.attachment_visual_lane.current_object_address or 0))
print(string.format("player primary type  = 0x%X", player.primary_visual_lane.current_object_type_id or 0))
print(string.format("bot primary type     = 0x%X", bot.primary_visual_lane.current_object_type_id or 0))
```

Use this when the visual regression is "the bot differs from stock" rather than "the field at offset X changed."

### 3. Snapshot and diff a render-owned window

```lua
sd.debug.snapshot("player_variants", player_actor + 0x23C, 8)
sd.debug.snapshot("bot_variants", bot_actor + 0x23C, 8)
sd.debug.diff("player_variants", "bot_variants")
```

Use this to prove exactly which bytes differ before escalating to trace or write-watch work.

### 4. Trace a stock accessor

```lua
sd.debug.trace_function(0x00570D80, "equip_attachment_get")
-- reproduce the behavior
print(sd.inspect(sd.debug.get_trace_hits("equip_attachment_get")))
sd.debug.clear_trace_hits("equip_attachment_get")
```

Use this when you know or suspect the consumer function and need register plus argument snapshots.

### 5. Dump a live object's vtable

```lua
local object = 0x12345678
print(sd.inspect(sd.debug.dump_vtable(object, 16)))
```

Use the entries to match the object class back to Ghidra or your recovered maps.

### 6. Chase a pointer chain from a known slot

```lua
local final = sd.debug.resolve_ptr_chain(0x00820000, {0x14, 0x08, 0x30})
print(string.format("final = 0x%X", final or 0))
print(sd.inspect(sd.debug.dump_ptr_chain(0x00820000, {0x14, 0x08, 0x30})))
```

Use the dump variant first when the chain is still being validated.

### 7. Build a one-off struct decoder

```lua
local fields = {
  { name = "type_id", offset = 0x04, type = "u32" },
  { name = "x", offset = 0x18, type = "float" },
  { name = "y", offset = 0x1C, type = "float" },
  { name = "owner", offset = 0x20, type = "ptr" },
}
print(sd.inspect(sd.debug.dump_struct(OBJECT_ADDR, fields)))
```

Use this while recovering a layout before promoting it into a first-class semantic helper.

### 8. Prove who writes a field

```lua
sd.debug.watch_write("actor.variant_window", player.actor_address + 0x23C, 8)
-- reproduce the behavior
print(sd.inspect(sd.debug.get_write_hits("actor.variant_window")))
sd.debug.clear_write_hits("actor.variant_window")
```

Use this when the question is "what mutated this window" rather than "what reads it."

## Runtime Limits And Practical Caveats

- Lua exec uses the first loaded Lua mod state and fails if no Lua mod is loaded.
- Lua exec takes a non-blocking lock on the Lua engine. Busy errors should be retried rather than treated as hard failures.
- The trace machinery is x86-only and stores a bounded hit history.
- The Lua debug transfer cap is 1 MiB per request or response-sized memory operation.
- `sd.debug.search_bytes` caps the requested search span at 64 MiB.
- `sd.debug.dump_vtable` caps the entry count at 512.
- `sd.debug.trace_function` defaults to a 7-byte patch and refuses to patch a target that already looks detoured.
- The current runtime debug code caps trace-hit history at 256 entries and write-hit history at 256 entries.
- Logged bytes are truncated; do not expect large write buffers to be preserved in full.
- Page-guard write watches and intrusive traces can destabilize a run if used indiscriminately. Use settled harnesses and narrow watch sizes.
- The generic native call shims are intentionally narrow and only return success or failure. Do not build a generalized arbitrary-calling workflow around them.

## Best Companion Artifacts In This Repo

- `tools/live_bot_render_debug.py`
  Use for current bot-render investigations on a settled `testrun` scene.

- `mods/lua_ui_sandbox_lab/README.md`
  Use for repeatable UI and gameplay probe entry points.

- `docs/lua-memory-tooling.md`
  Use for the baseline Lua-memory workflow and examples.

- `SolomonDarkModLoader/src/gameplay_seams.h`
- `SolomonDarkModLoader/src/gameplay_seams.cpp`
  Use for the authoritative recovered address and offset inventory.

- `SolomonDarkModLoader/src/mod_loader_gameplay/public_api.inl`
- `SolomonDarkModLoader/src/lua_engine_bindings_gameplay.cpp`
  Use to see which recovered layouts already have semantic wrappers.

- `tools/ghidra-scripts/README.md`
  Use for the supported headless Ghidra workflow when you need to label new functions, globals, or object layouts offline.

## Extension Strategy

If you identify a recurring live-data RE task, prefer adding:
- Semantic getters that return structured runtime state
- Enumerators over known containers like pointer lists, scene tables, actor registries, or puppet-manager state
- Layout-aware dumpers keyed by recovered names instead of ad hoc field tables
- Trace and write-watch post-processors that decode object identity and scene context

Do not default to adding:
- Another raw scalar helper when `dump_struct`, pointer chains, or a semantic getter would be better
- A generic arbitrary native call interface
- Large dump surfaces that should live in WinDbg, Ghidra, or standalone scripts
