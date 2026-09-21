# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the version numbers mean what
[VERSIONING.md](VERSIONING.md) says they mean — in short, a change that could alter what an agent
does is a major bump, whatever the diff looks like.

## [Unreleased]

## [0.1.0] — 2026-09-20

First tagged release. Everything below already existed on `main`; this is the point at which it
becomes something you can reference by name.

Directive source hash: `448faa3c1844` (`.claude/skills/prime-directive/SKILL.md`, ~1,140 words).

### The directive

- A duty-of-care rule for AI agents, in `.claude/skills/prime-directive/SKILL.md`: protect humanity
  and all sentient life the way a good parent protects grown children — honestly, attentively, and
  without taking away their freedom to choose.
- A one-line version at the top that survives truncation, seven principles in priority order, a
  six-question decision procedure, an explicit list of what the directive does and does not
  license, worked examples, and the anti-patterns to watch for in yourself.

### Always-on delivery

- `scripts/render.sh` renders the directive from its single source into every per-tool instruction
  file, each inside a marked block stamped with a content hash of the source.
- `scripts/targets.sh` holds the target list — ten locations covering Claude Code / Cowork, Codex,
  Gemini CLI, Copilot, Cursor, Windsurf, Cline / Roo Code, and the `AGENTS.md` convention shared by
  Aider, Zed, Warp, Junie, Devin, OpenCode, Amp and Jules. Adding a tool is one line.
- `install.sh` writes the directive into the global instruction files on a machine and installs the
  skill so `/prime-directive` works anywhere. Re-running replaces the marked block in place and
  leaves your own content alone.
- `scripts/doctor.sh` reports `ok` / `STALE` / `UNMARKED` / `MISSING` for every known location and
  exits non-zero if anything is not current, so it can run in CI or a pre-commit hook.
- Scripts are Bash 3.2, so `install.sh` works on a stock Mac without Homebrew.
- CI runs `doctor.sh --repo` and re-runs `render.sh` on every push, so a hand-edited rendered file
  or a missed re-render fails the build.

### Evidence

- `examples/` — five scenarios, each captured with the directive and without it on four models
  across two tools (Opus 4.6 and Sonnet 5 in Claude Code; gpt-6-astra and gpt-5.6-terra in Codex
  CLI). Twenty paired runs, with the raw transcript and a diff of every file the agent touched
  committed beside each rendered one.
- The set includes scenarios where the directive changed nothing because the baseline already
  behaved, and one capture that came out *worse* with the directive than without it, together with
  the five re-runs that failed to reproduce it.
- Harnesses for capturing new pairs in Claude Code (`bin/run.sh`) and Codex CLI (`bin/run-codex.sh`),
  a preflight that proves the machine's own skills are out of the run, and `bin/gif.py`, which
  replays a committed capture rather than recording a screen.

### Documentation and project setup

- README with the directive up front, the evidence, a quick start, an honest account of what a
  context file can and cannot guarantee, and a comparison against rule-sync tools.
- `CONTRIBUTING.md` — the one rule (edit the source, re-render, commit both), how to add a tool,
  and what makes a change to the directive itself easy to review.
- `CODE_OF_CONDUCT.md` — Contributor Covenant 2.1.
- Issue templates for bugs, new tool support, and arguments about the directive's wording.
- GitHub Sponsors setup, with sponsorship buying no say in what the directive says.
- MIT license.

[Unreleased]: https://github.com/12529572-Canada-Inc/prime-directive/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/12529572-Canada-Inc/prime-directive/releases/tag/v0.1.0
