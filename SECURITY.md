# Report security and privacy problems privately

This repository contains agent instructions, a local Python validator, the Guesswork CLI, Claude Code hooks, and a GitHub Action. None of them require network access, credentials, telemetry, or external services, except that the action posts a pull request comment when you ask it to.

## Report a vulnerability

Use GitHub's private vulnerability reporting feature for this repository. Do not open a public issue for a suspected vulnerability, exposed credential, or private data leak.

Include:

- the affected file and version;
- steps that reproduce the problem;
- the expected and observed behavior;
- the likely impact;
- a suggested correction, if available.

## Review third-party skill instructions

Agent skills can influence tool use and may include executable files. Read third-party skills before installing them, keep agent permissions narrow, and test unfamiliar instructions in an isolated workspace.

This package's validator uses only Python's standard library. It reads one supplied JSON file and writes validation results to standard output.

## Treat the Guesswork ledger like other repository instructions

Guesswork hooks place ledger titles and decisions into the agent's context, the same way an agent reads `CLAUDE.md` or `AGENTS.md`. Review changes to `.guesswork/` in pull requests from people you do not trust, as you would review changes to those files.

The ledger is committed with your code. Agents are told never to write secrets, credentials, or personal data into it, and in a public repository it is public. Hook session state stays in your user cache folder and never enters the repository.
