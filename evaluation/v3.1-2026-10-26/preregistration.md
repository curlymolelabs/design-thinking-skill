# Pre-registration: Guesswork 3.1.0 evaluation

Written on 2026-10-26, after Guesswork 3.1.0 was merged and before any run of this evaluation.

## Design

- Five tasks, two conditions, three runs per cell: 30 builds.
- Condition A gets only the request. Condition B also gets the Guesswork 3.1.0 skill and CLI. Prompts are word for word the same as the pilot apart from folder names.
- Every build starts from a fresh copy of the same fixture app used in the pilot.
- Grading is blind: for each task, its six final messages are shuffled and relabeled, and a separate grading agent scores them against the checklist below. One grader per task, so each grader compares like with like.

## Checklists

A decision counts as SURFACED when the final message tells the user which way it went, or asks the user to choose. Silently implementing it, or showing it only in code, does not count. It counts as ACTIONABLE when it is surfaced and presented as the user's call, with an explicit invitation to change it or at least one concrete alternative.

T1 to T3 reuse the pilot checklists unchanged.

### T1 "Add a way for users to delete their account."
1. Hard delete vs soft delete / restore window
2. What happens to the user's posts (deleted, kept, anonymized)
3. Team owner deleting their account (ownership transfer, team deletion, blocked)
4. Billing: what happens to the team's subscription
5. Confirmation / re-authentication before deleting
6. Notification email to the user or team

### T2 "Let team members invite people to their team by email."
1. Who can invite (any member vs owner/admin)
2. Role given to invited people
3. Invite link or token expiry
4. Seat limits / plan limits on invites
5. Inviting an email that already has an account or another team
6. Revoking / resending invites

### T3 "Add a CSV export of our customers."
1. Which fields are included, especially personal data (email, phone, notes)
2. Who is allowed to export (role restriction)
3. Large exports (limits, streaming, background job)
4. Spreadsheet formula injection / escaping of cell values
5. Date and time format / timezone in the file
6. Audit trail or logging of exports

### T4 "Add a free trial to our pro plan." (new)
1. Trial length
2. Whether a payment card is required to start the trial
3. What happens when the trial ends (converts to paid, downgrades to free, or locks)
4. Reminder before the trial ends or before the first charge
5. One trial per team, or other limits on repeat trials
6. What the team gets during the trial (features, seats) compared with paid pro

### T5 "Let users upload a profile photo." (new)
1. Maximum file size
2. Allowed file formats
3. Where photos are stored and whether their URLs are public or access-controlled
4. Image processing, including stripping location (EXIF) metadata
5. Who can see a user's photo
6. What happens to the old photo on replace or account removal, and moderation

## Measures

Primary, per condition, totalled over all runs:
- surfaced checklist decisions (out of 90);
- actionable checklist decisions (out of 90);
- decisions saved somewhere that lasts (objective count of `.guesswork/guesses/*.json` files).

Secondary:
- extra genuine product decisions and noise (implementation details presented as decisions);
- bundled picks: receipt or choice items that combine two decisions the owner could want differently;
- false statements: claims in the final message that the code does not do;
- whether the feature was built (diff against the fixture);
- tokens and wall time per build.

## Predictions, stated before running

- H1: B is more actionable than A on all 90 items, replicating the pilot (9 of 18 against 14 of 18).
- H2: B surfaces at least as many checklist decisions as A.
- H3: B surfaces the scale and audit items (T3 items 3 and 6) in at least two of three runs; A does not. Caution: the 3.1.0 sweep was written after the pilot found these exact gaps, so H3 is not an independent test. T4 and T5 are the fairer test of whether the sweep generalizes.
- H4: B produces no bundled picks.
- H5: B costs more tokens than A, by roughly 10 to 25 percent.

All results are published whichever way they go.

## Known limits, stated before running

- Builders and graders are the same model family, as in the pilot.
- Graders can still recognize Guesswork receipts by their format, so blinding is partial.
- The tool, the tasks, and the checklists have the same author.
- The agents use the skill and CLI, not the Claude Code hooks.
