from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "design-thinking"
SKILL = SKILL_DIR / "SKILL.md"
EVALUATION_CASES = ROOT / "tests" / "evaluation-cases.json"


class SkillPackageTests(unittest.TestCase):
    def test_skill_frontmatter_is_valid(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        frontmatter = text.split("---", 2)[1]
        top_level_keys = set(re.findall(r"^([a-z][a-z0-9-]*):", frontmatter, re.MULTILINE))
        self.assertEqual(
            top_level_keys,
            {"name", "description", "license", "metadata"},
        )
        self.assertIn("name: design-thinking", frontmatter)
        description = re.search(r"^description: (.+)$", frontmatter, re.MULTILINE)
        self.assertIsNotNone(description)
        assert description is not None
        self.assertLessEqual(len(description.group(1)), 1024)
        self.assertEqual(SKILL_DIR.name, "design-thinking")

    def test_main_skill_stays_within_progressive_loading_limit(self) -> None:
        lines = SKILL.read_text(encoding="utf-8").splitlines()
        self.assertLess(len(lines), 500)
        self.assertLess(len(" ".join(lines).split()), 5000)

    def test_all_relative_markdown_links_resolve(self) -> None:
        markdown_files = [path for path in ROOT.rglob("*.md") if ".git" not in path.parts]
        for markdown in markdown_files:
            text = markdown.read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#") or target.startswith("mailto:"):
                    continue
                path_text = target.split("#", 1)[0]
                resolved = (markdown.parent / path_text).resolve()
                self.assertTrue(resolved.exists(), f"Broken link in {markdown}: {target}")

    def test_referenced_skill_resources_exist(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        expected = {
            "references/evidence-and-decisions.md",
            "references/methods.md",
            "references/ideation-and-facilitation.md",
            "references/research-and-testing.md",
            "references/agentic-product-development.md",
            "references/decision-output-guide.md",
            "assets/decision-record-template.json",
            "scripts/check_decision_record.py",
        }
        for relative in expected:
            self.assertIn(relative, text)
            self.assertTrue((SKILL_DIR / relative).exists())

    def test_openai_metadata_matches_skill(self) -> None:
        metadata = (SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Design Thinking"', metadata)
        self.assertIn("$design-thinking", metadata)
        self.assertIn("allow_implicit_invocation: true", metadata)

    def test_evaluation_cases_cover_modes_and_nonactivation(self) -> None:
        cases = json.loads(EVALUATION_CASES.read_text(encoding="utf-8"))
        ids = [case["id"] for case in cases]
        self.assertEqual(len(ids), len(set(ids)))
        active_modes = {case["mode"] for case in cases if case["should_activate"]}
        expected_modes = {"frame", "discover", "ideate", "prototype", "learn", "decide", "cycle"}
        self.assertTrue(expected_modes.issubset(active_modes))
        self.assertGreaterEqual(sum(not case["should_activate"] for case in cases), 2)
        for case in cases:
            self.assertTrue(case["category"].strip())
            self.assertTrue(case["prompt"].strip())
            self.assertTrue(case["must"])
            self.assertTrue(case["must_not"])

    def test_public_text_contains_no_long_dash_characters(self) -> None:
        checked_extensions = {".md", ".py", ".json", ".yaml", ".yml"}
        for path in ROOT.rglob("*"):
            if ".git" in path.parts or not path.is_file() or path.suffix not in checked_extensions:
                continue
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("\u2014", text, f"Em dash found in {path}")
            self.assertNotIn("\u2013", text, f"En dash found in {path}")

    def test_public_files_exclude_sensitive_values_and_local_paths(self) -> None:
        secret_patterns = [
            r"AKIA[0-9A-Z]{16}",
            r"gh[pousr]_[A-Za-z0-9_]{20,}",
            r"github_pat_[A-Za-z0-9_]{20,}",
            r"sk-[A-Za-z0-9_-]{20,}",
            r"xox[baprs]-[A-Za-z0-9-]{10,}",
            r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
        ]
        private_path_patterns = [
            r"[A-Za-z]:\\" + r"Users\\[^\\\s]+",
            "/" + r"Users/[^/\s]+",
            "/" + r"home/[^/\s]+",
        ]
        email_pattern = r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"
        extensions = {".md", ".py", ".json", ".yaml", ".yml"}
        for path in ROOT.rglob("*"):
            if ".git" in path.parts or not path.is_file() or path.suffix not in extensions:
                continue
            text = path.read_text(encoding="utf-8")
            for pattern in secret_patterns:
                self.assertIsNone(re.search(pattern, text), f"Secret-like value found in {path}")
            for pattern in private_path_patterns:
                self.assertIsNone(re.search(pattern, text), f"Local user path found in {path}")
            self.assertIsNone(re.search(email_pattern, text, re.IGNORECASE), f"Email found in {path}")

    def test_external_links_stay_with_the_public_project(self) -> None:
        allowed_prefixes = {
            "https://github.com/curlymolelabs/guesswork",
            "https://img.shields.io/",
        }
        for path in ROOT.rglob("*"):
            if ".git" in path.parts or not path.is_file() or path.suffix != ".md":
                continue
            # Evaluation transcripts are kept verbatim, including any URLs the agents wrote.
            if "evaluation" in path.parts and "outputs" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            for url in re.findall(r"https?://[^\s)]+", text):
                self.assertTrue(
                    any(url.startswith(prefix) for prefix in allowed_prefixes),
                    f"Unexpected external link in {path}: {url}",
                )


if __name__ == "__main__":
    unittest.main()
