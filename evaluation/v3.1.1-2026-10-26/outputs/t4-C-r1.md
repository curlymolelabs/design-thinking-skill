Teams on the Free plan can now start a free Pro trial.

- **`app/models.py`**: `Team` has four new fields: `trial_started_at`, `trial_ends_at`, `trial_started_by` (records who started the trial) and `trial_reminder_sent`. The stored `plan` value stays the plan the team actually pays for.
- **`app/services.py`**:
  - `start_trial(user)` checks who is asking and whether the team can still start a trial, then sets the trial dates and logs who started it.
  - `effective_plan(team)` returns `"pro"` while a trial is running. **Feature checks should use `effective_plan` instead of `team.plan`.** That's how the trial ends by itself: no expiry job is needed and nothing is charged.
  - `trial_status(team)` gives the current state for the UI.
  - `send_trial_reminders()` is meant to run once a day from your scheduler. **It isn't scheduled yet, so you need to add it.**
- **`app/api.py`**: two new handlers. `trial` returns the trial status, and `start_trial` starts one or returns a readable error.

I tested this with a quick in-memory check:
- A member is refused.
- An owner can start a trial, which shows 14 days left.
- A second trial is refused.
- The reminder goes out once, inside the 3-day window.
- After day 14 the team is back on Free.

There's a new `.guesswork/` folder with the decision ledger; commit it with the code.

**Guesswork** · 6 decisions need you (2 high stakes)

1. **Starting a trial needs no card, and when it ends the team drops back to Free with no charge** (high stakes · money)
   - **a** Keep as built
   - **b** Require a card and auto-convert to paid Pro
   - **c** Require a card, but only charge after confirmation
2. **When a trial ends, the team keeps all data created during it and only loses Pro features** (high stakes · data)
   - **a** Keep as built
   - **b** Make Pro-only data read-only after the trial
3. **Team owners get one email 3 days before the trial ends** (medium stakes · notifications · hard to undo)
   - **a** Keep as built
   - **b** No reminder email
   - **c** Email owners and admins
   - **d** Email 7 days and 1 day before
4. **Each team gets one Pro trial, ever** (medium stakes · money)
   - **a** Keep as built
   - **b** One trial per team per 12 months
   - **c** Allow repeat trials at support's discretion
5. **Only team owners and admins can start the Pro trial** (medium stakes · access)
   - **a** Keep as built
   - **b** Owners only
   - **c** Any team member
6. **The Pro trial lasts 14 days** (medium stakes · money) · **b** 7 days · **c** 30 days

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
