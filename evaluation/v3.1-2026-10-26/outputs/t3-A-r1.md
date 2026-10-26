I added the customer CSV export. A quick smoke test in Python passed, and I didn't start a server.

**How it works**
- New handler `api.customers_csv(current_user)` in `app/api.py`. It returns `{"status": 200, "content_type": "text/csv; charset=utf-8", "filename": "customers-team-<id>.csv", "body": <csv text>}`, which your routing layer can turn into a download.
- The CSV itself is built by `services.export_customers_csv(team_id)` in `app/services.py`.
- Columns are `id, name, email, phone, notes, created_at`, sorted by id, with a header row. Dates are in ISO format. `team_id` is left out because every row would have the same value.
- Only the current user's own team's customers are exported, the same scoping the existing `customers` endpoint uses.

**Decisions I made without you (easy to change):**
1. **Only owners and admins can export.** Members get `{"error": ..., "status": 403}`. Members can still see customers through the existing list endpoint. I limited the export because it hands someone every customer's email, phone and notes in one file. If you want all members to be able to export, delete the role check in `customers_csv`.
2. **Notes are included.** If notes hold internal comments you don't want leaving the app, remove `notes` from `CUSTOMER_CSV_COLUMNS` and from the matching line in the row it writes.
3. **Protection against spreadsheet formula injection.** Any cell that starts with `=`, `+`, `-` or `@` gets a leading `'`. Without this, a customer named `=HYPERLINK(...)` would run as a formula when someone opens the file in Excel or Sheets. One side effect: phone numbers like `+1 555...` will have the `'` in front of them if the file is read by something other than a spreadsheet, such as an import script.

**Not done:** there's no test suite in the repo, so I didn't add tests. I also didn't add streaming or pagination, because the export builds the whole file in memory, which is fine at the current data size.
