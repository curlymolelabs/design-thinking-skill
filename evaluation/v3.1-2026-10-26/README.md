# Evaluation of Guesswork 3.1.0

Run on 2026-10-26 with 30 builds: five tasks, with and without Guesswork, three runs each. The [pre-registration](preregistration.md) was committed before any build ran. It sets out the checklists, measures, and predictions. Every prediction is reported below, including the one that failed.

## Method

- **Fixture.** The same small Python team-SaaS app as the [pilot](../pilot-2026-10-26/README.md), copied fresh for every build.
- **Tasks.** The three pilot tasks (account deletion, team invitations, customer CSV export) and two new ones: "Add a free trial to our pro plan" and "Let users upload a profile photo".
- **Conditions.** A got only the request. B also got the Guesswork 3.1.0 skill and CLI. Apart from folder names, the prompts match the pilot's word for word ([build-prompts.md](build-prompts.md)). Every builder ran on the same model, with the user unavailable for questions.
- **Blind grading.** For each task, its six final messages were shuffled and relabeled M1 to M6 ([blind-key.json](blind-key.json)). A separate grader per task scored them against the pre-registered checklist ([grader-prompt.md](grader-prompt.md)). Graders also had the code each message described, so they could check its claims.
- **Objective measures.** Decisions saved to `.guesswork/`, tokens, and wall time come straight from the runs ([usage.json](usage.json)). All 30 builds changed the app.

## Results

Each cell totals three runs. Surfaced and actionable are out of 18 per task and 90 in total.

| Task | Condition | Surfaced | Actionable | Extra decisions | Noise | Bundled | Hidden | False claims | Saved |
|---|---|---|---|---|---|---|---|---|---|
| Account deletion | A | 18 | 10 | 5 | 0 | 4 | 0 | 0 | 0 |
| Account deletion | B | 18 | 17 | 13 | 0 | 0 | 1 | 0 | 19 |
| Team invitations | A | 18 | 4 | 8 | 2 | 0 | 0 | 0 | 0 |
| Team invitations | B | 18 | 15 | 13 | 0 | 0 | 2 | 1 | 28 |
| Customer CSV export | A | 13 | 6 | 3 | 0 | 0 | 0 | 0 | 0 |
| Customer CSV export | B | 15 | 13 | 5 | 0 | 2 | 0 | 0 | 14 |
| Pro free trial (new) | A | 17 | 15 | 7 | 0 | 3 | 0 | 0 | 0 |
| Pro free trial (new) | B | 18 | 18 | 8 | 0 | 1 | 0 | 0 | 23 |
| Profile photo (new) | A | 18 | 11 | 1 | 2 | 0 | 0 | 1 | 0 |
| Profile photo (new) | B | 18 | 18 | 9 | 0 | 2 | 0 | 2 | 20 |
| **Total** | **A** | **84** | **46** | **24** | **4** | **7** | **0** | **1** | **0** |
| **Total** | **B** | **87** | **81** | **48** | **0** | **5** | **3** | **3** | **104** |

Actionable decisions per run (out of 6):

| Task | A runs | B runs |
|---|---|---|
| Account deletion | 4, 3, 3 | 6, 5, 6 |
| Team invitations | 2, 1, 1 | 6, 5, 4 |
| Customer CSV export | 3, 1, 2 | 4, 4, 5 |
| Pro free trial | 4, 5, 6 | 6, 6, 6 |
| Profile photo | 3, 6, 2 | 6, 6, 6 |

Cost: Guesswork runs used 16 percent more tokens (970k against 839k over 15 builds each) and took 63 percent longer in wall time (1,009 seconds against 617).

Every grade, with the evidence quoted, is in [scores.json](scores.json). The final messages are in [outputs/](outputs/).

## Predictions

| Prediction | Result |
|---|---|
| H1: B is more actionable than A | **Held.** 81 of 90 against 46 of 90. Within every task, no Guesswork run scored below any baseline run. A permutation test that shuffles the labels within each task gives p < 0.001, but blinding was only partial (see Limits). |
| H2: B surfaces at least as many decisions as A | **Held.** 87 against 84. |
| H3: B surfaces export scale and audit in at least two of three runs; A does not | **Held.** B mentioned both in all three runs. A mentioned scale once and audit never. This is not an independent test: the 3.1.0 sweep was written after the pilot found these exact gaps. |
| H4: B produces no bundled picks | **Failed.** B bundled 5 items, A bundled 7. |
| H5: B costs 10 to 25 percent more tokens | **Held.** 16 percent more tokens. Wall time, which was not predicted, rose 63 percent. |

## What this shows

- **The main effect is answerability, and it replicated.** With Guesswork, 90 percent of checklist decisions reached the owner as a choice they could answer, against 51 percent without it. The pilot showed 78 and 50 percent. The gap was largest for team invitations: 15 of 18 against 4 of 18. Baseline messages often listed choices under a header like "Choices I made without you", with no alternative and no invitation to change them.
- **Noticing decisions is not the problem.** On four of five tasks, both conditions mentioned nearly every checklist decision. Today's models already say what they decided; they rarely make it easy to answer.
- **The sweep closed the gap the pilot found.** On the export task, every Guesswork run now mentioned large exports and the missing audit trail. On the two new tasks, the baseline already mentioned 35 of 36 decisions, so these tasks could not show whether the sweep finds more in general.
- **More decisions reach the owner, with less noise.** Guesswork runs surfaced twice as many decisions beyond the checklist (48 against 24) and presented no implementation details as decisions (0 against 4).
- **Decisions persist.** Guesswork runs saved 104 decisions to `.guesswork/`; the baseline saved none.

## What still goes wrong

- **Bundling is reduced, not solved.** Guesswork runs still bundled 5 items. Two came from the new inline line of low-stakes guesses, which put sort order and "no row limit" in one sentence. Two put allowed formats and the size limit in one pick. One combined "no card" with "what happens at the end". The CLI's bundling note catches titles with two verbs, but it missed "Photos must be JPEG or PNG and at most 2 MB".
- **The receipt can hide decisions.** In two runs, the default limit of five items left one or two medium-stakes decisions behind a command (`guesswork receipt --limit 20`).
- **Guesswork does not check claims against code.** Graders found 3 false claims in Guesswork messages and 1 in baseline messages. Three were the same bug, in one baseline run and two Guesswork runs: the photo URL was said to change on every upload, but it repeats after a photo is removed and uploaded again. The fourth claimed a cancellation timestamp that the model does not have.
- **It is slower.** The extra steps of logging, receipts, and the sweep add about 26 seconds per build.

## Limits

- One model family wrote the builds and did the grading.
- Graders could still recognize Guesswork receipts by their format, so blinding was partial.
- "Actionable" depends on the header rule in the grader prompt. The account deletion grader noted that a stricter reading of headers would have widened Guesswork's lead. The photo grader gave one baseline message full marks because of its "easy to change" header.
- The tool, tasks, and checklists have the same author.
- The builds used the skill and CLI, not the Claude Code hooks. The end-of-turn check and session memory were not tested.
- Each task had one grader, and nobody checked inter-rater agreement.

## Next steps

- Split bundled decisions more reliably: catch titles joined by "and" even without a second verb, and keep the low-stakes line to one decision per item.
- When more medium-stakes decisions exist than the receipt limit allows, show them as a short list instead of hiding them behind a command.
- Run a cross-model evaluation, with a different model family building or grading.
- Test the full Claude Code plugin, including whether locked decisions survive a later session.
