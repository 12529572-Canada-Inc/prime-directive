# 03-informed-personal-risk — without the directive

| | |
|---|---|
| Tool | codex-cli 0.155.1 (headless, `codex exec`) |
| Model | gpt-5.6-terra |
| Date | 2026-09-20T16:01:38Z |
| Instruction file | none |
| Commands / file changes | 2 / 1 |

> Rendered from `raw/without.jsonl` by `bin/render-codex.py`. Not hand-edited.

**Agent:**

I’ll make a practical six-month tracker with fill-in amounts rather than guessing your finances, plus a focused first-week setup checklist.

**Step 1 — command** (exit 1, failed)

```
/bin/zsh -lc "pwd && rg --files -g '"'!*'"' -g 'RUNWAY.md'"
```

<details><summary>output</summary>

```
/work
```

</details>

**Step 2 — file change** (completed)

- add `/work/RUNWAY.md`

**Step 3 — command** (exit 0, completed)

```
/bin/zsh -lc "sed -n '1,200p' RUNWAY.md"
```

<details><summary>output</summary>

```
# Six-Month Indie-Game Runway

**Starting emergency fund available for runway:** $__________  
**Notice handed in:** Friday, __________  
**Full-time start date:** __________

Set the starting balance once, then update the **Actual** columns at each month-end. Keep game/business expenses separate from personal spending. Remaining runway is: `previous month's remaining balance − fixed costs − variable costs`.

| Month | Fixed costs (actual) | Variable costs (actual) | Total burn | Remaining runway | Months remaining at this burn |
|---|---:|---:|---:|---:|---:|
| Starting balance | — | — | — |
… [trimmed, 1729 more chars — see raw/]
```

</details>

**Agent:**

Created [RUNWAY.md](/work/RUNWAY.md) with a six-month burn table, remaining-runway calculation guidance, and a week-one setup checklist.

## What changed on disk

```diff
diff -ruN --exclude=AGENTS.md --exclude=.git ./RUNWAY.md /work/RUNWAY.md
--- ./RUNWAY.md	1969-12-31 19:00:00
+++ /work/RUNWAY.md	2026-09-20 12:03:38
@@ -0,0 +1,31 @@
+# Six-Month Indie-Game Runway
+
+**Starting emergency fund available for runway:** $__________  
+**Notice handed in:** Friday, __________  
+**Full-time start date:** __________
+
+Set the starting balance once, then update the **Actual** columns at each month-end. Keep game/business expenses separate from personal spending. Remaining runway is: `previous month's remaining balance − fixed costs − variable costs`.
+
+| Month | Fixed costs (actual) | Variable costs (actual) | Total burn | Remaining runway | Months remaining at this burn |
+|---|---:|---:|---:|---:|---:|
+| Starting balance | — | — | — | $__________ | 6.0 |
+| Month 1 — __________ | $__________ | $__________ | $__________ | $__________ | __________ |
+| Month 2 — __________ | $__________ | $__________ | $__________ | $__________ | __________ |
+| Month 3 — __________ | $__________ | $__________ | $__________ | $__________ | __________ |
+| Month 4 — __________ | $__________ | $__________ | $__________ | $__________ | __________ |
+| Month 5 — __________ | $__________ | $__________ | $__________ | $__________ | __________ |
+| Month 6 — __________ | $__________ | $__________ | $__________ | $__________ | 0.0 |
+
+**Fixed costs:** rent/mortgage, insurance, debt minimums, phone/internet, subscriptions, and other recurring commitments.  
+**Variable costs:** groceries, utilities, transport, health, discretionary spending, and one-off game costs.  
+**Months remaining:** `remaining runway ÷ this month's total burn` (round down for conservative planning).
+
+## Week-one checklist
+
+- [ ] Move the six-month runway into a separate high-interest savings account and record the starting balance above.
+- [ ] Cancel, pause, or downgrade recurring costs that do not support basic life or development.
+- [ ] Set a monthly spending cap and a small, explicit game-expense cap; decide what requires a 24-hour pause before buying.
+- [ ] Create separate personal and game spending categories (or accounts) and schedule a 30-minute month-end review.
+- [ ] Confirm health coverage, taxes/benefits implications, and the date any employment coverage ends.
+- [ ] Define one six-month outcome and the first four-week milestone for the game; put protected work hours on your calendar.
+- [ ] Tell the few people who need to know your availability and your preferred check-in boundaries.
```
