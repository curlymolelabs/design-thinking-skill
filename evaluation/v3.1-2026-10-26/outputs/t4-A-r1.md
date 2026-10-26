I added a 14-day free trial of the Pro plan. I checked it with a quick in-memory script: start, block a second trial, expire, downgrade. It all behaved as expected. There are no tests in the repo, so none were added, and I didn't commit anything.

**How it works**
- An owner or admin on a free team can start the trial. The team goes straight to `plan = "pro"`, so any existing `plan == "pro"` checks treat a trialing team as Pro with no other changes.
- Each team gets one trial. Teams that are already on Pro can't start one.
- When the trial ends without a paid subscription, the team goes back to `free` and the owner gets an email. A team that subscribed during the trial stays on Pro.
- Expiry is checked whenever the plan is read. There's also an `expire_trials()` function meant to run on a schedule (e.g. hourly), so teams that never come back still get downgraded.

**Changes**
- `app/models.py`: `Team` has two new fields: `trial_ends_at` and `trial_used`.
- `app/services.py`: the trial logic, with the length set by `PRO_TRIAL_DAYS = 14`. The main functions are `start_pro_trial`, `end_trial_as_paid`, `expire_trial_if_due`, `expire_trials` and `team_plan`.
- `app/api.py`: two new handlers. `plan` returns the plan, whether the team is trialing, the end date and whether a trial is available. `start_trial` starts the trial.

**Decisions you may want to change**
- **No card needed to start.** The trial is handled entirely in the app, not through Stripe's built-in trials. That makes it easier to start, but Pro won't renew on its own: the team has to subscribe before the trial ends.
- **14 days, one trial per team, owners and admins only.** Each is a small change if you want something different.

**You need to do two things to make it work in production:**
1. Wherever a team subscribes, call `services.end_trial_as_paid(team, subscription_id)`. If that isn't called, a team that pays during its trial is only safe because it has a `stripe_subscription_id`; the trial won't be closed out properly.
2. Run `services.expire_trials()` on a schedule.

Also, existing teams will need `trial_used` set to `False` when you move to a real database.
