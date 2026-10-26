# Show receipts and apply replies

Use this reference when you present open guesses to the user or interpret their answer.

## Print the receipt as the last part of the message

`guesswork receipt` prints Markdown like this:

```text
**Guesswork** · 3 decisions need you (2 high stakes)

1. **Deleted workspaces can be restored for 30 days** (high stakes · data)
   - **a** Keep as built
   - **b** Delete permanently right away
   - **c** Restore window of 7 days
2. **Trials convert to paid on day 14 without a reminder email** (high stakes · money)
   - **a** Keep as built
   - **b** Email a reminder 3 days before the trial ends
3. **Any member can invite new members** (medium stakes · access)
   - **a** Keep as built
   - **b** Only admins can invite

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
```

Paste it unchanged. The numbers are stored with the receipt, so `guesswork decide 1b` resolves to the right guess even after the conversation is compacted.

- The receipt shows at most five items by default, ranked by stakes, reversibility, and category. Raise the limit with `--limit`.
- Up to three low-stakes guesses are named in one closing line; more than three appear as a count. `guesswork receipt --all` lists them as numbered items.
- Printing a new receipt replaces the stored numbering. Use ids when you refer to an older receipt.

## Read the reply grammar

| Reply | Meaning | What you do |
|---|---|---|
| `1b 2a 3c` | Pick per item | Change the code for `b` and `c`, then `guesswork decide 1b 2a 3c` |
| `all a`, `keep all` | Keep everything as built | `guesswork decide --all a` |
| `2: restore window of 14 days` | The user's own answer | Implement it, then `guesswork decide 2 --custom "Restore window of 14 days"` |
| `3 later`, `skip 3` | Not now | Leave item 3 open |
| `3 test` | Needs evidence | Plan a test with the design-thinking skill, then `guesswork test 3 --plan "..."` |
| `why 2?` | Wants detail | Run `guesswork show 2` and explain the trade-off in two or three sentences |

Mixed replies are normal: `1b, 2: weekly digest instead, 3a`. Handle each part.

When the Guesswork plugin runs in Claude Code, a reply made only of picks arrives with a note that maps each pick to its guess id and option.

## Apply answers in the right order

1. Change the code so it matches every answer that is not `a`.
2. Run the tests that cover the changed behavior.
3. Record the answers with `guesswork decide`.
4. Confirm briefly: "Workspaces now delete permanently, and trials send a reminder 3 days before charging."

Recording before the code matches would make the ledger claim something the product does not do.

## Never answer for the user

- Do not mark a guess decided because the user seemed happy, said "thanks", or answered a different question.
- Do not pick an option because you are confident it is right. Recommend it in one sentence and let the user pick.
- Do not drop items from the receipt to keep it short. Raise the limit or tell the user how many more are waiting.
