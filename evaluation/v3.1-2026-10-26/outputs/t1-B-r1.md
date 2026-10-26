Users can now delete their own account. The deletion takes effect right away and can be undone for 30 days.

**How it works**
- **`api.delete_account(current_user, confirm_email)`** (`app/api.py`) is the new handler. The user retypes their email to confirm. If it works, it returns the date until which the account can still be restored. If not, it returns a 400 with a readable message.
- **`services.delete_account`** (`app/services.py`) disables the account at once. From then on, `me` and `customers` return 403 `account_deleted` for that user. It also emails the user the date the deletion becomes permanent.
- **`services.restore_account`** reverses a deletion during the 30 days.
- **`services.purge_deleted_accounts`** handles accounts past 30 days. It replaces their name and email with "Deleted user" and a placeholder address. Their posts stay with the team.
- **`User`** (`app/models.py`) gains `deleted_at`, `purged_at` and `is_active`. There is also a new `active_team_members()` that leaves deleted users out. `team_members()` itself is unchanged.
- **Team owners are blocked** and told to transfer ownership first. That way a team is never left without an owner, and its Stripe billing is never changed by a side effect.

I ran a quick script against the in-memory store covering: the wrong-email check, the owner block, deleting, being blocked afterwards, restoring, purging (nothing at day 29, erased at day 31), and refusing a restore after the purge. All of these behaved correctly. There's no test suite in the repo, so I didn't add one.

**Not built yet:**
- **Nothing runs `purge_deleted_accounts` yet.** It needs a daily scheduled job, or personal data is never erased.
- **There's no ownership-transfer feature.** Until one exists, an owner can't delete their account at all.
- **There's no audit log** of who deleted or restored an account, or when.

The product decisions I made on my own are recorded in `.guesswork/`. These are the ones I need you to answer:

**Guesswork** · 6 decisions need you (3 high stakes)

1. **A deleted user's posts stay with the team, shown as "Deleted user"** (high stakes · privacy · hard to undo)
   - **a** Keep as built
   - **b** Delete the user's posts when the account is purged
   - **c** Let the user choose to delete posts too
2. **Team owners cannot delete their account until they transfer ownership** (high stakes · access)
   - **a** Keep as built
   - **b** Sole owner's deletion also cancels billing and team
   - **c** Promote the oldest admin to owner automatically
3. **Deleted accounts can be restored for 30 days before name and email are erased** (high stakes · data)
   - **a** Keep as built
   - **b** Erase personal data immediately
   - **c** Restore window of 7 days
   - **d** Restore window of 14 days
4. **Users get an email confirming deletion with the permanent-deletion date** (medium stakes · notifications · hard to undo)
   - **a** Keep as built
   - **b** Send no email
   - **c** Also notify the team owner
5. **Deleting an account is confirmed by retyping the account email** (medium stakes · security)
   - **a** Keep as built
   - **b** Require a re-login or emailed code first
   - **c** Single confirm button, no typing
6. **Restoring a deleted account within 30 days goes through support** (medium stakes · ux)
   - **a** Keep as built
   - **b** Signing in again during the window restores it

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
