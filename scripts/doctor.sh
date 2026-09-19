#!/usr/bin/env bash
# Report whether the prime directive is present and current in every known location
# (repo files and this machine's global agent config). Exit 1 if anything is missing or stale.
set -uo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
. "$(dirname "${BASH_SOURCE[0]}")/targets.sh"

want="$(pd_hash)"
echo "source: $SOURCE_REL (sha:$want)"
echo
bad=0
pd_targets | while read -r scope path kind fm tool; do
  abs="$(pd_resolve "$scope" "$path")"
  st="$(pd_status "$abs")"
  case "$scope" in repo) shown="$path" ;; home) shown="~/$path" ;; esac
  case "$st" in
    current)  mark="ok      " ;;
    stale)    mark="STALE   " ;;
    unmarked) mark="UNMARKED" ;;
    missing)  mark="MISSING " ;;
  esac
  printf '%s  %-40s %s\n' "$mark" "$shown" "$tool"
  [ "$st" = current ] || echo "$st" >> "${TMPDIR:-/tmp}/pd-doctor.$$"
done
if [ -s "${TMPDIR:-/tmp}/pd-doctor.$$" ]; then bad=1; fi
rm -f "${TMPDIR:-/tmp}/pd-doctor.$$"
echo
if [ "$bad" = 0 ]; then
  echo "All known locations carry the current directive."
else
  echo "Fix: run scripts/render.sh for repo files, ./install.sh for global files."
  echo "UNMARKED = mentions the directive but was not generated from the source (hand-edited or older install)."
fi
exit "$bad"
