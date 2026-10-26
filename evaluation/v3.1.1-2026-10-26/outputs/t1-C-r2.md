Users can now delete their own account. I tested the main paths with a quick in-memory script; there's no test suite in the repo.

- **`api.delete_account(current_user, confirm_email)`** turns the account off straight away and returns the date it will be permanently deleted. **`api.restore_account(current_user)`** undoes the deletion if it's before that date.
- **Access while pending:** `me()` now shows when a deletion is pending, and `customers()` refuses to return data for an account in that state.
- **Permanent removal:** `services.purge_deleted_accounts()` removes accounts once their restore window has passed. Nothing calls it yet, so you'll need to run it from a daily scheduled job.
- **Audit log:** every step is written to a new `DB["audit_log"]`. It stores only ids and timestamps, no emails or names.
- **Model changes:** `User` and `Team` have a new `deleted_at` field, and `Post.author_id` can now be `None`.
- **Changed existing behaviour:** `team_members()` now leaves out accounts that are pending deletion.
- **New folder:** the decisions below are recorded in `.guesswork/`, which should be committed with the code.

Files changed: `app/models.py`, `app/services.py`, `app/api.py`.

**Guesswork** · 8 decisions need you (4 high stakes)

1. **When the last team member deletes their account, the paid subscription is cancelled immediately** (high stakes · money · hard to undo)
   - **a** Keep as built
   - **b** Cancel only when the account is purged after 30 days
   - **c** Block deletion until they cancel billing themselves
2. **When the last team member deletes their account, the team's customers and posts are deleted with it after 30 days** (high stakes · data · hard to undo)
   - **a** Keep as built
   - **b** Keep orphaned team data until support removes it
   - **c** Offer a data export before deletion
3. **Deleted accounts can be restored for 30 days, then are permanently purged** (high stakes · data)
   - **a** Keep as built
   - **b** Delete permanently right away
   - **c** Restore window of 7 days
4. **A team's only owner must make someone else owner before deleting their account** (high stakes · access)
   - **a** Keep as built
   - **b** Promote the longest-standing admin automatically
   - **c** Let them delete the whole team instead
5. **A deleted user's posts stay on the team with no author shown** (medium stakes · privacy · hard to undo)
   - **a** Keep as built
   - **b** Delete the user's posts when the account is purged
   - **c** Keep the author's name on their posts
6. **Users get an email when deletion is scheduled, with the date it becomes permanent; teammates are not notified** (medium stakes · notifications · hard to undo) · **b** Also email the team's owners and admins · **c** Send no email
7. **Accounts pending deletion lose access to team data immediately and leave the member list** (medium stakes · access) · **b** Keep access until the account is purged
8. **Users must retype their email to confirm account deletion** (medium stakes · ux) · **b** Require their password instead · **c** A simple yes/no confirmation

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
