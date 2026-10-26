Team members can now invite people to their team by email. Any member of a team can send an invite. The invited person gets an email with a link, and when they accept it they join the team as a regular member.

**What I added**
- **`app/models.py`**: a new `Invite` record and an `invites` table. Each invite stores the team, the email address, who sent it, an expiry date (7 days) and its status (accepted or revoked). For the link itself only a hash is stored, never the link token.
- **`app/services.py`**:
  - `create_invite`: checks the email address, sends the invite and returns it. It refuses an address that's already on the team, or one that would go over the team's seat limit. Pending invites count toward that limit.
  - `accept_invite`: adds the invited person to the team.
  - `revoke_invite`: cancels an invite that hasn't been accepted.
  - `pending_invites`: lists the team's open invites.
- **`app/api.py`**: four new handlers, `invites`, `create_invite`, `accept_invite` and `revoke_invite`. They follow the same pattern as your existing handlers. If something goes wrong they return `{"error": "..."}`.

**Choices I made without you**
- **Who can invite:** you said "team members", so anyone on the team can send invites. That lets any member spend your paid seats. If only owners and admins should invite, that's a one-line change.
- **Role on joining:** invited people always join as `member`. An invite can't make someone an owner or admin.
- **Matching email:** an invite only works for a signed-in user whose email matches the invited address. Someone who gets hold of the link can't use it with a different account.
- **Inviting the same address again:** this sends a fresh link and cancels the old one, so invites don't pile up.
- **Cancelling invites:** the person who sent an invite can cancel it, and so can a team owner or admin.
- **People already on another team:** a user can only be on one team, so accepting moves them to the new team. Owners are blocked from doing this so they don't leave their current team without an owner.

**What you need to know**
- **Invited people need an account:** there's no sign-up flow in the codebase, so `accept_invite` needs someone who is already signed in. When you add sign-up, the accept page should send new users through sign-up first and then call `accept_invite` with the token from the link.
- **Placeholder link address:** `APP_URL` in `services.py` is set to `https://app.example.com` and needs to be your real address. The page at `/invites/accept?token=...` doesn't exist yet. It just needs to call `api.accept_invite`.
- **No rate limit:** apart from the seat cap, nothing limits how many invite emails one person can send.

**Testing:** I ran the whole flow in a quick script with the database in memory. It covered:
- bad email addresses
- people already on the team
- the seat limit
- accepting with the wrong account
- accepting the same invite twice
- moving a user over from another team

Everything behaved as expected. I didn't add test files and didn't start a server.
