Team members can now invite people to their team by email. I checked the flow with a quick in-memory script: inviting, the seat limit, the daily cap, accepting, wrong-email rejection, expiry and revoking all behave as intended. The repo has no test suite, so I didn't add tests.

**How it works**
- **Inviting:** any team member sends an invite (`api.invite`). The email address is checked and lowercased. The person gets an email naming who invited them and the team, with a single-use link that expires in 7 days.
- **Accepting** (`api.accept_invitation`):
  - Someone without an account clicks the link, enters a name, and an account is created for them on the team.
  - Someone who is signed in can only accept an invite sent to their own email address.
  - Invited people always join as plain members, never admins.
- **Managing invites:** any member can list pending invites (`api.invitations`). The person who sent an invite, or an owner/admin, can revoke it (`api.revoke_invitation`). Inviting the same address again cancels the old link and sends a fresh one.
- **Limits:**
  - Pending invites count against the team's seat limit, and seats are checked again when someone accepts.
  - Each user can send at most 20 invites a day, so the feature can't be used to spam people.
- **Record-keeping:** each invite records who sent it and who accepted or revoked it, and when. Only a hash of the link's token is stored, not the token itself.

The changes are in `app/models.py` (new `Invitation` model), `app/services.py` and `app/api.py`. The decisions I made on your behalf are recorded in `.guesswork/`. I haven't committed anything.

**Gaps you may want next:**
- **Emails don't actually send yet.** `send_email` is still the print stub, and the link uses a placeholder `APP_URL` (`https://app.example.com`) that needs your real domain.
- **People already on another team can't join yet.** They have to leave their current team before accepting (item 7 below), but the app has no "leave team" action.
- **Accounts created from an invite have no password.** The app has no passwords or sign-up yet, so these accounts work the same way as the existing ones.

**Guesswork** · 9 decisions need you (3 high stakes)

1. **Clicking the invite link and entering a name creates an account for the invited email** (high stakes · security)
   - **a** Keep as built
   - **b** Invitee must sign up separately, then accept
2. **Invited people always join as plain members, never admins** (high stakes · access)
   - **a** Keep as built
   - **b** Owners/admins can pick the role when inviting
3. **Signed-in users can only accept an invite sent to their own email** (high stakes · security)
   - **a** Keep as built
   - **b** Anyone holding the link can accept it
4. **Every team member can see pending invites, including invitee emails** (medium stakes · privacy)
   - **a** Keep as built
   - **b** Only owners/admins can see pending invites
5. **Invite links expire after 7 days** (medium stakes · security)
   - **a** Keep as built
   - **b** Expire after 48 hours
   - **c** Expire after 30 days
6. **Pending invites can be revoked by the person who sent them or a team owner/admin** (medium stakes · access)
   - **a** Keep as built
   - **b** Only owners/admins can revoke
   - **c** Any member can revoke
7. **People already on another team cannot accept until they leave it** (medium stakes · access)
   - **a** Keep as built
   - **b** Accepting moves them to the new team
8. **Each user can send at most 20 invitations per day** (medium stakes · limits)
   - **a** Keep as built
   - **b** 5 per day
   - **c** No limit
9. **Pending invitations count against the team's seat limit** (medium stakes · limits)
   - **a** Keep as built
   - **b** Only count seats when an invite is accepted

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also decided, low stakes (say so to change any): Invite email shows the inviter's name and the team name; Inviting the same email again cancels the old link and sends a fresh one.
