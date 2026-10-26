I added a CSV export of your team's customers.

- **`app/api.py`**: new handler `customers_csv(current_user)`. It returns the CSV as a file download (`text/csv`, `Content-Disposition: attachment`). It only includes the requesting user's own team, and users outside the allowed roles get a 403.
- **`app/services.py`**: `export_customers_csv(team_id)` builds the CSV with Python's `csv` module, so commas, quotes and newlines in values are handled correctly. Values that start like a formula are escaped so spreadsheet apps won't run them. I also added a small `record_audit()` helper.
- **`app/models.py`**: added an `audit_log` list to the in-memory `DB` so exports can be traced.

I ran a quick in-process check with sample data. Customers from another team were left out, a member got the 403, an admin got the CSV, and the export was recorded in the audit log. There's no test suite yet, so nothing beyond that was run. The decisions I made on your behalf are in `.guesswork/`, which should be committed with the code.

**Guesswork** · 6 decisions need you (2 high stakes)

1. **The customer CSV includes customer emails and phone numbers** (high stakes · privacy · hard to undo)
   - **a** Keep as built
   - **b** Leave out emails and phone numbers
   - **c** Leave out phone numbers only
2. **Only team owners and admins can export customers; members get a 403** (high stakes · access)
   - **a** Keep as built
   - **b** Any team member can export
   - **c** Only team owners can export
3. **Cells starting with = + - or @ get a leading apostrophe, so phones like +1 555 show as '+1 555** (medium stakes · security)
   - **a** Keep as built
   - **b** Export values exactly as stored
   - **c** Escape formulas but leave phone numbers as is
4. **Customer notes are left out of the CSV export** (medium stakes · privacy)
   - **a** Keep as built
   - **b** Include notes in the export
5. **Every customer export is recorded in an audit log with who, when, and row count** (medium stakes · data)
   - **a** Keep as built
   - **b** Do not log exports
   - **c** Log exports and email team owners
6. **The export contains every customer in one file with no row limit** (medium stakes · limits) · **b** Cap the export at 10,000 rows · **c** Generate large exports in the background

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also decided, low stakes (say so to change any): The export file is named customers-YYYY-MM-DD.csv; Export rows are ordered oldest customer first.
