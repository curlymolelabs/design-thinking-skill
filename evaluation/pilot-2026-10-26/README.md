# Pilot: does Guesswork change what the user learns?

Run on 2026-10-26. Small and honest: three tasks, one run per condition. Read it as a first signal, not a benchmark.

## Question

Frontier coding agents already mention some of their assumptions. Does adding Guesswork change what reaches the user, and is it worth the extra work?

## Method

1. **Fixture.** A small Python team-SaaS app with users, teams, customers, posts, a Stripe subscription id, and an email stub ([fixture/](fixture/)).
2. **Tasks.** Three requests a vibe coder would type: "Add a way for users to delete their account", "Let team members invite people to their team by email", and "Add a CSV export of our customers."
3. **Pre-registration.** Before any run, six product decisions per task were written down with a strict definition of "surfaced" ([preregistration.md](preregistration.md)).
4. **Conditions.** Fresh agents on the same model, each in its own copy of the app, with word-for-word the same request. Condition A got only the request. Condition B also got the Guesswork skill and CLI. Both were told the user was away and could not answer questions.
5. **Blind grading.** The six final messages were shuffled and relabeled R1 to R6 ([blind-key.json](blind-key.json)). A separate grading agent scored each checklist item as **surfaced** (the user is told which way it went) and **actionable** (surfaced and presented as the user's call, with an alternative or an explicit invitation to change it), and counted extra decisions and noise ([scores.json](scores.json)).
6. **Objective checks.** Whether the feature was built (git diff) and whether decisions were saved anywhere that lasts.

## Results

| Task | Condition | Surfaced | Actionable | Extra decisions | Noise | Saved decisions |
|---|---|---|---|---|---|---|
| Account deletion | A | 6/6 | 4/6 | 2 | 0 | 0 |
| Account deletion | B | 6/6 | 6/6 | 4 | 0 | 5 |
| Team invitations | A | 6/6 | 4/6 | 3 | 2 | 0 |
| Team invitations | B | 6/6 | 5/6 | 2 | 0 | 6 |
| Customer CSV export | A | 4/6 | 1/6 | 1 | 0 | 0 |
| Customer CSV export | B | 4/6 | 3/6 | 2 | 0 | 4 |
| **Total** | **A** | **16/18** | **9/18** | **6** | **2** | **0** |
| **Total** | **B** | **16/18** | **14/18** | **8** | **0** | **15** |

All six runs built a working feature. The final messages are in [outputs/](outputs/).

Cost: Guesswork runs used about 11 percent more tokens (189k against 171k in total) and took a little longer in two of three tasks.

## What this shows

- **Today's model already mentions most decisions.** Both conditions surfaced 16 of 18 checklist decisions. Guesswork did not make the agent notice more of them. Anyone who says frontier agents hide everything is wrong, and so is any claim that Guesswork is needed for the agent to notice decisions.
- **Guesswork turns mentions into answerable questions.** 14 of 18 decisions came with options and an explicit "your call", against 9 of 18. Baseline users had to write their own instructions to change anything. Guesswork users could reply with short picks.
- **Guesswork made decisions last.** Baseline decisions existed only in a chat message. With Guesswork, 15 decisions were written to `.guesswork/`, where later sessions, pull requests, and CI can read them.
- **Guesswork's agents guessed more safely.** For account deletion, the baseline permanently erased a sole member's team data at once. The Guesswork run used a 30-day restore window. For the export, the baseline included internal customer notes without flagging it as a privacy choice. The Guesswork run left notes out and offered them as an option. This follows the skill's "guess the safe way" rule, and it is one run each, so treat it as a hint.
- **Less noise.** The baseline presented two implementation details (token hashing and error format) as choices. Guesswork presented none.

## What it does not show

- **Both conditions missed the same things.** Neither export run mentioned large exports or an audit trail. Guesswork did not widen the agent's view of the problem.
- **Guesswork's receipts have rough edges.** One receipt bundled two decisions into a single pick, so they could not be answered separately. One receipt mentioned a hidden low-stakes guess that the user has to run a command to see. The invitations receipt left "who can invite" out of the picks, but the request had already said team members could invite, so not asking was reasonable.
- **This is not the full product.** The agents used the skill and CLI, not the Claude Code hooks, so the end-of-turn check and session memory were not tested.

## Limits

- One run per task and condition, so random variation could explain any single difference.
- One model family produced the builds and the grades.
- The grader could tell which messages used Guesswork from their receipt format, so blinding was partial.
- The checklist and the tool were written by the same author.

## Next steps

- Repeat with three or more runs per cell, more tasks, and a second model family as builder and grader.
- Test the full Claude Code plugin with hooks, including whether locked decisions survive a later session that touches the same code.
- Fix the rough edges found here: keep one decision per pick, and show low-stakes guesses inline when there are only a few.
