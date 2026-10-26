I've built team invites. Any team member can now invite someone by email, and that person gets a link they use to join the team.

**What changed**
- `app/models.py`: there's a new `Invite` record (`DB["invites"]`) with the email, who sent it, an expiry date and a status (pending / accepted / revoked / expired). Only a hash of the link token is stored.
- `app/services.py`:
  - `create_invite` sends the email. It rejects an address that's invalid or already on the team, and it checks the seat limit.
  - `pending_invites` lists the open invites.
  - `revoke_invite` cancels one.
  - `accept_invite` uses the link to create the new person's account on the team, under the invited email address.
  - Inviting an address that already has a pending invite sends a new link and stops the old one working.
- `app/api.py`: four handlers, `invite_member`, `list_invites`, `revoke_invite` and `accept_invite`. They return `{"error": ...}` with a readable message when something's wrong. Links point at the `APP_URL` env var, which defaults to `http://localhost:8000`.

I ran a quick script through the whole flow: invite, re-invite, seat limit full, address already on the team, bad link, accept, reuse of a used link, and revoke. Everything behaved as expected. I didn't add test files or start a server.

**Not included:** there's no limit on how often someone can send invites, and accepting doesn't connect to a real sign-up or password step, because the app doesn't have one yet.

**Guesswork** · 5 decisions need you (1 high stakes)

1. **Invited people always join as plain members, never admin or owner** (high stakes · access)
   - **a** Keep as built
   - **b** Inviter picks the role, up to their own role
   - **c** Only owners/admins can invite as admin
2. **Invite links expire after 7 days and work once** (medium stakes · security)
   - **a** Keep as built
   - **b** Expire after 48 hours
   - **c** Expire after 30 days
   - **d** Never expire until revoked
3. **Only the sender or an owner/admin can revoke a pending invite** (medium stakes · access)
   - **a** Keep as built
   - **b** Any team member can revoke any invite
   - **c** Only owners/admins can revoke
4. **People who already belong to another team can't accept an invite** (medium stakes · access)
   - **a** Keep as built
   - **b** Accepting moves them to the new team
   - **c** Support users in multiple teams
5. **Pending invites count against the team's seat limit (5 on free)** (medium stakes · limits)
   - **a** Keep as built
   - **b** Count only accepted members against seats
   - **c** Don't enforce seats on invites at all

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also: 1 low-stakes guess logged (`guesswork list --stakes low`).
