---
name: ftb-quests-mod-authoring
description: Author, repair, validate, or package FTB Quests chapters against the installed Minecraft modpack.
---

# FTB Quests Mod Authoring

Use the active installed pack as the authority for versions, registries,
recipes, enabled features, and existing quest files. Verify facts the requested
change depends on; a title-key repair does not require auditing every mod.

## Select the work

Read the relevant sections of [authoring-workflow.md](references/authoring-workflow.md):

- New chapters or substantial expansion: Design Standard, inventory, authoring,
  layout, content validation, and Done Criteria.
- Missing titles or broken tasks: existing structure and mechanical validation;
  inspect target jars or runtime registry evidence for the affected IDs.
- Layout changes: graph layout and rendering checks.
- CurseForge export: packaging and applicable export criteria.

Do not turn layout rendering, a game relaunch, or a full export into a mandatory
step for an unrelated small edit. A reported in-game failure still needs a
current live check or an explicit statement that this evidence is unavailable.

## Preserve the chapter contract

- Write progression guides that explain setup, use, and upgrades. Expand rich
  systems into meaningful paths; keep real one-item endpoints small.
- Scope namespaces to the target mod and genuine addons. Compatibility with
  another mod does not make all of that mod's items part of this chapter.
- Preserve existing quest IDs and progress when reorganizing.
- Resolve all changed title keys and references. Language files or datagen alone
  do not prove an item-stack registry ID is valid; current runtime rejection wins.
- Keep dependency lines visible by default, progression accurate, and layouts
  readable. Render substantial graph changes and inspect overlaps or crossings.
- Export quest defaults under `overrides/config/ftbquests/quests/`; exclude
  saves, logs, caches, local backups, and personal data.

The bundled [inventory tool](scripts/ftbq_mod_inventory.py) inspects installed
jars and validates chapter namespaces and IDs. Use its `--help` and the selected
workflow section for arguments; include true addon namespaces in the same audit.

Finish when the requested chapter change and its applicable content, layout,
runtime, or packaging checks pass. Report exactly which layers were verified.
If the user asks for Claude collaboration, use it for design feedback while
Codex retains responsibility for installed content and validation.
