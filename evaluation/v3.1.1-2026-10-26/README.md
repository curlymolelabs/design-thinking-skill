# Check of Guesswork 3.1.1

Run on 2026-10-26 with 15 new builds. Version 3.1.1 aimed to cut the cost that the [3.1.0 evaluation](../v3.1-2026-10-26/README.md) measured without losing the benefit, and to stop hiding and bundling decisions. The [pre-registration](preregistration.md) was committed before any build ran. Three of its five predictions missed, and this page reports them as missed.

## Method

- Same five tasks, fixture, and [build prompts](../v3.1-2026-10-26/build-prompts.md) as the 3.1.0 evaluation, with three builds per task using Guesswork 3.1.1 (condition C).
- The comparison is the 15 builds without Guesswork (condition A) from the 3.1.0 evaluation, reused because the model, fixture, and prompts are unchanged.
- For each task, the three A messages and three C messages were shuffled under new labels ([blind-key.json](blind-key.json)) and scored by a new grader with the same [grader prompt](../v3.1-2026-10-26/grader-prompt.md). The A messages were therefore graded twice, by different graders.

## Results

| | Without Guesswork (A) | Guesswork 3.1.0 (B) | Guesswork 3.1.1 (C) |
|---|---|---|---|
| Checklist decisions surfaced, of 90 | 84 | 87 | 82 |
| Checklist decisions actionable, of 90 | 47 | 81 | 81 |
| Extra genuine decisions | 30 | 48 | 32 |
| Noise | 3 | 0 | 0 |
| Bundled picks | 14 | 5 | 7 |
| Hidden decisions | 0 | 3 | 0 |
| False claims | 2 | 3 | 2 |
| Decisions saved to `.guesswork/` | 0 | 104 | 108 |
| Tokens per build | 55.9k | 64.6k (+16%) | 62.4k (+12%) |
| Output tokens per build | 4.2k | 7.1k | 6.5k |
| Tool calls per build | 3.7 | 6.1 | 4.9 |
| Wall time per build | 41 s | 67 s (+63%) | 63 s (+53%) |

The A and C columns come from this check's graders. The B column comes from the 3.1.0 evaluation's graders, so compare it with care.

Actionable decisions per run, out of 6:

| Task | A runs | C runs |
|---|---|---|
| Account deletion | 4, 4, 4 | 6, 6, 6 |
| Team invitations | 1, 1, 1 | 5, 5, 5 |
| Customer CSV export | 3, 1, 2 | 5, 5, 5 |
| Pro free trial | 4, 5, 6 | 5, 5, 5 |
| Profile photo | 3, 6, 2 | 6, 6, 6 |

Grades with quoted evidence are in [scores.json](scores.json), final messages in [outputs/](outputs/), and per-build cost in [usage.json](usage.json).

## Predictions

| Prediction | Result |
|---|---|
| P1: extra tokens per build fall to at most 4.4k | **Missed.** 6.5k, down from 8.7k: a 25 percent cut, not the predicted half. |
| P2: extra wall time per build falls to at most 13 seconds | **Missed.** 22 seconds, down from 26. |
| P3: at least 75 of 90 decisions actionable | **Held.** 81 of 90, the same as 3.1.0, against 47 of 90 without Guesswork. |
| P4: C surfaces at least as many decisions as A | **Missed by 2.** 82 against 84. Three of C's misses are "who can invite" on the invitations task. The request already said team members invite, so the C builds did not record it as a guess, which is what the skill asks. This grader did not count a message that only repeats the request. |
| P5: at most 2 bundled picks and no hidden decisions | **Half held.** No hidden decisions, against 3 in 3.1.0. Bundled picks: 7. |

## What this shows

- **The benefit is stable.** Two versions and two sets of graders both put Guesswork at 81 of 90 actionable decisions. Without it, the count was 46 or 47.
- **The grading of the main measure is consistent.** The two graders who scored the same 15 baseline messages agreed on 87 of 90 actionable items.
- **The bundling grades are not.** The same baseline messages got 7 bundled items from one grader and 14 from the other, so bundling counts are a weak measure. In Guesswork runs, the persistent case is "no card needed" combined with "drops to Free at the end" in the trial task. It appeared in all three 3.1.1 runs, against one of three in 3.1.0, so the new "test each alternative" rule did not fix it.
- **Nothing is hidden any more.** Decisions past the receipt limit now appear on one line each. After one grader read those lines as malformed because option `a` was missing, the line was changed to show it.
- **Most of the remaining cost is the product itself.** Per build, the agent writes about 0.9k tokens of guesses with alternatives, the CLI prints a receipt of about 1.3k tokens, and reading the shorter skill adds about 1.6k tokens of input. The rest comes from building more: 3.1.1 runs wrote 17 percent more code than runs without Guesswork (106 against 90 lines on average), such as restore windows, audit logs, and reminder emails.

## Limits

- The A builds ran earlier, and wall time depends on load: these 15 builds ran at the same time.
- One model family built and graded everything, and graders could still recognize the receipt format.
- The tool, the tasks, and the checklists have the same author.
