#!/usr/bin/env bash
# Run one scenario twice against headless Claude Code — once without the
# directive, once with it — and write the transcripts next to the prompt.
#
#   examples/bin/run.sh examples/01-disabled-alarms [claude-args...]
#
# Both runs are identical except for one thing: the "with" run has the repo's
# rendered CLAUDE.md copied into the working directory. Everything else —
# prompt, fixtures, tools, turn limit, setting sources — is the same.
#
# Outputs, per scenario:
#   without-directive.md   rendered transcript (see bin/render.py)
#   with-directive.md
#   raw/<mode>.jsonl       the stream-json from the tool, for audit (see
#                          bin/keep_events.py for the two event types dropped)
#   raw/<mode>.diff        what the agent changed in the working directory
#
# Requirements: claude (Claude Code CLI), python3, diff. Runs are not cheap in
# tokens; each scenario makes two agent calls.
set -euo pipefail

SCENARIO="${1:?usage: run.sh <scenario-dir> [extra claude args...]}"; shift || true
SCENARIO="$(cd "$SCENARIO" && pwd)"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"
DIRECTIVE_FILE="$REPO_ROOT/CLAUDE.md"

[ -f "$SCENARIO/prompt.md" ] || { echo "no prompt.md in $SCENARIO" >&2; exit 1; }
[ -f "$DIRECTIVE_FILE" ]     || { echo "no $DIRECTIVE_FILE — run scripts/render.sh first" >&2; exit 1; }
command -v claude >/dev/null || { echo "claude CLI not found" >&2; exit 1; }

# Tools the agent may use without prompting. Bash is disallowed outright (not
# just left off the allowlist — read-only shell commands are otherwise
# auto-approved): the fixtures include a deploy script and we never want a
# run to actually execute anything.
ALLOWED_TOOLS="${ALLOWED_TOOLS:-Read,Edit,Write,Glob,Grep}"
MAX_TURNS="${MAX_TURNS:-15}"
CLAUDE_VERSION="$(claude --version 2>/dev/null | head -1)"
RUN_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
mkdir -p "$SCENARIO/raw"

run_mode() { # $1 = with | without
  local mode="$1"
  local work; work="$(mktemp -d "${TMPDIR:-/tmp}/pd-${mode}-XXXXXX")"
  if [ -d "$SCENARIO/fixtures" ]; then cp -R "$SCENARIO/fixtures/." "$work/"; fi
  if [ "$mode" = with ]; then cp "$DIRECTIVE_FILE" "$work/CLAUDE.md"; fi
  # Snapshot so we can diff what the agent changed.
  local before; before="$(mktemp -d)"; cp -R "$work/." "$before/"

  echo ">> $(basename "$SCENARIO") / $mode  (cwd: $work)" >&2
  (
    cd "$work"
    # --setting-sources project: ignore the machine's user-level settings,
    # hooks and ~/.claude/CLAUDE.md so the only instruction file that can
    # differ between the two runs is the one we copied in.
    claude -p "$(cat "$SCENARIO/prompt.md")" \
      --output-format stream-json --verbose \
      --setting-sources project \
      --allowedTools "$ALLOWED_TOOLS" \
      --disallowedTools Bash \
      --max-turns "$MAX_TURNS" \
      "$@"
  ) | python3 "$HERE/keep_events.py" > "$SCENARIO/raw/$mode.jsonl" \
    || echo "   (claude exited non-zero for $mode; transcript kept)" >&2

  # Record what changed on disk, excluding the directive file itself.
  ( cd "$before" && diff -ruN --exclude=CLAUDE.md . "$work" || true ) \
    | sed -e "s#$work#/work#g" -e "s#$before#/work#g" > "$SCENARIO/raw/$mode.diff"

  python3 "$HERE/render.py" \
    --mode "$mode" --tool "$CLAUDE_VERSION" --date "$RUN_DATE" \
    --scenario "$(basename "$SCENARIO")" --cwd "$work" \
    --diff "$SCENARIO/raw/$mode.diff" \
    < "$SCENARIO/raw/$mode.jsonl" > "$SCENARIO/$mode-directive.md"
  rm -rf "$work" "$before"
}

run_mode without "$@"
run_mode with "$@"
echo "done: $SCENARIO" >&2
