#!/usr/bin/env bash
# Install the prime directive as an always-on rule for every agent on this machine
# that reads a global instruction file:
#
#   ~/.claude/skills/prime-directive/SKILL.md   so /prime-directive works in any Claude Code / Cowork project
#   ~/.claude/CLAUDE.md                          Claude Code / Cowork
#   ~/.codex/AGENTS.md                           Codex CLI
#   ~/.gemini/GEMINI.md                          Gemini CLI
#
# The full directive text is written into each file inside a marked block, so it works
# for tools with no @import syntax. Safe to re-run: blocks are replaced in place, never duplicated.
set -euo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/scripts/lib.sh"
. "$(dirname "${BASH_SOURCE[0]}")/scripts/targets.sh"

DEST_DIR="${HOME}/.claude/skills/prime-directive"
mkdir -p "$DEST_DIR"
cp "$SOURCE" "$DEST_DIR/SKILL.md"
echo "installed  ~/.claude/skills/prime-directive/SKILL.md"

pd_targets | while read -r scope path kind fm _tool; do
  [ "$scope" = home ] || continue
  pd_upsert_block "$(pd_resolve "$scope" "$path")"
  echo "installed  ~/$path"
done

echo
echo "Done. Run scripts/doctor.sh to verify. Per-project files are rendered with scripts/render.sh."
