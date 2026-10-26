Users can now delete their own account. I tested it against the in-memory store with a few made-up users, but there are no automated tests and nothing is committed.

**How it works**
- `api.delete_account(current_user, confirm_email)` is the new handler. The user has to type their email address again to confirm. If it doesn't match, the account is left alone and an error is returned.
- `services.delete_account(user_id)` removes the user and sends them an email saying the account was deleted.
- **Their posts stay with the team** but no longer show who wrote them (`author_id` is set to `None`), so teammates keep the content. To allow this, `Post.author_id` in `app/models.py` can now be `None`.
- **The last owner of a team can't delete their account while other people are still on the team.** They get an error asking them to make someone else an owner first, so the team always has an owner.
- **If the user is the only person on their team, the whole team is deleted with them.** That means the team's Stripe subscription is cancelled and its customers and posts are deleted too.

**Please confirm these choices:**
1. **Deleting a one-person team is permanent and takes its customer records with it.** Nothing can be recovered afterwards. I did it this way so we aren't keeping customer contact details or billing a team nobody can use any more. If you'd rather keep a backup period, a soft delete (mark the account deleted and purge it after 30 days) would be a small change.
2. **Keeping posts without an author** is my guess at what teams would want. If deleting an account should also delete that person's posts (for example, if you treat posts as personal data), it's a one-line change.

Files changed: `app/api.py`, `app/services.py`, `app/models.py`.
