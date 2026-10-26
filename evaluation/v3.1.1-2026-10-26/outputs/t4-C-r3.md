I added a free trial of the Pro plan. Owners and admins can start it from the new `start_trial` handler, and it doesn't touch Stripe. A quick script run worked through the main cases (who can start it, the reminder email, and the team going back to Free). There are no automated tests for it.

**One step you need to do:** schedule `services.run_daily_trial_jobs()` to run once a day. Until it runs, no reminder emails go out and expired trials still show `plan == "pro"` on the team.

- **`app/models.py`:** `Team` has new fields that record when the trial started and ends, who started it, and whether the reminder was sent.
- **`app/services.py`:**
  - `start_pro_trial` checks the user's role and whether the team has already used its trial.
  - `is_trialing` / `has_pro` tell you whether a team currently has Pro. `has_pro` counts an expired trial as Free even if the daily job hasn't run yet. Nothing in the app checks for Pro features yet, so when you add those checks, use `has_pro` rather than reading `team.plan` directly.
  - `send_trial_reminders` and `expire_trials` are the daily jobs. A team that moves back to Free keeps all its data.
- **`app/api.py`:** new `plan` handler (current plan, whether the team is trialing, end date, whether a trial is still available) and `start_trial` handler.

My choices are recorded in `.guesswork/`; commit that folder with the code.

**Guesswork** · 5 decisions need you (1 high stakes)

1. **Pro trial needs no card and never charges; the team returns to Free when it ends** (high stakes · money)
   - **a** Keep as built
   - **b** Require a card and auto-convert to paid Pro
   - **c** Require a card but ask before converting
2. **Owners and admins get one email 3 days before the trial ends** (medium stakes · notifications · hard to undo)
   - **a** Keep as built
   - **b** No reminder email
   - **c** Remind 7 days and 1 day before
3. **Only team owners and admins can start a Pro trial** (medium stakes · access)
   - **a** Keep as built
   - **b** Only the team owner
   - **c** Any team member
4. **The Pro trial lasts 14 days** (medium stakes · money)
   - **a** Keep as built
   - **b** 7 days
   - **c** 30 days
5. **Each team can start a Pro trial only once, ever** (medium stakes · limits)
   - **a** Keep as built
   - **b** Allow a new trial after 12 months
   - **c** Let support grant extra trials

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also decided, low stakes (say so to change any): Teams that already paid for Pro and cancelled can still take a trial.
