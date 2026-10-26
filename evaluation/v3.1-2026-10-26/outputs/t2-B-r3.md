Team members can now invite people to their team by email.

**What I built**
- **`app/models.py`**: added an `Invite` record (team, email, inviter, hashed token, expiry, and when it was accepted or revoked) and a new `DB["invites"]` table.
- **`app/services.py`**:
  - `create_invite` checks the address, stops duplicates and over-inviting, and emails a one-time accept link through the existing `send_email`.
  - `pending_invites` lists the invites still open.
  - `revoke_invite` cancels a pending invite.
  - `accept_invite` creates the invitee's account on the team.
  - Only a SHA-256 hash of each token is stored, and a link stops working once it is used, revoked or expired.
- **`app/api.py`**: added the `create_invite`, `list_invites`, `revoke_invite` and `accept_invite` handlers. `accept_invite` needs no login because the invitee doesn't have an account yet. Errors come back as `{"error": ...}`, and the token hash is never returned.

I ran the whole flow once in memory with a small script, not with tests: inviting, re-inviting, hitting the seat limit, a bad email, accepting, reusing a used link, and revoking with and without permission. All of it behaved as expected. No web server was started, and I didn't add a test file.

**Gaps I didn't build (ask if you want them)**
- The accept link points to a placeholder URL, `https://app.example.com/invites/accept`. It needs your real domain and an accept page.
- Any member can find out whether an email already has an account, because inviting it returns an error that says so.
- There is no rate limit on invites per member across different addresses. The seat limit is the only cap.
- Invites aren't shown anywhere else in the app.

**Guesswork** · 7 decisions need you (2 high stakes)

1. **Invited people always join as a regular member** (high stakes · access)
   - **a** Keep as built
   - **b** Owners and admins can pick the role when inviting
2. **Every team member, not just owners and admins, can send invites** (high stakes · access)
   - **a** Keep as built
   - **b** Only owners and admins can invite
   - **c** Members invite, an admin must approve
3. **Inviting the same address again re-sends the email with a new link, at most once per 10 minutes** (medium stakes · notifications · hard to undo)
   - **a** Keep as built
   - **b** Reject duplicates; require revoke then re-invite
   - **c** Cooldown of 1 hour
4. **Invite links expire after 7 days** (medium stakes · security)
   - **a** Keep as built
   - **b** Expire after 48 hours
   - **c** Expire after 30 days
5. **Owners and admins can revoke any pending invite; members only their own** (medium stakes · access)
   - **a** Keep as built
   - **b** Only owners and admins can revoke
   - **c** Any member can revoke any invite

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also: 2 more decisions waiting (`guesswork receipt --limit 20`).
Also decided, low stakes (say so to change any): The invite email names the inviter and the team.
