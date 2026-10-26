I added account deletion. I ran it against some in-memory sample data (without starting a server) and these all behaved as expected: a wrong confirmation, an owner who still has teammates, a regular member, and an owner who is the last person on their team.

**How it works**
- **`api.delete_account(current_user, confirm_email)`** in `app/api.py`: the user has to type their email address again to confirm, so the account can't be deleted by an accidental click. It returns `{"deleted": True}` on success, or `{"error": ...}` with a message the UI can show.
- **`services.delete_account(user_id)`** in `app/services.py` does the deletion. It removes the user and emails them a confirmation.

**Choices I made that you should check**
1. **Owners with teammates are blocked.** An owner who still has other members on the team can't delete their account; they're told to transfer ownership first. The app has no way to transfer ownership yet, so for now those owners can't delete their account at all. Adding a transfer feature would be a natural next step.
2. **If the last member deletes their account, the team is deleted too.** That cancels the team's Stripe subscription and permanently deletes the team's customers and posts. This stops a team with no members from staying on a paid plan, but it can't be undone.
3. **Posts stay with the team.** Posts are shared team content, so a member's posts are kept, but they're no longer linked to that user. To allow this I changed `Post.author_id` to `int | None` in `app/models.py`. Anything that shows a post's author will need to handle `None`, for example by showing "Deleted user". If you'd rather a person's posts be deleted along with their account, that's a one-line change.
4. **Deletion is immediate and permanent.** There's no grace period or undo. Team `seats` are left unchanged, since I read that number as the seats the team paid for, not the seats in use.

**Not covered**
- The app has no sessions or auth tokens yet. Once it does, they should be revoked when an account is deleted.
- I didn't add tests, because the project doesn't have a test setup.
