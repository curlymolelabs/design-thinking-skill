# Changes to Design Thinking for AI Agents

This file records public changes that affect skill behavior, package structure, or the decision-record format.

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
