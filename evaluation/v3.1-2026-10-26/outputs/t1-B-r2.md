Users can now delete their own account. The account is soft-deleted and can be restored for 30 days. After that, the person's name and email are removed for good.

**How it works**
- `api.delete_account(current_user, confirm_email)`: the user retypes their email to confirm. The account is marked deleted, it stops counting as a team member or seat, and the user gets an email saying when the restore window closes.
- `api.restore_account(current_user)`: undoes the deletion while the 30 days are still open.
- `services.purge_deleted_accounts()`: run this once a day. It anonymizes accounts whose 30 days have passed. Their posts stay on the team, credited to "Deleted user".
- Team owners can't delete their account. This keeps a team from being left without an owner and means this feature never touches Stripe billing.

The changes are in `app/models.py` (a `deleted_at` / `purged` field on `User`), `app/services.py` and `app/api.py`. I ran a quick script covering the owner block, a wrong confirmation, delete, restore, purge, and restore after the window; all behaved as expected. There's no test suite in the repo, so I didn't add one.

**Not built yet, worth knowing:**
- **Deleted users can still sign in.** The repo has no sign-in or session code, so nothing stops this yet. Wherever you check the current user, reject users where `user.is_deleted` is true.
- **Owners have no way out.** There's no ownership-transfer feature, so owners can't delete their account at all for now.
- **Purging needs a scheduler.** `purge_deleted_accounts()` only runs if a daily job calls it.
- **No audit log.** Nothing records who deleted an account or when, apart from `deleted_at` on the user.

**Guesswork** · 6 decisions need you (3 high stakes)

1. **A deleted user's posts stay on the team, shown as written by "Deleted user"** (high stakes · privacy · hard to undo)
   - **a** Keep as built
   - **b** Delete the user's posts when the account is purged
   - **c** Keep posts with the author's original name
2. **Deleted accounts can be restored for 30 days before personal details are removed** (high stakes · data)
   - **a** Keep as built
   - **b** Delete permanently right away
   - **c** Restore window of 7 days
   - **d** Restore window of 90 days
3. **Team owners cannot delete their account until they transfer ownership** (high stakes · access)
   - **a** Keep as built
   - **b** Sole owner deletion also closes team and cancels billing
   - **c** Allow it and promote the longest-serving admin
4. **A deleted account frees its team seat immediately, not after the 30 days** (medium stakes · limits)
   - **a** Keep as built
   - **b** Hold the seat until the account is purged
5. **Users confirm deletion by retyping their email address** (medium stakes · ux)
   - **a** Keep as built
   - **b** Require the current password instead
   - **c** A simple yes/no confirmation

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also: 1 more decision waiting (`guesswork receipt --limit 20`).
