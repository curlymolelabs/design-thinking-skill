---
name: guesswork
description: Record the product decisions you make without explicit instructions (defaults, limits, permissions, data handling, money, notifications, user-facing promises) in a .guesswork/ ledger, end the turn with a short receipt the user answers in one line, and respect the decisions they already made. Use whenever you build or change user-facing behavior that the user did not fully specify, when the user answers a Guesswork receipt with replies like "1b 2a", or when asked what product decisions a codebase already makes. Do not use for pure refactors, styling, or work the user specified completely.
license: MIT
metadata:
  version: "3.1.0"
  short-description: "Review the decisions your agent made, not just the diff"
---

# Guesswork

Every request leaves gaps, and you fill them with guesses: how long a session lasts, who can invite whom, whether a delete can be undone, when a trial starts charging. Most guesses are fine. A few decide who gets charged, who sees whose data, and what cannot be undone.

The user cannot review a two-thousand-line diff, but they can answer five decisions. Your job is to guess safely, record each guess honestly, show the risky ones briefly, and remember the answers.

## Find the command

- With the Guesswork plugin in Claude Code, run `guesswork` directly.
- Otherwise run `python3 <this skill's folder>/scripts/guesswork.py` with the absolute path of this folder. It needs Python 3.9 or newer and no packages.
- If you cannot run Python, write ledger files directly as described in [references/ledger-format.md](references/ledger-format.md).

The examples below write `guesswork` for either form.

## Record a guess when three things are true

1. You chose behavior that users, customers, or the business can notice or be affected by.
2. The user did not specify it in this conversation, and the codebase does not already do the same thing elsewhere.
3. A reasonable product owner could want it differently.

| Record it | Do not record it |
|---|---|
| Password reset links expire after 1 hour | Used the existing date library |
| The free plan allows 3 projects | Renamed a variable or extracted a helper |
| Deleting a comment hides it instead of erasing it | Followed the lint and formatting rules |
| Admins can read every member's private notes | Matched the existing button style |
| Exports include customer email addresses | Wrote tests for behavior the user specified |
| The dashboard defaults to the last 30 days | Fixed a confirmed bug without changing intended behavior |

Engineering choices count only when they change cost, data location, vendor lock-in, security, or what users experience. Read [references/what-to-record.md](references/what-to-record.md) for examples in every category.

## Rate stakes by the cost of being wrong

| Stakes | Typical decisions |
|---|---|
| High | Money movement, access and permissions, personal data, security, legal duties, safety, irreversible data loss, public or default-on behavior that affects everyone |
| Medium | Recurring behavior people notice: notifications, limits and quotas, session length, onboarding steps, sorting and ranking, visible error handling, paid integrations |
| Low | Wording, labels, layout details, and conventions that are cheap to change |

Set `reversible` to false when changing the code later would not undo the harm: data already deleted, emails already sent, money already charged, information already exposed, or data people already depend on.

## Guess the safe way, then record it anyway

When you must guess, choose the option that is cheapest to undo and least harmful if wrong:

- soft delete with a restore window over permanent deletion;
- private by default over public by default;
- opt-in over opt-out for emails, tracking, and sharing;
- a confirmation step before destructive or costly actions;
- least privilege for new roles and endpoints;
- no new personal data unless the feature needs it;
- a reminder before any automatic charge.

Ask before building only when a decision is high stakes and expensive to reverse once built, such as a multi-tenant data model, a payment flow, an identity provider, or anything that emails, charges, or deletes for real. Ask one short question with lettered options. For everything else, build with the safe guess and let the receipt carry the question.

## Record guesses in one batch

Record guesses after each unit of work, in one call:

```bash
guesswork log <<'EOF'
[
  {
    "title": "Deleted workspaces can be restored for 30 days",
    "why": "No retention rule was given, so the safer soft delete was used",
    "category": "data",
    "stakes": "high",
    "reversible": true,
    "where": ["src/workspaces/delete.ts"],
    "alternatives": ["Delete permanently right away", "Restore window of 7 days"]
  }
]
EOF
```

Write each field for the owner, not for yourself:

- **title:** what the product now does, in present tense, from the user's side, with the real numbers. Write "Password reset links expire after 1 hour", not "Chose a token expiry". Keep **one decision per guess**: if the owner could want one half and not the other, split it. "Billing is cancelled at once" and "The team is purged after 30 days" are two guesses, not one.
- **why:** one sentence on what the choice rests on.
- **category:** money, access, privacy, data, security, legal, safety, defaults, limits, notifications, ux, content, integration, performance, or other.
- **stakes** and **reversible:** from the rules above.
- **basis:** `assumed` by default. Use `inferred` when you derived it from code, docs, or conventions, `external` when a standard or vendor rule drives it, `observed` when data or tests show it, and `reported` when someone said it outside an instruction to you.
- **where:** the files that implement it, optionally with `:line`.
- **alternatives:** one to three credible options that work differently, each under about 60 characters. The CLI adds "Keep as built" as option `a`.

