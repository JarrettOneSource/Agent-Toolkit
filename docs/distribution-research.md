# Agent Toolkit distribution research

Verified 2026-09-04. Local clients: Codex CLI **0.153.3**, Claude Code **2.1.261**. Read-only client help and exact Codex release source were inspected; no host configuration was changed or plugins installed.

## Recommendation

Ship one conventional skill bundle as both a **native Codex plugin** and a **Claude Code plugin**, with both marketplace manifests in this repository. Use their existing background update mechanisms; a custom updater is unnecessary for the requested ordinary startup-update behavior. Describe this accurately as **checks for updates after startup**, not a promise that the first prompt always sees the newest commit. Keep root `AGENTS.md` available separately, with an optional packaged startup hook if automatic loading of the working instructions is desired.

## Native Codex: automatic Git marketplace updates are real

The exact `rust-v0.153.3` implementation starts `plugins-marketplace-auto-upgrade` for configured Git marketplaces when plugin startup tasks run. It refreshes installed plugin caches after the marketplace snapshot changes, including a forced reinstall from the refreshed snapshot. The operation runs on a background thread, so startup does not wait for it. This is source-verified behavior, not a guarantee stated by the high-level docs. [Plugin startup and refresh implementation](https://github.com/openai/codex/blob/rust-v0.153.3/codex-rs/core-plugins/src/manager.rs#L2735-L2925)

`features.plugins` is stable and enabled by default. App-server startup invokes these tasks when the host enables plugin startup work; a new conversation in a long-lived server is not equivalent to restarting that server. Desktop/IDE clients therefore depend on their bundled backend version and configuration. [Feature default](https://github.com/openai/codex/blob/rust-v0.153.3/codex-rs/features/src/lib.rs#L1322-L1327), [app-server startup call](https://github.com/openai/codex/blob/rust-v0.153.3/codex-rs/app-server/src/message_processor.rs#L525-L544)

For marketplace name `agent-toolkit` and plugin name `agent-toolkit`, the verified CLI syntax is:

```sh
codex plugin marketplace add JarrettOneSource/Agent-Toolkit --ref main
codex plugin add agent-toolkit@agent-toolkit
```

An explicit refresh is `codex plugin marketplace upgrade agent-toolkit`. `--ref main` tracks that branch; pinning a full commit freezes the source. A local-directory marketplace does not receive Git updates. These commands were verified with local `--help`; the command reference documents GitHub shorthand, Git refs, and sparse checkouts. [Codex developer commands](https://learn.chatgpt.com/docs/developer-commands#codex-plugin-marketplace)

Updates resolve the remote revision, clone into staging, validate the marketplace, then replace Codex's managed snapshot. Git subprocesses have 30-second timeouts. Failed fetches do not replace the existing snapshot. **Managed marketplace/cache directories are disposable, not editable working checkouts:** there is no dirty-worktree preservation check before successful snapshot replacement. [Marketplace refresh](https://github.com/openai/codex/blob/rust-v0.153.3/codex-rs/core-plugins/src/marketplace_upgrade.rs#L223-L301), [snapshot activation](https://github.com/openai/codex/blob/rust-v0.153.3/codex-rs/core-plugins/src/marketplace_upgrade/activation.rs#L88-L172)

## Layout and skill names

```text
AGENTS.md
.agents/plugins/marketplace.json
.claude-plugin/marketplace.json
plugins/agent-toolkit/
  .codex-plugin/plugin.json
  .claude-plugin/plugin.json
  skills/<skill-name>/SKILL.md
  hooks/hooks.json                 # optional
  scripts/session-start.*          # optional
```

The Codex marketplace entry can use:

```json
{"name":"agent-toolkit","source":{"source":"local","path":"./plugins/agent-toolkit"}}
```

The Claude entry uses `"source": "./plugins/agent-toolkit"`. These paths are relative to the **repository/marketplace root**, not to the directory containing `marketplace.json`. Codex's manifest uses `"skills": "./skills/"`; Claude discovers the standard `skills/` directory. Keep every skill's referenced scripts, templates, and documents within the plugin root. [OpenAI marketplace formats](https://learn.chatgpt.com/docs/enterprise/plugin-management#supported-formats), [OpenAI plugin layout](https://learn.chatgpt.com/docs/build-plugins#create-a-skills-only-plugin-manually), [Claude plugin layout](https://code.claude.com/docs/en/plugins-reference)

Bundled skills are namespaced. A skill named `recursive-planning` in plugin `agent-toolkit` becomes `$agent-toolkit:recursive-planning` in Codex and `/agent-toolkit:recursive-planning` in Claude. Explain that bare `$skill-name` references in shared prose are logical names resolved through the installed catalog; remove hard-coded `/home/user/.codex/skills/...` paths. [Codex namespace implementation](https://github.com/openai/codex/blob/rust-v0.153.3/codex-rs/ext/skills/src/loader/namespace.rs#L11-L18), [Claude namespaced invocation](https://code.claude.com/docs/en/discover-plugins#install-plugins)

## Claude Code: enable third-party auto-update explicitly

```sh
claude plugin marketplace add JarrettOneSource/Agent-Toolkit
claude plugin install agent-toolkit@agent-toolkit
```

Third-party marketplaces default to automatic updates **off**. Users can enable them in `/plugin` → Marketplaces → agent-toolkit → Enable auto-update, or merge this entry into their existing `~/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "agent-toolkit": {
      "source": {"source": "github", "repo": "JarrettOneSource/Agent-Toolkit"},
      "autoUpdate": true
    }
  }
}
```

The current settings reference explicitly supports `autoUpdate` beside `source`; do not replace the user's whole settings file. [Claude marketplace settings](https://code.claude.com/docs/en/settings-reference#extraknownmarketplaces)

Current Claude docs specify a random delay of up to **ten minutes after startup**. Downloads update files on disk; the active session retains its loaded version until `/reload-plugins` or the next launch. `DISABLE_AUTOUPDATER` disables marketplace auto-updates unless paired with the documented plugin-only override. [Claude update lifecycle](https://code.claude.com/docs/en/discover-plugins#configure-auto-updates)

Use consistent release versions and bump them whenever publishing skill changes: an unchanged explicit version makes Claude skip the update. Alternatively, omitting `version` from both Claude's plugin manifest and its marketplace entry makes Git-backed relative-path plugins use the source commit as the version. Choose one documented release policy. [Claude version resolution](https://code.claude.com/docs/en/plugins-reference#version-management)

## AGENTS.md is a separate loading concern

Codex discovers instructions from its home directory and the active project's directory chain once per run. Merely placing `AGENTS.md` inside a plugin does not make it global project guidance. A standalone copy in the user's Codex home is straightforward but will not follow plugin updates automatically. Avoid overwriting an existing user file. [Codex AGENTS discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md#how-codex-discovers-guidance)

An optional synchronous `SessionStart` command can print the packaged guidance; both clients add that output to model context. Codex supplies `PLUGIN_ROOT` and `CLAUDE_PLUGIN_ROOT`, so the hook can resolve installed files without machine-specific paths. **Codex requires users to review and trust non-managed hooks in `/hooks` before execution; plugin installation does not grant that trust.** Changed definitions need review again. A hook should load local guidance, not run a second updater. [Codex hooks](https://learn.chatgpt.com/docs/hooks#plugin-bundled-hooks), [Claude hook output](https://code.claude.com/docs/en/hooks#exit-code-0)

If using a hook, keep the bundled instructions synchronized with root `AGENTS.md` through the release/build check. Do not symlink outside the plugin package. Account for hook output limits: Codex supports `additionalContextLimit`; Claude turns output above 10,000 characters into a preview plus saved file path. For a large guide, emit an instruction to read its absolute installed path instead of claiming the entire guide was injected. [Codex hook configuration](https://learn.chatgpt.com/docs/hooks#config-shape), [Claude context output](https://code.claude.com/docs/en/hooks#json-output)

## Community approaches and optional utilities

Vercel's `skills` CLI offers multi-agent installs, a canonical copy with symlinks, and an explicit `skills update` command. It does not document automatic client-launch updates. The inspected package is 1.5.23 and requires Node >=22.20.0, adding a dependency that native plugin installation avoids. [Vercel skills](https://github.com/vercel-labs/skills), [package requirements](https://github.com/vercel-labs/skills/blob/main/package.json)

Superpowers now distributes Codex support through the native plugin marketplace. Its former `.codex/INSTALL.md` path is absent from current upstream; old clone-and-symlink tutorials no longer describe its preferred Codex install. [Current Superpowers instructions](https://github.com/obra/superpowers#codex-cli), [current source tree](https://github.com/obra/superpowers/tree/b36e0829c6d0140e93cfef2ca599b1b07d4a7797)

Standalone local skills remain useful for other agents: Codex supports `~/.agents/skills` and symlinked folders, and local skills are available in CLI, desktop, and IDE. A pre-launch fast-forward-only updater would be needed only for strict fresh-before-first-prompt semantics outside native plugins. If implemented later, it should preserve dirty checkouts and permit offline launch using existing content. [Codex local discovery](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)

Keep Local Tools and the tmux watcher optional, with separate install instructions or plugin entries. A skills-only installation should not start utility processes or enable their MCP servers. This is the requested packaging boundary, not an upstream requirement.

## Attribution

The exact Matt Pocock source revision `ed37663cc5fbef691ddfecd080dff42f7e7e350d` carries the **MIT License**, copyright **2026 Matt Pocock**. Preserve the full upstream license and credit the source revision in a third-party notice. Record local adaptations without implying that all custom toolkit skills are authored by Matt. [Exact upstream license](https://raw.githubusercontent.com/mattpocock/skills/ed37663cc5fbef691ddfecd080dff42f7e7e350d/LICENSE)

Research limits: native startup behavior was verified in exact Codex release source and current primary documentation; no desktop/IDE launch or live remote plugin update was exercised. Recheck client behavior when the supported baseline changes.

## Local Tools MCP packaging follow-up

Use client-specific MCP entries in the two plugin manifests, pointing to one shared Python implementation:

- Codex's manifest declares its MCP entry inline. Its command is `python3`, arguments are `scripts/run.py`, and `cwd` is `.`. Codex resolves relative `cwd` against the installed plugin directory. Its native parser does not expand Claude's plugin-root placeholder in command arguments. This distinction was confirmed by a failing native startup followed by successful startup with a plugin-relative working directory. [Native normalization implementation](https://github.com/openai/codex/blob/rust-v0.153.3/codex-rs/codex-mcp/src/plugin_config.rs#L236-L291)
- Claude's manifest declares its MCP entry inline. Its arguments use `${CLAUDE_PLUGIN_ROOT}/scripts/run.py`, the client's documented installed-plugin path. [Claude plugin environment variables](https://code.claude.com/docs/en/plugins-reference#environment-variables)

Codex's `startup_timeout_sec: 30`, `tool_timeout_sec: 604800`, and `omit_tools_from: ["code_mode", "deferred"]` are regular native MCP configuration. The omission list keeps long-running tools directly callable, including in code-mode-only sessions, without a global namespace override. The default tool namespace is `mcp__local_tools`. [Configuration parser](https://github.com/openai/codex/blob/rust-v0.153.3/codex-rs/codex-mcp/src/plugin_config.rs#L125-L161), [exposure mapping](https://github.com/openai/codex/blob/rust-v0.153.3/codex-rs/core/src/tools/spec_plan.rs#L197-L266), [upstream integration coverage](https://github.com/openai/codex/blob/rust-v0.153.3/codex-rs/core/tests/suite/code_mode.rs#L854-L1048)

Claude uses a per-server `timeout` in milliseconds: `604800000` is one week and raises the idle-timeout floor for intentionally silent waits. A variable placed inside the MCP child's environment would not configure the parent client's tool timeout. [Claude MCP timeout behavior](https://code.claude.com/docs/en/mcp)

The separate client configurations avoid relying on unknown-key tolerance or a placeholder expansion that one client does not implement. `tests/test_codex_plugin.py` verifies actual installed-plugin startup, rather than only validating manifest syntax. It runs in isolated client state and creates no model turn.
