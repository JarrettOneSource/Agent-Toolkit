# Source notices

## Matt Pocock's skills

The skills identified in [SOURCES.json](SOURCES.json) are derived from [mattpocock/skills](https://github.com/mattpocock/skills), revision `ed37663cc5fbef691ddfecd080dff42f7e7e350d`. Copyright 2026 Matt Pocock. The full MIT license is preserved in [the plugin package](plugins/agent-toolkit/licenses/Matt-Pocock-MIT.txt).

The toolkit includes adapted definitions and supporting files. Codex display metadata and toolkit working instructions are local additions. The TDD, diagnosis, and ticket-implementation guidance is adapted to use established interfaces without routine approval prompts and to keep investigation and verification proportional to the task. Invocation policies are retained per skill. The `qa` skill comes from the upstream deprecated directory and is included because the installed tracker-setup guidance refers to it.

`recursive-planning`, `ai-desloppification`, and `implement-full-send` are custom toolkit skills. They are not attributed to Matt Pocock.

## Optional utilities

Local Tools was imported from `JarrettOneSource/local-tools-mcp`. The tmux watcher was imported from `Pernasua/tmux-keep-waiting`. Original commit IDs are recorded in [SOURCES.json](SOURCES.json).

This distribution adds portable packaging, separates Local Tools' responsibilities into cohesive modules, removes installation-specific documentation and timezone assumptions, and makes the watcher discover its executable and sockets from the current environment. These adaptations are maintained in this repository.
