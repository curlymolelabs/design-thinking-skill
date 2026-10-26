Users can now delete their own account.

- **`api.delete_account(current_user, confirm_email)`** deletes the signed-in user's account. They have to type their email address to confirm. On success it returns the date until which the account can still be restored. On failure it returns an error message.
- **`services.delete_account`** deactivates the account right away by setting `User.deleted_at`, which hides the user from `team_members`. It then records an audit entry and emails the user the purge date.
- **`services.restore_account(user_id)`** undoes a deletion while it's still inside the restore window.
- **`services.purge_deleted_accounts()`** permanently removes accounts whose window has passed. Their posts stay with the team, and the post's `author_id` is set to `None`. This function needs to run on a daily schedule, and nothing calls it yet.
- **Model changes:** `User.deleted_at`, `Post.author_id` can now be `None`, and there's a new `DB["audit_log"]`.

I checked the main paths with a quick script: owner blocked, wrong email, delete, restore, and purge. The app has no login code yet, so whatever handles sign-in must reject users whose `deleted_at` is set. Changed files: `app/models.py`, `app/services.py`, `app/api.py`. The choices below are also recorded in `.guesswork/`.

**Guesswork** · 6 decisions need you (3 high stakes)

1. **Posts by a deleted user stay with the team, shown as by a deleted user** (high stakes · data · hard to undo)
   - **a** Keep as built
   - **b** Delete the user's posts along with the account
   - **c** Keep posts with the author's name still shown
2. **Deleted accounts can be restored for 30 days before being purged** (high stakes · data)
   - **a** Keep as built
   - **b** Delete permanently right away
   - **c** Restore window of 7 days
3. **Team owners cannot delete their account until they transfer ownership** (high stakes · access)
   - **a** Keep as built
   - **b** Sole owner deletes account, team and subscription
   - **c** Ownership passes to the oldest admin automatically
4. **Users get an email confirming deletion and the purge date** (medium stakes · notifications · hard to undo)
   - **a** Keep as built
   - **b** Send no email
   - **c** Also email team owners and admins
5. **Account deletions, restores and purges are kept in an audit log by user id** (medium stakes · privacy)
   - **a** Keep as built
   - **b** Keep no audit record
   - **c** Also log the email address
6. **Users must re-type their email address to confirm deletion** (medium stakes · ux) · **b** Require the current password instead · **c** A simple yes/no confirmation

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also decided, low stakes (say so to change any): Restoring a deleted account goes through support.
