# Sponsorship — setup notes and tier copy

**Status: live.** The profile is published at
[github.com/sponsors/12529572-Canada-Inc](https://github.com/sponsors/12529572-Canada-Inc) and
`.github/FUNDING.yml` points at it, so the Sponsor button works. The tier copy below is still
what goes *into* the profile — tiers are configured on GitHub, not in this repo, so this file is
the source text and the standing commitments, not a description of what is currently set.
Issue: [#11](https://github.com/12529572-Canada-Inc/prime-directive/issues/11).

## What the money is actually for

Be specific in public, because "support the project" funds nothing in particular. The real
recurring costs here are:

- **Model API credits for `examples/`.** Twenty paired runs across four models and two tools,
  and the number grows with every new scenario and every new model worth checking. Re-running
  the matrix after a directive edit is the single largest cost, and it is the thing that makes
  the evidence section worth reading.
- **Keeping the rendered copies honest across tools.** Each tool moves its instruction
  convention on its own schedule; `scripts/targets.sh` and the doctor check have to follow.
- **Maintainer time** on issues, PRs, and the wording arguments that matter (see
  [`docs/issue-20-conflict-wording.md`](issue-20-conflict-wording.md) for what one of those
  looks like).

If sponsorship covers the API bill, the example matrix gets re-run on directive changes instead
of when it is affordable. That is a concrete improvement to the repo's central claim, which is
why it is the thing to promise.

## Tiers to paste into GitHub Sponsors

GitHub asks for an amount, a short public description, and an optional welcome message per
tier. Keep descriptions under about 100 characters — longer ones get clipped in the sidebar.
Amounts are a starting point, not a pricing study.

Two one-time tiers and four monthly ones is enough; more than that is a menu nobody reads.

### Monthly

| Amount | Public description | Notes |
| --- | --- | --- |
| **$5** | Covers a few example runs. Name in `SPONSORS.md` if you want it there. | The default tier. Most sponsors will pick this one. |
| **$25** | Covers a full scenario re-run on one model after a directive change. | Ties the amount to a real unit of work. |
| **$100** | Covers a full re-run of the example matrix — all models, both tools. | The number that makes the evidence section reproducible on demand. |
| **$500** | Organization tier. Logo and link in `SPONSORS.md` and the README. | For companies that have the directive in their repos. |

### One-time

| Amount | Public description |
| --- | --- |
| **$10** | One-off thanks. No strings, nothing owed. |
| **$250** | One-off backing for the next round of example runs. |

### Welcome message (same for every tier)

> Thank you — this pays for model credits, which is what keeps `examples/` current instead of
> aspirational.
>
> Two things worth saying plainly: sponsorship buys no influence over what the directive says,
> and nothing here moves behind a paywall. If you want to change the directive's wording, open
> an issue — that path is the same for sponsors and non-sponsors, and it is the better one.
>
> If you would like your name or logo in `SPONSORS.md`, reply and tell me how to list you.
> Silence means I leave you out.

Note the default: **listed only on request.** Publishing a sponsor's name without asking is a
small thing to get wrong and an easy one to get right.

## What sponsorship does not buy

State this on the Sponsors profile as well as here. A funding relationship that goes unstated
is the kind of quiet influence this repo is nominally against.

- **No influence over the directive's content.** Wording changes go through issues and PRs, and
  get argued on their merits. A sponsor's issue is read the same way as anyone else's.
- **No paid tier of the directive.** The text stays MIT, whole, for everyone. There is no
  "pro" version and there will not be one.
- **No support SLA.** This is one maintainer. A tier is a thank-you, not a contract, and
  nothing here promises a response time.
- **No endorsement in either direction.** Listing a sponsor is not a claim that their products
  follow the directive.

## Transparency

Promise only what survives a bad month:

- **`SPONSORS.md`** in the repo root, listing sponsors who asked to be listed. Updated when
  someone joins or leaves.
- **A yearly note** — one section appended to this file, in December — with the year's total
  received, what it was spent on, and what is left. Totals and categories, not per-sponsor
  amounts.
- **Disclosure at the point of use.** When a sponsored run produces something committed to
  `examples/`, the note beside it says the runs were sponsor-funded. That is where a reader
  evaluating the evidence would want to know.

Monthly reporting sounds better and is harder to sustain; a promise of monthly updates that
goes quiet in March is worse than a yearly one that holds.

## Checklist

- [x] Publish the GitHub Sponsors profile for the `12529572-Canada-Inc` org.
- [x] Point `.github/FUNDING.yml` at it.
- [ ] Add the tiers above. The profile currently offers a custom amount only.
- [ ] Set the welcome message.
- [ ] Replace the default bio — "Support 12529572-Canada-Inc's open source work" says nothing —
      with what the money pays for and the "what sponsorship does not buy" list.
- [ ] Confirm the Sponsor button appears on the repo.
- [ ] Create `SPONSORS.md` when the first sponsor asks to be listed.
- [ ] Optional: swap the README badge for the live sponsor count.
      `[![Sponsor](https://img.shields.io/github/sponsors/12529572-Canada-Inc?logo=githubsponsors&logoColor=white&color=ea4aaa)](https://github.com/sponsors/12529572-Canada-Inc)`
      — shields.io documents that endpoint for user accounts and this is an org, so check it
      renders a number rather than an error before committing it. The static badge works either
      way, and a badge reading "0 sponsors" is its own kind of honest.
