from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "guesswork"
SCRIPT = SKILL_DIR / "scripts" / "guesswork.py"


def frontmatter(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), path
    return text.split("---", 2)[1]


def cli_version() -> str:
    match = re.search(r'^__version__ = "([^"]+)"', SCRIPT.read_text(encoding="utf-8"), re.MULTILINE)
    assert match is not None
    return match.group(1)


class GuessworkSkillTests(unittest.TestCase):
    def test_frontmatter_is_valid(self) -> None:
        meta = frontmatter(SKILL_DIR / "SKILL.md")
        keys = set(re.findall(r"^([a-z][a-z0-9-]*):", meta, re.MULTILINE))
        self.assertEqual(keys, {"name", "description", "license", "metadata"})
        self.assertIn("name: guesswork", meta)
        description = re.search(r"^description: (.+)$", meta, re.MULTILINE)
        assert description is not None
        self.assertLessEqual(len(description.group(1)), 1024)
        self.assertIn(f'version: "{cli_version()}"', meta)

    def test_skill_stays_short_and_links_resolve(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertLess(len(text.splitlines()), 500)
        self.assertLess(len(text.split()), 5000)
        for relative in (
            "references/what-to-record.md",
            "references/receipts-and-replies.md",
            "references/ledger-format.md",
            "references/clients.md",
        ):
            self.assertIn(relative, text)
            self.assertTrue((SKILL_DIR / relative).exists(), relative)

    def test_openai_metadata_matches(self) -> None:
        metadata = (SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Guesswork"', metadata)
        self.assertIn("$guesswork", metadata)


class PluginManifestTests(unittest.TestCase):
    def test_plugin_manifest_points_at_real_skills(self) -> None:
        manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "guesswork")
        self.assertEqual(manifest["version"], cli_version())
        for entry in manifest["skills"]:
            self.assertTrue(entry.startswith("./"))
            self.assertTrue((ROOT / entry / "SKILL.md").exists(), entry)

    def test_marketplace_lists_the_plugin_at_the_root(self) -> None:
        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        self.assertTrue(marketplace["owner"]["name"])
        entries = {plugin["name"]: plugin for plugin in marketplace["plugins"]}
        self.assertEqual(entries["guesswork"]["source"], "./")

    def test_package_versions_agree(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn(f'version = "{cli_version()}"', pyproject)
        self.assertIn('guesswork = "guesswork:main"', pyproject)

    def test_hooks_call_known_events_through_the_launcher(self) -> None:
        sys.path.insert(0, str(SCRIPT.parent))
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location("guesswork_hooks_check", SCRIPT)
            assert spec is not None and spec.loader is not None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        finally:
            sys.path.pop(0)
        config = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        expected = {"SessionStart": "session-start", "UserPromptSubmit": "prompt", "PostToolUse": "post-edit", "Stop": "stop"}
        self.assertEqual(set(config["hooks"]), set(expected))
        for event, groups in config["hooks"].items():
            for group in groups:
                for hook in group["hooks"]:
                    self.assertEqual(hook["type"], "command")
                    self.assertTrue(hook["command"].startswith('"${CLAUDE_PLUGIN_ROOT}"/bin/guesswork hook '))
                    name = hook["command"].rsplit(" ", 1)[-1]
                    self.assertEqual(name, expected[event])
                    self.assertIn(name, module.HOOKS)

    def test_commands_have_descriptions(self) -> None:
        commands = sorted((ROOT / "commands").glob("*.md"))
        self.assertTrue(commands)
        for command in commands:
            self.assertRegex(frontmatter(command), r"(?m)^description: \S")

    def test_action_runs_the_bundled_cli(self) -> None:
        action = (ROOT / "action.yml").read_text(encoding="utf-8")
        self.assertIn("guesswork/scripts/guesswork.py", action)
        self.assertIn("using: composite", action)


class LauncherTests(unittest.TestCase):
    @unittest.skipIf(os.name == "nt", "the launcher is a POSIX shell script")
    def test_launcher_runs_the_cli(self) -> None:
        launcher = ROOT / "bin" / "guesswork"
        self.assertTrue(launcher.read_text(encoding="utf-8").startswith("#!/bin/sh\n"))
        self.assertTrue(os.access(launcher, os.X_OK), "bin/guesswork must be executable")
        result = subprocess.run([str(launcher), "--version"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(result.stdout.strip(), f"guesswork {cli_version()}")

    def test_script_runs_with_this_interpreter(self) -> None:
        result = subprocess.run([sys.executable, str(SCRIPT), "--version"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, msg=result.stderr)


if __name__ == "__main__":
    unittest.main()
