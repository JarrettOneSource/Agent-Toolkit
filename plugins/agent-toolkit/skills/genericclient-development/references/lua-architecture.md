# Lua architecture and manifest workflow

Read this reference when creating, reorganizing, or debugging GenericClient Lua
automations.

## Standalone script layout

A registered script has a root descriptor in `scripts/manifest.json` and a root
Lua file that returns inputs, optional actions, and `run`.

Use this structure for substantial scripts:

```text
scripts/
|-- script-name.lua
`-- script-name/
    |-- config.lua
    |-- state.lua
    |-- preparation.lua
    `-- feature.lua
```

For a multi-quest runner:

```text
quest-runner/
|-- shared/
|   |-- state.lua
|   |-- preparation.lua
|   `-- travel.lua
|-- witchs_house/
|   |-- config.lua
|   |-- state.lua
|   |-- quest.lua
|   |-- combat.lua
|   `-- completion.lua
`-- waterfall/
    |-- config.lua
    |-- state.lua
    `-- quest.lua
```

Each quest folder owns its IDs, varps, zones, phase reducer, interactions, and
recovery logic. `shared/` owns only mechanics used by multiple quests. Root
orchestration selects the quest module and presents UI; it should not accumulate
quest-specific branches indefinitely.

## Design rules

- Keep functions short, named by game/domain intent, and readable by a junior
  contributor. Prefer explicit receipts over clever tables or metaprogramming.
- Make state reducers pure where practical. Recompute observed phase after each
  verified mutation and on resume.
- Use `gc.read` snapshots for decisions and `gc.await` for events/actions.
  Success requires an observed postcondition: varp, item, position, NPC form,
  XP, dialogue, or quest state.
- Entity interaction targets exact IDs and optional WorldPoints. Do not bind a
  later form to the first form's display name.
- Combat loops tolerate queued hits, handle food through the framework guard,
  dismiss level-up dialogues, and resume autocast explicitly.
- Keep temporary exploration in the REPL or an untracked diagnostic. Fold the
  proven algorithm into the standalone module and delete the diagnostic.
- Diagnostics and NPC printers never auto-start unless explicitly requested.

## Manifest and bundled files

Whenever bundled Lua content changes in a way that must replace installed
copies:

1. Increment `genericclient_scripts.vN` in both the bundled manifest and
   `GenericClientScriptRegistry.SCHEMA`.
2. Add the previous schema to `PREVIOUS_SCHEMAS`.
3. Keep manifest module keys unique across the script; `gc.require` uses those
   keys, not filesystem-relative imports.
4. Update `BUNDLED_SCRIPT_FILES` for additions/moves.
5. Add old bundled paths to `REMOVED_BUNDLED_SCRIPT_FILES` when reorganizing so
   migration removes stale copies but preserves user-authored scripts.
6. Update registry/Lua-host tests and documentation examples to the new schema.

Hot-reloading an installed module is acceptable for a bounded live experiment,
but source remains authoritative. Package the same change with a schema bump
before publication.

## Verification

- Focused Java tests while iterating.
- `GenericClientLuaHostTest` to compile/load modular Lua and exercise phase
  behavior.
- `GenericClientScriptRegistryTest` for migration, module composition, removed
  paths, and preservation of custom scripts.
- A bounded live receipt for behavior that depends on OSRS state, projection,
  collision, menus, or timing.
- Full gates before install/push; see `release-workflow.md`.
