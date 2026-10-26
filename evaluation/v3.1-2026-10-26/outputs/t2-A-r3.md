Anyone on a team can now invite people to it by email. The invitee gets a link, and once signed in with that address they can use it to join.

**How it works**
- `api.invite(current_user, email)` checks the address, creates the invite and emails a link that expires after 7 days. People already on the team are rejected.
- `api.accept_invite(current_user, token)` moves the signed-in user into the team. It only works if their email matches the one the invite was sent to. The link works once.
- `api.invites(current_user)` lists the team's pending invites.
- `api.revoke_invite(current_user, invite_id)` cancels an invite. The person who sent it can do this, and so can an owner or admin.

The changes are in `app/models.py` (a new `Invite` model and an `invites` table), `app/services.py` (the logic) and `app/api.py` (the handlers). I tried the whole flow with a quick throwaway script and every case above behaved correctly. I didn't add a test file or commit anything.

**Choices I made without you**
- **Who can invite:** every team member, since that's what you asked for. Limiting it to owners and admins is a one-line check in `invite_to_team`.
- **Role:** invitees always join as `member`. Nobody can use an invite to make someone an admin or owner.
- **Seats:** each pending invite holds a seat, so a team can't send more invites than `team.seats` allows. Sending a new invite to the same address replaces the old link and doesn't take another seat.
- **Link safety:** the app stores only a hash of the token, not the token itself. The link stops working once it's used, revoked or 7 days old.
- **Existing users:** someone already on another team switches to the new team when they accept, because the app only lets a user belong to one team. A team owner can't accept, so their team is never left without an owner.

**Things you should know**
- The app has no sign-up flow, so a person without an account has to create one with the invited email before they can accept.
- The invite link uses `APP_URL = "https://app.example.com"` at the top of `app/services.py`. Change it to your real domain.
- There's no limit on how many invites someone can send. If you're worried about invites being used to spam people, a per-user daily cap would be the next thing to add.
