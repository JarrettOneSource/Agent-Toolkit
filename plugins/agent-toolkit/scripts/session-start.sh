#!/bin/sh
set -eu

plugin_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
printf 'Agent Toolkit is installed. Read and apply the working instructions in "%s/AGENTS.md" before working. Resolve the skill names in that file through the installed agent-toolkit plugin catalog.\n' "$plugin_root"
