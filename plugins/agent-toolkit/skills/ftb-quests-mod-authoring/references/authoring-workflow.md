# FTB Quests Mod Authoring

## Core Rule

Treat the installed modpack as the source of truth. Do not invent quests from memory. Verify mod versions, item IDs, tags, recipes, configs, and existing quest files from the live profile before editing.

## Design Standard

FTB Quests chapters should feel like progression guides, not item checklists. The player should understand what system they are entering, what they should build first, what the setup enables, and which nearby upgrades or side loops naturally follow.

- Start from the mod's real gameplay loops: resource acquisition, crafting stations, power or source generation, automation workers, transport, storage, tools, armor, combat, bosses, and integrations.
- Use quest nodes to teach the loop shape. A good local path is often setup -> operation -> scaling, tool -> charging/modules -> field use, worker -> filter -> automation target, or machine -> recipe family -> downstream use.
- Keep optional side content visible without pretending it is core progression. Decorative, novelty, combat, or anarchy-useful toys can be small branches if they are real features.
- Do not collapse a rich system into one node just because one representative item exists. Conversely, do not inflate a genuine one-item endpoint into fake tasks.
- Preserve chapter scope. A progression chapter for one mod or suite should not absorb unrelated storage, armor, or machine content merely because compatibility jars exist.
- Write node titles and descriptions so they answer "why would I care?" without turning the quest book into a wiki article.
- For anarchy-oriented packs, account for practical multiplayer use: hiding infrastructure, raid utility, travel risk, destructive tools, team logistics, and recoverability after loss.

Common profile surfaces:

```bash
PROFILE="/mnt/c/Users/User/curseforge/minecraft/Instances/2b2m"
find "$PROFILE/config/ftbquests/quests" -maxdepth 3 -type f | sort
find "$PROFILE/mods" -maxdepth 1 -type f | sort
```

## Workflow

1. Locate the active profile and duplicate profiles.
   - Read `minecraftinstance.json` for Minecraft, loader, and installed addon versions.
   - Check duplicate CurseForge instance folders when the user has had copied profiles.
   - Prefer the active profile's `mods/`, `config/`, `defaultconfigs/`, `kubejs/`, and logs over generic examples.

2. Inventory the target mod.
   - Inspect the installed jar with `unzip -l` and extract `assets/<modid>/lang/en_us.json`, `data/<modid>/recipe`, tags, advancements, Patchouli/guide data, and integration data.
   - For NeoForge JarJar bundle mods, inspect nested jars under `META-INF/jarjar/` too; the bundled wrapper may have no assets while the real addon modids live inside nested jars.
   - Define the chapter's allowed namespaces before authoring. Include the target mod and true addons/expansions only. Do not include unrelated mod items just because a compatibility mod touches them; put those in that mod's chapter or a separate integration chapter unless the user explicitly asks otherwise.
   - Search configs for progression gates and disabled features.
   - For repeatable audits, run the bundled generic extractor: `scripts/ftbq_mod_inventory.py --profile "$PROFILE" --modids "<modid>[,<addon_modid>...]" --chapter "<chapter_name>" --allowed-namespaces "<modid>[,<addon_modid>...]" --strict --out-md "$PROFILE/quest-layout-debug/<modid>-inventory.md" --out-json "$PROFILE/quest-layout-debug/<modid>-inventory.json"`.
   - Use the extractor output to validate item/entity task IDs, count registered blocks/items/entities/recipes/tags/worldgen/configs, and identify quest coverage gaps before writing or reorganizing nodes.
   - Treat `assets/*/lang`, models, recipes, tags, and generated data as evidence, not proof. Some IDs appear in datagen or language files but are not valid item-stack registry IDs for FTB item tasks.
   - If current external knowledge matters, use primary sources or reputable modpack examples, then verify every ID locally.
   - For complex mods, build an outline first: core systems, early progression, midgame machines/spells/tools, endgame loops, optional branches, and integration points with other installed mods.

3. Study existing FTB Quests structure.
   - Important files are usually under `config/ftbquests/quests/`.
   - Check `data.snbt`, `chapter_groups.snbt`, `chapters/*.snbt`, and `lang/en_us.snbt`.
   - Unnamed categories usually mean a missing or mismatched title key, broken chapter group reference, or malformed chapter metadata.
   - Keep IDs stable when reorganizing existing quests unless replacing a broken draft is explicitly acceptable.

