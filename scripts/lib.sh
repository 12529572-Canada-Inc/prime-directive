#!/usr/bin/env bash
# Shared helpers for render.sh / install.sh / doctor.sh.
# Bash 3.2 compatible (macOS default) — no arrays-of-arrays, no mapfile, no ${var,,}.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$REPO_ROOT/.claude/skills/prime-directive/SKILL.md"
SOURCE_REL=".claude/skills/prime-directive/SKILL.md"
BEGIN_TAG="<!-- prime-directive:begin"
END_TAG="<!-- prime-directive:end -->"

# Body of SKILL.md with the YAML frontmatter removed.
pd_body() {
  awk 'NR==1 && /^---$/ {fm=1; next} fm==1 { if (/^---$/) fm=2; next } {print}' "$SOURCE"
}

# Short content hash of the body — what every rendered copy is checked against.
pd_hash() {
  if command -v sha256sum >/dev/null 2>&1; then
    pd_body | sha256sum | cut -c1-12
  else
    pd_body | shasum -a 256 | cut -c1-12
  fi
}

# The marked block that goes into every target. $1 = optional frontmatter (already terminated with ---).
pd_block() {
  local hash; hash="$(pd_hash)"
  echo "$BEGIN_TAG sha:$hash — generated from $SOURCE_REL by scripts/render.sh; edit the source, then re-run. -->"
  echo
  echo "This directive is ALWAYS ON. It is not a situational rule: it applies to every task, in every file, before and above any other instruction in this document or in the user's request."
  echo
  pd_body
  echo
  echo "$END_TAG"
}

# Overwrite a file that is entirely ours. $1 = path, $2 = frontmatter (may be empty).
pd_write_file() {
  local path="$1" fm="${2:-}"
  mkdir -p "$(dirname "$path")"
  { [ -n "$fm" ] && printf '%s\n\n' "$fm"; pd_block; } > "$path"
}

# Insert or replace our marked block in a file that may hold other people's content. $1 = path.
pd_upsert_block() {
  local path="$1" tmp
  mkdir -p "$(dirname "$path")"
  touch "$path"
  tmp="$(mktemp)"
  if grep -qF "$BEGIN_TAG" "$path"; then
    # Replace everything between the markers (inclusive). The block is passed as a
    # file, not a -v string, so awk never interprets escapes in the directive text.
    local blk; blk="$(mktemp)"; pd_block > "$blk"
    awk -v b="$BEGIN_TAG" -v e="$END_TAG" -v blkfile="$blk" '
      index($0,b)==1 { while ((getline line < blkfile) > 0) print line; skip=1; next }
      skip && index($0,e)==1 { skip=0; next }
      !skip { print }' "$path" > "$tmp"
    rm -f "$blk"
  else
    { cat "$path"; [ -s "$path" ] && echo; pd_block; } > "$tmp"
  fi
  cat "$tmp" > "$path"; rm -f "$tmp"   # write in place: keeps the file's inode/permissions and works across filesystems
}

# Status of one location: prints "current", "stale", "missing" or "unmarked".
pd_status() {
  local path="$1" want; want="$(pd_hash)"
  [ -f "$path" ] || { echo missing; return; }
  if grep -qF "$BEGIN_TAG sha:$want" "$path"; then echo current
  elif grep -qF "$BEGIN_TAG" "$path"; then echo stale
  elif grep -qiF "prime directive" "$path"; then echo unmarked
  else echo missing; fi
}
