# Agent Toolkit

Working instructions, engineering skills, and optional local utilities for coding agents. The toolkit favors clear code, proactive cleanup, root-cause fixes, and complete implementations.

The main plugin includes [AGENTS.md](AGENTS.md), three custom skills, and 18 involved skills from Matt Pocock's collection, with their supporting files and licenses.

[Ponytail core](plugins/ponytail/README.md) is a separate, instruction-only plugin for choosing the smallest complete solution. It retains the upstream decision ladder without the modes, hooks, scoreboards, status line, or extra commands.

## Codex

With Codex CLI 0.153.3 or later:

```sh
codex plugin marketplace add JarrettOneSource/Agent-Toolkit --ref main
codex plugin add agent-toolkit@agent-toolkit
```

Restart Codex. Open `/hooks` and review/trust the toolkit's startup hook to have it direct the agent to the bundled working instructions. The hook reads local guidance; it starts no utility processes and makes no network requests.

The startup hook requires `sh`, available on Linux, macOS, WSL, or Git Bash. Without it, the skills remain usable and you can load the bundled guide manually.

Invoke a skill as `$agent-toolkit:recursive-planning` or `$agent-toolkit:ai-desloppification`. The bare names in the guide refer to the matching installed plugin skills.

Codex 0.153.3 refreshes Git-backed marketplaces in the background at startup, following this repository's `main` branch. A running session can retain its earlier inventory; restart after a refresh when you need the new version. See the [verified startup implementation](https://github.com/openai/codex/blob/rust-v0.153.3/codex-rs/core-plugins/src/manager.rs#L2735-L2925).

To request a refresh explicitly:

```sh
codex plugin marketplace upgrade agent-toolkit
```

## Claude Code

```sh
claude plugin marketplace add JarrettOneSource/Agent-Toolkit
claude plugin install agent-toolkit@agent-toolkit
```

Open `/plugin` and select **Marketplaces → agent-toolkit → Enable auto-update**. Third-party marketplaces need this opt-in. Claude can delay its background check by up to ten minutes after startup; updated plugins load on the next launch or `/reload-plugins`. See [Claude's update documentation](https://code.claude.com/docs/en/discover-plugins#configure-auto-updates).

Invoke a skill as `/agent-toolkit:recursive-planning`. The startup hook directs Claude to the same bundled instructions.

## Optional plugins and utilities

| Utility | Purpose | Installation |
| --- | --- | --- |
| [Ponytail core](plugins/ponytail/README.md) | Reuse-first coding guidance with no added runtime or hooks | Install `ponytail@agent-toolkit`. |
| [Local Tools](plugins/local-tools/README.md) | Local shell jobs, logs, an instruction dashboard, and Codex completion callbacks | Install `local-tools@agent-toolkit`. Requires Python 3.11+ and a POSIX host. |
| [tmux waiting-menu watcher](utilities/tmux-keep-waiting/README.md) | Select **Keep waiting** in recognized Codex waiting menus | Run or install the standalone script. Requires Bash 4+ and tmux. |

Installing the main plugin activates neither utility.

## Other agents and standalone instructions

The directories under `plugins/agent-toolkit/skills/` use the standard `SKILL.md` layout. Copy or symlink them into another client's documented skill directory and integrate [AGENTS.md](AGENTS.md) with its working instructions. Preserve existing personal instructions.

Manual copies and local-directory marketplace installs do not receive Git updates automatically. Use the native Git marketplace installs above for startup updates. Codex also supports [local skill folders and symlinks](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills).

## Maintenance

To uninstall a plugin, run `codex plugin remove agent-toolkit@agent-toolkit` or `claude plugin uninstall agent-toolkit@agent-toolkit`. Use `local-tools@agent-toolkit` for the optional server or `ponytail@agent-toolkit` for Ponytail. Stop the watcher using its documented service command when installed.

If you added Ponytail activation to a global `AGENTS.md`, remove that section when uninstalling it.

Edit a working checkout. Client-managed marketplace snapshots and plugin caches can be replaced during updates.

After changing guidance or skills, bump `VERSION` and run:

```sh
python3 scripts/sync_package.py
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
sh scripts/validate.sh
```

The sync command updates both clients' manifest versions and the packaged copy of the root guide. Bump the version for every release: Claude can skip updates whose explicit version did not change. [Version-management reference](https://code.claude.com/docs/en/plugins-reference#version-management).

See [distribution research](docs/distribution-research.md) for the source comparison and client limitations, and [validation results](docs/validation.md) for measured checks and remaining gaps.

## License and sources

MIT. Matt Pocock's skills retain their [upstream MIT license](plugins/agent-toolkit/licenses/Matt-Pocock-MIT.txt), and Ponytail retains [DietrichGebert's MIT license](plugins/ponytail/LICENSE). [Third-party notices](THIRD_PARTY_NOTICES.md) and [source inventory](SOURCES.json) identify imported material and local adaptations.
