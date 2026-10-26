Pro now has a free trial. An owner or admin can start a 14-day Pro trial for their team with no card. When it ends, the team goes back to Free and is never charged automatically.

**What changed**
- `app/models.py`: `Team` has new trial fields: start time, end time, who started it, and when the reminder was sent.
- `app/services.py`:
  - `start_pro_trial` starts a trial. It is refused if the user isn't an owner or admin, if the team is already on Pro, or if the team has used its trial before.
  - `effective_plan` is what feature checks should use. It returns `"free"` as soon as a trial has expired, even if the daily job hasn't run yet.
  - `trial_status` reports the plan, whether a trial is running, days left and whether a trial is still available.
  - `process_trials` is meant to run once a day. It emails owners and admins 3 days before the trial ends, then moves expired teams back to Free and tells them.
- `app/api.py`: new `billing` handler (read trial status) and `start_trial` handler (start a trial).

I tested the whole flow in a quick script: a member is refused, an owner can start a trial, a second trial is refused, the reminder email goes out on schedule, and the team is back on Free after day 14. There are no automated tests in the repo yet.

**Not built, so you know they're missing**
- **Daily job:** nothing calls `process_trials` yet. It needs to be hooked up to a daily scheduler, or the emails never go out and expired teams stay on Pro in the database.
- **Pro feature gating:** the code doesn't define any Pro-only features, so nothing calls `effective_plan` yet. Whatever Pro unlocks should check it.
- **Paying for Pro:** there's no checkout or upgrade flow. A team that pays (gets a `stripe_subscription_id`) is treated as paid Pro and its trial stops applying.

**Guesswork** · 5 decisions need you (1 high stakes)

1. **The Pro trial needs no card and never charges; at the end the team drops back to Free** (high stakes · money)
   - **a** Keep as built
   - **b** Require a card and auto-convert to paid Pro
   - **c** Require a card, but ask to confirm before charging
2. **Only team owners and admins can start the Pro trial** (medium stakes · access)
   - **a** Keep as built
   - **b** Only the owner can start it
   - **c** Any member can start it
3. **The Pro trial lasts 14 days** (medium stakes · money)
   - **a** Keep as built
   - **b** 7 days
   - **c** 30 days
4. **Each team can start the Pro trial only once, ever** (medium stakes · limits)
   - **a** Keep as built
   - **b** Allow another trial after 12 months
   - **c** No limit on trials
5. **Owners and admins get a reminder email 3 days before the trial ends** (medium stakes · notifications)
   - **a** Keep as built
   - **b** Remind 7 days before
   - **c** No reminder email

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also decided, low stakes (say so to change any): Owners and admins get an email when the trial ends and the team returns to Free; Seat count stays at 5 during the trial.
