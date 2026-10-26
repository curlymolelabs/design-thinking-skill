from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "guesswork" / "scripts" / "guesswork.py"


def load_module():
    spec = importlib.util.spec_from_file_location("guesswork_cli", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gw = load_module()

SAMPLE = [
    {
        "title": "Deleting a workspace is permanent and immediate",
        "why": "No retention rule was given",
        "category": "data",
        "stakes": "high",
        "reversible": False,
        "where": ["src/workspaces.ts:2"],
        "alternatives": ["30-day soft delete with restore", "Require typing the name to confirm"],
    },
    {
        "title": "Trials convert to paid on day 14 without a reminder",
        "category": "money",
        "stakes": "high",
        "where": ["src/billing.ts"],
        "alternatives": ["Email a reminder 3 days before"],
    },
    {
        "title": "Any member can invite new members",
        "category": "access",
        "stakes": "medium",
        "where": ["src/invites.ts"],
        "alternatives": ["Only admins can invite"],
    },
    {
        "title": "Search results show 20 items per page",
        "category": "limits",
        "stakes": "low",
        "where": ["src/search.ts"],
    },
]


class Sandbox(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name).resolve()
        self.root = base / "project"
        self.root.mkdir()
        self.env = dict(os.environ)
        for name in ("CLAUDE_PROJECT_DIR", "GUESSWORK_DISABLE", "GITHUB_BASE_REF", "GUESSWORK_AGENT"):
            self.env.pop(name, None)
        self.env.update(
            {
                "GUESSWORK_STATE_DIR": str(base / "state"),
                "GIT_AUTHOR_NAME": "test",
                "GIT_AUTHOR_EMAIL": "test",
                "GIT_COMMITTER_NAME": "test",
                "GIT_COMMITTER_EMAIL": "test",
            }
        )
        self.git("init", "-q")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def git(self, *args: str) -> str:
        result = subprocess.run(["git", *args], cwd=self.root, env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        return result.stdout

    def run_cli(self, *args: str, input_text: str | None = None, expect: int | None = 0) -> subprocess.CompletedProcess:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root), *args],
            cwd=self.root,
            env=self.env,
            input=input_text if input_text is not None else "",
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if expect is not None:
            self.assertEqual(result.returncode, expect, msg=result.stdout + result.stderr)
        return result

    def hook(self, event: str, payload: dict) -> dict | None:
        body = {"session_id": "s1", "cwd": str(self.root), **payload}
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "hook", event],
            cwd=self.root,
            env=self.env,
            input=json.dumps(body),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        return json.loads(result.stdout) if result.stdout.strip() else None

    def log_sample(self) -> None:
        self.run_cli("log", input_text=json.dumps(SAMPLE))

    def guess_files(self) -> list[Path]:
        return sorted((self.root / ".guesswork" / "guesses").glob("*.json"))

    def guess(self, prefix: str) -> dict:
        matches = [path for path in self.guess_files() if path.stem.startswith(prefix)]
        self.assertEqual(len(matches), 1, msg=f"{prefix}: {matches}")
        return json.loads(matches[0].read_text(encoding="utf-8"))

    def write(self, rel: str, text: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path


class LogTests(Sandbox):
    def test_batch_log_creates_valid_files_and_scaffolding(self) -> None:
        result = self.run_cli("log", input_text=json.dumps(SAMPLE))
        files = self.guess_files()
        self.assertEqual(len(files), 4)
        for path in files:
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(gw.validate_guess(data, path.name), [])
            self.assertEqual(data["status"], "open")
            self.assertTrue(data["id"].startswith("g-"))
        self.assertTrue((self.root / ".guesswork" / "README.md").exists())
        self.assertIn("report.html", (self.root / ".guesswork" / ".gitignore").read_text(encoding="utf-8"))
        self.assertIn("Created .guesswork/", result.stdout)
        self.assertIn("end your reply with the output of `guesswork receipt`", result.stdout)

    def test_flags_log_a_single_guess(self) -> None:
        self.run_cli(
            "log", "--title", "Sessions last 30 days", "--category", "security", "--stakes", "medium",
            "--irreversible", "--where", "src/auth.py", "--alt", "Sessions last 1 day",
        )
        guess = self.guess("g-sessions-last-30-days")
        self.assertFalse(guess["reversible"])
        self.assertEqual(guess["alternatives"], ["Sessions last 1 day"])

    def test_invalid_batch_writes_nothing(self) -> None:
        bad = [SAMPLE[0], {"title": "Exports include emails", "category": "privacy", "stakes": "huge"}]
        result = self.run_cli("log", input_text=json.dumps(bad), expect=2)
        self.assertIn("stakes must be high, medium, or low", result.stderr)
        self.assertEqual(self.guess_files(), [])

    def test_relogging_an_open_title_updates_instead_of_duplicating(self) -> None:
        self.log_sample()
        again = dict(SAMPLE[2], where=["src/team.ts"], alternatives=["Owners approve each invite"])
        result = self.run_cli("log", input_text=json.dumps([again]))
        self.assertIn("~ g-", result.stdout)
        self.assertEqual(len(self.guess_files()), 4)
        guess = self.guess("g-any-member")
        self.assertEqual(guess["where"], ["src/invites.ts", "src/team.ts"])
        self.assertEqual(guess["alternatives"], ["Only admins can invite", "Owners approve each invite"])

    def test_relogging_a_decided_title_keeps_the_decision(self) -> None:
        self.log_sample()
        self.run_cli("decide", "g-any-member=b")
        result = self.run_cli("log", input_text=json.dumps([SAMPLE[2]]))
        self.assertIn("already decided: Only admins can invite", result.stdout)
        self.assertEqual(self.guess("g-any-member")["status"], "decided")

    def test_absolute_paths_are_stored_relative_with_anchor(self) -> None:
        target = self.root / "src" / "a.ts"
        entry = dict(SAMPLE[3], where=[f"{target}:12"])
        self.run_cli("log", input_text=json.dumps([entry]))
        self.assertEqual(self.guess("g-search")["where"], ["src/a.ts:12"])

    def test_supersedes_closes_the_old_guess(self) -> None:
        self.log_sample()
        old = self.guess("g-trials")["id"]
        new = {"title": "Trials last 7 days", "category": "money", "stakes": "high", "supersedes": old}
        self.run_cli("log", input_text=json.dumps([new]))
        self.assertEqual(self.guess("g-trials-convert")["status"], "superseded")
        self.assertEqual(self.guess("g-trials-convert")["superseded_by"], self.guess("g-trials-last-7")["id"])


class ReceiptAndDecisionTests(Sandbox):
    def test_receipt_ranks_by_risk_and_counts_low_stakes(self) -> None:
        self.log_sample()
        text = self.run_cli("receipt").stdout
        first = text.index("Deleting a workspace")
        second = text.index("Trials convert")
        third = text.index("Any member can invite")
        self.assertLess(first, second)
        self.assertLess(second, third)
        self.assertIn("Also decided, low stakes (say so to change any): Search results show 20 items per page", text)
        self.assertIn("3 decisions need you (2 high stakes)", text)
        self.assertIn("**a** Keep as built", text)

    def test_receipt_counts_low_stakes_when_there_are_many(self) -> None:
        many = [{"title": f"Page {n} shows 20 rows", "category": "ux", "stakes": "low"} for n in range(4)]
        self.run_cli("log", input_text=json.dumps(many))
        text = self.run_cli("receipt").stdout
        self.assertIn("no decisions need you. 4 low-stakes guesses logged", text)
        self.assertNotIn("Page 0", text)

    def test_log_flags_titles_that_bundle_two_decisions(self) -> None:
        bundled = {"title": "Photos must be JPEG or PNG and at most 2 MB", "category": "limits", "stakes": "medium"}
        result = self.run_cli("log", input_text=json.dumps([bundled, SAMPLE[3]]))
        self.assertEqual(result.stdout.count("holds two decisions"), 1)

    def test_bundling_check_skips_restatements(self) -> None:
        # Titles taken from the 3.1.0 evaluation: the first two join two settings, the rest are one decision each.
        self.assertTrue(gw.looks_bundled("Photos must be JPEG or PNG and at most 2 MB"))
        self.assertTrue(gw.looks_bundled("The trial lasts 14 days and owners get a reminder 3 days before it ends"))
        self.assertFalse(gw.looks_bundled("Only team owners and admins can export customers; members get a 403"))
        self.assertFalse(gw.looks_bundled("Inviting the same email again cancels the old link and sends a fresh one"))
        self.assertFalse(gw.looks_bundled("Deleted accounts can be restored for 30 days before name and email are erased"))

    def test_receipt_lists_decisions_past_the_limit_on_one_line(self) -> None:
        many = [
            {"title": f"Limit {n} allows {n + 1} exports a day", "category": "limits", "stakes": "medium", "alternatives": ["No limit"]}
            for n in range(7)
        ]
        self.run_cli("log", input_text=json.dumps(many))
        text = self.run_cli("receipt").stdout
        self.assertIn("7 decisions need you", text)
        self.assertNotIn("more decision", text)
        brief_lines = [line for line in text.splitlines() if line.startswith(("6. ", "7. "))]
        self.assertEqual(len(brief_lines), 2)
        self.assertIn("**b** No limit", brief_lines[0])
        self.run_cli("decide", "7b")
        decided = [g for g in map(json.loads, (p.read_text() for p in (self.root / ".guesswork" / "guesses").glob("*.json"))) if g["status"] == "decided"]
        self.assertEqual(len(decided), 1)
        self.assertEqual(decided[0]["resolution"]["decision"], "No limit")

    def test_receipt_json_and_limit(self) -> None:
        self.log_sample()
        payload = json.loads(self.run_cli("receipt", "--format", "json", "--limit", "2").stdout)
        self.assertEqual([item["n"] for item in payload["items"]], [1, 2])
        self.assertEqual(payload["more"], 1)
        self.assertEqual(payload["items"][0]["options"][1]["key"], "b")

    def test_decide_by_receipt_numbers(self) -> None:
        self.log_sample()
        self.run_cli("receipt")
        result = self.run_cli("decide", "1b", "2a", "--note", "owner reply")
        self.assertIn("Update the code so it matches these decisions", result.stdout)
        deleted = self.guess("g-deleting")
        self.assertEqual(deleted["status"], "decided")
        self.assertEqual(deleted["resolution"]["choice"], "b")
        self.assertEqual(deleted["resolution"]["decision"], "30-day soft delete with restore")
        self.assertEqual(deleted["resolution"]["note"], "owner reply")
        trials = self.guess("g-trials")
        self.assertEqual(trials["resolution"]["decision"], trials["title"])
        self.assertEqual([entry["status"] for entry in trials["history"]], ["open", "decided"])

    def test_decide_all_and_custom(self) -> None:
        self.log_sample()
        self.run_cli("receipt", "--limit", "2")
        self.run_cli("decide", "g-any-member", "--custom", "Admins and owners can invite")
        # Item 3 sits past the limit, on one line, so "all a" covers it too unless it was already answered.
        self.run_cli("decide", "--all", "a")
        self.assertEqual(self.guess("g-deleting")["status"], "decided")
        guess = self.guess("g-any-member")
        self.assertEqual(guess["resolution"]["choice"], "custom")
        self.assertEqual(guess["resolution"]["decision"], "Admins and owners can invite")

    def test_decide_rejects_unknown_options_and_missing_receipt(self) -> None:
        self.log_sample()
        result = self.run_cli("decide", "1a", expect=2)
        self.assertIn("no item 1 in the latest receipt", result.stderr)
        self.run_cli("receipt")
        result = self.run_cli("decide", "3c", expect=2)
        self.assertIn("has options a, b, not c", result.stderr)
        self.assertEqual(self.guess("g-any-member")["status"], "open")

    def test_test_dismiss_and_reopen(self) -> None:
        self.log_sample()
        self.run_cli("test", "g-trials", "--plan", "Fake-door upgrade prompt for two weeks")
        self.assertEqual(self.guess("g-trials")["status"], "testing")
        self.run_cli("dismiss", "g-search", "--note", "Not a product decision")
        self.assertEqual(self.guess("g-search")["status"], "dismissed")
        self.run_cli("reopen", "g-search")
        guess = self.guess("g-search")
        self.assertEqual(guess["status"], "open")
        self.assertEqual([entry["status"] for entry in guess["history"]], ["open", "dismissed", "open"])

    def test_context_shows_locked_decisions_for_a_file(self) -> None:
        self.log_sample()
        self.run_cli("decide", "g-deleting=b")
        text = self.run_cli("context", "src/workspaces.ts").stdout
        self.assertIn("Locked decisions for src/workspaces.ts", text)
        self.assertIn("30-day soft delete with restore", text)
        self.assertNotIn("Trials", text)
        self.assertIn("No recorded decisions", self.run_cli("context", "README.md").stdout)

    def test_status_formats(self) -> None:
        self.log_sample()
        self.run_cli("decide", "g-deleting=a")
        self.assertIn("3 open (1 high, 1 medium), 1 decided", self.run_cli("status").stdout)
        self.assertEqual(self.run_cli("status", "--format", "statusline").stdout.strip(), "guesswork: 2 need you")
        counts = json.loads(self.run_cli("status", "--format", "json").stdout)
        self.assertAlmostEqual(counts["coverage"], 1 / 3)


class ReplyParsingTests(unittest.TestCase):
    def receipt(self, count: int = 3, age: float = 0) -> dict:
        return {"at": time.time() - age, "items": [{"n": n, "id": f"g-{n}", "keys": ["a", "b"]} for n in range(1, count + 1)]}

    def test_pure_picks_parse(self) -> None:
        self.assertEqual(gw.parse_reply("1b 2a, 3a please", self.receipt()), [(1, "b"), (2, "a"), (3, "a")])
        self.assertEqual(gw.parse_reply("1: b and 2) a", self.receipt()), [(1, "b"), (2, "a")])

    def test_all_forms(self) -> None:
        self.assertEqual(gw.parse_reply("all a", self.receipt(2)), [(1, "a"), (2, "a")])
        self.assertEqual(gw.parse_reply("Keep all.", self.receipt(2)), [(1, "a"), (2, "a")])
        self.assertEqual(gw.parse_reply("all b", self.receipt(2)), [(1, "b"), (2, "b")])

    def test_other_messages_do_not_parse(self) -> None:
        self.assertEqual(gw.parse_reply("add a settings page with 2 tabs", self.receipt()), [])
        self.assertEqual(gw.parse_reply("1b and also make the button blue", self.receipt()), [])
        self.assertEqual(gw.parse_reply("4b", self.receipt()), [])
        self.assertEqual(gw.parse_reply("1b", self.receipt(age=2 * 24 * 3600)), [])
        self.assertEqual(gw.parse_reply("1b", None), [])


class HookTests(Sandbox):
    def test_session_start_without_ledger_states_the_convention(self) -> None:
        output = self.hook("session-start", {"source": "startup"})
        assert output is not None
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Project convention", context)
        self.assertFalse((self.root / ".guesswork").exists())

    def test_session_start_lists_locked_decisions(self) -> None:
        self.log_sample()
        self.run_cli("decide", "g-deleting=b")
        output = self.hook("session-start", {"source": "compact"})
        assert output is not None
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Locked decisions", context)
        self.assertIn("30-day soft delete with restore", context)
        self.assertIn("Open guesses waiting for the owner: 1 high, 1 medium, 1 low stakes", context)

    def test_prompt_hook_maps_a_receipt_reply(self) -> None:
        self.log_sample()
        self.run_cli("receipt")
        output = self.hook("prompt", {"prompt": "1b 2a"})
        assert output is not None
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn('change to "30-day soft delete with restore"', context)
        self.assertIn("guesswork decide 1b 2a", context)
        self.assertIsNone(self.hook("prompt", {"prompt": "please add dark mode"}))

    def test_post_edit_blocks_invalid_guess_files(self) -> None:
        path = self.write(".guesswork/guesses/g-broken.json", json.dumps({"schema": "guesswork/1", "id": "g-broken"}))
        output = self.hook("post-edit", {"tool_name": "Write", "tool_input": {"file_path": str(path)}})
        assert output is not None
        self.assertEqual(output["decision"], "block")
        self.assertIn("title must state the decision as built", output["reason"])

    def test_post_edit_announces_locked_decisions_once(self) -> None:
        self.log_sample()
        self.run_cli("decide", "g-deleting=b")
        target = self.write("src/workspaces.ts", "export {}\n")
        payload = {"tool_name": "Edit", "tool_input": {"file_path": str(target)}}
        output = self.hook("post-edit", payload)
        assert output is not None
        self.assertIn("30-day soft delete with restore", output["hookSpecificOutput"]["additionalContext"])
        self.assertIsNone(self.hook("post-edit", payload))

    def test_stop_nudges_once_after_unrecorded_code_changes(self) -> None:
        self.assertIsNone(self.hook("prompt", {"prompt": "add an export button"}))
        self.write("src/export.ts", "export const FORMAT = 'csv'\n")
        output = self.hook("stop", {"last_assistant_message": "Done."})
        assert output is not None
        self.assertEqual(output["decision"], "block")
        self.assertIn("src/export.ts", output["reason"])
        self.assertIsNone(self.hook("stop", {"last_assistant_message": "Guesswork: no new guesses."}))
        self.assertIsNone(self.hook("stop", {"stop_hook_active": True}))

    def test_stop_ignores_markdown_only_turns(self) -> None:
        self.hook("prompt", {"prompt": "update the readme"})
        self.write("README.md", "# Notes\n")
        self.assertIsNone(self.hook("stop", {"last_assistant_message": "Updated."}))

    def test_stop_asks_for_the_receipt_when_decisions_were_not_shown(self) -> None:
        self.hook("prompt", {"prompt": "add exports"})
        self.run_cli("log", "--title", "Exports include member emails", "--category", "privacy", "--stakes", "high")
        output = self.hook("stop", {"last_assistant_message": "Added exports."})
        assert output is not None
        self.assertIn("guesswork receipt", output["reason"])
        self.hook("prompt", {"prompt": "show me"})
        self.run_cli("log", "--title", "Exports run nightly", "--category", "performance", "--stakes", "medium")
        self.assertIsNone(self.hook("stop", {"last_assistant_message": "**Guesswork** · 2 decisions need you"}))

    def test_stop_check_can_be_turned_off(self) -> None:
        self.write(".guesswork/config.json", json.dumps({"stop_check": "off"}))
        self.hook("prompt", {"prompt": "add a page"})
        self.write("src/page.ts", "export {}\n")
        self.assertIsNone(self.hook("stop", {}))
        self.write(".guesswork/config.json", json.dumps({"stop_check": "nudge"}))
        self.env["GUESSWORK_DISABLE"] = "1"
        self.hook("prompt", {"prompt": "add a page"})
        self.write("src/page2.ts", "export {}\n")
        self.assertIsNone(self.hook("stop", {}))

    def test_hooks_survive_bad_input(self) -> None:
        for event in ("session-start", "prompt", "post-edit", "stop"):
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "hook", event],
                cwd=self.root, env=self.env, input="not json", capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, msg=event)


