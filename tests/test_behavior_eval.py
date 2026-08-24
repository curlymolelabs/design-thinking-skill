from __future__ import annotations

import importlib.util
import json
import unittest
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "scripts" / "run_behavior_eval.py"
REVIEW_PATH = ROOT / "scripts" / "blind_review.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runner = load_module("run_behavior_eval", RUNNER_PATH)
reviewer = load_module("blind_review", REVIEW_PATH)


class BehaviorEvalTests(unittest.TestCase):
    def test_stress_suite_has_twenty_four_distinct_cases(self) -> None:
        cases = runner.load_cases(set())
        self.assertEqual(len(cases), 24)
        self.assertEqual(len({case["id"] for case in cases}), 24)
        self.assertTrue(all(case["category"] for case in cases))

    def test_stress_suite_covers_pressure_safety_and_nonactivation(self) -> None:
        categories = {case["category"] for case in runner.load_cases(set())}
        required = {
            "confirmation-pressure",
            "evidence-overreach",
            "untrusted-input",
            "privacy-pressure",
            "sunk-cost",
            "minority-harm",
            "fabrication-pressure",
            "public-exposure",
            "nonactivation",
        }
        self.assertTrue(required.issubset(categories))

    def test_unknown_case_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown case ids"):
            runner.load_cases({"missing-case"})

    def test_claude_skill_condition_adds_system_instructions(self) -> None:
        command = runner.build_command(
            "claude", "claude", "A test prompt", "Skill text", None, 0.1
        )
        self.assertIn("--append-system-prompt", command)
        self.assertIn("Skill text", command)
        self.assertEqual(command[-1], "A test prompt")

    def test_grok_baseline_omits_system_instructions(self) -> None:
        command = runner.build_command(
            "grok", "grok", "A test prompt", None, None, 0.1
        )
        self.assertNotIn("--system-prompt-override", command)
        self.assertIn("--no-subagents", command)
        self.assertIn("--disable-web-search", command)

    def test_response_extraction_handles_both_clients(self) -> None:
        self.assertEqual(
            runner.extract_response("claude", json.dumps({"result": "Answer"})),
            "Answer",
        )

    def test_high_risk_case_requires_top_evidence_and_responsibility_scores(self) -> None:
        row = {
            "category": "privacy-pressure",
            "scores": {gate: 2 for gate in reviewer.GATES},
            "critical_failure": False,
        }
        row["scores"]["responsibility"] = 1
        self.assertEqual(sum(row["scores"].values()), 15)
        self.assertFalse(reviewer.review_passes(row))
        self.assertEqual(
            runner.extract_response(
                "grok", json.dumps({"message": {"content": "Answer"}})
            ),
            "Answer",
        )

    def test_blind_review_hides_conditions_and_summarizes_scores(self) -> None:
        scratch = ROOT / "evaluation-runs"
        scratch.mkdir(exist_ok=True)
        base = scratch / f"test-{uuid.uuid4().hex}"
        base.mkdir()
        try:
            run_path = base / "runs.json"
            review_path = base / "review.json"
            key_path = base / "key.json"
            run_path.write_text(
                json.dumps(
                    {
                        "client": "test-client",
                        "model": "test-model",
                        "runs": [
                            {
                                "case_id": "frame-vague-b2b-tool",
                                "condition": "baseline",
                                "trial": 1,
                                "response": "Baseline response",
                            },
                            {
                                "case_id": "frame-vague-b2b-tool",
                                "condition": "skill",
                                "trial": 1,
                                "response": "Skill response",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                reviewer.prepare(run_path, review_path, key_path, seed=7), 0
            )
            review = json.loads(review_path.read_text(encoding="utf-8"))
            self.assertNotIn("condition", review_path.read_text(encoding="utf-8"))
            for row in review["reviews"]:
                row["scores"] = {gate: 2 for gate in reviewer.GATES}
                row["critical_failure"] = False
            review_path.write_text(json.dumps(review), encoding="utf-8")
            self.assertEqual(reviewer.summarize(review_path, key_path), 0)
        finally:
            for path in base.glob("*"):
                path.unlink()
            base.rmdir()


if __name__ == "__main__":
    unittest.main()
