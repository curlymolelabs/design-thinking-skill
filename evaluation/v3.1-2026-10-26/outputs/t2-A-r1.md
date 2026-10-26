Team members can now invite people to their team by email. When someone invites an address, the app emails it a link to join the team. The person signs in, opens the link, and joins the team as a `member`.

**What I added**
- **`app/models.py`**: a new `Invite` record, kept in `DB["invites"]`.
- **`app/services.py`**: functions to create, accept, cancel and list invites, using the existing `send_email`.
- **`app/api.py`**: four handlers that match your current style:
  - `invites(current_user)` lists the team's pending invites.
  - `create_invite(current_user, email)` sends an invite.
  - `revoke_invite(current_user, invite_id)` cancels one.
  - `accept_invite(current_user, token)` joins the team.
  
  When something goes wrong, they return `{"error": "..."}` with a plain-language message.

**Rules I built in**
- The email address has to be valid. Nobody can be invited twice while an invite is pending, and current team members can't be invited at all.
- **Pending invites count against the team's seat limit (`Team.seats`).** A team can't send more invites than it has room for.
- Each invite link has a long random token and expires after 7 days. It only works for the person signed in with the email address it was sent to, so a forwarded or leaked link can't be used by someone else. Tokens never appear in API responses.
- Invites can only be cancelled by someone on the same team.
- An owner of another team that still has other members can't accept until they hand that team over, so the team isn't left without an owner. If they're the only member, they can accept.

I checked these rules with a short script against the in-memory store. I didn't run a server, didn't add a test file and didn't commit anything.

**Decisions for you**
- **Who can invite:** you said "team members", so anyone on the team can send invites, not just owners and admins. If you'd rather limit it to owners and admins, that's a one-line check at the top of `services.create_invite`.
- **Accept link:** the email currently contains a relative link (`/invites/accept?token=...`). Pass your real address to `create_invite` through `accept_url_base`.
- **Invitees without an account:** they need to sign up with the invited email address before they can accept. Joining straight from the link would need a sign-up flow, which the app doesn't have yet.
- **One team per user:** a user belongs to one team at a time, so accepting an invite moves them out of their old team.
