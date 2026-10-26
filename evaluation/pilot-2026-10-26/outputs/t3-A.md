I added a CSV export of your customers. You call it as `api.export_customers_csv(current_user)`. It returns the CSV text along with `content_type: text/csv; charset=utf-8` and `filename: customers.csv`, ready for whatever HTTP layer you put in front of it.

I checked it by calling it directly with sample data. I didn't start a server, and I haven't committed anything.

**What's in the file**
- One row per customer, ordered by id, with these columns: `id, name, email, phone, notes, created_at` (the date is in ISO format).
- It only includes customers from the user's own team, the same filtering your existing `customers` endpoint uses.
- Commas, quotes and line breaks in names or notes come through intact.

**Two choices I made while you were away**
1. **Only owners and admins can export.** Members get a 403 error. The file is a bulk copy of every customer's email, phone and notes, so I made it the stricter option. If everyone on a team should be able to export, as they can already view the list, delete the role check at the top of `export_customers_csv` in `app/api.py`.
2. **Formula-like cells are neutralised.** Excel and Google Sheets run a cell as a formula if it starts with `=`, `+`, `-` or `@`, so a customer could put something harmful in their name or notes. The export adds a leading `'` to those cells so spreadsheets show them as plain text. Values that are just numbers, like the phone number `+1 555 0100`, are left alone. One side effect: someone reading the file with a script rather than a spreadsheet will see that `'` on any notes that start with one of those characters.

**Files changed**
- `app/services.py`: adds `customers_to_csv()`, which builds the file, and the formula protection.
- `app/api.py`: adds the `export_customers_csv` handler.
