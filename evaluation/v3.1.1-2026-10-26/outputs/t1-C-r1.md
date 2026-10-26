Users can now delete their own account. Deleting is a soft delete first, so they can undo it during a restore window before the account is removed for good.

**What's in place**
- `api.delete_account(current_user, confirm_email)` deletes the account, and `api.restore_account(current_user)` undoes it. Signed-in handlers (`me`, `customers`) return an `account_deleted` error with the restore deadline for a deleted account.
- `services.delete_account`, `restore_account` and `purge_deleted_accounts` are in `app/services.py`. `User` has a new `deleted_at` field, and `Post.author_id` can now be `None`.
- `active_team_members()` leaves out deleted users.

I ran delete, restore, the owner and subscription blocks, and the purge in a quick script. They behaved as expected. There's no test suite in the repo yet, and I didn't run a server.

**Two things you need to act on**
- **The purge job isn't scheduled.** Nothing calls `purge_deleted_accounts()` yet, so deleted accounts are never permanently removed until a daily job runs it.
- **Owners with teammates can't delete their account.** They're told to transfer ownership first, but the app has no way to transfer ownership. Until one exists, they have to go through support.

The ledger is in `.guesswork/`; commit it with the code.

**Guesswork** · 6 decisions need you (4 high stakes)

1. **A deleted user's posts stay with the team, unattributed, after permanent removal** (high stakes · privacy · hard to undo)
   - **a** Keep as built
   - **b** Delete the user's posts too
   - **c** Keep posts showing the user's name
2. **Deleted accounts can be restored for 30 days, then are permanently removed** (high stakes · data)
   - **a** Keep as built
   - **b** Delete permanently right away
   - **c** Restore window of 7 days
3. **A sole owner must cancel the paid subscription before deleting their account** (high stakes · money)
   - **a** Keep as built
   - **b** Cancel the subscription automatically on deletion
   - **c** Cancel it when the account is purged
4. **Team owners cannot delete their account while other members remain** (high stakes · access)
   - **a** Keep as built
   - **b** Promote another member to owner automatically
   - **c** Delete the whole team with the owner
5. **Users get an email confirming deletion with their restore deadline** (medium stakes · notifications · hard to undo)
   - **a** Keep as built
   - **b** Send no email
6. **Deleted users leave the member list and free their seat immediately** (medium stakes · access) · **b** Keep them listed and seated until purged

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also decided, low stakes (say so to change any): Deleting an account requires typing your email address to confirm.
