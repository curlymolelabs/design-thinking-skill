Team members can now invite people to their team by email.

**What I built**
- `app/models.py`: a new `Invite` record that stores the team, the email, who sent it, its expiry, and when it was accepted or revoked. Only a hash of the invite code is stored.
- `app/services.py`: `invite_member`, `revoke_invite`, `accept_invite` and `pending_invites`, plus the email that goes to the invitee. Accepting an invite creates the invitee's account on the team.
- `app/api.py`: handlers `create_invite`, `list_invites`, `revoke_invite` and `accept_invite`. Errors come back as `{"error": ...}` with a message users can read. `accept_invite` doesn't need a login, since the invitee has no account yet.

The project has no test suite, so I ran a quick script against the in-memory store instead. It covered sending, resending, the seat limit, a wrong email, an old code, double acceptance, someone from another team, and revoking. Everything behaved as expected. Nothing else in the app changed.

Add the new `.guesswork/` folder to your commit along with the code.

**Guesswork** · 8 decisions need you (2 high stakes)

1. **Pending invites take up a seat, and invites are refused once the team's seats are full** (high stakes · money)
   - **a** Keep as built
   - **b** Only accepted members count toward seats
   - **c** Allow over-limit invites and add paid seats
2. **People who already have an account on another team cannot accept an invite** (high stakes · access)
   - **a** Keep as built
   - **b** Accepting moves them to the new team
   - **c** Ask them to confirm leaving their old team
3. **Invite emails show the inviter's name and email address** (medium stakes · privacy · hard to undo)
   - **a** Keep as built
   - **b** Show only the inviter's name
   - **c** Show only the team name
4. **To accept, the invitee must enter the same email address the invite was sent to** (medium stakes · security)
   - **a** Keep as built
   - **b** Anyone with the code can join with any email
5. **Invited people always join as members, never admins** (medium stakes · access)
   - **a** Keep as built
   - **b** Owners and admins can choose the invitee's role
6. **Invites expire after 7 days** (medium stakes · security) · **b** Expire after 48 hours · **c** Expire after 30 days
7. **Only the person who sent an invite, or a team owner or admin, can revoke it** (medium stakes · access) · **b** Any team member can revoke · **c** Only owners and admins can revoke
8. **A team can send at most 20 new invites per 24 hours** (medium stakes · limits) · **b** 50 invites per day · **c** No limit

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also decided, low stakes (say so to change any): Re-inviting an address resends it with a new code and a fresh 7-day expiry; the old code stops working; The same address can be re-sent an invite at most once every 10 minutes.