class GitTests(Sandbox):
    def commit_base(self) -> None:
        self.write("src/app.ts", "export {}\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "base")
        self.git("branch", "-M", "main")
        self.git("checkout", "-qb", "feature")

    def test_pr_summary_lists_the_decisions_on_a_branch(self) -> None:
        self.commit_base()
        self.log_sample()
        self.run_cli("decide", "g-trials=b")
        self.git("add", "-A")
        self.git("commit", "-qm", "feature")
        text = self.run_cli("pr", "--base", "main").stdout
        self.assertIn(gw.PR_MARKER, text)
        self.assertIn("4 product decisions in this change", text)
        self.assertIn("2 decisions still need an owner, including 1 with high stakes", text)
        self.assertIn("Email a reminder 3 days before", text)
        self.assertIn("Changed by owner in this change", text)
        self.assertIn("1 low-stakes decision", text)

    def test_pr_without_changes(self) -> None:
        self.commit_base()
        self.assertIn("no recorded product decisions", self.run_cli("pr", "--base", "main").stdout)

    def test_check_gates_open_high_stakes_guesses(self) -> None:
        self.commit_base()
        self.log_sample()
        result = self.run_cli("check", expect=1)
        self.assertIn("2 open guesses at or above high stakes", result.stdout)
        self.run_cli("check", "--fail-on", "never")
        self.run_cli("decide", "g-deleting=a", "g-trials=b")
        self.run_cli("check", "--base", "main")
        self.run_cli("check", "--base", "main", "--fail-on", "medium", expect=1)


class ReportScanValidateTests(Sandbox):
    def test_report_is_self_contained_and_escaped(self) -> None:
        entry = dict(SAMPLE[0], title="Deleting <script>alert(1)</script> is permanent")
        self.run_cli("log", input_text=json.dumps([entry, SAMPLE[2]]))
        self.run_cli("decide", "g-any-member=b")
        self.run_cli("report", "--title", "demo")
        text = (self.root / ".guesswork" / "report.html").read_text(encoding="utf-8")
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", text)
        self.assertNotIn("<script>alert(1)", text)
        self.assertNotIn("http://", text)
        self.assertNotIn("https://", text)
        self.assertIn("1 decision needs you", text)
        self.assertIn("Only admins can invite", text)

    def test_scan_finds_decisions_and_skips_tests(self) -> None:
        source = "SESSION_TTL_SECONDS = 60 * 60 * 24 * 30\nTRIAL_PRICE_CENTS = 0\nFREE_PLAN_PROJECT_LIMIT = 3\nanalytics.track('signup', {'ip_address': ip, 'plan': plan})\n"
        self.write("src/settings.py", source)
        self.write("tests/test_settings.py", source)
        payload = json.loads(self.run_cli("scan", "--json").stdout)
        paths = {item["path"] for item in payload}
        categories = {item["category"] for item in payload}
        self.assertEqual(paths, {"src/settings.py"})
        self.assertTrue({"security", "money", "privacy"}.issubset(categories))
        by_line = {item["line"]: item["category"] for item in payload}
        self.assertEqual(by_line[4], "privacy")
        self.assertEqual(by_line[3], "limits")

    def test_validate_reports_broken_files(self) -> None:
        self.log_sample()
        self.run_cli("validate")
        self.write(".guesswork/guesses/g-bad.json", "{not json")
        result = self.run_cli("validate", expect=2)
        self.assertIn("g-bad.json: not valid JSON", result.stdout)


class DemoTests(Sandbox):
    def test_demo_builds_a_project_with_a_receipt_and_report(self) -> None:
        target = self.root / "demo"
        result = self.run_cli("demo", "--dir", str(target))
        self.assertIn("4 decisions need you (2 high stakes)", result.stdout)
        self.assertTrue((target / ".guesswork" / "report.html").exists())
        self.assertIn("decided g-workspace", self.run_cli("--root", str(target), "decide", "1b").stdout)
        again = self.run_cli("demo", "--dir", str(target), expect=2)
        self.assertIn("already has a ledger", again.stderr)


class HelperTests(unittest.TestCase):
    def test_slugify(self) -> None:
        self.assertEqual(gw.slugify("Exports include every member's email address"), "g-exports-include-every-members-email")
        self.assertEqual(gw.slugify("!!!"), "g-guess")
        self.assertTrue(len(gw.slugify("word " * 40)) <= 42)

    def test_where_matching(self) -> None:
        self.assertTrue(gw.where_matches("src/a.ts:12", "src/a.ts"))
        self.assertTrue(gw.where_matches("src/billing/", "src/billing/plans.ts"))
        self.assertTrue(gw.where_matches("src/**/*.sql", "src/db/schema.sql"))
        self.assertFalse(gw.where_matches("src/a.ts", "src/a.tsx"))

    def test_markdown_cells_cannot_inject_html_or_columns(self) -> None:
        self.assertEqual(gw.md_cell("Terms & <b>bold</b> | more\nlines"), "Terms &amp; &lt;b&gt;bold&lt;/b&gt; \\| more lines")

    def test_validation_messages(self) -> None:
        errors = gw.validate_guess({"schema": "guesswork/1", "id": "Bad Id"})
        self.assertTrue(any(error.startswith("id must look like") for error in errors))
        self.assertTrue(any(error.startswith("category must be one of") for error in errors))


if __name__ == "__main__":
    unittest.main()
