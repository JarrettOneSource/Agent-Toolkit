#!/usr/bin/env bash
# Install the forward-implementation-first skill for every agent found on this
# machine. Re-running overwrites the installed copy.
set -euo pipefail

SKILL="forward-implementation-first"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -f "$SRC/SKILL.md" ]; then
  echo "error: SKILL.md not found next to install.sh" >&2
  exit 1
fi

# Agent skill roots. ~/.agents is the shared convention; the others are
# per-agent. Only roots whose parent directory already exists are used, so this
# does not create config for an agent you have not installed.
ROOTS=(
  "$HOME/.claude/skills"
  "$HOME/.codex/skills"
  "$HOME/.agents/skills"
)

installed=0
for root in "${ROOTS[@]}"; do
  parent="$(dirname "$root")"
  [ -d "$parent" ] || continue
  dest="$root/$SKILL"
  mkdir -p "$dest/examples"
  cp "$SRC/SKILL.md" "$dest/SKILL.md"
  cp "$SRC"/examples/*.md "$dest/examples/"
  echo "installed: $dest"
  installed=$((installed + 1))
done

if [ "$installed" -eq 0 ]; then
  echo "No agent directory found. Copy SKILL.md to your agent's skills path by hand." >&2
  exit 1
fi

echo
echo "Restart your agent. Running sessions do not reload skills."
