# Source notices

## Matt Pocock's skills

The skills identified in [SOURCES.json](SOURCES.json) are derived from [mattpocock/skills](https://github.com/mattpocock/skills), revision `3cca18b368ae95cdbdebbff572ccafa662551015`. Retained legacy skills come from revision `ed37663cc5fbef691ddfecd080dff42f7e7e350d`. Copyright 2026 Matt Pocock. The full MIT license is preserved in [the plugin package](plugins/agent-toolkit/licenses/Matt-Pocock-MIT.txt).

The toolkit includes adapted definitions and supporting files. Codex display metadata and toolkit working instructions are local additions. The TDD, diagnosis, and ticket-implementation guidance is adapted to use established interfaces without routine approval prompts and to keep investigation and verification proportional to the task. Invocation policies are retained per skill. The `qa` skill comes from the upstream deprecated directory and is included because the installed tracker-setup guidance refers to it.

The `custom_skills` inventory identifies locally maintained workflows, including `recursive-planning`, `ai-desloppification`, and `implement-full-send`. These definitions and local adaptations were imported from the installed skill collection. Personal contact values and machine-specific skill installation paths are omitted from the public package.

## Forward Implementation First

`forward-implementation-first` is adapted from [Vuk97/forward-implementation-first](https://github.com/Vuk97/forward-implementation-first), revision `2d4dd7eacb4c41a31d85501f6f44d33fef21017a`. Copyright 2026 Vuk97. Its [MIT license](plugins/agent-toolkit/skills/forward-implementation-first/LICENSE) and supporting examples are included. The installed task-scope safeguards and optional execution-profile guidance are retained.

## Optional utilities

Local Tools was imported from `JarrettOneSource/local-tools-mcp`. The tmux watcher was imported from `Pernasua/tmux-keep-waiting`. Original commit IDs are recorded in [SOURCES.json](SOURCES.json).

This distribution adds portable packaging, separates Local Tools' responsibilities into cohesive modules, removes installation-specific documentation and timezone assumptions, and makes the watcher discover its executable and sockets from the current environment. These adaptations are maintained in this repository.
