# Report security and privacy problems privately

This repository contains instructions and a local Python validator. The skill does not require network access, credentials, telemetry, or external services.

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
