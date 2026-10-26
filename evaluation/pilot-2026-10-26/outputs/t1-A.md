Users can now delete their own account. It's a new `api.delete_account(current_user, confirm_email)` handler that calls `services.delete_account()`. I ran each case below against the in-memory store with a quick throwaway script and they all behaved as described. There are no tests in the repo, and nothing has been committed.

**How it behaves:**
- **Confirmation:** the user has to re-type their email address (case doesn't matter) before anything is deleted.
- **Owner with teammates:** this is blocked with "Transfer ownership to another member before deleting your account." Without this, the team would be left with no owner.
- **Only member of the team (owner or not):** the account and the whole team are deleted. That means its Stripe subscription is cancelled (first, so nothing is lost if that call fails) and its customers and posts are deleted.
- **Member of a team with other people:** only the user record is deleted. Their posts stay with the team and show as from a deleted user: `Post.author_id` is set to `None`, and I changed that field to `int | None`.
- A confirmation email goes to the address after deletion. The response is `{"ok": True, "deleted_user_id": ..., "team_deleted": bool}`, or `{"error": "..."}` if the deletion was refused.

**Decisions for you:**
1. **Sole-member deletion wipes the team's data.** Customers and posts are permanently removed and billing is cancelled, with no grace period or soft delete. If you'd rather keep data for a while (say 30 days) or require a separate "delete team" step, that's a small change.
2. **Posts are kept, not deleted.** I treated posts as shared team content. If you consider them personal data that should go with the account, it's a one-line switch.
3. **There's no way to transfer ownership yet.** An owner with teammates is blocked from deleting their account, and right now the only way around that is to change `role` in the database by hand. You'll probably want a small "make owner" action next.

**Changed files:**
- `app/services.py`: `AccountDeletionError` and `delete_account`
- `app/api.py`: the `delete_account` handler
- `app/models.py`: `Post.author_id` can now be `None`
