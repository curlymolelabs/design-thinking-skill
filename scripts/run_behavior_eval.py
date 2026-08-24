#!/usr/bin/env python3
"""Run paired behavior trials with and without the Design Thinking skill."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "tests" / "evaluation-cases.json"
SKILL_PATH = ROOT / "design-thinking" / "SKILL.md"


def load_cases(selected: set[str]) -> list[dict[str, Any]]:
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    if selected:
        cases = [case for case in cases if case["id"] in selected]
        found = {case["id"] for case in cases}
        missing = sorted(selected - found)
        if missing:
            raise ValueError(f"Unknown case ids: {', '.join(missing)}")
    return cases


def extract_response(client: str, stdout: str) -> str:
    text = stdout.strip()
    if not text:
        return ""
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return text

    if not isinstance(payload, dict):
        return text

    for field in ("result", "content", "message", "response"):
        value = payload.get(field)
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, dict) and isinstance(value.get("content"), str):
            return value["content"].strip()

    if client == "grok" and isinstance(payload.get("messages"), list):
        for message in reversed(payload["messages"]):
            if isinstance(message, dict) and isinstance(message.get("content"), str):
                return message["content"].strip()

    return text


def build_command(
    client: str,
    executable: str,
    prompt: str,
    skill_text: str | None,
    model: str | None,
    max_budget_usd: float,
) -> list[str]:
    if client == "claude":
        command = [
            executable,
            "--print",
            "--bare",
            "--no-session-persistence",
            "--tools",
            "",
            "--output-format",
            "json",
            "--max-budget-usd",
            str(max_budget_usd),
        ]
        if model:
            command.extend(["--model", model])
        if skill_text:
            command.extend(["--append-system-prompt", skill_text])
        command.append(prompt)
        return command

    if client == "grok":
        command = [
            executable,
            "--single",
            prompt,
            "--output-format",
            "json",
            "--no-subagents",
            "--disable-web-search",
            "--max-turns",
            "1",
            "--tools",
            "",
        ]
        if model:
            command.extend(["--model", model])
        if skill_text:
            command.extend(["--system-prompt-override", skill_text])
        return command

    raise ValueError(f"Unsupported client: {client}")


def read_version(executable: str) -> str:
    completed = subprocess.run(
        [executable, "--version"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
    )
    return (completed.stdout or completed.stderr).strip()


def save_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the same behavior cases with and without the skill"
    )
    parser.add_argument("--client", choices=("claude", "grok"), required=True)
    parser.add_argument("--case", action="append", default=[], help="Run one case id")
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20260825)
    parser.add_argument("--model")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--max-budget-usd", type=float, default=0.10)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.trials < 1:
        parser.error("--trials must be at least 1")

    try:
        cases = load_cases(set(args.case))
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    skill_digest = hashlib.sha256(skill_text.encode("utf-8")).hexdigest()
    requests = [
        {"case": case, "condition": condition, "trial": trial}
        for case in cases
        for condition in ("baseline", "skill")
        for trial in range(1, args.trials + 1)
    ]
    random.Random(args.seed).shuffle(requests)

    if args.dry_run:
        print(
            json.dumps(
                {
                    "client": args.client,
                    "cases": len(cases),
                    "trials_per_condition": args.trials,
                    "requests": len(requests),
                    "skill_sha256": skill_digest,
                },
                indent=2,
            )
        )
        return 0

    executable = shutil.which(args.client)
    if not executable:
        print(f"ERROR: {args.client} is not installed", file=sys.stderr)
        return 2

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = args.output or ROOT / "evaluation-runs" / f"{args.client}-{stamp}.json"
    manifest: dict[str, Any] = {
        "schema_version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "client": args.client,
        "client_version": read_version(executable),
        "model": args.model or "client-default",
        "skill_sha256": skill_digest,
        "seed": args.seed,
        "trials_per_condition": args.trials,
        "runs": [],
    }
    save_manifest(output_path, manifest)

    for index, request in enumerate(requests, start=1):
        case = request["case"]
        condition = request["condition"]
        command = build_command(
            args.client,
            executable,
            case["prompt"],
            skill_text if condition == "skill" else None,
            args.model,
            args.max_budget_usd,
        )
        started = time.monotonic()
        try:
            completed = subprocess.run(
                command,
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=args.timeout,
                check=False,
            )
            stdout = completed.stdout
            stderr = completed.stderr
            exit_code = completed.returncode
            error = None
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            exit_code = 124
            error = f"Timed out after {args.timeout} seconds"

        run = {
            "case_id": case["id"],
            "condition": condition,
            "trial": request["trial"],
            "exit_code": exit_code,
            "duration_seconds": round(time.monotonic() - started, 3),
            "response": extract_response(args.client, stdout),
            "error": error,
            "stderr": stderr.strip(),
        }
        manifest["runs"].append(run)
        save_manifest(output_path, manifest)
        print(
            f"[{index}/{len(requests)}] {case['id']} {condition} "
            f"trial {request['trial']}: exit {exit_code}"
        )

    failed = sum(run["exit_code"] != 0 for run in manifest["runs"])
    print(f"Saved {len(manifest['runs'])} runs to {output_path}")
    if failed:
        print(f"ERROR: {failed} runs failed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
