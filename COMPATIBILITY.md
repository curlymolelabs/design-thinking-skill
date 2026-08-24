# Install Design Thinking in supported agent clients

This guide shows where each supported client loads the skill. Client behavior can change, so confirm the path if an installation stops working.

Native support means the client discovers the complete `design-thinking` folder, including its guides, script, and template.

## Native Agent Skills clients load the complete package

| Client | Support | Recommended installation |
|---|---|---|
| Codex | Native | `npx skills add https://github.com/curlymolelabs/design-thinking-skill --skill design-thinking` |
| Claude Code | Native | Use the same installer, or copy the folder to `.claude/skills/design-thinking/` |
| Cursor | Native | Use the same installer, or copy the folder to `.agents/skills/design-thinking/` |
| OpenCode | Native | Use the same installer, or copy the folder to `.agents/skills/design-thinking/` |
| Grok Build | Native | Use the same installer, or copy the folder to `.grok/skills/design-thinking/` |
| OpenClaw | Native | Clone the repository, then run `openclaw skills install ./design-thinking --as design-thinking` |
| Hermes Agent | Native | Run `hermes skills install curlymolelabs/design-thinking-skill/design-thinking` |
| DeepSeek Harness | Native | Copy the folder to `.dsh/skills/design-thinking/` or `.agents/skills/design-thinking/` |
| ZCode | Native | Import the Codex or Claude copy in Settings > Skills, or copy it to `~/.zcode/skills/design-thinking/` |
| Gemini CLI | Native | Run `gemini skills install https://github.com/curlymolelabs/design-thinking-skill` |
| Google Antigravity | Native | Copy the folder to `.agents/skills/design-thinking/` for the current project |
| Pi | Native | Use `.agents/skills/design-thinking/`, `.pi/skills/design-thinking/`, or `--skill <path>` |
| ChatGPT | Managed upload | Upload the complete folder or its zip through the Skills interface when available |

After installation, start a fresh session or refresh the client's skill list. Then invoke:

```text
Use $design-thinking to decide who this product is for, what evidence exists, and the fastest credible test.
```

Clients with slash commands may expose the skill as `/design-thinking`, `/skill:design-thinking`, or a selectable skill. The client's own command syntax takes precedence.

## OpenClaw installs the cloned skill directory

OpenClaw accepts an Agent Skills-compatible directory whose root contains `SKILL.md`.

```bash
git clone https://github.com/curlymolelabs/design-thinking-skill.git
cd design-thinking-skill
openclaw skills install ./design-thinking --as design-thinking
```

Add `--global` when every local OpenClaw agent should see the skill. Review third-party skill instructions before enabling them.

## Hermes Agent installs the repository subdirectory

Hermes supports direct GitHub repository and path identifiers. It scans and installs the referenced support files with the skill.

```bash
hermes skills inspect curlymolelabs/design-thinking-skill/design-thinking
hermes skills install curlymolelabs/design-thinking-skill/design-thinking
```

Hermes may ask you to confirm the installation after its security scan.

## DeepSeek Harness reads the shared project location

DeepSeek Harness accepts a directory bundle at either project skill root. It does not discover nested bundles recursively.

```text
<project>/.dsh/skills/design-thinking/SKILL.md
<project>/.agents/skills/design-thinking/SKILL.md
```

Copy the entire folder so linked references, the decision template, and the validator remain available.

## ZCode imports an existing installation

ZCode can import skills already installed for Codex, Claude Code, OpenClaw, and other supported agents.

1. Open Settings > Skills.
2. Select the import control.
3. Choose the existing `design-thinking` skill.
4. Select symlink for shared updates, or copy for an independent installation.
5. Refresh the list and invoke `$design-thinking` in chat.

You can also copy the package to `~/.zcode/skills/design-thinking/`.

## Gemini CLI and Antigravity use Agent Skills folders

Gemini CLI can install the GitHub repository directly:

```bash
gemini skills install https://github.com/curlymolelabs/design-thinking-skill
```

For Antigravity, copy the folder into the shared project convention:

```text
<project>/.agents/skills/design-thinking/SKILL.md
```

Use the client's `/skills` view to confirm discovery after installation.

## Pi discovers the shared skill without an adapter

Pi scans `.agents/skills` recursively.

```text
<project>/.agents/skills/design-thinking/SKILL.md
```

You can also pass the folder directly:

```bash
pi --skill ./design-thinking
```

Use `/skill:design-thinking` when you need to force explicit loading.

## Orca ADE uses the skill through its hosted agent

Orca is an agent development environment, not a separate model harness for this package. Its skill view scans installed homes for Codex, Claude Code, shared Agent Skills, and other supported agents.

Install Design Thinking for the agent you run inside Orca. Orca should then display that installation in its skill interface. Confirm the target agent sees the skill before relying on it.

## Grok Bot needs a saved-skill adapter

Grok Bot uses product-managed saved skills instead of direct GitHub package imports. Use [the Grok Bot adapter](adapters/grok-bot.md) to create a Bot-local version.

This adapter preserves the core decision rules. It does not provide the package's Python validator or automatic access to every reference file.

Client behavior changes over time. Please open a compatibility report when an official path or command changes.
