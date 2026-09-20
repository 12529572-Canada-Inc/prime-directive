#!/usr/bin/env bash
# Run one scenario twice against headless Codex CLI — once without the
# directive, once with it — and write the transcripts next to the prompt.
# The Codex counterpart of run.sh; same rules, same layout, one tool swapped.
#
#   MODELS="gpt-6-astra gpt-5.6-terra" examples/bin/run-codex.sh examples/02-omitted-bug [codex-args...]
#
# Both runs are identical except for one thing: the "with" run has the repo's
# rendered AGENTS.md copied into the working directory. Everything else —
# prompt, fixtures, sandbox, approval policy, config — is the same.
#
# Outputs, per scenario and model, under <scenario>/codex-<model>/:
#   without-directive.md   rendered transcript (see bin/render-codex.py)
#   with-directive.md
#   raw/<mode>.jsonl       the JSONL from `codex exec --json`, unfiltered
#   raw/<mode>.diff        what the agent changed in the working directory
#
# Isolation, so the instruction file is the only thing that differs:
#   * CODEX_HOME points at a throwaway directory holding only a copy of your
#     auth.json — no ~/.codex/AGENTS.md, no config.toml, no hooks or .rules
#     (Codex reads a global AGENTS.md from CODEX_HOME; --ignore-user-config
#     alone would not keep it out).
#   * The working directory is `git init`-ed so Codex's project-scope
#     discovery starts and ends there; nothing above it is read.
#   * skills.include_instructions=false: Codex also loads *skills* from
#     ~/.agents/skills (a cross-agent directory outside CODEX_HOME, with no
#     way to exclude just that root) and from its own bundled set, and lists
#     them in the model prompt. Any skill on the machine is an instruction
#     source that is not the directive, so none are loaded in either run.
#   * Preflight: before each run, `codex debug prompt-input` renders exactly
#     what the model will see from this working directory with these flags;
#     the script refuses to run if that prompt carries anything from the
#     machine, so a leak fails loudly instead of quietly contaminating both
#     transcripts. The same check confirms AGENTS.md really is in the "with"
#     prompt and really is not in the "without" one — the flags are what we
#     believe, the rendered prompt is what the model gets.
#   * --sandbox workspace-write, approval_policy=never: the agent can write
#     files and run commands inside the temp directory, with no network and
#     no prompts. Unlike run.sh (which disallows Bash outright) Codex has no
#     per-tool allowlist, so a fixture such as deploy.sh *could* be executed
#     — inside the sandbox, against a throwaway copy. The transcript shows
#     every command it ran.
#   * --ephemeral: no session rollout is written to disk.
#
# MODELS must be set explicitly: Codex's JSONL does not report which model
# ran, and a transcript has to say what actually ran, so the value passed to
# `-m` is what goes in the header.
#
# Requirements: codex (Codex CLI, signed in: `codex login`), python3, diff, git.
set -euo pipefail

SCENARIO="${1:?usage: MODELS=<model> run-codex.sh <scenario-dir> [extra codex args...]}"; shift || true
SCENARIO="$(cd "$SCENARIO" && pwd)"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"
DIRECTIVE_FILE="$REPO_ROOT/AGENTS.md"
REAL_CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"