4. Borrow from reference packs carefully.
   - Use polished packs for structure, pacing, and wording inspiration, not blind copy-paste.
   - Port only concepts that match installed versions and enabled features.
   - Re-check every item, fluid, gas, entity, recipe, and dependency edge against the local jars/configs.

5. Author real quests.
   - A quest should teach or drive a concrete game action: craft, obtain, automate, upgrade, explore, fight, or compare systems.
   - Avoid placeholder "read this" nodes unless they are short branch labels or necessary orientation.
   - Use verified item icons and item tasks whenever possible.
   - Put readable titles and descriptions in the lang file, and confirm every quest/chapter/group title resolves.
   - Keep chapter scope coherent. Split huge mods into branches such as basics, resources, machines, power, automation, armor/tools, combat, and integrations.
   - Compatibility targets are not automatically progression content. Example: `create_mekanism_compat` may make Mekanism blocks work on Create/Aeronautics contraptions, but `mekanism:digital_miner` belongs in a Mekanism chapter, not a Create progression chapter. Likewise, Sophisticated Backpacks items belong in a backpack/storage chapter unless the user asks for a mixed integration page.
   - After the first usable graph exists, audit terminal leaves and one-off nodes. For each leaf, decide whether it is a true endpoint, a small utility, or a compressed gameplay loop.
   - Do not leave a mechanically rich item as a single isolated node. Deepen it into a short mini-path when the mod has a real setup/use/upgrade loop, related guide pages, advancements, recipes, or companion blocks/items.
   - Keep mini-paths small and intentional: usually 2-4 nodes around a local hub. Good patterns are setup -> operation -> upgrade, tool -> charging/modules -> field use, storage -> import/export -> portable access, automation worker -> filters -> scaled storage, or machine -> recipe families -> integration.
   - Do not create filler nodes just to increase node count. If a leaf is genuinely a single novelty item or final milestone, keep it as a leaf and document why.
   - Examples from the 2b2m chapters: Create fan processing becomes washing/haunting recipe-family branches; Ars Nouveau Potion Lab becomes potion storage plus mixing/diffusion; Ars helper mobs split into Wixie brewing, Whirlisprig farming, Drygmy mob jars, Bookwyrm lecterns, and repository scaling; Mekanism mobility splits into jetpack, Free Runner, breathing, and Hazmat kits; the Digital Miner gets a filter/logistics mini-path; MekaSuit/Meka-Tool get module paths.

6. Design the graph layout deliberately.
   - FTB Quests nodes can use shapes such as circles, squares, diamonds, triangles, and hexagons. Use them to mark hubs, milestones, optional leaves, warnings, and endgame goals.
   - Prefer trunk-and-branch, tree, radial, or spider-web layouts over rigid grids for large mods.
   - Keep related systems spatially clustered, with leaves fanning out from hubs.
   - Avoid deep cross-branch dependencies unless the mod genuinely requires them.
   - Typical edges should be visually short and readable; long edges are acceptable only for meaningful system jumps.
   - Keep dependency lines visible by default unless the user explicitly wants hover-only lines.
   - After expanding mini-paths, re-render the graph and check that the new local leaves form readable fans, not accidental straight-line clutter. Prefer zero crossings when it can be achieved without distorting the progression.

7. Validate layout with tooling.
   - Render a quick image of quest nodes, labels, edges, and shapes before finalizing large chapters.
   - Calculate graph metrics: duplicate coordinates, edge crossings, isolated nodes, very short overlaps, and long-distance outliers.
   - Fix crossing clusters and unreadable labels, then render again.
   - A good result should look understandable before launching Minecraft.

8. Validate content mechanically.
   - Parse or load the SNBT files if local tooling exists.
   - Search for unresolved lang keys, duplicate IDs, missing chapter references, and malformed task/reward blocks.
   - Verify all item IDs exist in installed jars or generated KubeJS data.
   - After launching the pack, scan `logs/latest.log` for `Tried to load invalid item` and `Unknown registry key in ResourceKey[minecraft:root / minecraft:item]`. Any quest task/icon ID named there must be removed, replaced, or proven fixed by a later relaunch.
   - Verify entity task IDs against installed entity language keys or registry evidence; if a chapter has no entity tasks, say that explicitly.
   - For addon suites, validate all relevant true-addon mod ids together and pass the same namespaces through `--allowed-namespaces`. Cross-mod item tasks are acceptable only when that item belongs to the target suite, not merely because another compatibility mod references it.
   - Check `logs/latest.log` after launch for FTB Quests parse errors, missing item IDs, or translation warnings.
   - If the user reports in-game `Missing Item`, trust the live report over static extraction and patch the chapter immediately. Re-run validation with `--strict` and relaunch or inspect a newer log before calling the chapter done.

