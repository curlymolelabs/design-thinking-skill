I added a CSV export of your team's customers.

- **`app/services.py`**: new `export_customers_csv(user)`. It returns the current team's customers as CSV text with the columns `id, name, email, phone, created_at`. Values that could run as spreadsheet formulas are escaped. Each export also prints an `AUDIT` log line.
- **`app/api.py`**: new `customers_csv(current_user)` handler. It returns a 200 response with `text/csv` and `filename: customers.csv`, or a 403 if the user's role isn't allowed to export.
- I ran it once against sample data. It only returned customers from the user's own team, a member got a 403, quoting and the formula escaping worked, and phone numbers like `+1 555 0100` came through unchanged. I didn't add any automated tests.

The decisions are recorded in `.guesswork/`, which should be committed with the code.

**Guesswork** · 5 decisions need you (3 high stakes)

1. **Customer CSV includes email and phone for every customer** (high stakes · privacy · hard to undo)
   - **a** Keep as built
   - **b** Names and IDs only
   - **c** Email only, no phone numbers
2. **Customer CSV leaves out the private notes field** (high stakes · privacy · hard to undo)
   - **a** Keep as built
   - **b** Include notes in the export
   - **c** Admins choose columns per export
3. **Only team owners and admins can export customers; members get a 403** (high stakes · access · hard to undo)
   - **a** Keep as built
   - **b** Any team member can export
   - **c** Owners only
4. **Every customer export is logged with who ran it, team, and row count** (medium stakes · security)
   - **a** Keep as built
   - **b** No export logging
   - **c** Also notify team owners on each export
5. **Export returns all of the team's customers in one file, sorted by ID, with no row cap** (medium stakes · limits)
   - **a** Keep as built
   - **b** Cap at 10,000 rows per export
   - **c** Sort by name instead

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also decided, low stakes (say so to change any): Cells starting with = + - or @ get a leading apostrophe in the CSV, except plain phone numbers.
