#!/usr/bin/env bash
# Render the prime directive from its single source (.claude/skills/prime-directive/SKILL.md)
# into every per-tool instruction file in this repo. Safe to re-run; commit the results.
set -euo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
. "$(dirname "${BASH_SOURCE[0]}")/targets.sh"

pd_targets | while read -r scope path kind fm _tool; do
  [ "$scope" = repo ] || continue
  abs="$(pd_resolve "$scope" "$path")"
  case "$kind" in
    file)  pd_write_file "$abs" "$(pd_frontmatter "$fm")" ;;
    block) pd_upsert_block "$abs" ;;
  esac
  echo "rendered  $path"
done
echo "source hash: $(pd_hash)"
