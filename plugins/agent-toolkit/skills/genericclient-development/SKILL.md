---
name: genericclient-development
description: "Develop, live-test, or release GenericClient and its Lua automation. Excludes unrelated RuneLite plugins and general OSRS advice."
---

# GenericClient Development

Work in `/home/user/GenericClient`. Treat the source tree, installed artifact,
live client, and current account snapshot as separate states that must be
verified rather than inferred from one another.

## Start from current evidence

1. Inspect `git status --short`, the relevant source modules, and current plan.
   Preserve unrelated dirty changes.
2. For live work, call GenericClient `client_status` first. Call
   `account_snapshot` before planning account mutations. Use
   `client_screenshot` whenever structured state does not fully explain the
   camera, menu, dialogue, widget, or world.
3. For live account work, read the active thread goal and account note. Preserve user-specified stat
   caps, cash reserves, purchasing policy, and mutation boundaries; do not
   invent permanent account rules from an old run.
4. Distinguish a passing unit test, a built JAR, an installed JAR, a loaded
   plugin, and a live in-game receipt. Claim only the layer actually proved.

## Evidence isolation and skill evolution

Use this approved skill for ordinary GenericClient execution. Do not load
`/home/user/.codex/genericclient-evolution/wiki/` into routine coding or live
account turns; historical knowledge must influence execution only after it has
been consolidated, gated, and promoted into this skill.

When the user asks to learn across multiple runs, audit recurring behavior, or
evolve this skill, use `genericclient-skill-evolution`. Preserve exact source
paths, hashes, receipts, and validation layers for that workflow, but do not
turn one incident into a permanent rule or modify this skill automatically
during ordinary development.

## Implementation shape

- Keep GenericClient a framework of semantic client actions and snapshots.
  Quest, skilling, and account-specific decisions belong in standalone Lua
  scripts.
- Organize every substantial standalone script under its own folder. Give each
  quest its own subfolder; place genuinely shared state, preparation, travel,
  and interaction mechanics under `shared/`.
- Keep root Lua descriptors focused on inputs, actions, overlay, and
  orchestration. Split growing scripts into cohesive, junior-readable modules.
  Do not create tiny placeholder modules merely to satisfy a pattern.
- Resolve entities by exact ID and observed postconditions. Do not use fixed
  screen coordinates, stale snapshots, prose-only locations, or sleep-only
  success checks.
- Treat temporary REPL diagnostics as experiments. Once proven, fold the logic
  into the standalone script, add regression coverage, and remove the temporary
  file.

For Lua structure, manifest migrations, and semantic-action conventions, read
[references/lua-architecture.md](references/lua-architecture.md).

## Live work

If quest automation behaves in a novel, visibly wrong, or poorly understood
way, stop the active script safely, inspect current client state and the exact
installed RuneLite Quest Helper guidance, and ask before recovery. Quest Helper
is a development oracle; runtime Lua remains standalone.

Use synthetic client input and GenericClient's Lua/MCP surface. Monitor long
operations through local background jobs and emit state changes rather than
poll noise. Break state is expected; manually end a break when the user has
authorized it and it obstructs an active validation.

Safety must remain independent of script happy paths. Configure approved food
with exact heal amounts, preserve the framework's forced-heal behavior below
30% max HP, and retain an observed escape fallback when the current workflow
requires one. Never interpret a stale/null player frame as account state.

For detailed live paths, interaction rules, logs, screenshots, JIT purchasing,
and account workflow, read
[references/live-client.md](references/live-client.md).

## Verification and publication

Test proportionally while iterating, then run the full Java suite, MCP suite,
and `git diff --check` before packaging. Never overwrite the installed JAR
while RuneLite is running. Verify source and installed SHA-256 values, launch
through the active Jagex Launcher session, and re-check the live endpoint,
account, installed manifest schema, and requested behavior.

Do not push an unfinished live phase. Before commit/push, remove diagnostics,
update authoritative docs/account notes with only verified milestones, inspect
the diff, and confirm the remote branch after pushing.

For exact build, install, launcher, and publication procedure, read
[references/release-workflow.md](references/release-workflow.md).
