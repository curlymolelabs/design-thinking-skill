# Read and write the ledger format

Use this reference when you cannot run the CLI, when you edit ledger files directly, or when another tool must read the ledger.

## The ledger is one JSON file per guess

```text
.guesswork/
|-- README.md          explains the folder to people who find it
|-- config.json        optional settings
|-- .gitignore         ignores the generated report
`-- guesses/
    |-- g-workspace-restore-window.json
    `-- g-trial-reminder.json
```

One file per guess keeps parallel agents and branches from colliding. Commit the folder with the code it describes.

## Each guess has a fixed set of fields

```json
{
  "schema": "guesswork/1",
  "id": "g-workspace-restore-window",
  "title": "Deleted workspaces can be restored for 30 days",
  "why": "No retention rule was given, so the safer soft delete was used",
  "category": "data",
  "stakes": "high",
  "reversible": true,
  "basis": "assumed",
  "where": ["src/workspaces/delete.ts"],
  "alternatives": ["Delete permanently right away", "Restore window of 7 days"],
  "question": null,
  "status": "open",
  "resolution": null,
  "test": null,
  "superseded_by": null,
  "created_by": "agent",
  "created_at": "2026-10-26T14:03:00Z",
  "updated_at": "2026-10-26T14:03:00Z",
  "history": [
    {"at": "2026-10-26T14:03:00Z", "status": "open", "by": "agent", "note": "recorded"}
  ]
}
```

| Field | Rule |
|---|---|
| `schema` | Always `guesswork/1` |
| `id` | `g-` followed by lowercase words joined with hyphens, at most 64 characters, matching the file name |
| `title` | The decision as built, at most 240 characters |
| `category` | money, access, privacy, data, security, legal, safety, defaults, limits, notifications, ux, content, integration, performance, or other |
| `stakes` | high, medium, or low |
| `reversible` | `false` when changing the code would not undo the harm |
| `basis` | assumed, inferred, reported, observed, or external |
| `where` | Repository-relative paths, optionally with `:line` or `#symbol` |
| `alternatives` | At most four short labels; option `a` is always "Keep as built" |
| `status` | open, decided, testing, dismissed, or superseded |
| `resolution` | Required when decided: `choice` (`a` to `e` or `custom`), `decision`, `by`, `at`, optional `note` |
| `test` | Required when testing: `plan`, `by`, `at` |
| `superseded_by` | Required when superseded: the id of the replacing guess |
| `history` | Every status change, newest last |

Run `guesswork validate` after editing files by hand. In Claude Code, the plugin validates guess files as soon as an edit tool writes them.

## A decided guess records the owner's answer

```json
"status": "decided",
"resolution": {
  "choice": "b",
  "decision": "Delete permanently right away",
  "by": "owner",
  "at": "2026-10-26T15:10:00Z",
  "note": "Customers asked for real deletion"
}
```

`decision` holds the behavior the product must now have. For `choice` `a`, it repeats the title. For a custom answer, it holds the owner's words.

## Settings live in config.json

```json
{
  "hooks": true,
  "stop_check": "nudge",
  "fail_on": "high",
  "receipt_limit": 5,
  "ignore": ["docs/**"]
}
```

| Setting | Effect |
|---|---|
| `hooks` | `false` turns off every Claude Code hook for this project |
| `stop_check` | `nudge` asks the agent once per turn to record guesses after code changes and to show unseen decisions; `receipt` only checks that recorded decisions were shown; `off` disables the check |
| `fail_on` | Default threshold for `guesswork check`: high, medium, low, or never |
| `receipt_limit` | Most items in a receipt |
| `ignore` | Extra glob patterns that never trigger the end-of-turn check; Markdown files and lockfiles are always ignored |

Set the environment variable `GUESSWORK_DISABLE=1` to turn the hooks off for one session.
