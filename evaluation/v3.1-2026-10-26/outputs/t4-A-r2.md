I added a free trial to the pro plan. Teams can now try pro free for 14 days without a card, and they drop back to free when the trial ends unless they've subscribed. I checked the main flow with a quick script against the in-memory store. The app has no test suite, so I didn't add one, and nothing is committed.

**What I changed**
- `app/models.py`: `Team` has two new fields. `trial_ends_at` is set while a trial is running, and `trial_used` makes sure each team only gets one trial.
- `app/services.py`:
  - `start_pro_trial(user)` puts the team on pro for `TRIAL_DAYS = 14` and emails the person who started it.
  - `end_trial_if_expired(team)` and `expire_trials()` move teams back to free when the trial is over and email the team owner(s). If the team has a Stripe subscription by then, it stays on pro.
  - `current_plan(team_id)` returns a team's plan with any expired trial already applied.
  - There are also small helpers: `get_team`, `is_trialing`, `trial_days_left`, and `TrialError`.
- `app/api.py`: two new handlers.
  - `billing` shows the plan, whether a trial is running, its end date, days left and whether the trial can be started.
  - `start_trial` starts the trial, or returns an error message if it isn't allowed.

**Choices I made without you (all easy to change)**
- **Length:** 14 days, set in one constant.
- **No card needed:** the trial doesn't create anything in Stripe.
- **Who can start it:** only team owners and admins, only on a free team, and only once per team.
- **No change to seats:** I left the seat count alone because the code doesn't link it to the plan.

**Things to know**
- **Trials only end when something checks:** nothing runs on a schedule yet. A trial ends when `current_plan()` is called for that team or when `expire_trials()` runs. To end trials on time, run `expire_trials()` regularly (hourly is fine), or switch any place that reads `team.plan` directly to `current_plan()`. Right now nothing in the code checks the plan, but future plan checks should use `current_plan()`.
- **Billing isn't wired up yet:** there's no code for subscribing yet, so going from trial to paid is just "if the team has a Stripe subscription when the trial ends, it stays on pro". When you add checkout, you may want to clear `trial_ends_at` as soon as the team pays.
- **No reminder email:** there's no "your trial ends in 3 days" email. That would be easy to add to the same scheduled job.
