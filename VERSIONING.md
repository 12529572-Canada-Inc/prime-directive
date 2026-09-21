# Versioning

This repo follows [Semantic Versioning](https://semver.org), but what is being versioned is not a
library. It is a piece of text an agent reads and behaves differently because of. So the rule here
is about behaviour, not about the diff.

## The test

> Could an agent following this version do something different, in a case the previous version
> already handled, because of this change?

**Yes → major. No → minor or patch.**

That is the whole rule. Everything below is what it means in practice.

## Major

Anything that can change what an agent does in a case the previous version already covered:

- Adding, removing, or reordering one of the core principles. That list is a *priority* order —
  reordering it changes which side of a conflict wins.
- Changing a step in the decision procedure, or what triggers the procedure at all.
- Changing who is in the agent's care, or how their interests are weighed against each other.
- Moving something between "what the directive does license" and "what it does not".
- Resolving an ambiguity the old text left open. If the old wording let two agents act differently
  and the new wording doesn't, then for one of those agents the behaviour just changed.
- Changing the one-line version at the top. Several tools truncate long instruction files; for
  those agents, that sentence *is* the directive.

## Minor

New capability, no change to what the directive asks of an agent:

- A new tool target in `scripts/targets.sh`.
- New scenarios, new models, or new re-runs in `examples/`.
- New documentation, new README sections.
- Wording changes to the directive that make the same instruction easier to read — tightening a
  sentence, unwinding an awkward clause — where you can state what the old text asked for and the
  new text asks for exactly that.

## Patch

Nothing an agent reads changes meaning:

- Typos, punctuation, broken links, formatting.
- Script fixes that make the tooling do what it already claimed to do.
- Re-rendering to clear drift between the source and a generated copy.

## The judgement call

"Wording-only" is the category that will get abused, because every author believes their edit is a
clarification. The check that keeps it honest: **name the case.**

If you are calling a directive edit minor, write down a concrete prompt where the old text and the
new text produce the same behaviour. That should be easy. If it isn't — if you find yourself
arguing that agents *probably* won't read the difference, or that the change is "just emphasis" —
it is a major.

When it is genuinely too close to call, `examples/` is the tiebreaker: run the affected scenario
both ways and look. That is what the example set is for. If the behaviour moves, it is a major.

If you can't afford the run, call it major. The cost of an over-loud version number is that someone
reads release notes they didn't need. The cost of a quiet one is that an agent's behaviour changed
underneath a user who pinned a version specifically so it wouldn't.

## Before 1.0

`0.x` means the directive's substance is still settling, and majors will land. The rule above still
applies — a behaviour change is still a major bump — it just costs less to make one right now.

`1.0` is a claim that the substance has stopped moving. It is not a claim that the repo is finished.

## Why the version is not stamped in `SKILL.md`

Every rendered copy already carries a content hash of the directive body, and `doctor.sh` uses it
to tell a current copy from a stale one. Putting a version number in the source would change that
hash on every release and force a re-render for a line no agent acts on. The tag identifies the
release; the hash identifies the text. They answer different questions.

## What a pin buys you

Pinning a tag gets you fixed directive text and a fixed source hash: `doctor.sh` stays green on that
checkout, and the agent reads the same words next month as today.

It does not get you fixed *behaviour*. That belongs to the model, not to this repo — see
[Honest limits](README.md#honest-limits).

## Cutting a release

1. Move the `Unreleased` items in [`CHANGELOG.md`](CHANGELOG.md) under the new version and date.
2. Write the release body at `docs/releases/vX.Y.Z.md`.
3. `scripts/render.sh && scripts/doctor.sh --repo` — every location `ok`, nothing drifted.
4. Tag the merge commit on `main`, annotated:
   `git tag -a vX.Y.Z -m "vX.Y.Z — <one line>"`
5. `git push origin vX.Y.Z`
6. `gh release create vX.Y.Z --notes-file docs/releases/vX.Y.Z.md`

The tag is the release. There is no build artifact — the directive is the text at that commit.
