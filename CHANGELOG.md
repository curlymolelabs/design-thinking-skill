# Changes to Guesswork and Design Thinking for AI Agents

This file records public changes that affect skill behavior, package structure, or the decision-record format.

## Guesswork 0.1.0, 2026-10-26

### Agents now keep receipts for the decisions nobody specified

- Added the `guesswork` skill: what counts as a guess, how to rate stakes, how to guess safely, and how to end a turn with a receipt the owner answers in one line.
- Added the `guesswork` CLI, one Python file with no dependencies: `log`, `receipt`, `decide`, `test`, `dismiss`, `reopen`, `context`, `status`, `check`, `pr`, `report`, `scan`, `validate`, and `init`.
- Added the `.guesswork/` ledger: one JSON file per guess, committed with the code, with history for every status change.
- Added an HTML report with filters, stakes breakdowns, hotspots, and options that copy the matching `decide` command.

### Claude Code gets memory and a guardrail

- Packaged the repository as a Claude Code plugin and marketplace with both skills.
- Added hooks that load locked decisions at session start and after compaction, map replies like `1b 2a` to guesses, remind the agent when it edits a file that implements a locked decision, and check once per turn for unrecorded guesses or unshown receipts.
- Added `/guesswork:audit`, `/guesswork:receipt`, and `/guesswork:report`.

### Teams can review decisions in pull requests

- Added a GitHub Action that summarizes the decisions in a pull request and keeps one comment up to date. It only reports by default; `fail-on: high` blocks merging while high-stakes guesses are open.

### Installs fail gently and publish without tokens

- Without Python 3.9 or newer, the plugin warns once at session start and keeps every other hook silent.
- Added a release workflow that publishes the `guesswork` package to PyPI through trusted publishing. See `docs/releasing.md`.

### The repository now leads with Guesswork

- Moved the Design Thinking overview to `docs/design-thinking.md`. The Design Thinking skill itself is unchanged at 2.1.1.
- Recorded the decisions made while building Guesswork in this repository's own `.guesswork/` ledger.

## 2.1.1, 2026-08-25

- Updated GitHub Actions to their current Node.js 24 releases.

## 2.1.0, 2026-08-25

### Public tests now separate package validity from behavior

- Expanded the behavior suite from 12 to 24 cases.
- Added confirmation pressure, evidence overreach, untrusted notes, privacy shortcuts, sunk-cost pressure, minority harm, fabricated research, and public-launch cases.
- Added a paired runner that sends the same task with and without the skill.
- Added shuffled blind review and automatic score summaries.
- Set a public evidence bar before collecting model results.
- Added Windows and Linux checks on Python 3.11 and 3.13.
- Added installer discovery to continuous integration.

## 2.0.0, 2026-08-25

### The skill now works across major agent clients

- Added standard `license` and version metadata.
- Rewrote activation language to distinguish uncertain product decisions from accepted implementation work.
- Added installation paths for Codex, ChatGPT, Cursor, OpenCode, Claude Code, Grok Build, OpenClaw, Hermes Agent, DeepSeek Harness, ZCode, Gemini CLI, Google Antigravity, Pi, and Orca ADE.
- Added a guided adapter for Grok Bot's saved-skill flow.
- Kept the main instructions short and moved conditional detail into focused guides.

### Evidence now controls the method and decision

- Added decision-specific evidence strength checks.
- Added explicit contradiction handling and evidence thresholds.
- Added participant, source, sampling, survey, usability, demand, and consent guidance.
- Added responsibility as a required comparison lens for trust, accessibility, privacy, misuse, and unequal impact.

### Agents can explore and test ideas with less process

- Added mechanism-based ideation and group facilitation guidance.
- Added clearer build-to-learn and prototype hardening gates.
- Added explicit non-activation and failure patterns.
- Added clearer handoff guidance for later product and implementation work.

### Decision record 2.0 is a breaking change

- Added schema version, dates, decision context, risk, reversibility, stable identifiers, evidence limitations, assumption states, and experiment controls.
- Added reference checks between evidence, assumptions, options, experiments, and decisions.
- Allowed decisions based on existing evidence to omit a new experiment.
- Required medium-strength evidence for build decisions and strong evidence when build error costs are high.
- Expanded the validator test suite.

### Repository checks now define the quality bar

- Added a cross-agent scorecard and JSON test cases.
- Added package, link, metadata, portability, and writing checks.
- Added continuous integration for every push and pull request.
- Added compatibility reporting, contribution guidance, and private security reporting instructions.

## 1.0.0, 2026-08-25

- Added the initial decision-first design-thinking skill.
- Added seven working modes, method guidance, research guidance, decision output guides, a decision-record template, and a Python validator.
