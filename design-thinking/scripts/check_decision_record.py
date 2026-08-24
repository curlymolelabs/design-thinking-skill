#!/usr/bin/env python3
"""Validate a design-thinking decision record with Python's standard library."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "2.0"
EVIDENCE_TYPES = {"observed", "reported", "external", "inferred", "assumed"}
STRENGTHS = {"strong", "medium", "weak"}
RISK_LEVELS = {"high", "medium", "low"}
RATINGS = {"high", "medium", "low", "unknown"}
LENSES = {"user_value", "feasibility", "financial_fit", "responsibility"}
ASSUMPTION_STATES = {"untested", "supported", "challenged", "retired"}
RECORD_STATES = {"draft", "decided"}
EXPERIMENT_STATES = {"planned", "running", "complete", "cancelled"}
EXPERIMENT_RESULTS = {"pending", "supported", "challenged", "mixed", "inconclusive", "not-run"}
OUTCOMES = {"build", "revise", "retest", "defer", "stop"}

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "decision_id",
    "title",
    "status",
    "created_at",
    "updated_at",
    "decision_owner",
    "context",
    "target_user",
    "problem",
    "evidence",
    "assumptions",
    "options",
    "experiment",
    "decision",
    "next_step",
}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any, *, allow_empty: bool = True) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(nonempty(item) for item in value)
    )


def iso_date_or_datetime(value: Any, *, allow_none: bool = False) -> bool:
    if value is None:
        return allow_none
    if not nonempty(value):
        return False
    try:
        if "T" in value:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        else:
            date.fromisoformat(value)
    except ValueError:
        return False
    return True


def require_fields(value: Any, fields: set[str], path: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return
    for field in sorted(fields):
        if field not in value:
            errors.append(f"{path}.{field} is required")


def require_nonempty_fields(
    value: Any, fields: set[str], path: str, errors: list[str]
) -> None:
    require_fields(value, fields, path, errors)
    if not isinstance(value, dict):
        return
    for field in sorted(fields):
        if field in value and not nonempty(value[field]):
            errors.append(f"{path}.{field} must be a non-empty string")


def collect_ids(items: Any, path: str, errors: list[str]) -> set[str]:
    ids: set[str] = set()
    if not isinstance(items, list):
        return ids
    for index, item in enumerate(items):
        if not isinstance(item, dict) or not nonempty(item.get("id")):
            continue
        item_id = item["id"]
        if item_id in ids:
            errors.append(f"{path}[{index}].id duplicates {item_id}")
        ids.add(item_id)
    return ids


def check_references(
    values: Any,
    valid_ids: set[str],
    path: str,
    errors: list[str],
    *,
    allow_empty: bool = True,
) -> None:
    if not string_list(values, allow_empty=allow_empty):
        qualifier = "an array of non-empty strings"
        if not allow_empty:
            qualifier += " with at least one item"
        errors.append(f"{path} must be {qualifier}")
        return
    for item_id in values:
        if item_id not in valid_ids:
            errors.append(f"{path} references unknown id {item_id}")


def validate_record(record: Any, mode: str) -> list[str]:
    errors: list[str] = []
    require_fields(record, REQUIRED_TOP_LEVEL, "record", errors)
    if errors or not isinstance(record, dict):
        return errors

    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"record.schema_version must be {SCHEMA_VERSION}")

    for field in ("decision_id", "title", "decision_owner"):
        if not nonempty(record.get(field)):
            errors.append(f"record.{field} must be a non-empty string")

    if record.get("status") not in RECORD_STATES:
        errors.append(f"record.status must be one of {sorted(RECORD_STATES)}")

    for field in ("created_at", "updated_at"):
        if not iso_date_or_datetime(record.get(field)):
            errors.append(f"record.{field} must be an ISO date or datetime")

    context = record.get("context")
    require_fields(
        context,
        {"decision", "deadline", "cost_of_error", "reversibility", "affected_people"},
        "record.context",
        errors,
    )
    if isinstance(context, dict):
        if not nonempty(context.get("decision")):
            errors.append("record.context.decision must be a non-empty string")
        if not iso_date_or_datetime(context.get("deadline"), allow_none=True):
            errors.append("record.context.deadline must be null or an ISO date or datetime")
        for field in ("cost_of_error", "reversibility"):
            if context.get(field) not in RISK_LEVELS:
                errors.append(f"record.context.{field} must be one of {sorted(RISK_LEVELS)}")
        if not string_list(context.get("affected_people"), allow_empty=False):
            errors.append("record.context.affected_people must contain at least one string")

    require_nonempty_fields(
        record.get("target_user"),
        {"role", "context", "desired_progress"},
        "record.target_user",
        errors,
    )
    require_nonempty_fields(
        record.get("problem"),
        {"statement", "current_behavior", "barrier", "consequence"},
        "record.problem",
        errors,
    )

    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("record.evidence must contain at least one evidence item")
    else:
        for index, item in enumerate(evidence):
            path = f"record.evidence[{index}]"
            fields = {
                "id",
                "claim",
                "source_type",
                "source",
                "observed_at",
                "strength",
                "limitations",
                "decision_effect",
            }
            require_fields(item, fields, path, errors)
            if not isinstance(item, dict):
                continue
            for field in ("id", "claim", "source", "decision_effect"):
                if not nonempty(item.get(field)):
                    errors.append(f"{path}.{field} must be a non-empty string")
            if item.get("source_type") not in EVIDENCE_TYPES:
                errors.append(f"{path}.source_type must be one of {sorted(EVIDENCE_TYPES)}")
            if item.get("strength") not in STRENGTHS:
                errors.append(f"{path}.strength must be one of {sorted(STRENGTHS)}")
            if not iso_date_or_datetime(item.get("observed_at"), allow_none=True):
                errors.append(f"{path}.observed_at must be null or an ISO date or datetime")
            if not string_list(item.get("limitations")):
                errors.append(f"{path}.limitations must be an array of non-empty strings")

    assumptions = record.get("assumptions")
    if not isinstance(assumptions, list):
        errors.append("record.assumptions must be an array")
    else:
        for index, item in enumerate(assumptions):
            path = f"record.assumptions[{index}]"
            fields = {
                "id",
                "statement",
                "lens",
                "consequence_if_false",
                "evidence_ids",
                "status",
                "test",
            }
            require_fields(item, fields, path, errors)
            if not isinstance(item, dict):
                continue
            for field in ("id", "statement", "test"):
                if not nonempty(item.get(field)):
                    errors.append(f"{path}.{field} must be a non-empty string")
            if item.get("lens") not in LENSES:
                errors.append(f"{path}.lens must be one of {sorted(LENSES)}")
            if item.get("consequence_if_false") not in RISK_LEVELS:
                errors.append(
                    f"{path}.consequence_if_false must be one of {sorted(RISK_LEVELS)}"
                )
            if item.get("status") not in ASSUMPTION_STATES:
                errors.append(f"{path}.status must be one of {sorted(ASSUMPTION_STATES)}")

    options = record.get("options")
    if not isinstance(options, list) or len(options) < 2:
        errors.append("record.options must contain at least two materially different options")
    else:
        for index, item in enumerate(options):
            path = f"record.options[{index}]"
            fields = {
                "id",
                "name",
                "mechanism",
                "depends_on",
                "user_value",
                "feasibility",
                "financial_fit",
                "responsibility",
                "failure_condition",
            }
            require_fields(item, fields, path, errors)
            if not isinstance(item, dict):
                continue
            for field in ("id", "name", "mechanism", "responsibility", "failure_condition"):
                if not nonempty(item.get(field)):
                    errors.append(f"{path}.{field} must be a non-empty string")
            for field in ("user_value", "feasibility", "financial_fit"):
                if item.get(field) not in RATINGS:
                    errors.append(f"{path}.{field} must be one of {sorted(RATINGS)}")

    evidence_ids = collect_ids(evidence, "record.evidence", errors)
    assumption_ids = collect_ids(assumptions, "record.assumptions", errors)
    option_ids = collect_ids(options, "record.options", errors)

    problem = record.get("problem")
    if isinstance(problem, dict):
        check_references(
            problem.get("evidence_ids"),
            evidence_ids,
            "record.problem.evidence_ids",
            errors,
            allow_empty=False,
        )

    if isinstance(assumptions, list):
        for index, item in enumerate(assumptions):
            if isinstance(item, dict):
                check_references(
                    item.get("evidence_ids"),
                    evidence_ids,
                    f"record.assumptions[{index}].evidence_ids",
                    errors,
                )

    if isinstance(options, list):
        for index, item in enumerate(options):
            if isinstance(item, dict):
                check_references(
                    item.get("depends_on"),
                    assumption_ids,
                    f"record.options[{index}].depends_on",
                    errors,
                )

    experiment = record.get("experiment")
    if experiment is not None:
        fields = {
            "status",
            "decision_enabled",
            "assumption_ids",
            "question",
            "hypothesis",
            "method",
            "prototype",
            "participants_or_source",
            "task_or_trigger",
            "supporting_signal",
            "challenging_signal",
            "threshold",
            "stop_rule",
            "intentional_omissions",
            "controls",
            "result",
            "limitations",
        }
        require_fields(experiment, fields, "record.experiment", errors)
        if isinstance(experiment, dict):
            nonempty_fields = fields - {
                "status",
                "assumption_ids",
                "intentional_omissions",
                "controls",
                "result",
                "limitations",
            }
            for field in sorted(nonempty_fields):
                if not nonempty(experiment.get(field)):
                    errors.append(f"record.experiment.{field} must be a non-empty string")
            if experiment.get("status") not in EXPERIMENT_STATES:
                errors.append(
                    f"record.experiment.status must be one of {sorted(EXPERIMENT_STATES)}"
                )
            if experiment.get("result") not in EXPERIMENT_RESULTS:
                errors.append(
                    f"record.experiment.result must be one of {sorted(EXPERIMENT_RESULTS)}"
                )
            check_references(
                experiment.get("assumption_ids"),
                assumption_ids,
                "record.experiment.assumption_ids",
                errors,
                allow_empty=False,
            )
            for field in ("intentional_omissions", "controls", "limitations"):
                if not string_list(experiment.get(field)):
                    errors.append(
                        f"record.experiment.{field} must be an array of non-empty strings"
                    )

    decision = record.get("decision")
    require_fields(
        decision,
        {
            "outcome",
            "reason",
            "evidence_ids",
            "rejected_option_ids",
            "decided_at",
            "unknowns",
            "revisit_trigger",
        },
        "record.decision",
        errors,
    )
    if isinstance(decision, dict):
        check_references(
            decision.get("evidence_ids"),
            evidence_ids,
            "record.decision.evidence_ids",
            errors,
        )
        check_references(
            decision.get("rejected_option_ids"),
            option_ids,
            "record.decision.rejected_option_ids",
            errors,
        )
        if not string_list(decision.get("unknowns")):
            errors.append(
                "record.decision.unknowns must be an array of non-empty strings"
            )
        revisit_trigger = decision.get("revisit_trigger")
        if revisit_trigger is not None and not nonempty(revisit_trigger):
            errors.append("record.decision.revisit_trigger must be null or a non-empty string")

    require_nonempty_fields(
        record.get("next_step"),
        {"owner", "action", "completion_signal"},
        "record.next_step",
        errors,
    )

    if mode == "decision" and isinstance(decision, dict):
        if record.get("status") != "decided":
            errors.append("record.status must be decided in decision mode")
        if decision.get("outcome") not in OUTCOMES:
            errors.append(f"record.decision.outcome must be one of {sorted(OUTCOMES)}")
        if not nonempty(decision.get("reason")):
            errors.append("record.decision.reason must be a non-empty string")
        if not iso_date_or_datetime(decision.get("decided_at")):
            errors.append("record.decision.decided_at must be an ISO date or datetime")
        if not string_list(decision.get("evidence_ids"), allow_empty=False):
            errors.append("record.decision.evidence_ids must contain at least one evidence id")
        if decision.get("outcome") == "defer" and not nonempty(
            decision.get("revisit_trigger")
        ):
            errors.append("record.decision.revisit_trigger is required when outcome is defer")

        if decision.get("outcome") == "build" and string_list(
            decision.get("evidence_ids"), allow_empty=False
        ):
            evidence_by_id = {
                item.get("id"): item
                for item in evidence
                if isinstance(item, dict) and nonempty(item.get("id"))
            }
            strengths = {
                evidence_by_id[item_id].get("strength")
                for item_id in decision["evidence_ids"]
                if item_id in evidence_by_id
            }
            if not strengths.intersection({"strong", "medium"}):
                errors.append("a build decision requires at least medium-strength evidence")
            if (
                isinstance(context, dict)
                and context.get("cost_of_error") == "high"
                and "strong" not in strengths
            ):
                errors.append("a high-cost build decision requires strong evidence")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a design-thinking decision record")
    parser.add_argument("record", type=Path, help="Path to the JSON record")
    parser.add_argument("--mode", choices=("draft", "decision"), default="draft")
    args = parser.parse_args()

    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: record not found: {args.record}", file=sys.stderr)
        return 2
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: could not read valid JSON: {exc}", file=sys.stderr)
        return 2

    errors = validate_record(record, args.mode)
    if errors:
        print(f"Decision record failed {args.mode} validation:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Decision record passed {args.mode} validation: {args.record}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
