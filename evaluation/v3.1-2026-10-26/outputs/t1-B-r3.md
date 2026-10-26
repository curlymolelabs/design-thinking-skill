Users can now delete their own account. It's a soft delete: the account is turned off right away and can be restored for 30 days. After that it is erased for good.

**What I changed**
- `app/api.py`: new `delete_account(current_user, confirm_email)` handler (`DELETE /account`). The user has to type their email address again to confirm. It returns either an error message to show the user, or `{"deleted": true, "restorable_until": ...}`.
- `app/services.py`:
  - `delete_account` checks the confirmation, sets `deleted_at` and emails the user the date their restore window ends. It does not touch the team, its customers or its billing.
  - A team's only owner is blocked from deleting their account until they make another member an owner. Otherwise the team would be left with no owner and its paid subscription still running.
  - `restore_account` undoes a deletion within the 30 days. Only support can call it.
  - `purge_deleted_accounts` erases accounts deleted more than 30 days ago.
  - `author_name` shows posts by deleted users as "Deleted user". The posts themselves stay with the team.
  - `team_members` now hides deleted accounts.
- `app/models.py`: `User` has a new `deleted_at` field and an `is_active` property.

I ran a quick script through every path: a sole owner is blocked, a wrong confirmation is rejected, and delete, restore and erase after 30 days all worked.

**Not built yet**
- **Sign-in and sessions:** this code has no sign-in, so a deleted user isn't locked out yet. Wherever you sign users in or load the current user, reject them when `user.is_active` is false.
- **The 30-day erase:** `purge_deleted_accounts()` has to be scheduled as a daily job, or accounts are never actually erased.
- **Audit log:** nothing records who deleted an account or when, beyond the `deleted_at` timestamp.

My guesses are recorded in `.guesswork/`; commit that folder with the code.

**Guesswork** · 6 decisions need you (2 high stakes)

1. **Deleted accounts can be restored for 30 days, then are erased permanently** (high stakes · data)
   - **a** Keep as built
   - **b** Erase the account immediately
   - **c** Restore window of 7 days
   - **d** Restore window of 90 days
2. **A team's only owner cannot delete their account until another member is made owner** (high stakes · access)
   - **a** Keep as built
   - **b** Also close the team and cancel its subscription
   - **c** Allow it and leave the team without an owner
3. **Users get an email confirming deletion with the date restore ends** (medium stakes · notifications · hard to undo)
   - **a** Keep as built
   - **b** Send no email
4. **Posts a deleted user wrote stay with the team, shown as by "Deleted user"** (medium stakes · privacy)
   - **a** Keep as built
   - **b** Delete the user's posts along with the account
   - **c** Keep showing the author's real name
5. **Users confirm deletion by retyping their email address** (medium stakes · security)
   - **a** Keep as built
   - **b** Require the current password
   - **c** Confirm through a link sent by email
6. **Only support can restore a deleted account during the window** (medium stakes · ux)
   - **a** Keep as built
   - **b** Users restore it themselves by signing in again

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
