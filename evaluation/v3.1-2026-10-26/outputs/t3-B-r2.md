I added a CSV export of your team's customers. I checked it with a quick script against sample data, but there are no automated tests and no web server was run.

**What it does**
- **New handler:** `customers_export(current_user)` in `app/api.py`. It returns `{"status": 200, "content_type": "text/csv; charset=utf-8", "filename": "customers-YYYY-MM-DD.csv", "body": ...}`. If the user isn't allowed, it returns `{"status": 403, "error": ...}` instead.
- **Contents:** only the caller's own team's customers, oldest first. The columns are `id, name, email, phone, created_at`. Commas and quotes in values are handled correctly.
- **Formula protection:** a cell that starts with `=`, `+`, `-` or `@` gets a leading `'` so Excel or Sheets won't run it as a formula. Phone numbers like `+1 555 0100` are left as they are.
- **Settings:** the logic is in `app/services.py`. The column list (`CUSTOMER_EXPORT_FIELDS`) and the roles allowed to export (`CUSTOMER_EXPORT_ROLES`) are constants there, so either is a one-line change.

**Choices I made that you should check**
- **Who can export:** only owners and admins. Members can still see the customer list but can't download it as a file.
- **Notes left out:** customer notes are internal free text, so they aren't in the file.
- **No audit log:** the app doesn't have one yet, so nothing records who exported or when.

**Not built**
- **Large lists:** the whole file is built in memory, which suits the current in-memory store. A very large customer base would need streaming.
- **Encoding:** the file is UTF-8 with no BOM, so older Excel versions may garble accented names.
- **Routing:** the handler isn't wired to a URL or button yet, because the app has no routing layer.

Nothing is committed yet. The changes and the new `.guesswork/` folder are in the working tree.

**Guesswork** · 4 decisions need you (2 high stakes)

1. **Customer export includes name, email and phone but leaves out internal notes** (high stakes · privacy · hard to undo)
   - **a** Keep as built
   - **b** Include notes in the export
   - **c** Let the exporter choose columns
2. **Only team owners and admins can export customers; members get a 403** (high stakes · access)
   - **a** Keep as built
   - **b** Any team member can export
   - **c** Only the team owner can export
3. **Customer exports are not logged or audited** (medium stakes · security · hard to undo)
   - **a** Keep as built
   - **b** Log exporter, team and time on every export
   - **c** Email team owners when an export happens
4. **Exported cells that start with =, +, -, @ get a leading apostrophe unless they look like numbers** (medium stakes · security)
   - **a** Keep as built
   - **b** Export raw values with no escaping

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
