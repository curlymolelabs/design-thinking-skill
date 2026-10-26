I added a CSV export of your team's customers, with a new handler at `api.customers_csv(current_user)`.

- **What it returns:** a dict with `status`, `content_type` (`text/csv; charset=utf-8`), `filename` (`customers.csv`) and `body`. The columns are `id, name, email, phone, notes, created_at`, sorted by id, and dates are in ISO format.
- **Scope:** it only includes customers from the current user's own team.

I made two choices you may want to change:

1. **Only owners and admins can export.** Members get a 403 response instead of the file. The existing `customers` endpoint lets any member see customers, but a one-click download of every contact's email, phone and notes felt like it should be limited. If you want everyone to be able to export, delete the role check at the top of `customers_csv`.
2. **Some cells get a leading apostrophe.** Any cell that starts with `=`, `+`, `-` or `@` gets a `'` in front, so Excel or Sheets won't run it as a formula; this guards against CSV injection, since notes, names and other fields can contain anything. The side effect is that phone numbers like `+1 555…` show up as `'+1 555…`. If your phone numbers are always clean, I can stop applying this to the phone column.

I checked it with sample data in a quick script: other teams' customers were left out, commas, quotes and multi-line notes came through correctly, and members got the 403. I didn't add a test file or start a server. Nothing is committed yet.

The changes are in `app/services.py`, where the new `export_customers_csv(team_id)` builds the file, and `app/api.py`, where the new `customers_csv` handler lives. You'll still need to add the route and a download button in whatever serves these handlers.
