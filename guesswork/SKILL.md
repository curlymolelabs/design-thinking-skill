---
name: guesswork
description: Record the product decisions you make without explicit instructions (defaults, limits, permissions, data handling, money, notifications, user-facing promises) in a .guesswork/ ledger, end the turn with a short receipt the user answers in one line, and respect the decisions they already made. Use whenever you build or change user-facing behavior that the user did not fully specify, when the user answers a Guesswork receipt with replies like "1b 2a", or when asked what product decisions a codebase already makes. Do not use for pure refactors, styling, or work the user specified completely.
license: MIT
metadata:
  version: "3.1.1"
  short-description: "Review the decisions your agent made, not just the diff"
---

# Guesswork

Every request leaves gaps, and you fill them with guesses. Most are harmless. A few decide who gets charged, who sees whose data, and what cannot be undone. Guess safely, record each guess, show the risky ones briefly, and respect the answers.

Run `guesswork` if the plugin installed it. Otherwise run `python3 <this skill's folder>/scripts/guesswork.py` (Python 3.9 or newer, no packages). Without Python, write ledger files as described in [references/ledger-format.md](references/ledger-format.md).

## Record a guess when all three are true

1. You chose behavior that users, customers, or the business can notice.
2. Nobody specified it, and the codebase does not already do the same elsewhere.
3. A reasonable product owner could want it differently.

Record "reset links expire after 1 hour", "deleting a comment hides it", "exports include customer emails". Do not record library choices, refactors, lint fixes, matching existing styles, or anything the user specified. Engineering choices count only when they change cost, data location, security, or what users experience. Examples by category: [references/what-to-record.md](references/what-to-record.md).

**Stakes** follow the cost of being wrong. High: money, access, personal data, security, legal duties, irreversible loss, default-on behavior that affects everyone. Medium: notifications, limits, session length, sorting, visible errors. Low: wording, labels, layout. Set `reversible` to false when changing the code later would not undo the harm, such as data deleted, emails sent, money charged, or information exposed.

## Guess the safe way

Prefer what is cheapest to undo: soft delete with a restore window, private by default, opt-in for emails and sharing, confirmation before destructive or costly actions, least privilege, no new personal data, and a reminder before any charge.

Ask before building only when a decision is high stakes and expensive to reverse once built, such as a payment flow, a multi-tenant data model, or anything that emails, charges, or deletes for real. Ask one short question with lettered options. Otherwise build with the safe guess and let the receipt ask.

## Check what agents forget, when the feature touches money, personal data, access, deletion, or people outside the app

- **Scale:** what happens with 1,000 times the usual data?
- **Abuse:** can someone repeat it, spam it, or reach other people's data?
- **Who can see or do it,** and does that match the rest of the app?
- **Audit:** will anyone need to know who did it and when?
- **Failure and undo:** what if a step fails halfway, and can the user take it back?
- **People outside the app:** does it email, charge, or expose anything to them?

Record the answers that are product decisions. Skip this check for features that touch none of those areas.

## Record and show the receipt in one call

After the work, record every guess in one batch. The `--receipt` flag prints the receipt right after:

```bash
guesswork log --receipt <<'EOF'
[{"title": "Deleted workspaces can be restored for 30 days", "why": "No retention rule was given", "category": "data", "stakes": "high", "reversible": true, "where": ["src/workspaces/delete.ts"], "alternatives": ["Delete permanently right away", "Restore window of 7 days"]}]
EOF
```

- **title:** what the product now does, from the user's side, with real numbers. Write "Password reset links expire after 1 hour", not "Chose a token expiry".
- **One decision per guess.** Test each alternative: if it would change only part of the title, split the guess. "Photos must be JPEG or PNG" and "Photos can be at most 2 MB" are two guesses. When `log` prints `split:`, log the parts separately and dismiss the original with `guesswork dismiss <id> --note "split"`.
- **why:** one sentence. **category:** money, access, privacy, data, security, legal, safety, defaults, limits, notifications, ux, content, integration, performance, or other.
- **alternatives:** one to three credible options under about 60 characters. Option `a` is always "Keep as built".
- **basis:** `assumed` by default. Use `inferred` when derived from code or docs, and `external` when a standard or vendor rule drives it.
- Never write secrets, credentials, or personal data into the ledger. It is committed with the code.

## End the turn with the receipt

Paste the receipt unchanged as the last part of your final message. Do not renumber it, paraphrase it, or repeat its decisions in your own words above it; summarize what you built in a few lines instead. When the receipt says no decisions need the user, include its single line. When the turn changed code with no product decisions, end with `Guesswork: no new guesses.` Format and reply grammar: [references/receipts-and-replies.md](references/receipts-and-replies.md).

## Apply the user's answers

Users reply like `1b 2a 3c`, `all a`, or `2: restore window of 14 days`.

1. Change the code for every pick other than `a`, and for every answer in the user's own words.
2. Record the answers: `guesswork decide 1b 2a 3c`, or `guesswork decide 2 --custom "Restore window of 14 days"`. Numbers refer to the latest receipt.
3. Confirm in one or two sentences what changed.

Only an explicit answer from the user marks a guess decided. Silence, thanks, or your own confidence is not an answer. When an answer depends on how real users behave, offer a test instead: `guesswork test <id> --plan "..."`, planned with the design-thinking skill.

## Respect decisions that already exist

Before changing behavior in existing code, run `guesswork context <files>`. Decided guesses are locked. When the user asks to change one, do it and record it with `guesswork decide <id> --custom "New behavior" --note "Changed at the user's request"`. When a locked behavior would change as a side effect, stop and ask first.

To audit an existing codebase, set up other clients, or use the remaining commands, read [references/clients.md](references/clients.md).
