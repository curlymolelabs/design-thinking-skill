I added a free trial to the Pro plan. Teams can now try Pro without paying. When the trial ends, a team without a subscription goes back to Free. Nothing is ever charged automatically.

**What changed**
- **`app/models.py`:** `Team` now records the trial: when it ends, whether the team has used it, who started it and when, and whether the reminder email went out.
- **`app/services.py`:**
  - `start_pro_trial` puts the team on Pro for 14 days, with no card and no Stripe subscription.
  - `end_trial_if_expired` returns an expired trial to Free. A team that subscribed during its trial stays on Pro.
  - `team_plan` reports the plan and also expires a finished trial when the plan is read.
  - `process_trials` sends the reminder emails and expires trials. It's meant to run from a scheduler (hourly is fine).
- **`app/api.py`:** two new handlers. `plan` returns the plan status and `start_trial` starts the trial; it returns an error message when the trial isn't allowed.

I ran a quick script against the in-memory store and it all behaved as intended:
- A member was refused.
- An owner started the trial.
- The reminder went out once, at 3 days before the end.
- The team dropped to Free after day 14.
- Starting a second trial was refused.

There's no test suite, so I didn't add one.

**Not built yet; tell me if you want any of these**
- **Nothing is limited to Pro.** "pro" is only a label in this codebase, so the trial doesn't unlock any features yet.
- **No upgrade or checkout flow.** A trial only stays on Pro if something else sets `stripe_subscription_id`.
- **Nothing runs `process_trials` yet.** A scheduler needs to call it, or no reminder emails go out. Expired trials still drop to Free when the plan is read.
- **No stored audit log.** Trial start and expiry are only printed as `AUDIT` lines.

**Guesswork** · 7 decisions need you (2 high stakes)

1. **Starting the pro trial needs no card** (high stakes · money)
   - **a** Keep as built
   - **b** Require a card to start the trial
2. **When the trial ends without a subscription, the team drops back to free and is never charged automatically** (high stakes · money)
   - **a** Keep as built
   - **b** Auto-convert to paid pro at trial end
   - **c** Charge only after the owner confirms
3. **Owners and admins get one reminder email 3 days before the trial ends** (medium stakes · notifications · hard to undo)
   - **a** Keep as built
   - **b** No reminder email
   - **c** Also email when the trial has ended
   - **d** Email the owner only
4. **Only team owners and admins can start the pro trial** (medium stakes · access)
   - **a** Keep as built
   - **b** Only the owner can start it
   - **c** Any member can start it
5. **The pro trial lasts 14 days** (medium stakes · money)
   - **a** Keep as built
   - **b** 7 days
   - **c** 30 days
6. **When a trial ends, the team keeps all its data and only the plan changes to free** (medium stakes · data)
   - **a** Keep as built
   - **b** Make over-limit data read-only until they subscribe
7. **Each team can use the pro trial once, ever** (medium stakes · limits)
   - **a** Keep as built
   - **b** Allow a new trial after 12 months
   - **c** Let admins grant extra trials manually

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
