Team members can now invite people to their team by email. The invitee gets a link, and opening it creates their account on that team.

**How it works**
- `api.invite(current_user, email)` sends the invitation email with a one-time link. Inviting an address that already has a pending invite sends a fresh link, and the old link stops working.
- `api.accept_invitation(token, name)` creates the invitee's account as a member of the team. No login is needed, because the emailed link proves who they are.
- `api.invitations(current_user)` lists the team's pending invites. `api.revoke_invitation(current_user, id)` cancels one; the person who sent it or any admin or owner can do that.
- It refuses to invite someone already on the team, invalid email addresses, and invites that would go past the team's seat limit (pending invites count toward it).
- The link token is never stored or returned by the API; only a hash of it is kept. Each invitation records who sent it, when it was accepted or cancelled, and who cancelled it.

The changes are in `app/models.py` (new `Invitation` model and `DB["invitations"]`), `app/services.py` and `app/api.py`. I ran the whole flow against a scratch copy of the app: invite, resend, the seat limit, accepting, reusing a link, an address that belongs to another team, and cancelling. There's no test suite in the repo, so I didn't add one.

**Not built yet:**
- `send_email` still only prints. Real email sending needs a provider.
- The link uses `https://app.example.com` as a placeholder (`APP_URL` in `app/services.py`).
- Nothing tells the inviter when an invite is accepted.

**Guesswork** · 7 decisions need you (2 high stakes)

1. **People who already have an account on another team cannot accept** (high stakes · access)
   - **a** Keep as built
   - **b** Accepting moves them to the new team
   - **c** Support users on several teams
2. **Every team member, not just admins or owners, can send invitations** (high stakes · access)
   - **a** Keep as built
   - **b** Only admins and owners can invite
   - **c** Members invite, an admin approves
3. **Invitation emails show the inviter's name and email address** (medium stakes · privacy · hard to undo)
   - **a** Keep as built
   - **b** Show only the inviter's name
4. **Invitation links expire after 7 days** (medium stakes · security)
   - **a** Keep as built
   - **b** Expire after 48 hours
   - **c** Expire after 30 days
5. **Invited people always join as plain members** (medium stakes · access)
   - **a** Keep as built
   - **b** Admins can choose the invitee's role
6. **Pending invitations count against the team's seat limit** (medium stakes · limits)
   - **a** Keep as built
   - **b** Count only accepted members
   - **c** Allow invites past the limit and prompt to upgrade
7. **A team can send at most 20 invitations per rolling 24 hours** (medium stakes · limits)
   - **a** Keep as built
   - **b** Cap of 50 per day
   - **c** Cap per inviter instead of per team

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also decided, low stakes (say so to change any): The inviter or any admin or owner can cancel a pending invitation; Inviting the same email again sends a fresh link and cancels the old one.
