# Pre-registration: Guesswork 3.1.1 check

Written on 2026-10-26, after the 3.1.1 changes were committed and before any build of this check ran.

## Why

The [3.1.0 evaluation](../v3.1-2026-10-26/README.md) found that Guesswork made 81 of 90 decisions answerable against 46 of 90 without it, but cost 8.7k more tokens and 26 more seconds per feature. It also bundled 5 decisions and hid decisions past the receipt limit in 2 runs. Version 3.1.1 tries to cut that cost and fix both problems without losing the benefit.

## Design

- The same five tasks, fixture, and build prompts as the [3.1.0 evaluation](../v3.1-2026-10-26/build-prompts.md).
- 15 new builds with Guesswork 3.1.1 (condition C), three per task.
- The comparison is the 15 builds without Guesswork already recorded in the 3.1.0 evaluation (condition A). They are reused, not re-run, because the model, fixture, and prompts are unchanged.
- Grading uses the same grader prompt. For each task, the three A messages and three C messages are shuffled under new labels, and a new grader scores them. Because the A messages are graded a second time by a different grader, comparing the two sets of A grades shows how consistent the grading is.

## Predictions

- P1: C's extra tokens per build over A are at most half of 3.1.0's (at most 4.4k, against 8.7k).
- P2: C's extra wall time per build over A is at most half of 3.1.0's (at most 13 seconds, against 26).
- P3: C keeps the benefit: at least 75 of 90 checklist decisions are actionable.
- P4: C surfaces at least as many checklist decisions as A.
- P5: C has at most 2 bundled picks and no hidden decisions.

All results are published whichever way they go.

## Known limits

- Wall time depends on load. The 3.1.0 builds ran 10 to 20 at a time; these 15 run at once.
- Reusing the A builds means A and C ran at different times.
- The limits of the 3.1.0 evaluation also apply: one model family, partial blinding, one author.
