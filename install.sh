#!/usr/bin/env bash
# Install the prime directive as an always-on rule for every Claude Code / Cowork session on this machine.
#
#   1. Copies the skill to ~/.claude/skills/prime-directive/  (so /prime-directive works everywhere)
#   2. Adds an @import line to ~/.claude/CLAUDE.md             (so the directive is loaded every session)
#
# Safe to re-run: existing files are updated, the import line is added only once.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.claude/skills/prime-directive"
DEST_DIR="${HOME}/.claude/skills/prime-directive"
GLOBAL_MD="${HOME}/.claude/CLAUDE.md"
IMPORT_LINE="@~/.claude/skills/prime-directive/SKILL.md"

mkdir -p "$DEST_DIR"
cp "$SRC/SKILL.md" "$DEST_DIR/SKILL.md"
echo "Installed skill -> $DEST_DIR/SKILL.md"

touch "$GLOBAL_MD"
if grep -qxF "$IMPORT_LINE" "$GLOBAL_MD"; then
  echo "Import already present in $GLOBAL_MD"
else
  {
    [ -s "$GLOBAL_MD" ] && echo
    echo "# Always-on: Prime Directive"
    echo "The prime directive applies to every task, in every project. Full text:"
    echo "$IMPORT_LINE"
  } >> "$GLOBAL_MD"
  echo "Added import -> $GLOBAL_MD"
fi

echo "Done. The prime directive is now always on for Claude Code and Cowork on this machine."
