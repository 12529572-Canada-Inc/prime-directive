#!/usr/bin/env bash
# The list of places the directive is rendered to. One line per target:
#   scope  path  kind  frontmatter-id  tool
# scope: repo (relative to repo root) | home (relative to $HOME)
# kind:  file   (file is entirely ours, overwritten)
#        block  (file may hold other content; our marked block is upserted)
# Add a line here when a new tool shows up; render.sh, install.sh and doctor.sh all read this list.

pd_targets() {
cat <<'LIST'
repo AGENTS.md                              block none     Codex, Copilot, Gemini (via context.fileName), Aider, Zed, Warp, Junie, Devin, OpenCode, Amp, Jules
repo CLAUDE.md                              block none     Claude Code / Cowork (project)
repo GEMINI.md                              file  none     Gemini CLI (project)
repo .cursor/rules/prime-directive.mdc      file  cursor   Cursor (alwaysApply)
repo .github/copilot-instructions.md        block none     GitHub Copilot
repo .windsurf/rules/prime-directive.md     file  windsurf Windsurf (always_on)
repo .clinerules/prime-directive.md         file  none     Cline / Roo Code
home .codex/AGENTS.md                       block none     Codex (global)
home .claude/CLAUDE.md                      block none     Claude Code / Cowork (global)
home .gemini/GEMINI.md                      block none     Gemini CLI (global)
LIST
}

pd_frontmatter() {
  case "$1" in
    cursor) printf -- '---\ndescription: Prime directive — always-on duty of care toward humanity and all sentient life\nalwaysApply: true\n---' ;;
    windsurf) printf -- '---\ntrigger: always_on\ndescription: Prime directive — always-on duty of care toward humanity and all sentient life\n---' ;;
    *) printf '' ;;
  esac
}

pd_resolve() { # $1 scope, $2 path -> absolute path
  case "$1" in repo) echo "$REPO_ROOT/$2" ;; home) echo "$HOME/$2" ;; esac
}
