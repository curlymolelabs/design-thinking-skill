I added a free trial for the Pro plan. Team owners can now start a 14-day trial with no card. When it ends, the team goes back to Free and is never charged.

**What changed**
- **`app/models.py`**: `Team` has new trial fields. They record when the trial started and ends, who started it (for audit), and whether each email has been sent.
- **`app/services.py`**:
  - `start_trial(user)` starts the trial. It refuses if the user isn't the owner, if the team is already on Pro, or if the team has already had a trial.
  - `effective_plan(team)` returns the plan the team gets right now, including Pro during a trial. The trial never changes `team.plan`, so the trial ends on time even if no background job runs.
  - `trial_status(team)` gives the details to show in the UI, including days left.
  - `process_trials()` emails team owners 3 days before the trial ends and again when it ends. Each email goes out only once.
- **`app/api.py`**: two new handlers. `billing(current_user)` returns the trial and plan status, and `start_trial(current_user)` starts the trial.

I checked the full flow with a quick script, not a test suite. It covered the owner-only rule, one trial per team, the reminder on day 11, the end notice on day 14, and the team showing as Free after day 14.

**Gaps I didn't build**
- **Nothing reads the trial yet:** the code doesn't define any Pro-only features. Wherever you add Pro checks, they should use `effective_plan(team)` rather than `team.plan`.
- **Nothing runs `process_trials()` yet:** it needs a daily scheduled job, or the reminder and end emails won't be sent.
- **No upgrade from a trial to paid Pro:** there's no checkout or Stripe code in the app yet. Paying would mean setting `plan="pro"` and the subscription ID.
- **Repeat trials:** one person could get more trials by creating new teams. The limit is one per team, not one per person.

The decisions you didn't specify are listed below and recorded in `.guesswork/`.

**Guesswork** · 6 decisions need you (2 high stakes)

1. **Starting the pro trial needs no payment card** (high stakes · money)
   - **a** Keep as built
   - **b** Require a card before the trial starts
2. **When the trial ends the team returns to free; nothing is charged automatically** (high stakes · money)
   - **a** Keep as built
   - **b** Auto-convert to paid pro if a card is on file
   - **c** Keep pro for a 7-day grace period, then free
3. **Team owners get an email 3 days before the trial ends and another when it ends** (medium stakes · notifications · hard to undo)
   - **a** Keep as built
   - **b** No emails
   - **c** Also email admins
   - **d** Only the reminder, no end notice
4. **Only the team owner can start the pro trial** (medium stakes · access)
   - **a** Keep as built
   - **b** Owners and admins can start it
   - **c** Any member can start it
5. **The pro trial lasts 14 days** (medium stakes · money)
   - **a** Keep as built
   - **b** 7 days
   - **c** 30 days
6. **Each team gets one pro trial, ever, and only if not already on pro** (medium stakes · limits)
   - **a** Keep as built
   - **b** Allow a new trial after 12 months
   - **c** Let support grant extra trials

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also decided, low stakes (say so to change any): Trial teams keep their seat count; the trial only changes the effective plan.
