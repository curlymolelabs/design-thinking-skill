I added a CSV export of your team's customers.

- **`app/services.py`**: new `export_customers_csv(user)`. It builds the CSV from the current user's team only, with columns `id, name, email, phone, created_at`. It also checks the user's role and writes an audit line for each export.
- **`app/api.py`**: new `export_customers(current_user)` handler. It returns `status`, `content_type: text/csv`, a `filename` and the CSV `body`. If the user isn't allowed to export, it returns a 403.

I ran it against sample in-memory data and did not start a server. An owner or admin got only their own team's rows. A member got a 403. A name starting with `=` was escaped, and a phone number like `+1 (555) 010-0` came through unchanged. There are no automated tests yet.

The decision log is in the new `.guesswork/` folder. Please commit it along with the code.

**Guesswork** · 5 decisions need you (3 high stakes)

1. **Exports include customer names, emails and phone numbers** (high stakes · privacy · hard to undo)
   - **a** Keep as built
   - **b** Names and emails only, no phone numbers
2. **Customer notes are left out of the export** (high stakes · privacy)
   - **a** Keep as built
   - **b** Include notes in the export
3. **Only team owners and admins can export customers; members get a 403** (high stakes · access)
   - **a** Keep as built
   - **b** Any team member can export
   - **c** Owners only
4. **Every export writes an audit line with who exported, which team, and how many rows** (medium stakes · security)
   - **a** Keep as built
   - **b** No audit logging
5. **Cells starting with = + - @ get a leading apostrophe so spreadsheets do not run them as formulas** (medium stakes · security)
   - **a** Keep as built
   - **b** Export raw values unchanged

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also decided, low stakes (say so to change any): The export includes all of the team's customers in one file, sorted by ID, named customers-YYYY-MM-DD.csv.
