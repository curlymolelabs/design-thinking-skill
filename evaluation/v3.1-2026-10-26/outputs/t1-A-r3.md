Users can now delete their own account. The new handler is `api.delete_account(current_user, confirm_email)` and the logic is in `services.delete_account`.

**How it works:**
- **Confirmation:** the user has to re-type their email address. Case and surrounding spaces don't matter.
- **Their posts stay with the team.** The author is cleared (`Post.author_id` becomes `None`, so I changed that field in `models.py` to allow `None`). Team customers aren't touched.
- **The team's only owner can't delete their account while other members remain.** They get an error asking them to make someone else an owner first, so the team always has an owner.
- **If they're the last member of the team, the whole team is deleted:** its Stripe subscription is cancelled, and its customers and posts are removed. The subscription is cancelled before anything is deleted, so if Stripe fails nothing has been lost and they can try again.
- **They get an email** saying the account was deleted.
- **Return values:** success returns `{"ok": True}`; a refusal returns `{"ok": False, "error": "..."}`.

I checked each case by hand with a short script against the in-memory store. The repo has no test suite, so I didn't add one.

**Decisions for you to check:**
1. **Deleting a team when its last member leaves is permanent.** Its customer records go with it. That stops billing and avoids keeping orphaned personal data, but there's no grace period or undo. If you'd rather use a soft delete (e.g. a 30-day window), that's a small change.
2. **Keeping posts with the team instead of deleting them.** I treated posts as shared team content. If you see them as personal data the user should be able to remove, they can be deleted with the account instead.
3. **Logging the user out isn't handled.** The app has no session or auth layer, so whatever handles authentication will need to drop the user's session after a successful delete.
4. **Seat count is unchanged.** `Team.seats` stays the same when a member leaves, because it looked like a billing setting rather than a headcount.

Changed files: `app/services.py`, `app/api.py`, `app/models.py`. Nothing is committed.
