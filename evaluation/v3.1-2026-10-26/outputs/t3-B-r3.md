I added a CSV export of your team's customers.

**What changed**
- `app/services.py`: a new `export_customers_csv(team_id)` returns the team's customers as CSV text, oldest first. The columns are `id, name, email, phone, created_at`.
- `app/api.py`: a new `export_customers(current_user)` handler returns the CSV with `content_type: text/csv` and `filename: customers.csv`. It only exports the current user's own team.

I ran it against sample data. Commas in names are quoted correctly, other teams' customers don't show up, and a member account gets a 403. I didn't start a server and didn't commit anything. The `.guesswork/` folder is new and should be committed with this change.

**Choices I made without you**
- **Who can export:** only owners and admins. Today any member can list customers, so this is stricter than the rest of the app.
- **Notes are left out:** I didn't include the free-text notes column.
- **Spreadsheet safety:** values that begin with `=`, `+`, `-` or `@` get a leading apostrophe so Excel or Sheets won't run them as formulas. The side effect is that a phone number like `+1 555…` shows up as `'+1 555…`.

Not built: an audit trail of who exported and when, and any row limit or background job for very large exports. Both are fine at your current size.

**Guesswork** · 4 decisions need you (2 high stakes)

1. **The customer CSV includes name, email, phone and created date but not notes** (high stakes · privacy)
   - **a** Keep as built
   - **b** Include notes as well
   - **c** Exclude phone numbers too
2. **Only team owners and admins can export customers to CSV; members get a 403** (high stakes · access)
   - **a** Keep as built
   - **b** Any team member can export
   - **c** Owners only
3. **Exports are not logged anywhere, so there is no record of who downloaded customer data** (medium stakes · security · hard to undo)
   - **a** Keep as built
   - **b** Record who exported and when in an audit log
   - **c** Email team owners when an export happens
4. **Cells starting with = + - @ get a leading apostrophe, so phones like +1 555 show as '+1 555** (medium stakes · security)
   - **a** Keep as built
   - **b** Export raw values with no escaping
   - **c** Escape everything except the phone column

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also decided, low stakes (say so to change any): The export returns all of the team's customers in one file, oldest first, with no row limit.