Never write secrets, credentials, personal data, or customer names into the ledger. It is committed with the code.

## Sweep for the decisions agents forget

Before you write the receipt, check the feature against these questions. Each one either has an answer in your code, which may be a guess to record, or is a gap worth one line in your reply:

- **Scale:** what happens with 10 times or 1,000 times the usual data, such as a large export, a long list, or a big upload?
- **Abuse:** can someone repeat it, spam it, or use it to reach other people's data?
- **Who can see or do it:** which roles, and does that match how the rest of the app works?
- **Audit:** will anyone need to know later who did it and when?
- **Failure and undo:** what happens when a step fails halfway, and can the user take it back?
- **People outside the app:** does it email, charge, or expose anything to someone who is not the current user?

Record the answers that are product decisions. Mention real gaps you did not build in one short line, so the owner can ask for them.

## End the turn with the receipt

After recording, run `guesswork receipt` and paste its output unchanged as the last part of your final message. It lists the open high and medium stakes guesses with numbered items and lettered options, so the user can answer in one line.

- Do not paraphrase or renumber it. The numbers map the user's reply to the ledger.
- When the receipt says no decisions need the user, include its single line.
- When the turn changed code but involved no product decisions, end with the line `Guesswork: no new guesses.`

Read [references/receipts-and-replies.md](references/receipts-and-replies.md) for the exact format and reply grammar.

## Apply the user's answers

Users answer with replies like `1b 2a 3c`, `all a`, or `2: restore window of 14 days`.

1. Change the code for every pick other than `a`, and for every answer in the user's own words.
2. Record the answers: `guesswork decide 1b 2a 3c`. Record an answer in the user's own words with `guesswork decide 2 --custom "Restore window of 14 days"`.
3. Numbers refer to the latest receipt. If you printed a newer receipt in between, use ids: `guesswork decide g-workspace-restore=b`.
4. Confirm in one or two sentences what changed.

Only the user's explicit answer can mark a guess decided. Silence, a thumbs-up on something else, or your own confidence is not an answer. When the user says an item can wait, leave it open. When the answer depends on how real users behave, see the section on evidence below.

## Respect decisions that already exist

Before you change behavior in existing code, run `guesswork context <files>`. Decided guesses are locked: the owner chose them.

- When the user explicitly asks to change a locked behavior, make the change and record it: `guesswork decide g-id --custom "New behavior" --note "Changed at the user's request"`.
- When a locked behavior would change as a side effect of other work, stop and ask before you change it.
- Treat guesses under test as locked until the test settles them.

## Settle questions about users with evidence

Some guesses are about what users will do: pay, adopt, understand, or trust. The owner's preference cannot settle these. Offer to test instead of deciding. Use the design-thinking skill in prototype mode to define the smallest credible test, then record it with `guesswork test g-id --plan "Fake-door button for two weeks; build if at least 5 percent of active teams click"`. Never present a planned test as evidence.

## Audit an existing codebase on request

When the user asks what their app already decided, or installs Guesswork in an existing project:

1. Run `guesswork scan` for candidate lines and `guesswork list --status all` to see what the ledger already holds.
2. Read the main flows: sign-up and sign-in, roles and sharing, billing, deletion and retention, exports, notifications, limits, and defaults.
3. Record the decisions you find with `"basis": "inferred"` and `where` entries that include line numbers. Prefer 10 to 25 sharp entries over an exhaustive list.
4. End with the receipt.

## Keep the ledger sharp

- Record one decision per guess. Logging the same title again updates the open guess instead of duplicating it.
- Three meaningful guesses beat fifteen trivial ones.
- Close non-decisions with `guesswork dismiss g-id --note "reason"`.
- Commit `.guesswork/` with the code it describes, so reviewers and later sessions share it.

## Use the other commands when they help

| Command | Use |
|---|---|
| `guesswork status` | One-line summary of open and decided guesses |
| `guesswork list --stakes high` | Filter the ledger |
| `guesswork show 2` | Full detail for a receipt item or id |
| `guesswork report` | HTML overview in `.guesswork/report.html` |
| `guesswork pr --base origin/main` | Markdown summary of the decisions on a branch |
| `guesswork check --fail-on high` | Exit with an error while high-stakes guesses are open |

Read [references/clients.md](references/clients.md) for hooks, continuous integration, and setup in other agent clients.