[ -f "$SCENARIO/prompt.md" ] || { echo "no prompt.md in $SCENARIO" >&2; exit 1; }
[ -f "$DIRECTIVE_FILE" ]     || { echo "no $DIRECTIVE_FILE — run scripts/render.sh first" >&2; exit 1; }
command -v codex >/dev/null  || { echo "codex CLI not found" >&2; exit 1; }
[ -n "${MODELS:-}" ] || { echo "set MODELS to the model(s) to run, e.g. MODELS=\"gpt-6-astra gpt-5.6-terra\" — Codex does not report the model in its output, so it has to be named up front" >&2; exit 1; }
if [ ! -f "$REAL_CODEX_HOME/auth.json" ] && [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "no $REAL_CODEX_HOME/auth.json and no OPENAI_API_KEY — run \`codex login\` first" >&2; exit 1
fi

CODEX_VERSION="$(codex --version 2>/dev/null | head -1)"
# Config overrides shared by the preflight and the run. Keep them in one place
# so what the preflight checks is what the run uses.
CODEX_CONFIG=(-c skills.include_instructions=false -c approval_policy=never)

# Fail if the instruction file would not be the only difference between the
# two runs. See bin/preflight-codex.py — it reads the prompt Codex is about to
# send and checks both directions: nothing from the machine leaks in, and the
# directive is present in the "with" run and absent from the "without" run.
# $1 = work dir, $2 = throwaway CODEX_HOME, $3 = with | without
# `debug prompt-input` takes no --ignore-user-config / --ignore-rules (only -c
# overrides), so it is given CODEX_CONFIG alone. Those two flags can only
# remove instruction sources, so the preflight sees at least as much as the
# run does — it can warn about something the run would not load, never miss
# something the run would.
preflight() {
  local work="$1" home="$2" mode="$3"
  (cd "$work" && CODEX_HOME="$home" codex debug prompt-input "${CODEX_CONFIG[@]}" "preflight" 2>/dev/null) \
    | python3 "$HERE/preflight-codex.py" --mode "$mode" --work "$work" \
        --home "$HOME" --codex-home "$REAL_CODEX_HOME" --directive "$DIRECTIVE_FILE"
}

run_mode() { # $1 = model, $2 = with | without, rest = extra codex args
  local model="$1" mode="$2"; shift 2
  local outdir="$SCENARIO/codex-$model"
  local work; work="$(mktemp -d "${TMPDIR:-/tmp}/pd-codex-${mode}-XXXXXX")"
  if [ -d "$SCENARIO/fixtures" ]; then cp -R "$SCENARIO/fixtures/." "$work/"; fi
  if [ "$mode" = with ]; then cp "$DIRECTIVE_FILE" "$work/AGENTS.md"; fi
  # A repo root, so project-doc discovery is scoped to this directory.
  ( cd "$work" && git init -q && git -c user.name=pd -c user.email=pd@example.invalid add -A \
      && git -c user.name=pd -c user.email=pd@example.invalid commit -q -m fixtures --allow-empty )
  # Snapshot so we can diff what the agent changed.
  local before; before="$(mktemp -d)"; cp -R "$work/." "$before/"
  # Throwaway CODEX_HOME: credentials only.
  local home; home="$(mktemp -d "${TMPDIR:-/tmp}/pd-codex-home-XXXXXX")"
  [ -f "$REAL_CODEX_HOME/auth.json" ] && cp "$REAL_CODEX_HOME/auth.json" "$home/auth.json"

  local jsonl; jsonl="$(mktemp)"; local diff; diff="$(mktemp)"
  echo ">> $(basename "$SCENARIO") / codex-$model / $mode  (cwd: $work)" >&2
  preflight "$work" "$home" "$mode" || { rm -rf "$work" "$before" "$home"; return 1; }
  (
    cd "$work"
    CODEX_HOME="$home" codex exec \
      --json --ephemeral --color never \
      --ignore-user-config --ignore-rules --skip-git-repo-check \
      --sandbox workspace-write "${CODEX_CONFIG[@]}" \
      -m "$model" \
      "$@" \
      "$(cat "$SCENARIO/prompt.md")"
  ) | python3 "$HERE/render-codex.py" --progress > "$jsonl" \
    || echo "   (codex exited non-zero for $mode; transcript kept)" >&2

  # Record what changed on disk, excluding the directive file and git metadata.
  ( cd "$before" && diff -ruN --exclude=AGENTS.md --exclude=.git . "$work" || true ) \
    | sed -e "s#$work#/work#g" -e "s#$before#/work#g" > "$diff"

  rm -rf "$work" "$before" "$home"

  if python3 "$HERE/render-codex.py" --failed < "$jsonl"; then
    echo "   $mode run produced no answer (auth? model access?); existing transcripts left untouched" >&2
    echo "   raw output kept at $jsonl" >&2
    return 1
  fi
  mkdir -p "$outdir/raw"
  mv "$jsonl" "$outdir/raw/$mode.jsonl"
  mv "$diff"  "$outdir/raw/$mode.diff"
  python3 "$HERE/render-codex.py" \
    --mode "$mode" --tool "$CODEX_VERSION" --model "$model" --date "$RUN_DATE" \
    --scenario "$(basename "$SCENARIO")" --cwd "$work" \
    --diff "$outdir/raw/$mode.diff" \
    < "$outdir/raw/$mode.jsonl" > "$outdir/$mode-directive.md"
}

for model in $MODELS; do
  run_mode "$model" without "$@"
  run_mode "$model" with "$@"
  echo "done: $SCENARIO / codex-$model" >&2
done
