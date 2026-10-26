Team members can now invite people to their team by email.

- **`app/models.py`**: there's a new `Invite` record and a `DB["invites"]` table. Each invite keeps an audit trail: who sent it and when, plus when it was accepted or cancelled and by whom. Only a hash of the link token is stored; the full link appears only in the email.
- **`app/services.py`**:
  - `create_invite` checks the email address, refuses people already on the team, enforces a per-member limit and the team's seat limit, and sends a one-time accept link through the existing `send_email`.
  - `accept_invite` turns a valid link into a new user on the team.
  - `revoke_invite` cancels a pending invite.
  - `pending_invites` lists the open invites.
  - Every failure raises `InviteError` with a message you can show the user.
- **`app/api.py`**: new handlers `invites`, `create_invite`, `revoke_invite` and `accept_invite`. `accept_invite` is public because the invitee isn't signed in yet. Errors come back as `{"error": ...}`.

The README says not to run anything, so I haven't executed the code. I only checked that the three files parse. The decisions I made are recorded in `.guesswork/`; commit it with the code.

**Guesswork** · 7 decisions need you (3 high stakes)

1. **Invited people always join as regular members** (high stakes · access)
   - **a** Keep as built
   - **b** Owners/admins can choose the invitee's role
2. **Invites to an email that already has an account are refused at acceptance** (high stakes · access)
   - **a** Keep as built
   - **b** Accepting moves the user to the new team
   - **c** Block such invites when they are sent
3. **Pending invites count toward the team's seat limit (5 on free)** (high stakes · money)
   - **a** Keep as built
   - **b** Only accepted members count toward seats
   - **c** No seat check on invites
4. **Invite emails show the inviter's name and team name to the recipient** (medium stakes · privacy · hard to undo)
   - **a** Keep as built
   - **b** Show only the team name
5. **Invite links expire after 7 days** (medium stakes · security)
   - **a** Keep as built
   - **b** Expire after 48 hours
   - **c** Expire after 30 days
6. **Only the inviter or an owner/admin can cancel a pending invite** (medium stakes · access) · **b** Any team member can cancel any invite · **c** Only owners/admins can cancel
7. **Each member can send at most 20 invites per 24 hours** (medium stakes · limits) · **b** 50 invites per day · **c** No per-member limit

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also decided, low stakes (say so to change any): Every team member can see the team's pending invites; Re-inviting the same email sends a new link and disables the old one.
