# Contributing

Thanks for taking an interest. This repo is small on purpose, and the rules below are what keep it that way.

## Conduct

This project is about duty of care, so it holds itself to one. Participation here — issues, pull requests, reviews, discussions — is covered by the [Code of Conduct](CODE_OF_CONDUCT.md), which is the Contributor Covenant 2.1. Reports go to the address named there and are handled privately.

Disagreeing hard with the directive, or with a review, is not a conduct problem — it is the point of the repo. Argue the text, not the person.

## The one rule

**Edit `.claude/skills/prime-directive/SKILL.md` only.** Every other copy of the directive in this repo — `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, the Cursor / Windsurf / Cline / Copilot files — is generated from it. After you change the source:

```sh
scripts/render.sh     # rewrites every rendered copy and stamps it with the new source hash
scripts/doctor.sh --repo   # should print "ok" for every repo location
```

Commit the source **and** the rendered files together. CI runs `doctor.sh --repo` and re-runs `render.sh` to check nothing drifted, so a PR that edits a rendered file by hand, or forgets to re-render, will fail.

## Adding support for a new tool

This is the most common contribution and takes one line. In `scripts/targets.sh`, add a row to the list:

```
scope  path  kind  frontmatter-id  tool
```

- `scope`: `repo` (path relative to the repo root) or `home` (relative to `$HOME`, written by `install.sh`).
- `kind`: `file` if the file is entirely ours and can be overwritten, or `block` if the tool's file may also hold the user's own content and our marked block should be upserted into it.
- `frontmatter-id`: `none`, or a key you add to `pd_frontmatter()` in the same file if the tool needs YAML frontmatter (see `cursor` and `windsurf` for examples).
- `tool`: the human-readable name shown by `doctor.sh`.

Then run `scripts/render.sh`, add the tool to the table in `README.md`, and open a PR that links to the tool's documentation for where it reads instructions and how to make a rule always-on. That link is what lets a reviewer check the row without installing the tool.

## Changing the directive itself

Wording changes to the directive are welcome, and so is disagreement about where it draws its lines. A few things make that kind of PR easy to review:

- Say what case the current text gets wrong, ideally as a concrete prompt and the behaviour you'd expect.
- Keep the one-line version at the top true to the whole. Several tools truncate long instruction files, and that sentence is what survives.
- Keep the decision procedure short enough to run in the middle of a task. If a change makes it longer, say why the extra step earns its place.
- Don't add clauses that only reduce usefulness without reducing real risk — "safety theatre" is listed as an anti-pattern in the directive for a reason.

For anything larger than a wording fix, open an issue or discussion first so the argument can happen before the diff does.

## Versioning and releases

Any PR that changes something a user would notice adds a line to the `Unreleased` section of
[`CHANGELOG.md`](CHANGELOG.md). For a change to the directive itself, say in the PR whether you
read it as a major or a minor under [VERSIONING.md](VERSIONING.md) — that judgement is part of the
review, not something the maintainer reconstructs afterwards.

The rule in one sentence: a change that could make an agent act differently in a case the previous
version already handled is a major bump, however small the diff. So if you are calling a directive
edit minor, name a concrete prompt where the old text and the new text behave the same. If naming
one is hard, it is a major.

## Scripts

The scripts are plain Bash 3.2 (the macOS default) — no arrays-of-arrays, `mapfile`, or `${var,,}`. Please keep them that way so `install.sh` works on a stock Mac without Homebrew.

## License

By contributing you agree that your contributions are licensed under the MIT License in `LICENSE`.
