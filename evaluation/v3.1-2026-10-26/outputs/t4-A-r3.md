I added a free trial of the Pro plan. Teams can now start a 14-day trial with no card required. I ran a quick script against the in-memory store and the whole flow behaved as expected. I didn't start a server and there's no test suite yet.

**How it works:**
- **Who can start it:** a team owner or admin. Each team gets one trial, and only while it's on Free.
- **During the trial:** the team counts as Pro. Owners and admins get an email when the trial starts, with the end date.
- **When it ends:** the team goes back to Free. Nothing needs to run for this, because the app checks the end date each time it looks up the plan. The trial can't be restarted, and nothing is charged.

**Changes:**
- `app/models.py`: added `trial_started_at` and `trial_ends_at` to `Team`.
- `app/services.py`: added `start_pro_trial(user)` and `effective_plan(team)`, which returns "pro" for paid or trialing teams. Also added `is_on_trial` and `trial_days_left`, and a `PRO_TRIAL_DAYS = 14` setting.
- `app/api.py`: added two handlers:
  - `plan(current_user)` shows the plan, trial status, days left and whether a trial is still available.
  - `start_trial(current_user)` returns a 403 error for non-admins and a 409 error if the team is already Pro or has used its trial.

**Choices I made that you may want to change:**
- **14 days, no card, back to Free at the end.** A trial that turns into a paid plan automatically needs a card up front and Stripe trial handling, and that would be a bigger change.
- **One trial per team, not per user.**
- **Seats don't change during the trial.** Nothing in the app sets a different seat count for Pro, so I didn't guess one.

**One thing to know:** nothing in the app checks the plan yet, so there are no Pro features for a trial to unlock. When you add them, check `services.effective_plan(team) == "pro"` rather than `team.plan`. Otherwise trialing teams won't get them and expired trials will keep them.

**Possible next steps:** a "your trial ends in 3 days" reminder email, and a path from the trial to paid Pro through Stripe.
