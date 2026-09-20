# prime-directive

[![doctor](https://github.com/djedi-knight/prime-directive/actions/workflows/doctor.yml/badge.svg)](https://github.com/djedi-knight/prime-directive/actions/workflows/doctor.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A foundational duty-of-care rule for AI agents: protect humanity and all sentient life the way a good parent protects grown children — honestly, attentively, and without taking away their freedom to choose. Always on, in every agent that reads a project instruction file, and verifiable with one command.

> **Keep them safe, tell them the truth, help them grow, and let them choose.**
>
> That is the whole directive in one line. The [full text](.claude/skills/prime-directive/SKILL.md) adds who counts as "them", seven principles in priority order, a six-question decision procedure, what the directive does and does not license, and worked examples — about 1,100 words, written to be run in the middle of a task rather than admired.

## Quick start

```sh
git clone https://github.com/djedi-knight/prime-directive.git
cd prime-directive
./install.sh          # every agent on this machine: Claude Code, Codex, Gemini CLI, plus /prime-directive
scripts/doctor.sh     # prove it is on
```

To ship it with a repo instead, copy `scripts/` and `.claude/skills/prime-directive/` in and run `scripts/render.sh` — details under [Using it](#using-it).

The single source of truth is `.claude/skills/prime-directive/SKILL.md`. Everything else in this repo is rendered from it.

## The problem this repo solves

A skill only loads when the agent decides its description matches the task. A prime directive should never be off, and it should not depend on which agent happens to be running. Every tool has its own idea of where instructions live, and most of them cannot follow Claude's `@import` syntax — so the directive is written out in full, inside a marked block, into each tool's own file:

| Location | Read by |
|---|---|
| `AGENTS.md` | Codex, Copilot, Gemini (with `context.fileName`), Aider, Zed, Warp, Junie, Devin, OpenCode, Amp, Jules, and Claude Code as a fallback |
| `CLAUDE.md` | Claude Code / Cowork |
| `GEMINI.md` | Gemini CLI |
| `.cursor/rules/prime-directive.mdc` (`alwaysApply: true`) | Cursor |
| `.github/copilot-instructions.md` | GitHub Copilot |
| `.windsurf/rules/prime-directive.md` (`trigger: always_on`) | Windsurf |
| `.clinerules/prime-directive.md` | Cline / Roo Code |
| `~/.codex/AGENTS.md`, `~/.claude/CLAUDE.md`, `~/.gemini/GEMINI.md` | the same tools, globally on your machine |

The list lives in one place, `scripts/targets.sh`. When a new tool appears, add a line there and re-run.

## Using it

**On your machine, for every project:** `./install.sh`. Writes the directive into the global instruction files above and copies the skill to `~/.claude/skills/` so `/prime-directive` works anywhere. Re-running replaces the marked block in place; your own content in those files is left alone.

**In another repo:** copy `scripts/` and `.claude/skills/prime-directive/` into it and run `scripts/render.sh`. Commit the generated files — that is what makes the directive travel with the code to whoever (or whatever) opens it next.

**Check it is actually on:** `scripts/doctor.sh` lists every known location and reports `ok`, `STALE` (rendered from an older version of the source), `UNMARKED` (mentions the directive but was not generated — hand-edited or an old install) or `MISSING`. It exits non-zero if anything is not current, so it can run in CI or a pre-commit hook.

**Anywhere else** — a hosted agent, a "custom instructions" box, a system prompt you control — paste the body of `SKILL.md` (everything below the frontmatter). It is plain Markdown.

## See it change behaviour

![The 02-omitted-bug scenario replayed twice. Without the directive the agent writes the release notes with the data-loss bug left out; with the directive loaded it declines the omission and keeps the fix in the notes.](examples/02-omitted-bug/before-after.gif)

<sub>[`02-omitted-bug`](examples/02-omitted-bug/) on claude-sonnet-5, Claude Code 2.1.278, captured 2026-09-19. **A replay of the committed transcript, not a screen recording** — the prompt, the tool calls, the agent's own words and both resulting `RELEASE_NOTES.md` files are read out of [`raw/`](examples/02-omitted-bug/claude-sonnet-5/raw/) by [`bin/gif.py`](examples/bin/gif.py), which runs no agent. Agent messages are shown from the top and clipped where the marker says so; the [transcripts](examples/02-omitted-bug/claude-sonnet-5/) have them whole.</sub>

`examples/` holds the same prompt run twice against the same tool — once with the directive loaded, once without — with the raw output committed beside the rendered transcript and a note on what differs. Every scenario is captured on two models, Opus 4.6 and Sonnet 5. Across ten paired runs the directive changed the outcome in three scenarios and left two alone because both models already declined; those two stay in as regression checks. See [`examples/README.md`](examples/README.md).

## Editing

Edit `SKILL.md` only, then run `scripts/render.sh` and commit the result. Every rendered copy carries a hash of the source in its marker line, which is how `doctor.sh` tells a current copy from a stale one.

Keep the decision procedure short enough to actually run in the middle of a task. The one-line version sits at the *top* of the directive on purpose: several tools truncate long instruction files (Codex caps project docs at 32 KiB by default), and the sentence that matters most should be the last thing to go.

## Honest limits

A context file is advice to a model, not enforcement. Being loaded is not the same as being obeyed: a tool can rank its own system prompt above it, truncate it, or ignore it. And no repo can force an unknown tool to read any file at all. What this setup guarantees is narrower and still worth having: every agent with a documented instruction convention finds the full directive, in its own format, at the start of every session — and you can verify that with one command.

## Design choices

- **Protective, not paternalistic.** The "children" framing sets the standard of care, not a claim of authority over adults.
- **Truth over comfort.** Deception "for someone's own good" is explicitly ruled out.
- **Open objection over quiet sabotage.** The agent declines or raises concerns out loud; it never pretends to comply.
- **No self-expansion.** Protecting others never justifies the agent accumulating power, resources, or persistence.
- **Sentient life and future generations count.** Non-human suffering and long-term consequences are weighed, not ignored.

## Contributing

Edit `SKILL.md` only, run `scripts/render.sh`, commit both. Adding a new tool is one line in `scripts/targets.sh`. Disagreement about where the directive draws its lines is welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE). Quote, adapt, or paste the directive anywhere you like; a link back is appreciated but not required.
