I added the customer CSV export.

**What I built**
- `app/api.py`: a new `customers_csv(current_user)` handler. It returns a CSV download named `customers-YYYY-MM-DD.csv` (`text/csv`, sent as an attachment). The file starts with a UTF-8 byte-order mark so Excel shows accented names correctly.
- `app/services.py`: `export_customers_csv(team_id)` and `can_export_customers(user)`.
  - The file only contains customers from the user's own team, oldest first.
  - Columns are id, name, email, phone and created_at (as an ISO time in UTC).
  - Commas and quotes are escaped properly.
  - Any cell a spreadsheet would read as a formula, such as `=HYPERLINK(...)`, gets a leading apostrophe so it can't run when the file is opened. Phone numbers like `+1 555 0100` are left as they are.

I tested it with a quick in-memory script. A member gets a 403. An admin gets the CSV with only their own team's customers. Formula-like cells came out escaped, and commas and quotes came out correctly. There are no automated tests in the repo, and I didn't add any or run a server.

A few choices weren't in the request, so I went with the safer option for each. They're logged in `.guesswork/`; commit that folder with the code.

**Guesswork** · 3 decisions need you (2 high stakes)

1. **Customer CSV includes id, name, email, phone and created date, but not internal notes** (high stakes · privacy · hard to undo)
   - **a** Keep as built
   - **b** Also include internal notes
   - **c** Name and email only
2. **Only team owners and admins can export customers; members get a 403** (high stakes · access · hard to undo)
   - **a** Keep as built
   - **b** Any team member can export
   - **c** Owners only
3. **Cells that look like spreadsheet formulas get a leading apostrophe; phone numbers like +1 555 0100 are kept as-is** (medium stakes · security)
   - **a** Keep as built
   - **b** Export raw values with no escaping
   - **c** Escape every cell starting with + or -

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also: 1 low-stakes guess logged (`guesswork list --stakes low`).
