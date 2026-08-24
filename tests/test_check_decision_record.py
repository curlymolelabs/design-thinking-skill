from __future__ import annotations

import importlib.util
import json
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "design-thinking" / "scripts" / "check_decision_record.py"
TEMPLATE = ROOT / "design-thinking" / "assets" / "decision-record-template.json"

spec = importlib.util.spec_from_file_location("check_decision_record", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DecisionRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    def make_decision(self, outcome: str = "build") -> dict:
        record = deepcopy(self.record)
        record["status"] = "decided"
        record["evidence"][0].update(
            {
                "source_type": "observed",
                "strength": "strong",
                "limitations": [],
            }
        )
        record["decision"] = {
            "outcome": outcome,
            "reason": "The observed task result met the declared evidence threshold.",
            "evidence_ids": ["E1"],
            "rejected_option_ids": ["O2"],
            "decided_at": "2026-08-25",
            "unknowns": ["Long-term retention remains unknown."],
            "revisit_trigger": None,
        }
        return record

    def test_template_passes_draft_validation(self) -> None:
        self.assertEqual(module.validate_record(self.record, "draft"), [])

    def test_complete_build_decision_passes(self) -> None:
        self.assertEqual(module.validate_record(self.make_decision(), "decision"), [])

    def test_deferred_decision_requires_revisit_trigger(self) -> None:
        record = self.make_decision("defer")
        errors = module.validate_record(record, "decision")
        self.assertIn(
            "record.decision.revisit_trigger is required when outcome is defer",
            errors,
        )

    def test_unknown_evidence_type_fails(self) -> None:
        self.record["evidence"][0]["source_type"] = "verified-by-agent"
        errors = module.validate_record(self.record, "draft")
        self.assertTrue(any("source_type" in error for error in errors))

    def test_one_option_fails(self) -> None:
        self.record["options"] = self.record["options"][:1]
        errors = module.validate_record(self.record, "draft")
        self.assertIn(
            "record.options must contain at least two materially different options",
            errors,
        )

    def test_unknown_reference_fails(self) -> None:
        self.record["problem"]["evidence_ids"] = ["E404"]
        errors = module.validate_record(self.record, "draft")
        self.assertIn(
            "record.problem.evidence_ids references unknown id E404",
            errors,
        )

    def test_duplicate_ids_fail(self) -> None:
        self.record["evidence"].append(deepcopy(self.record["evidence"][0]))
        errors = module.validate_record(self.record, "draft")
        self.assertTrue(any("duplicates E1" in error for error in errors))

    def test_existing_evidence_decision_can_omit_experiment(self) -> None:
        record = self.make_decision("stop")
        record["experiment"] = None
        self.assertEqual(module.validate_record(record, "decision"), [])

    def test_invalid_date_fails(self) -> None:
        self.record["updated_at"] = "August 25"
        errors = module.validate_record(self.record, "draft")
        self.assertIn("record.updated_at must be an ISO date or datetime", errors)

    def test_high_cost_build_requires_strong_evidence(self) -> None:
        record = self.make_decision()
        record["context"]["cost_of_error"] = "high"
        record["evidence"][0]["strength"] = "medium"
        errors = module.validate_record(record, "decision")
        self.assertIn("a high-cost build decision requires strong evidence", errors)


if __name__ == "__main__":
    unittest.main()
