I added a CSV export of your team's customers. It downloads one file with every customer in the current user's team, oldest first. I checked it by calling the code directly with sample data, not through a web server: it only returns your own team's customers, and members get a 403.

**What changed**
- `app/services.py`: `export_customers_csv(team_id)` builds the CSV with these columns: `id, name, email, phone, created_at`. `can_export_customers(user)` checks the user's role.
- `app/api.py`: a new handler, `customers_csv(current_user)`, returns the CSV text with a `text/csv` content type and a `customers-team-<id>.csv` filename. Users who aren't allowed get a 403.

**Choices I made without asking**
- **Who can export:** only owners and admins. Members can already see customers in the app, but a file of everyone's contact details can be passed around once downloaded, so I started narrow.
- **Notes are left out.** Notes are free text and can hold sensitive details.
- **Formula protection:** customer-entered text that starts with `=`, `+`, `-` or `@` gets an apostrophe in front so Excel or Sheets won't run it as a formula. Phone numbers like `+1 (555) 010-0100` export unchanged.

**What I didn't build**
- **No log of exports.** Nothing records who exported or when.
- **No rate limit.**
- **No route or button yet.** The app has no router, so you'll need to hook `customers_csv` up to your URL and UI.
- **Very large lists:** the whole file is built in memory at once. That's fine at your current size, but past tens of thousands of customers it should stream instead.

The decisions are recorded in `.guesswork/`; commit it along with the code.

**Guesswork** · 4 decisions need you (2 high stakes)

1. **The customer CSV includes name, email, phone, id and created date** (high stakes · privacy · hard to undo)
   - **a** Keep as built
   - **b** Names and ids only, no contact details
   - **c** Email but not phone
2. **Only team owners and admins can download the customer CSV; members get a 403** (high stakes · access · hard to undo)
   - **a** Keep as built
   - **b** Any team member can export
   - **c** Owners only
3. **Customer notes are left out of the CSV export** (medium stakes · privacy)
   - **a** Keep as built
   - **b** Include notes as a column
   - **c** Optional notes column on request
4. **Exported cells that start with =, +, -, @ are prefixed with an apostrophe, except phone-shaped values** (medium stakes · security)
   - **a** Keep as built
   - **b** Export raw values with no escaping
   - **c** Prefix every risky cell, phones too

Reply with your picks, like `1b 2a 3a`. `all a` keeps everything as built. `2: your own answer` sets something else.
Also decided, low stakes (say so to change any): The export contains every customer in the team, oldest first, in one file.
