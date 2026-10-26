Users can now delete their own account. Deletion is a soft delete: the account is turned off right away and permanently removed after 30 days. Until then the user can restore it.

**What changed**
- `app/api.py`: there are two new handlers.
  - `delete_account(current_user, confirm_email)` returns `{"deleted": True, "restorable_until": ...}`, or `{"error": ...}` if the deletion is refused.
  - `restore_account(current_user)` brings the account back.
- `app/services.py`: this holds the deletion logic.
  - `request_account_deletion` only goes ahead if the user types their account email to confirm. If they are the team's only owner and other people are still on the team, it is refused.
  - It sends the user an email giving the date the account will be purged.
  - `restore_account` and `active_team_members` are new.
- **Scheduled cleanup**: `purge_deleted_accounts()` is meant to run daily. It permanently deletes accounts once their 30 days are up.
  - The deleted user's posts stay with the team, with no author shown.
  - If the user was the last person on the team, the team and all its customers and posts are deleted too.
- **Billing**: if the last person on a team deletes their account, the team's Stripe subscription is cancelled straight away, so nobody gets billed during the 30 days. Restoring the account does not restart the subscription.
- `app/models.py`: `User` has new `deleted_at` and `purge_after` fields, and `Post.author_id` can now be empty.

I ran a quick script through the main cases (refusals, restore, the solo-team case and the 30-day purge) and they behaved as intended. There's no test suite in the repo, so I didn't add one.

**Still to do before this is complete:**
- Nothing runs `purge_deleted_accounts()` yet. It needs a daily job, or nothing is ever actually deleted after the 30 days.
- The app has no login code, so nothing stops a deleted user from signing in during the 30 days.
- The existing `team_members()` still lists users who have deleted their account, so anything counting members (seats, for example) still counts them. Use `active_team_members()` where they should be left out.

**Guesswork** · 5 decisions need you (4 high stakes)

1. **When the last member of a team deletes their account, the paid subscription is cancelled immediately and the team with all its customers and posts is purged after 30 days** (high stakes · money · hard to undo)
   - **a** Keep as built
   - **b** Cancel the subscription only at purge time
   - **c** Block deletion until the team is deleted separately
2. **Posts by a deleted user stay visible to the team with no author after purge** (high stakes · privacy · hard to undo)
   - **a** Keep as built
   - **b** Delete the user's posts with their account
   - **c** Let the user choose at deletion time
3. **Deleted accounts can be restored for 30 days, then are purged permanently** (high stakes · data)
   - **a** Keep as built
   - **b** Delete permanently right away
   - **c** Restore window of 7 days
   - **d** Restore window of 14 days
4. **A sole team owner cannot delete their account until they make another member an owner** (high stakes · access)
   - **a** Keep as built
   - **b** Auto-promote the longest-tenured admin or member
   - **c** Allow it and leave the team without an owner
5. **Users confirm deletion by typing their account email, and get an email with the purge date** (medium stakes · ux)
   - **a** Keep as built
   - **b** Re-enter password instead of email
   - **c** No confirmation email

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
