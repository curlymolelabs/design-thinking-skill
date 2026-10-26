Team members can now invite people to their team by email.

- **`app/models.py`**: there's a new `Invitation` record and a `DB["invitations"]` store. Each invitation keeps who sent it, its status, and when it was created, accepted or revoked. Only a hash of the link token is stored.
- **`app/services.py`**:
  - `invite_member` checks the email, refuses people already on the team or already invited, enforces the seat limit and a daily cap per sender, then emails a single-use link.
  - `revoke_invitation` cancels a pending invitation.
  - `accept_invitation` takes the token from the link and creates the new user's account on the team.
- **`app/api.py`**: there are new handlers `invite`, `invitations` (lists pending invitations), `revoke_invite` and `accept_invite`. If an action is refused, they return `{"error": ...}` with a message the user can read.

I ran a quick in-memory check of these paths and they behaved as expected: sending, duplicate invite, seats full, bad email, bad token, accepting, reusing a used link, and revoking an accepted invitation. Emails still go through the existing `send_email` stub, so nothing is actually delivered yet. The link base URL is a placeholder (`APP_URL` in `services.py`) that needs setting to your real domain. The decisions I made are logged in `.guesswork/`, which should be committed with the code.

**Guesswork** · 6 decisions need you (2 high stakes)

1. **An invite to an email that already has an account is refused at accept time** (high stakes · access)
   - **a** Keep as built
   - **b** Move the existing user to the new team
   - **c** Refuse at invite time instead
2. **Invited people always join as plain members, never admins** (high stakes · access)
   - **a** Keep as built
   - **b** Inviter picks the role, up to their own
   - **c** Admins/owners can invite as admin
3. **Invitation links expire after 7 days** (medium stakes · security)
   - **a** Keep as built
   - **b** Expire after 48 hours
   - **c** Expire after 30 days
4. **The inviter or a team owner/admin can revoke a pending invitation** (medium stakes · access)
   - **a** Keep as built
   - **b** Any team member can revoke any invite
   - **c** Only owners/admins can revoke
5. **Each member can send at most 20 invitations per 24 hours** (medium stakes · limits)
   - **a** Keep as built
   - **b** No per-user limit
   - **c** 5 per day
6. **Pending invitations count against the team's seat limit** (medium stakes · limits) · **b** Only count accepted members against seats · **c** Allow invites past the limit, block on accept

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also decided, low stakes (say so to change any): Invitation email shows the inviter's name and email address and the team name; A second invite to an email with a pending invite is refused, not resent.
