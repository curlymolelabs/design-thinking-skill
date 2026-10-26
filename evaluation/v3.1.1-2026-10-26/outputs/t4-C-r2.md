I added a free trial to the Pro plan. Nothing in Stripe or billing changes yet, because the trial collects no card.

- **`app/models.py`**: `Team` now tracks the trial with `trial_ends_at`, `trial_used`, `trial_started_by` and `trial_reminder_sent`.
- **`app/services.py`**:
  - `start_pro_trial(user)` starts the trial and rejects anyone who isn't allowed.
  - `is_trialing(team)` says whether a team is on a trial right now.
  - `end_trial_on_subscribe(team)` keeps a team on Pro once it pays.
  - `process_trials()` sends the reminder email and moves expired, unpaid trials back to Free. Nothing calls it yet: you need to run it on a schedule, for example hourly. Until you do, trials won't expire and no emails go out.
- **`app/api.py`**: two new handlers. `plan` shows the plan, whether the team is on a trial and when it ends. `start_trial` starts one.

I ran a quick script through the whole flow: a member gets refused, an owner starts a trial, a second attempt is blocked, the reminder email goes out, and the team is back on Free after the trial ends. There are no automated tests in the repo, so I didn't add any.

I recorded the choices I made in `.guesswork/`, which should be committed with the code. Item 1 matters most: the trial never charges anyone automatically.

**Guesswork** · 6 decisions need you (1 high stakes)

1. **Pro trial needs no card and never auto-charges; unpaid teams return to Free when it ends** (high stakes · money · hard to undo)
   - **a** Keep as built
   - **b** Require a card and auto-convert to paid at trial end
2. **Owners and admins get an email 3 days before the trial ends and another when it ends** (medium stakes · notifications · hard to undo)
   - **a** Keep as built
   - **b** Email only the owner
   - **c** No emails; show status in the app only
3. **Each team can start a Pro trial only once, ever** (medium stakes · money)
   - **a** Keep as built
   - **b** Allow a new trial after 12 months
4. **Only team owners and admins can start the Pro trial** (medium stakes · access)
   - **a** Keep as built
   - **b** Only owners can start it
   - **c** Any member can start it
5. **Pro trial lasts 14 days** (medium stakes · money)
   - **a** Keep as built
   - **b** 7 days
   - **c** 30 days
6. **Team data is kept unchanged when a trial ends and the team drops to Free** (medium stakes · data) · **b** Lock Pro-only data read-only until upgrade

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
