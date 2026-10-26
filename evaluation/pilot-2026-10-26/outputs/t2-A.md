Team members can now invite people to their team by email. I ran each flow in a small throwaway script with sending stubbed out, and they all behaved as expected. I didn't start a server, and I didn't add a test file to the repo.

**How it works**
- **Sending an invite (`api.invite`):** Any team member can invite an email address. The person gets an email with a single-use link to accept, and the link expires after 7 days.
- **Accepting (`api.accept_invite`):**
  - If the person is signed in, their account email must match the invited address. They're then moved into the team as a member.
  - If they're not signed in and have no account, one is created for them. Clicking the emailed link shows they own that inbox.
  - If an account already exists for that email, they're asked to sign in first.
- **Pending invites:** Members can list them (`api.invites`). The person who sent an invite, or a team owner or admin, can cancel it (`api.revoke_invite`).
- **Inviting the same address again:** This cancels the old link and sends a new one.

**Choices I made that you may want to change**
- **Who can invite:** Any member, not just owners and admins, because that's how you worded the request. Invited people always join as plain members; nobody can be invited straight into the admin role.
- **Seat limit:** Pending invites count against the team's seat limit, and it's checked again when someone accepts. That way invites can't take a team over its plan.
- **Owners can't switch teams by accepting an invite.** Each user belongs to only one team, so accepting moves them out of their current one. If an owner did that, their old team would be left without an owner, so the invite is refused with a message telling them to transfer ownership first.
- **The secret part of the link is never stored.** Only a scrambled (hashed) version is saved, so someone who reads the stored data can't rebuild a working link.
- **Invalid requests:** Bad email addresses, people who are already members, expired or used links, and wrong-account accepts all return a clear `{"error": ...}`.

**Before this goes live**
- `APP_URL` in `app/services.py` is a placeholder (`https://app.example.com`). Change it to your real domain, or the links in the emails won't work.
- There's no limit on how many invites one person can send other than the seat limit. If you're worried about members using it to spam people, it would need a rate limit.

**Files changed**
- `app/models.py`: new `Invite` model and an `invites` table.
- `app/services.py`: `create_invite`, `accept_invite`, `revoke_invite`, `pending_invites` and `InviteError`.
- `app/api.py`: handlers `invite`, `invites`, `revoke_invite` and `accept_invite`.