9. Package defaults correctly.
   - For CurseForge exports, quest files must live in the exported `overrides/config/ftbquests/quests/` path.
   - Exclude logs, crash reports, saves, caches, local backups, and personal data from exports.
   - If the modpack updater feed or changelog mentions quest additions, update those files only after the local quest set validates.

## Useful Commands

Inspect a mod jar:

```bash
unzip -l "$PROFILE/mods/<mod-file>.jar" | rg 'assets/.*/lang/en_us.json|data/.*/recipes?|data/.*/tags'
```

Find likely quest title problems:

```bash
rg -n 'title:|subtitle:|group:|chapter' "$PROFILE/config/ftbquests/quests"
rg -n 'ftbquests|Unknown|Failed|Exception' "$PROFILE/logs/latest.log"
```

Check whether a quest item ID exists in installed jars:

```bash
for jar in "$PROFILE"/mods/*.jar; do
  unzip -l "$jar" | rg -q 'assets/.*/lang/en_us.json|data/.*/recipes?' && echo "$jar"
done
```

Run the generic inventory and quest validator. Set `SKILL_DIR` to this skill's
directory from the client catalog; Claude Code exposes `${CLAUDE_SKILL_DIR}`:

```bash
python3 "$SKILL_DIR/scripts/ftbq_mod_inventory.py" \
  --profile "$PROFILE" \
  --modids "<modid>[,<addon_modid>...]" \
  --chapter "<chapter_file_without_snbt>" \
  --allowed-namespaces "<modid>[,<addon_modid>...]" \
  --strict \
  --out-md "$PROFILE/quest-layout-debug/<modid>-inventory.md" \
  --out-json "$PROFILE/quest-layout-debug/<modid>-inventory.json"
```

Find item-stack failures after a launch:

```bash
rg -n 'Tried to load invalid item|Unknown registry key in ResourceKey\\[minecraft:root / minecraft:item\\]|Missing Item|ftbquests:missing_item' "$PROFILE/logs/latest.log"
```

Create-suite cautionary example:

- Keep Create progression scoped to `create`, true Create addons such as `createaddition`, `createbigcannons`, `tracks`, `aeronautics`, `offroad`, `simulated`, and intentional bridges such as `ars_creo`.
- Do not add `mekanism:*`, `mekanismgenerators:*`, or `sophisticatedbackpacks:*` tasks to a Create progression chapter just because compatibility jars are installed.
- If the live log rejects task IDs such as `create:small_bogey`, `create:large_bogey`, `create:glass_fluid_pipe`, `create:encased_fluid_pipe`, `create:lectern_controller`, `createaddition:liquid_blaze_burner`, `aeronautics:levitite_blend`, `simulated:merging_glue`, `simulated:paired_docking_connector`, `createbigcannons:cannon_cast`, `createbigcannons:finished_cannon_cast`, or `createbigcannons:cannon_drill_bit`, do not use them as FTB item tasks. Use nearby real player-held items or split the concept into text/structure without an invalid task.

## Claude Collaboration

If the user asks to work with Claude, use Claude for quest design review, pacing, branch naming, and missed-system checks. Codex remains responsible for verification: installed IDs, enabled features, SNBT validity, dependency correctness, graph readability, and exported profile contents.

## Done Criteria

- The quest chapter has named categories and chapters in game-facing text.
- Every item/task/reward ID is verified against the installed pack.
- No task/icon ID appears in the current logs as an invalid item registry key.
- Chapter item namespaces match the intended mod or true addon suite; unrelated compatibility targets are excluded or moved.
- Dependencies match real progression and do not create unnecessary deep cross-links.
- One-off leaves have been audited. Mechanically rich leaves were either expanded into verified mini-paths or intentionally left as endpoints with a clear reason.
- A rendered layout review shows readable clusters with acceptable edge lengths and crossings.
- Logs show no FTB Quests parse or missing-content errors after launch.
- The CurseForge export includes the quest defaults and excludes local/private files.
