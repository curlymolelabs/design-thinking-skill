I added a CSV export of your team's customers. I ran it against sample data in a quick in-memory script and the output parsed back correctly; there are no automated tests for it yet.

**What I added**
- **`app/services.py`**: a new `export_customers_csv(team_id)` that returns CSV text. It has a header row, then one row per customer sorted by id. The columns are `id, name, email, phone, notes, created_at`, with dates in ISO format. Commas, quotes and line breaks inside fields come through correctly.
- **`app/api.py`**: a new `customers_csv(current_user)` handler. It returns `content_type` (`text/csv; charset=utf-8`), a `filename` like `customers-2026-10-26.csv`, and the CSV text as `body`. You'll need to hook it up wherever your routes are defined and send `filename` as the download name (a `Content-Disposition: attachment` header).

**Choices I made without you**
- **Who sees what:** the export only includes customers from the user's own team, using the same lookup as the existing `customers` endpoint. It doesn't add a role check, so any team member can export, just as any member can already list customers. Because the export holds customer emails, phone numbers and notes in bulk, you may want only owners and admins to have it. That's a two-line change if you do.
- **Formula protection:** if a cell starts with `=`, `+`, `-` or `@`, I put an apostrophe in front of it. Without that, a customer name or note could run as a formula when someone opens the file in Excel or Google Sheets. The downside is that phone numbers like `+1 555…` show up as `'+1 555…` in the file. Spreadsheet apps usually hide that apostrophe, but other tools that read the CSV will see it.
- **Left out:** `team_id`, since everything in the file belongs to the same team.

Nothing is committed yet.
