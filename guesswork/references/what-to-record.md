# Decide what deserves a record

Use this reference when you are unsure whether a choice is a product decision, how to rate it, or how to write it.

## Ask three questions about each choice

1. **Can someone notice it or be affected by it?** Users, customers, admins, support staff, or the business budget.
2. **Did anyone tell you?** An instruction in this conversation, an accepted spec, or a decided guess in the ledger means it is not a guess.
3. **Could a reasonable owner want something else?** If every competent team would do the same, skip it.

Record the choice only when the answers are yes, no, and yes.

## Recognize decisions by category

| Category | Decisions that usually deserve a record |
|---|---|
| money | Trial length and what happens at its end, proration, refunds, failed-payment handling, currency, taxes, free-plan limits, who pays for seats |
| access | Who can invite, edit, delete, export, or see billing; default role for new members; sharing links; admin powers over member content |
| privacy | New personal fields, what appears in exports or logs, analytics events, retention of IP addresses, data shown to other users |
| data | Hard or soft delete, cascade rules, retention periods, what an import overwrites, backup and restore promises |
| security | Session length, password rules, lockout after failed attempts, token lifetime, rate limits, allowed origins |
| legal | Consent capture, age gates, cookie behavior, terms acceptance, data residency, accessibility commitments |
| safety | Content moderation, reporting abuse, blocking, anything that affects health or physical safety |
| defaults | Public or private by default, opt-in or opt-out, auto-renew, auto-join, auto-approve |
| limits | Upload size, page size, quotas, timeouts, maximum members, search result caps |
| notifications | Which events send email or push, frequency, digests, who receives them, unsubscribe behavior |
| ux | Confirmation steps, undo, empty and error states, what happens after a key action |
| content | Wording that promises something: delivery times, guarantees, refund language, "free forever" |
| integration | Choice of payment, email, auth, or storage vendor when it adds cost, lock-in, or data transfer |
| performance | Caching that shows stale data, sync versus async processing users can see, cost per request |

## Rate stakes from the worst realistic outcome

Ask what happens to a real person if the guess is wrong.

- **High:** someone loses money or data, sees what they should not, cannot access what they need, faces a legal or safety risk, or everyone gets a default they did not choose.
- **Medium:** many people notice and some are annoyed or confused, but nothing is lost and a fix is straightforward.
- **Low:** few people notice, and changing it later costs minutes.

Raise the rating one level when the harm is hard to detect. Set `reversible` to false when changing the code would not repair what already happened.

## Write titles the owner can judge in five seconds

| Weak | Strong |
|---|---|
| Implemented deletion | Deleting a project erases its files immediately with no restore |
| Chose session config | Sessions last 30 days and survive browser restarts |
| Added invite logic | Any member, not only admins, can invite new members |
| Set up billing | Trials convert to paid on day 14 without a reminder email |
| Notifications | Every new comment sends an email to all project members |

A strong title names the behavior, the people it affects, and the number when there is one.

## Offer alternatives that change the mechanism

Good alternatives work differently. They do not restate the same choice with a new number unless the number is the decision.

- For "Deleting a project erases its files immediately": "30-day restore window", "Require typing the project name", "Archive instead of delete".
- For "Every new comment emails all members": "Email only people mentioned", "Daily digest", "Off by default, opt in per project".

Keep each alternative under about 60 characters. Offer at most four.

## Skip the noise

Do not record:

- refactors, renames, file layout, and test structure;
- choices the codebase already makes the same way elsewhere;
- styling that follows the existing design;
- library choices with no cost, data, or security effect;
- anything the user specified, even if you implemented it differently in detail.

When you recorded something that turned out not to matter, close it with `guesswork dismiss <id> --note "reason"`.
