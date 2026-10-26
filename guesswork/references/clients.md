# Set Guesswork up in each client

Use this reference when you install Guesswork, explain what its hooks do, or connect it to continuous integration.

## Claude Code gets the full loop through the plugin

The plugin adds the `guesswork` command to the Bash tool's path and runs four hooks:

| Hook | What it does |
|---|---|
| Session start | Tells the agent which decisions are locked, how many guesses are open, and the recording convention. It runs again after compaction, so decisions survive long sessions |
| Prompt submit | Notes when the turn started. When the user's message is only a receipt reply such as `1b 2a`, it adds a note mapping each pick to its guess id and option |
| After edits | Validates guess files written by edit tools. The first time a file with decided guesses is edited in a session, it reminds the agent which owner decisions that file implements |
| Stop | Once per turn, asks the agent to record guesses when code changed and none were recorded, or to show the receipt when recorded decisions were never shown |

The stop check costs one extra short reply on turns that change code without recording anything. Set `"stop_check": "receipt"` or `"off"` in `.guesswork/config.json` to reduce it.

To skip permission prompts for the CLI, allow `Bash(guesswork:*)` in your Claude Code permission settings.

To show open decisions in the status line, call `guesswork status --format statusline` from your status line command. It prints nothing when no decision needs you.

## Other Agent Skills clients use the skill and AGENTS.md

Codex, Cursor, Gemini CLI, OpenCode, and other clients that load Agent Skills can use the skill without hooks:

1. Install the `guesswork` skill folder in the client's skill directory.
2. Run `python3 <skill folder>/scripts/guesswork.py init --agents-md` in the project. It creates `.guesswork/` and adds a short convention to `AGENTS.md`, which most agents read on every task.
3. Invoke the skill when you start building, or rely on the client's automatic skill matching.

Without hooks, the agent depends on the skill and `AGENTS.md` to remember the receipt. Ask for it with "show me the guesswork receipt" when it does not appear.

Hook adapters for other clients are welcome contributions. The `guesswork hook` command reads the same JSON shape that Claude Code sends, so an adapter mostly maps event names and fields.

## Continuous integration reads the ledger from the branch

The repository ships a GitHub Action. It writes a decision summary to the job summary and can post it as a pull request comment. By default it only reports:

```yaml
name: Guesswork
on: pull_request
permissions:
  contents: read
  pull-requests: write
jobs:
  decisions:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0
      - uses: curlymolelabs/design-thinking-skill@main
        with:
          comment: "true"
```

Add `fail-on: high` to block merging while a pull request adds open high-stakes guesses, or `medium` to include medium stakes. Pin the action to a release tag or commit once one exists. `fetch-depth: 0` lets Guesswork compare the branch with its base. Without the comment input, the action needs only `contents: read`.

Any other CI system can run the CLI directly:

```bash
python3 guesswork/scripts/guesswork.py pr --base origin/main
python3 guesswork/scripts/guesswork.py check --base origin/main --fail-on high
```
