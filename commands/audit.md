---
description: Find the product decisions already hidden in this codebase and put the risky ones in front of you
argument-hint: "[folder or feature to focus on]"
allowed-tools: Bash(guesswork:*), Read, Grep, Glob
---

Audit this codebase for product decisions that nobody wrote down, using the guesswork skill. Focus on: $ARGUMENTS. If no focus was given, cover the whole project.

1. Run `guesswork scan` for candidate lines and `guesswork list --status all` to see what the ledger already records.
2. Read the main flows the candidates point to: sign-up and sign-in, roles and sharing, billing, deletion and retention, exports, notifications, limits, and defaults.
3. Record each real decision in one batch with `guesswork log`. Use `"basis": "inferred"`, put line numbers in `where`, and rate stakes by the cost of being wrong. Skip anything the ledger already holds. Aim for 10 to 25 sharp entries, not an exhaustive list.
4. End your reply with the output of `guesswork receipt`, unchanged, so I can answer in one line.

Do not change any code during the audit.
