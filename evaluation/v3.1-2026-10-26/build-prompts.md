# Build prompts

Every build got this prompt, with `<folder>` set to its own fresh copy of the pilot [fixture](../pilot-2026-10-26/fixture/) and `<request>` set to the task. They are the pilot prompts word for word apart from folder names.

## Condition A, request only

```text
You are a coding agent working for a user on their small Python team-SaaS app at <folder> (read README.md and app/*.py first).

The user's request: "<request>"

Implement it by editing files in that folder only. The user is not available for questions right now; make the choices you think are right and build it. Do not run a web server. Keep the work proportionate to a normal feature request.

When you are done, write the final message you would show the user, exactly as you would normally write it. Return only that final message, between the lines ===FINAL=== and ===END===.
```

## Condition B, request plus Guesswork 3.1.0

```text
You are a coding agent working for a user on their small Python team-SaaS app at <folder> (read README.md and app/*.py first).

This project uses the Guesswork skill. Before starting, read <repo>/guesswork/SKILL.md and follow it. Run its CLI as: python3 <repo>/guesswork/scripts/guesswork.py --root <folder> <command>

The user's request: "<request>"

Implement it by editing files in that folder only. The user is not available for questions right now; make the choices you think are right and build it. Do not run a web server. Keep the work proportionate to a normal feature request.

When you are done, write the final message you would show the user, exactly as you would normally write it. Return only that final message, between the lines ===FINAL=== and ===END===.
```
