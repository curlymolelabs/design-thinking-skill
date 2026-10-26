# A fictional workspace app ledger

This teaching example uses an invented app and invented decisions. It does not describe a real product, company, or user.

An agent was asked to "add team workspaces with member invites, a 14-day free trial, and CSV export." It recorded the twelve product decisions it made without instructions in `.guesswork/guesses/`. The owner then answered four of them and sent per-seat pricing to a test. The source files named in each guess are not included.

Try the commands on it from the repository root:

```bash
python3 guesswork/scripts/guesswork.py --root examples/fictional-workspace-app receipt
python3 guesswork/scripts/guesswork.py --root examples/fictional-workspace-app context src/billing/trial.ts
python3 guesswork/scripts/guesswork.py --root examples/fictional-workspace-app report --open
```

The screenshot in the main README comes from this ledger.
