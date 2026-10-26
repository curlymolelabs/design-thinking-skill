#!/usr/bin/env python3
"""Guesswork keeps a ledger of the product decisions an agent made without instructions.

Agents fill every gap in a request with a guess: how long a session lasts, who can
invite whom, whether a delete can be undone. Guesswork records each guess in plain
language, shows the risky ones to the project owner as a short receipt, records the
owner's answers, and feeds those decisions back into later sessions, pull requests,
and CI. It uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import time
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

__version__ = "3.0.0"

SCHEMA = "guesswork/1"
LEDGER_DIR = ".guesswork"
GUESS_DIR = "guesses"
CONFIG_NAME = "config.json"
REPORT_NAME = "report.html"
PR_MARKER = "<!-- guesswork:pr-summary -->"

CATEGORIES = {
    "money": "Pricing, billing, charges, refunds, trials, taxes, payouts",
    "access": "Sign-in, roles, permissions, sharing, invitations",
    "privacy": "Personal data that is collected, shown, kept, shared, or tracked",
    "data": "Storage, deletion, retention, import, export, data loss",
    "security": "Secrets, validation, rate limits, sessions, encryption",
    "legal": "Consent, terms, age, cookies, regulated domains, accessibility duties",
    "safety": "Harm to people, moderation, abuse, wellbeing",
    "defaults": "What happens when nobody chooses: visibility, opt-in, automatic actions",
    "limits": "Quotas, sizes, timeouts, plan limits, caps",
    "notifications": "Emails, pushes, alerts, their frequency and recipients",
    "ux": "Flows, confirmations, empty and error states, behavior people notice",
    "content": "User-facing wording that names, promises, or sets expectations",
    "integration": "Third-party services, vendors, APIs, webhooks, lock-in",
    "performance": "Scale, speed, caching, freshness, running cost",
    "other": "Anything else a product owner would want a say in",
}
SENSITIVE_CATEGORIES = {"money", "access", "privacy", "data", "security", "legal", "safety"}
STAKES = ("high", "medium", "low")
BASIS = ("assumed", "inferred", "reported", "observed", "external")
STATUSES = ("open", "decided", "testing", "dismissed", "superseded")
ACTIVE_STATUSES = ("open", "decided", "testing")
FAIL_LEVELS = ("high", "medium", "low", "never")
STOP_CHECK_MODES = ("nudge", "receipt", "off")
OPTION_KEYS = "abcde"
MAX_ALTERNATIVES = len(OPTION_KEYS) - 1
MAX_TITLE = 240
MAX_ALTERNATIVE = 120
ID_PATTERN = re.compile(r"^g-[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_ID = 64
CLOCK_SLACK = 2.0
SESSION_TTL = 3 * 24 * 3600
RECEIPT_TTL = 24 * 3600
SESSION_DECISION_LIMIT = 25

DEFAULT_STOP_IGNORE = [
    "*.md",
    "*.lock",
    "*.lockb",
    "package-lock.json",
    "pnpm-lock.yaml",
    "go.sum",
]
DEFAULT_CONFIG: dict[str, Any] = {
    "hooks": True,
    "stop_check": "nudge",
    "fail_on": "high",
    "receipt_limit": 5,
    "ignore": [],
}

GUESS_KEY_ORDER = (
    "schema",
    "id",
    "title",
    "why",
    "category",
    "stakes",
    "reversible",
    "basis",
    "where",
    "alternatives",
    "question",
    "status",
    "resolution",
    "test",
    "superseded_by",
    "created_by",
    "created_at",
    "updated_at",
    "history",
)

PROTOCOL_NOTE = (
    "Project convention: when work implements product behavior the user did not specify "
    "(defaults, limits, permissions, data handling, money, notifications, or wording that makes "
    "promises), each such decision is recorded with `guesswork log`, and the turn ends with the "
    "output of `guesswork receipt`. Decisions the owner already made are listed by "
    "`guesswork context <files>`. The guesswork skill describes the details."
)

LEDGER_README = """# Guesswork ledger

This folder records product decisions that were made without explicit instructions, usually by a coding agent. Each file in `guesses/` is one decision: what was built, why, how much it matters, and what the project owner decided.

- `guesswork receipt` lists the open decisions that need an owner.
- `guesswork decide 1b 2a` records answers to the latest receipt.
- `guesswork context <file>` shows the decisions that cover a file.
- `guesswork report` writes an HTML overview to `.guesswork/report.html`.

Commit this folder. It is the project's memory of why things work the way they do.
"""

AGENTS_SECTION = """## Guesswork

This project records product decisions that were made without explicit instructions in `.guesswork/`.

- When you implement behavior the user did not specify (defaults, limits, permissions, data handling, money, notifications, or wording that makes promises), record each decision with `guesswork log`.
- Before changing existing behavior, run `guesswork context <files>`. Decisions with status `decided` were chosen by the project owner. Ask before changing them.
- End every turn that recorded guesses with the output of `guesswork receipt`.
"""


class GuessworkError(Exception):
    """A problem the user can fix, reported without a traceback."""


# ---------------------------------------------------------------------------
# Small helpers


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def clean_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    text = " ".join(value.split())
    return text or None


def plural(count: int, singular: str, plural_form: Optional[str] = None) -> str:
    word = singular if count == 1 else (plural_form or singular + "s")
    return f"{count} {word}"


def now_iso() -> str:
    stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return stamp.replace("+00:00", "Z")


def parse_time(value: Any) -> Optional[float]:
    if not nonempty(value):
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        if "T" in text:
            moment = datetime.fromisoformat(text)
        else:
            moment = datetime.fromisoformat(text + "T00:00:00+00:00")
    except ValueError:
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.timestamp()


def day_of(value: Any) -> str:
    return value[:10] if nonempty(value) else ""


def configure_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with open(temporary, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    os.replace(temporary, path)


def write_json_atomic(path: Path, data: Any) -> None:
    write_text_atomic(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def slugify(text: str, max_words: int = 6, max_length: int = 40) -> str:
    stop_words = {
        "a", "an", "the", "is", "are", "be", "of", "to", "for", "and", "or", "in", "on",
        "by", "with", "as", "at", "it", "its", "that", "this", "when", "from", "into",
    }
    words = re.findall(r"[a-z0-9]+", re.sub(r"['’]", "", text.lower()))
    kept = [word for word in words if word not in stop_words] or words
    chosen: list[str] = []
    for word in kept[:max_words]:
        if chosen and len("-".join(chosen + [word])) > max_length:
            break
        chosen.append(word[:max_length])
    return "g-" + ("-".join(chosen) or "guess")


def unique_id(base: str, taken: set[str]) -> str:
    if base not in taken:
        return base
    counter = 2
    while f"{base}-{counter}" in taken:
        counter += 1
    return f"{base}-{counter}"


def strip_anchor(entry: str) -> str:
    match = re.match(r"^(.+?)(?::\d+(?:-\d+)?|#.+)$", entry)
    return match.group(1) if match else entry


def where_matches(entry: str, file_rel: str) -> bool:
    base = strip_anchor(entry).rstrip("/")
    if not base:
        return False
    left, right = base, file_rel
    if os.name == "nt":
        left, right = left.lower(), right.lower()
    if any(char in left for char in "*?["):
        return fnmatch.fnmatchcase(right, left)
    return right == left or right.startswith(left + "/")


def is_ignored(rel: str, patterns: Iterable[str]) -> bool:
    name = rel.rsplit("/", 1)[-1]
    return any(fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(name, pattern) for pattern in patterns)


def find_root(start: Path) -> Path:
    start = start.resolve()
    for candidate in (start, *start.parents):
        if (candidate / LEDGER_DIR).is_dir() or (candidate / ".git").exists():
            return candidate
    return start


def git(root: Path, *args: str, timeout: int = 30) -> Optional[subprocess.CompletedProcess]:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError):
        return None


# ---------------------------------------------------------------------------
# The ledger


class Project:
    """One project and its `.guesswork/` ledger."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.ledger = self.root / LEDGER_DIR
        self.guess_dir = self.ledger / GUESS_DIR

    @property
    def initialized(self) -> bool:
        return self.guess_dir.is_dir()

    def config(self) -> dict[str, Any]:
        config = dict(DEFAULT_CONFIG)
        path = self.ledger / CONFIG_NAME
        if path.is_file():
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                loaded = {}
            if isinstance(loaded, dict):
                config.update({key: value for key, value in loaded.items() if key in config})
        if not isinstance(config["hooks"], bool):
            config["hooks"] = True
        if config["stop_check"] not in STOP_CHECK_MODES:
            config["stop_check"] = DEFAULT_CONFIG["stop_check"]
        if config["fail_on"] not in FAIL_LEVELS:
            config["fail_on"] = DEFAULT_CONFIG["fail_on"]
        limit = config["receipt_limit"]
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            config["receipt_limit"] = DEFAULT_CONFIG["receipt_limit"]
        if not isinstance(config["ignore"], list):
            config["ignore"] = []
        config["ignore"] = [item for item in config["ignore"] if nonempty(item)]
        return config

    def ensure(self) -> bool:
        created = not self.guess_dir.is_dir()
        self.guess_dir.mkdir(parents=True, exist_ok=True)
        gitignore = self.ledger / ".gitignore"
        if not gitignore.exists():
            write_text_atomic(gitignore, f"{REPORT_NAME}\n")
        readme = self.ledger / "README.md"
        if not readme.exists():
            write_text_atomic(readme, LEDGER_README)
        return created

    def display(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self.root).as_posix()
        except ValueError:
            return str(path)

    def relative(self, value: str) -> str:
        """Return a path as repository-relative POSIX text, keeping any :line or #symbol anchor."""
        text = value.strip().replace("\\", "/")
        anchor = ""
        match = re.match(r"^(.+?)((?::\d+(?:-\d+)?)|(?:#.+))$", text)
        if match:
            text, anchor = match.group(1), match.group(2)
        path = Path(text)
        if path.is_absolute():
            try:
                text = path.resolve().relative_to(self.root).as_posix()
            except (ValueError, OSError):
                text = path.as_posix()
        else:
            text = Path(os.path.normpath(text)).as_posix()
        if text == ".":
            text = ""
        return text + anchor

    def load(self) -> tuple[list[dict[str, Any]], list[str]]:
        guesses: list[dict[str, Any]] = []
        problems: list[str] = []
        if not self.guess_dir.is_dir():
            return guesses, problems
        for path in sorted(self.guess_dir.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                problems.append(f"{self.display(path)}: not valid JSON ({exc})")
                continue
            errors = validate_guess(data, path.name)
            if errors:
                problems.extend(f"{self.display(path)}: {error}" for error in errors)
                continue
            guesses.append(data)
        return guesses, problems

    def save(self, guess: dict[str, Any]) -> Path:
        self.ensure()
        path = self.guess_dir / f"{guess['id']}.json"
        write_json_atomic(path, order_guess(guess))
        return path


def order_guess(guess: dict[str, Any]) -> dict[str, Any]:
    ordered = {key: guess[key] for key in GUESS_KEY_ORDER if key in guess}
    ordered.update({key: value for key, value in guess.items() if key not in ordered})
    return ordered


def validate_guess(guess: Any, filename: Optional[str] = None) -> list[str]:
    if not isinstance(guess, dict):
        return ["a guess must be a JSON object"]
    errors: list[str] = []
    if guess.get("schema") != SCHEMA:
        errors.append(f'schema must be "{SCHEMA}"')
    guess_id = guess.get("id")
    if not isinstance(guess_id, str) or not ID_PATTERN.match(guess_id) or len(guess_id) > MAX_ID:
        errors.append("id must look like g-short-slug (lowercase letters, digits, and hyphens, at most 64 characters)")
    elif filename and Path(filename).stem != guess_id:
        errors.append(f"file name must match the id ({guess_id}.json)")
    title = guess.get("title")
    if not nonempty(title):
        errors.append("title must state the decision as built")
    elif len(title) > MAX_TITLE:
        errors.append(f"title must be at most {MAX_TITLE} characters")
    for field in ("why", "question"):
        if guess.get(field) is not None and not isinstance(guess.get(field), str):
            errors.append(f"{field} must be a string or null")
    if guess.get("category") not in CATEGORIES:
        errors.append(f"category must be one of: {', '.join(CATEGORIES)}")
    if guess.get("stakes") not in STAKES:
        errors.append("stakes must be high, medium, or low")
    if not isinstance(guess.get("reversible"), bool):
        errors.append("reversible must be true or false")
    if guess.get("basis") not in BASIS:
        errors.append(f"basis must be one of: {', '.join(BASIS)}")
    where = guess.get("where")
    if not isinstance(where, list) or not all(nonempty(item) for item in where):
        errors.append("where must be a list of file paths (it may be empty)")
    alternatives = guess.get("alternatives")
    if not isinstance(alternatives, list) or not all(nonempty(item) for item in alternatives):
        errors.append("alternatives must be a list of short option labels (it may be empty)")
    elif len(alternatives) > MAX_ALTERNATIVES:
        errors.append(f"alternatives may hold at most {MAX_ALTERNATIVES} options")
    elif any(len(item) > MAX_ALTERNATIVE for item in alternatives):
        errors.append(f"each alternative must be at most {MAX_ALTERNATIVE} characters")
    status = guess.get("status")
    if status not in STATUSES:
        errors.append(f"status must be one of: {', '.join(STATUSES)}")
    for field in ("created_at", "updated_at"):
        if parse_time(guess.get(field)) is None:
            errors.append(f"{field} must be an ISO date or datetime")
    if not nonempty(guess.get("created_by")):
        errors.append("created_by must name who recorded the guess")
    resolution = guess.get("resolution")
    if status == "decided":
        if not isinstance(resolution, dict):
            errors.append("a decided guess needs a resolution")
        else:
            choice = resolution.get("choice")
            allowed = {"custom"} | set(OPTION_KEYS[: 1 + (len(alternatives) if isinstance(alternatives, list) else 0)])
            if choice not in allowed:
                errors.append(f"resolution.choice must be one of: {', '.join(sorted(allowed))}")
            if not nonempty(resolution.get("decision")):
                errors.append("resolution.decision must state what was decided")
            if not nonempty(resolution.get("by")):
                errors.append("resolution.by must name who decided")
            if parse_time(resolution.get("at")) is None:
                errors.append("resolution.at must be an ISO date or datetime")
    elif resolution is not None and not isinstance(resolution, dict):
        errors.append("resolution must be an object or null")
    test = guess.get("test")
    if status == "testing" and (not isinstance(test, dict) or not nonempty(test.get("plan"))):
        errors.append("a guess under test needs test.plan")
    if status == "superseded" and not nonempty(guess.get("superseded_by")):
        errors.append("a superseded guess needs superseded_by")
    history = guess.get("history")
    if history is not None and not (isinstance(history, list) and all(isinstance(item, dict) for item in history)):
        errors.append("history must be a list of objects")
    return errors


def validate_file(path: Path) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return [f"cannot read the file ({exc})"]
    except ValueError as exc:
        return [f"not valid JSON ({exc})"]
    return validate_guess(data, path.name)


def options_for(guess: dict[str, Any]) -> list[tuple[str, str]]:
    options = [("a", "Keep as built")]
    for index, label in enumerate(guess.get("alternatives") or [], start=1):
        options.append((OPTION_KEYS[index], label))
    return options


def decision_for(guess: dict[str, Any], choice: str) -> str:
    if choice == "a":
        return guess["title"]
    index = OPTION_KEYS.index(choice)
    return guess["alternatives"][index - 1]


def current_behavior(guess: dict[str, Any]) -> str:
    resolution = guess.get("resolution")
    if guess.get("status") == "decided" and isinstance(resolution, dict) and nonempty(resolution.get("decision")):
        return resolution["decision"]
    return guess["title"]


def risk(guess: dict[str, Any]) -> int:
    score = {"high": 30, "medium": 20, "low": 10}.get(guess.get("stakes"), 0)
    if not guess.get("reversible", True):
        score += 5
    if guess.get("category") in SENSITIVE_CATEGORIES:
        score += 2
    if guess.get("basis") == "assumed":
        score += 1
    return score


def sort_by_risk(guesses: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(guesses, key=lambda guess: (-risk(guess), guess.get("created_at", ""), guess["id"]))


def tag_line(guess: dict[str, Any]) -> str:
    parts = [f"{guess['stakes']} stakes", guess["category"]]
    if not guess.get("reversible", True):
        parts.append("hard to undo")
    return " · ".join(parts)


def coverage(guesses: Iterable[dict[str, Any]]) -> Optional[float]:
    counted = [g for g in guesses if g["status"] in ACTIVE_STATUSES and g["stakes"] in ("high", "medium")]
    if not counted:
        return None
    reviewed = [g for g in counted if g["status"] in ("decided", "testing")]
    return len(reviewed) / len(counted)


def record(guess: dict[str, Any], status: str, by: str, note: Optional[str] = None) -> None:
    stamp = now_iso()
    guess["status"] = status
    guess["updated_at"] = stamp
    entry = {"at": stamp, "status": status, "by": by}
    if note:
        entry["note"] = note
    guess.setdefault("history", []).append(entry)


# ---------------------------------------------------------------------------
# Building guesses from agent input


def first_present(data: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in data and data[name] is not None:
            return data[name]
    return None


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def build_guess(project: Project, data: Any, taken: set[str], by: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise GuessworkError("each guess must be a JSON object")
    title = clean_text(first_present(data, "title", "guess", "decision"))
    if not title:
        raise GuessworkError("each guess needs a title that states the decision as built")
    reversible = True
    if "irreversible" in data:
        reversible = not bool(data["irreversible"])
    elif "reversible" in data:
        reversible = bool(data["reversible"])
    where = []
    for item in as_list(first_present(data, "where", "files", "paths", "file")):
        text = clean_text(item)
        if text:
            normalized = project.relative(text)
            if normalized and normalized not in where:
                where.append(normalized)
    alternatives = []
    for item in as_list(first_present(data, "alternatives", "alts", "options")):
        if isinstance(item, dict):
            item = first_present(item, "label", "title", "text")
        text = clean_text(item)
        if text and text not in alternatives and text.lower().rstrip(".") not in ("keep as built", "keep it", "keep"):
            alternatives.append(text)
    guess_id = clean_text(data.get("id"))
    if guess_id:
        guess_id = guess_id.lower()
        if not guess_id.startswith("g-"):
            guess_id = "g-" + guess_id
        if guess_id in taken:
            raise GuessworkError(f"the id {guess_id} is already used")
    else:
        guess_id = unique_id(slugify(title), taken)
    stamp = now_iso()
    guess = {
        "schema": SCHEMA,
        "id": guess_id,
        "title": title,
        "why": clean_text(first_present(data, "why", "reason", "rationale")),
        "category": clean_text(data.get("category")) or "other",
        "stakes": (clean_text(data.get("stakes")) or "").lower(),
        "reversible": reversible,
        "basis": (clean_text(data.get("basis")) or "assumed").lower(),
        "where": where,
        "alternatives": alternatives,
        "question": clean_text(data.get("question")),
        "status": "open",
        "resolution": None,
        "test": None,
        "superseded_by": None,
        "created_by": clean_text(data.get("by")) or by,
        "created_at": stamp,
        "updated_at": stamp,
        "history": [{"at": stamp, "status": "open", "by": clean_text(data.get("by")) or by, "note": "recorded"}],
    }
    guess["category"] = guess["category"].lower()
    errors = validate_guess(guess)
    if errors:
        raise GuessworkError(f'guess "{title}" is invalid: ' + "; ".join(errors))
    return guess


def read_log_input(args: argparse.Namespace) -> list[Any]:
    if args.file is not None:
        text = sys.stdin.read() if str(args.file) == "-" else Path(args.file).read_text(encoding="utf-8")
    elif args.title:
        entry: dict[str, Any] = {
            "title": args.title,
            "why": args.why,
            "category": args.category,
            "stakes": args.stakes,
            "basis": args.basis,
            "where": args.where,
            "alternatives": args.alt,
            "question": args.question,
            "id": args.id,
            "supersedes": args.supersedes,
        }
        if args.irreversible:
            entry["irreversible"] = True
        return [{key: value for key, value in entry.items() if value is not None}]
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        raise GuessworkError("give --title, or pipe a JSON object or array of guesses on standard input")
    if not text.strip():
        raise GuessworkError("no guesses were given")
    try:
        payload = json.loads(text)
    except ValueError as exc:
        raise GuessworkError(f"could not read the guesses as JSON ({exc})") from exc
    if isinstance(payload, dict) and isinstance(payload.get("guesses"), list):
        payload = payload["guesses"]
    return payload if isinstance(payload, list) else [payload]


# ---------------------------------------------------------------------------
# Session state used by hooks and receipts (kept outside the repository)


def state_file(root: Path) -> Path:
    override = os.environ.get("GUESSWORK_STATE_DIR")
    if override:
        base = Path(override)
    else:
        try:
            if os.name == "nt":
                base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "guesswork" / "state"
            else:
                base = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "guesswork" / "state"
        except RuntimeError:
            import tempfile

            base = Path(tempfile.gettempdir()) / "guesswork-state"
    digest = hashlib.sha256(str(root).encode("utf-8")).hexdigest()[:16]
    return base / f"{digest}.json"


def load_state(root: Path) -> dict[str, Any]:
    path = state_file(root)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    if not isinstance(data.get("sessions"), dict):
        data["sessions"] = {}
    return data


def save_state(root: Path, state: dict[str, Any]) -> None:
    cutoff = time.time() - SESSION_TTL
    sessions = state.get("sessions") or {}
    state["sessions"] = {
        key: value
        for key, value in sessions.items()
        if isinstance(value, dict) and float(value.get("seen_at") or value.get("started_at") or 0) >= cutoff
    }
    try:
        write_json_atomic(state_file(root), state)
    except OSError:
        pass


def session_entry(state: dict[str, Any], session_id: Any) -> dict[str, Any]:
    key = session_id if nonempty(session_id) else "default"
    entry = state["sessions"].setdefault(key, {})
    entry["seen_at"] = time.time()
    return entry


# ---------------------------------------------------------------------------
# Receipts


def receipt_items(guesses: list[dict[str, Any]], include_low: bool = False, since: Optional[float] = None) -> list[dict[str, Any]]:
    items = [g for g in guesses if g["status"] == "open" and (include_low or g["stakes"] != "low")]
    if since is not None:
        items = [g for g in items if (parse_time(g.get("created_at")) or 0) >= since]
    return sort_by_risk(items)


def render_receipt(shown: list[dict[str, Any]], hidden: int, low_open: int, fmt: str = "md") -> str:
    bold = (lambda text: f"**{text}**") if fmt == "md" else (lambda text: text)
    code = (lambda text: f"`{text}`") if fmt == "md" else (lambda text: text)
    if not shown:
        if low_open:
            return (
                f"{bold('Guesswork')}: no decisions need you. "
                f"{plural(low_open, 'low-stakes guess', 'low-stakes guesses')} logged "
                f"({code('guesswork list --stakes low')})."
            )
        return f"{bold('Guesswork')}: no open guesses."
    total = len(shown) + hidden
    high = sum(1 for g in shown if g["stakes"] == "high")
    need_word = "needs" if total == 1 else "need"
    header = f"{bold('Guesswork')} · {plural(total, 'decision')} {need_word} you"
    if high:
        header += f" ({high} high stakes)"
    lines = [header, ""]
    for number, guess in enumerate(shown, start=1):
        lines.append(f"{number}. {bold(guess['title'])} ({tag_line(guess)})")
        for key, label in options_for(guess):
            lines.append(f"   - {bold(key)} {label}")
    lines.append("")
    picks = []
    for number, guess in enumerate(shown[:3], start=1):
        picks.append(f"{number}{'b' if number == 1 and guess['alternatives'] else 'a'}")
    example = " ".join(picks)
    lines.append(
        f"Reply with your picks, like {code(example)}. {code('all a')} keeps everything as built. "
        f"{code('2: your own answer')} sets something else."
    )
    extras = []
    if hidden:
        extras.append(f"{plural(hidden, 'more decision')} waiting ({code('guesswork receipt --limit 20')})")
    if low_open:
        extras.append(f"{plural(low_open, 'low-stakes guess', 'low-stakes guesses')} logged ({code('guesswork list --stakes low')})")
    if extras:
        lines.append("Also: " + "; ".join(extras) + ".")
    return "\n".join(lines)


def remember_receipt(project: Project, shown: list[dict[str, Any]]) -> None:
    state = load_state(project.root)
    state["receipt"] = {
        "at": time.time(),
        "items": [
            {"n": number, "id": guess["id"], "keys": [key for key, _ in options_for(guess)]}
            for number, guess in enumerate(shown, start=1)
        ],
    }
    save_state(project.root, state)


REPLY_TOKEN = re.compile(r"(?<![\w])(\d{1,2})\s*[:.)]?\s*([a-e])(?![\w])", re.IGNORECASE)
REPLY_FILLER = re.compile(r"^[\s,;.&+!]*(?:(?:and|then|ok|okay|yes|please|thanks|thank you)[\s,;.&+!]*)*$", re.IGNORECASE)
REPLY_ALL = re.compile(
    r"^\s*(?:all\s*[:=]?\s*([a-e])|keep\s+(?:it\s+)?all|keep\s+everything(?:\s+as\s+built)?|all\s+as\s+built)\s*[.!]*\s*$",
    re.IGNORECASE,
)


def parse_reply(text: str, receipt: Optional[dict[str, Any]]) -> list[tuple[int, str]]:
    """Return (number, option) pairs when the whole message is a receipt reply."""
    if not isinstance(receipt, dict) or not isinstance(receipt.get("items"), list) or not receipt["items"]:
        return []
    if time.time() - float(receipt.get("at") or 0) > RECEIPT_TTL:
        return []
    text = text.strip()
    if not text or len(text) > 200:
        return []
    numbers = [item.get("n") for item in receipt["items"] if isinstance(item, dict)]
    match = REPLY_ALL.match(text)
    if match:
        key = (match.group(1) or "a").lower()
        return [(number, key) for number in numbers]
    pairs = [(int(n), key.lower()) for n, key in REPLY_TOKEN.findall(text)]
    if not pairs or not REPLY_FILLER.match(REPLY_TOKEN.sub(" ", text)):
        return []
    if any(number not in numbers for number, _ in pairs):
        return []
    return pairs


# ---------------------------------------------------------------------------
# Resolving references to guesses


def resolve_ref(ref: str, by_id: dict[str, dict[str, Any]], receipt: Optional[dict[str, Any]]) -> dict[str, Any]:
    text = ref.strip()
    if text in by_id:
        return by_id[text]
    if text.isdigit():
        items = receipt.get("items") if isinstance(receipt, dict) else None
        for item in items or []:
            if isinstance(item, dict) and item.get("n") == int(text):
                guess = by_id.get(item.get("id"))
                if guess is None:
                    raise GuessworkError(f"receipt item {text} points to {item.get('id')}, which no longer exists")
                return guess
        raise GuessworkError(f"there is no item {text} in the latest receipt; run guesswork receipt or use a guess id")
    matches = [guess for key, guess in by_id.items() if key.startswith(text)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise GuessworkError(f"{text} matches several guesses: {', '.join(sorted(g['id'] for g in matches))}")
    raise GuessworkError(f"no guess matches {text}")


def load_or_fail(project: Project) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    guesses, problems = project.load()
    for problem in problems:
        print(f"guesswork: skipped invalid file {problem}", file=sys.stderr)
    return guesses, {guess["id"]: guess for guess in guesses}


# ---------------------------------------------------------------------------
# Commands


def project_from(args: argparse.Namespace) -> Project:
    if getattr(args, "root", None):
        return Project(Path(args.root))
    return Project(find_root(Path.cwd()))


def cmd_init(args: argparse.Namespace) -> int:
    project = project_from(args)
    created = project.ensure()
    config_path = project.ledger / CONFIG_NAME
    if not config_path.exists():
        write_json_atomic(config_path, DEFAULT_CONFIG)
    print(f"{'Created' if created else 'Found'} {project.display(project.ledger)}/ in {project.root}")
    if args.agents_md:
        agents = project.root / "AGENTS.md"
        existing = agents.read_text(encoding="utf-8") if agents.exists() else ""
        if "## Guesswork" in existing:
            print("AGENTS.md already describes Guesswork")
        else:
            separator = "\n" if existing.endswith("\n") or not existing else "\n\n"
            write_text_atomic(agents, existing + (separator if existing else "") + AGENTS_SECTION)
            print("Added the Guesswork convention to AGENTS.md")
    print("Commit .guesswork/ so every agent session and reviewer shares the same decisions.")
    return 0


def cmd_log(args: argparse.Namespace) -> int:
    project = project_from(args)
    entries = read_log_input(args)
    guesses, by_id = load_or_fail(project)
    by = clean_text(args.by) or os.environ.get("GUESSWORK_AGENT") or "agent"
    taken = set(by_id)
    if project.guess_dir.is_dir():
        taken.update(path.stem for path in project.guess_dir.glob("*.json"))
    by_title = {guess["title"].lower(): guess for guess in guesses}
    prepared: list[tuple[str, dict[str, Any], Optional[str]]] = []
    for data in entries:
        if not isinstance(data, dict):
            raise GuessworkError("each guess must be a JSON object")
        title = clean_text(first_present(data, "title", "guess", "decision")) or ""
        existing = by_title.get(title.lower())
        supersedes = clean_text(data.get("supersedes"))
        if supersedes and supersedes not in by_id:
            raise GuessworkError(f"supersedes points to {supersedes}, which does not exist")
        if existing and existing["status"] in ("open", "testing"):
            merged = {field: existing[field] for field in ("category", "stakes", "reversible", "basis")}
            merged.update(data)
            merged["id"] = None
            update = build_guess(project, merged, taken, by)
            for item in update["where"]:
                if item not in existing["where"]:
                    existing["where"].append(item)
            for item in update["alternatives"]:
                if item not in existing["alternatives"] and len(existing["alternatives"]) < MAX_ALTERNATIVES:
                    existing["alternatives"].append(item)
            for field in ("why", "question"):
                if update[field]:
                    existing[field] = update[field]
            for field in ("category", "stakes", "reversible", "basis"):
                existing[field] = update[field]
            existing["updated_at"] = now_iso()
            prepared.append(("updated", existing, None))
            continue
        if existing and existing["status"] == "decided":
            prepared.append(("decided", existing, None))
            continue
        guess = build_guess(project, data, taken, by)
        taken.add(guess["id"])
        by_title[guess["title"].lower()] = guess
        prepared.append(("logged", guess, supersedes))
    created = project.ensure()
    if created:
        print(f"Created {LEDGER_DIR}/ (commit it with your code)")
    for action, guess, supersedes in prepared:
        if action == "decided":
            print(f"= {guess['id']} was already decided: {current_behavior(guess)}")
            continue
        project.save(guess)
        marker = "+" if action == "logged" else "~"
        print(f"{marker} {guess['id']}  {guess['stakes'].upper():6} {guess['category']:13} {guess['title']}")
        if supersedes:
            old = by_id[supersedes]
            old["superseded_by"] = guess["id"]
            record(old, "superseded", by, f"replaced by {guess['id']}")
            project.save(old)
            print(f"  {supersedes} is now superseded by {guess['id']}")
    if args.receipt:
        print()
        return cmd_receipt(argparse.Namespace(root=args.root, limit=None, format="md", all=False, since=None))
    if any(action != "decided" and guess["status"] == "open" and guess["stakes"] != "low" for action, guess, _ in prepared):
        print("Next: end your reply with the output of `guesswork receipt` so the owner can answer.")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    project = project_from(args)
    guesses, _ = load_or_fail(project)
    if args.status == "active":
        selected = [g for g in guesses if g["status"] in ACTIVE_STATUSES]
    elif args.status == "all":
        selected = list(guesses)
    else:
        selected = [g for g in guesses if g["status"] == args.status]
    if args.stakes:
        selected = [g for g in selected if g["stakes"] == args.stakes]
    if args.category:
        selected = [g for g in selected if g["category"] == args.category]
    if args.where:
        target = project.relative(args.where)
        selected = [g for g in selected if any(where_matches(w, target) or where_matches(target, strip_anchor(w)) for w in g["where"])]
    status_rank = {status: index for index, status in enumerate(STATUSES)}
    selected.sort(key=lambda g: (status_rank[g["status"]], -risk(g), g["id"]))
    if args.json:
        print(json.dumps([order_guess(g) for g in selected], indent=2, ensure_ascii=False))
        return 0
    if not selected:
        print("No guesses match." if guesses else "No guesses recorded yet. Agents add them with guesswork log.")
        return 0
    for guess in selected:
        status = guess["status"]
        if status == "decided" and guess["resolution"]["choice"] != "a":
            status = "changed"
        print(f"{status:10} {guess['stakes']:6} {guess['category']:13} {guess['id']}")
        print(f"           {current_behavior(guess)}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    project = project_from(args)
    _, by_id = load_or_fail(project)
    guess = resolve_ref(args.ref, by_id, load_state(project.root).get("receipt"))
    if args.json:
        print(json.dumps(order_guess(guess), indent=2, ensure_ascii=False))
        return 0
    print(f"{guess['id']}  [{guess['status']}]")
    print(f"  {guess['title']}")
    print(f"  {tag_line(guess)} · basis: {guess['basis']}")
    if guess.get("why"):
        print(f"  Why: {guess['why']}")
    if guess.get("question"):
        print(f"  Question: {guess['question']}")
    if guess["where"]:
        print(f"  Where: {', '.join(guess['where'])}")
    for key, label in options_for(guess):
        print(f"    {key}) {label}")
    if guess["status"] == "decided":
        resolution = guess["resolution"]
        print(f"  Decided by {resolution['by']} on {day_of(resolution['at'])}: {resolution['decision']}")
        if resolution.get("note"):
            print(f"  Note: {resolution['note']}")
    if guess["status"] == "testing":
        print(f"  Testing: {guess['test']['plan']}")
    if guess["status"] == "superseded":
        print(f"  Superseded by {guess['superseded_by']}")
    print(f"  Recorded by {guess['created_by']} on {day_of(guess['created_at'])}")
    return 0


def cmd_receipt(args: argparse.Namespace) -> int:
    project = project_from(args)
    guesses, _ = load_or_fail(project)
    limit = args.limit or project.config()["receipt_limit"]
    since = parse_time(args.since) if args.since else None
    if args.since and since is None:
        raise GuessworkError("--since must be an ISO date or datetime")
    items = receipt_items(guesses, include_low=args.all, since=since)
    shown, hidden = items[:limit], max(0, len(items) - limit)
    low_open = 0 if args.all else sum(1 for g in guesses if g["status"] == "open" and g["stakes"] == "low")
    if args.format == "json":
        payload = [
            {"n": number, "id": g["id"], "title": g["title"], "stakes": g["stakes"], "category": g["category"],
             "reversible": g["reversible"], "options": [{"key": k, "label": label} for k, label in options_for(g)]}
            for number, g in enumerate(shown, start=1)
        ]
        print(json.dumps({"items": payload, "more": hidden, "low_open": low_open}, indent=2, ensure_ascii=False))
    else:
        print(render_receipt(shown, hidden, low_open, args.format))
    remember_receipt(project, shown)
    return 0


def parse_decide_tokens(tokens: list[str]) -> list[tuple[str, Optional[str]]]:
    pairs: list[tuple[str, Optional[str]]] = []
    joined = " ".join(tokens).strip()
    for part in re.split(r"[\s,;]+", joined):
        if not part:
            continue
        match = re.fullmatch(r"(\d{1,2})[:.)]?([a-eA-E])", part)
        if match:
            pairs.append((match.group(1), match.group(2).lower()))
            continue
        match = re.fullmatch(r"(g-[a-z0-9-]+)[=:]([a-eA-E])", part)
        if match:
            pairs.append((match.group(1), match.group(2).lower()))
            continue
        pairs.append((part, None))
    return pairs


def cmd_decide(args: argparse.Namespace) -> int:
    project = project_from(args)
    _, by_id = load_or_fail(project)
    receipt = load_state(project.root).get("receipt")
    by = clean_text(args.by) or "owner"
    targets: list[tuple[dict[str, Any], str]] = []
    if args.all:
        items = receipt.get("items") if isinstance(receipt, dict) else None
        if not items:
            raise GuessworkError("--all needs a recent receipt; run guesswork receipt first")
        for item in items:
            guess = by_id.get(item.get("id"))
            if guess is not None and guess["status"] == "open":
                targets.append((guess, args.all.lower()))
    pairs = parse_decide_tokens(args.choices)
    for ref, choice in pairs:
        guess = resolve_ref(ref, by_id, receipt)
        if choice is None:
            if not args.custom:
                raise GuessworkError(f"say which option to pick for {ref}, like {ref}b, or give --custom")
            choice = "custom"
        targets.append((guess, choice))
    if args.custom and sum(1 for _, choice in targets if choice == "custom") != 1:
        raise GuessworkError("--custom applies to exactly one guess, given without an option letter")
    if not targets:
        raise GuessworkError("nothing to decide; give choices like 1b 2a, or ids like g-some-guess=b")
    for guess, choice in targets:
        if guess["status"] in ("dismissed", "superseded"):
            raise GuessworkError(f"{guess['id']} is {guess['status']} and cannot be decided")
        keys = [key for key, _ in options_for(guess)]
        if choice != "custom" and choice not in keys:
            raise GuessworkError(f"{guess['id']} has options {', '.join(keys)}, not {choice}")
    changes = []
    for guess, choice in targets:
        previous = guess.get("resolution")
        decision = clean_text(args.custom) if choice == "custom" else decision_for(guess, choice)
        guess["resolution"] = {"choice": choice, "decision": decision, "by": by, "at": now_iso(), "note": clean_text(args.note)}
        guess["test"] = None
        record(guess, "decided", by, clean_text(args.note))
        project.save(guess)
        verb = "changed" if previous else "decided"
        print(f"{verb} {guess['id']}: {decision}")
        if choice != "a":
            changes.append((guess, decision))
    if changes:
        print()
        print("Update the code so it matches these decisions:")
        for guess, decision in changes:
            where = f" ({', '.join(guess['where'])})" if guess["where"] else ""
            print(f"- {guess['id']}: {decision}{where}")
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    project = project_from(args)
    _, by_id = load_or_fail(project)
    guess = resolve_ref(args.ref, by_id, load_state(project.root).get("receipt"))
    plan = clean_text(args.plan)
    if not plan:
        raise GuessworkError("--plan must describe the test that will settle this guess")
    by = clean_text(args.by) or "owner"
    guess["test"] = {"plan": plan, "by": by, "at": now_iso()}
    record(guess, "testing", by, plan)
    project.save(guess)
    print(f"testing {guess['id']}: {plan}")
    return 0


def cmd_dismiss(args: argparse.Namespace) -> int:
    project = project_from(args)
    _, by_id = load_or_fail(project)
    guess = resolve_ref(args.ref, by_id, load_state(project.root).get("receipt"))
    record(guess, "dismissed", clean_text(args.by) or "owner", clean_text(args.note))
    project.save(guess)
    print(f"dismissed {guess['id']}")
    return 0


def cmd_reopen(args: argparse.Namespace) -> int:
    project = project_from(args)
    _, by_id = load_or_fail(project)
    guess = resolve_ref(args.ref, by_id, load_state(project.root).get("receipt"))
    guess["resolution"] = None
    guess["test"] = None
    guess["superseded_by"] = None
    record(guess, "open", clean_text(args.by) or "owner", clean_text(args.note))
    project.save(guess)
    print(f"reopened {guess['id']}")
    return 0


def related_guesses(guesses: list[dict[str, Any]], files: list[str]) -> list[dict[str, Any]]:
    return [
        guess
        for guess in guesses
        if guess["status"] in ACTIVE_STATUSES and any(where_matches(entry, file) for entry in guess["where"] for file in files)
    ]


def render_context(guesses: list[dict[str, Any]], files: list[str]) -> str:
    selected = related_guesses(guesses, files) if files else [g for g in guesses if g["status"] in ACTIVE_STATUSES]
    locked = sorted((g for g in selected if g["status"] == "decided"), key=lambda g: (g["category"], g["id"]))
    testing = [g for g in selected if g["status"] == "testing"]
    pending = sort_by_risk(g for g in selected if g["status"] == "open")
    lines: list[str] = []
    scope = f" for {', '.join(files)}" if files else ""
    if not selected:
        return f"No recorded decisions{scope}."
    if locked:
        lines.append(f"Locked decisions{scope} (the owner chose these; ask before changing them):")
        for guess in locked:
            lines.append(f"- {guess['id']} [{guess['category']}] {current_behavior(guess)} (decided {day_of(guess['resolution']['at'])})")
    if testing:
        lines.append("Under test (leave as is until the test settles it):")
        for guess in testing:
            lines.append(f"- {guess['id']} [{guess['category']}] {guess['title']} (test: {guess['test']['plan']})")
    if pending:
        lines.append("Open guesses (still waiting for the owner):")
        for guess in pending:
            lines.append(f"- {guess['id']} [{guess['stakes']} · {guess['category']}] {guess['title']}")
    return "\n".join(lines)


def cmd_context(args: argparse.Namespace) -> int:
    project = project_from(args)
    guesses, _ = load_or_fail(project)
    files = [project.relative(path) for path in args.paths]
    if args.json:
        selected = related_guesses(guesses, files) if files else [g for g in guesses if g["status"] in ACTIVE_STATUSES]
        print(json.dumps([order_guess(g) for g in selected], indent=2, ensure_ascii=False))
        return 0
    print(render_context(guesses, files))
    return 0


def summary_counts(guesses: list[dict[str, Any]]) -> dict[str, Any]:
    open_ = [g for g in guesses if g["status"] == "open"]
    return {
        "total": sum(1 for g in guesses if g["status"] in ACTIVE_STATUSES),
        "open": len(open_),
        "open_high": sum(1 for g in open_ if g["stakes"] == "high"),
        "open_medium": sum(1 for g in open_ if g["stakes"] == "medium"),
        "open_low": sum(1 for g in open_ if g["stakes"] == "low"),
        "decided": sum(1 for g in guesses if g["status"] == "decided"),
        "testing": sum(1 for g in guesses if g["status"] == "testing"),
        "coverage": coverage(guesses),
    }


def cmd_status(args: argparse.Namespace) -> int:
    project = project_from(args)
    guesses, _ = load_or_fail(project)
    counts = summary_counts(guesses)
    if args.format == "json":
        print(json.dumps(counts, indent=2))
        return 0
    needs = counts["open_high"] + counts["open_medium"]
    if args.format == "statusline":
        if needs:
            print(f"guesswork: {needs} need{'s' if needs == 1 else ''} you")
        return 0
    if not counts["total"]:
        print("guesswork: no guesses recorded yet")
        return 0
    reviewed = "" if counts["coverage"] is None else f", {round(counts['coverage'] * 100)}% of high and medium stakes reviewed"
    print(
        f"guesswork: {counts['open']} open ({counts['open_high']} high, {counts['open_medium']} medium), "
        f"{counts['decided']} decided, {counts['testing']} testing{reviewed}"
    )
    return 0


# ---------------------------------------------------------------------------
# Git-aware checks and pull request summaries


class Change:
    def __init__(self, kind: str, before: Optional[dict[str, Any]], after: Optional[dict[str, Any]]) -> None:
        self.kind = kind
        self.before = before
        self.after = after


def resolve_base(root: Path, base: Optional[str]) -> str:
    candidates: list[str] = []
    if base:
        candidates.append(base)
    else:
        env_base = os.environ.get("GITHUB_BASE_REF")
        if env_base:
            candidates.append(f"origin/{env_base}")
        head = git(root, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
        if head is not None and head.returncode == 0 and head.stdout.strip():
            candidates.append(head.stdout.strip())
        candidates += ["origin/main", "origin/master", "main", "master"]
    for ref in candidates:
        result = git(root, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
        if result is not None and result.returncode == 0:
            return ref
    raise GuessworkError(
        f"could not find the base branch (tried {', '.join(candidates)}). Pass --base, and in CI check out "
        "full history (actions/checkout with fetch-depth: 0)."
    )


def read_json_text(text: str) -> Optional[dict[str, Any]]:
    try:
        data = json.loads(text)
    except ValueError:
        return None
    return data if isinstance(data, dict) and not validate_guess(data) else None


def changed_guesses(project: Project, base: str) -> list[Change]:
    merge_base = git(project.root, "merge-base", base, "HEAD")
    point = merge_base.stdout.strip() if merge_base is not None and merge_base.returncode == 0 and merge_base.stdout.strip() else base
    prefix = f"{LEDGER_DIR}/{GUESS_DIR}"
    diff = git(project.root, "diff", "--name-status", "--no-renames", point, "--", prefix)
    if diff is None or diff.returncode != 0:
        raise GuessworkError(f"git diff against {base} failed: {diff.stderr.strip() if diff is not None else 'git is not available'}")
    entries: dict[str, str] = {}
    for line in diff.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[-1].endswith(".json"):
            entries[parts[-1]] = parts[0][:1]
    untracked = git(project.root, "ls-files", "--others", "--exclude-standard", "--", prefix)
    if untracked is not None and untracked.returncode == 0:
        for line in untracked.stdout.splitlines():
            if line.endswith(".json"):
                entries.setdefault(line, "A")
    changes: list[Change] = []
    for path, letter in sorted(entries.items()):
        before = None
        if letter in ("M", "D"):
            shown = git(project.root, "show", f"{point}:{path}")
            if shown is not None and shown.returncode == 0:
                before = read_json_text(shown.stdout)
        after = None
        if letter != "D":
            full = project.root / path
            try:
                after = read_json_text(full.read_text(encoding="utf-8"))
            except OSError:
                after = None
        kind = {"A": "added", "M": "modified", "D": "deleted"}.get(letter, "modified")
        changes.append(Change(kind, before, after))
    return changes


def blocking(guesses: Iterable[dict[str, Any]], level: str) -> list[dict[str, Any]]:
    levels = {"high": ("high",), "medium": ("high", "medium"), "low": STAKES, "never": ()}[level]
    return sort_by_risk(g for g in guesses if g["status"] == "open" and g["stakes"] in levels)


def cmd_check(args: argparse.Namespace) -> int:
    project = project_from(args)
    guesses, problems = project.load()
    if problems:
        print("guesswork check: the ledger has invalid files:")
        for problem in problems:
            print(f"- {problem}")
        return 2
    level = args.fail_on or project.config()["fail_on"]
    scope = guesses
    scope_note = ""
    if args.base:
        base = resolve_base(project.root, args.base)
        scope = [change.after for change in changed_guesses(project, base) if change.after]
        scope_note = f" changed since {base}"
    found = blocking(scope, level) if level != "never" else []
    open_total = sum(1 for g in scope if g["status"] == "open")
    if found:
        print(f"guesswork check: {plural(len(found), 'open guess', 'open guesses')}{scope_note} at or above {level} stakes")
        for guess in found:
            print(f"- {guess['id']} [{guess['stakes']} · {guess['category']}] {guess['title']}")
        print("Answer them in your agent session (reply to the receipt) or run: guesswork decide <id>=<option>")
        return 1
    threshold = "no threshold" if level == "never" else f"none at or above {level} stakes"
    print(f"guesswork check: passed ({plural(open_total, 'open guess', 'open guesses')}{scope_note}, {threshold})")
    return 0


def md_cell(text: str) -> str:
    """Flatten text for a Markdown table cell so ledger content cannot add HTML or break the table."""
    flat = " ".join(str(text).split())
    return flat.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("|", "\\|")


def stakes_icon(stakes: str) -> str:
    return {"high": "\U0001F534", "medium": "\U0001F7E1", "low": "⚪"}.get(stakes, "")


def change_status(change: Change) -> str:
    guess = change.after
    assert guess is not None
    if guess["status"] == "open":
        return "**Open**, needs the owner"
    if guess["status"] == "decided":
        before_decided = change.before is not None and change.before.get("status") == "decided"
        verb = "Changed" if guess["resolution"]["choice"] != "a" else "Kept"
        when = "" if before_decided else " in this change"
        return f"{verb} by {guess['resolution']['by']}{when}"
    if guess["status"] == "testing":
        return "Under test"
    return guess["status"].capitalize()


def render_pr(changes: list[Change], base: str) -> str:
    present = [change for change in changes if change.after is not None]
    lines = [PR_MARKER]
    if not present:
        lines += [
            "### Guesswork: no recorded product decisions in this change",
            "",
            f"Compared with `{base}`. If this change adds behavior nobody specified, ask your agent to record it with `guesswork log`.",
        ]
        return "\n".join(lines) + "\n"
    guesses = [change.after for change in present]
    open_ = [g for g in guesses if g["status"] == "open" and g["stakes"] != "low"]  # type: ignore[index]
    open_high = sum(1 for g in open_ if g["stakes"] == "high")  # type: ignore[index]
    open_low = sum(1 for g in guesses if g["status"] == "open" and g["stakes"] == "low")  # type: ignore[index]
    lines.append(f"### Guesswork: {plural(len(present), 'product decision')} in this change")
    lines.append("")
    if open_:
        need = "needs" if len(open_) == 1 else "need"
        detail = f", including {open_high} with high stakes" if open_high else ""
        lines.append(
            f"> **{plural(len(open_), 'decision')} still {need} an owner{detail}.** "
            "An agent made these choices without instructions. Review them before merging."
        )
    elif open_low:
        lines.append("Every high and medium stakes decision in this change has an owner's answer.")
    else:
        lines.append("Every decision in this change has an owner's answer.")
    lines.append("")
    status_rank = {"open": 0, "testing": 1, "decided": 2}

    def order(change: Change) -> tuple[int, int, str]:
        guess = change.after
        assert guess is not None
        return (status_rank.get(guess["status"], 3), -risk(guess), guess["id"])

    main_rows = sorted((c for c in present if c.after["stakes"] != "low"), key=order)  # type: ignore[index]
    low_rows = sorted((c for c in present if c.after["stakes"] == "low"), key=order)  # type: ignore[index]

    def table(rows: list[Change]) -> list[str]:
        out = ["| | Decision | Category | Status | Where |", "|:-:|:--|:--|:--|:--|"]
        for change in rows:
            guess = change.after
            assert guess is not None
            where = ", ".join(f"`{md_cell(item)}`" for item in guess["where"][:3]) or " "
            out.append(
                f"| {stakes_icon(guess['stakes'])} | {md_cell(current_behavior(guess))} | {guess['category']} | "
                f"{change_status(change)} | {where} |"
            )
        return out

    if main_rows:
        lines += table(main_rows)
        lines.append("")
    if low_rows:
        lines.append(f"<details><summary>{plural(len(low_rows), 'low-stakes decision')}</summary>")
        lines.append("")
        lines += table(low_rows)
        lines.append("")
        lines.append("</details>")
        lines.append("")
    if open_:
        lines.append("<details><summary>How to answer the open decisions</summary>")
        lines.append("")
        for guess in sort_by_risk(open_):  # type: ignore[arg-type]
            options = "; ".join(f"**{key}** {md_cell(label)}" for key, label in options_for(guess))
            lines.append(f"- `{guess['id']}`: {options}")
        lines.append("")
        lines.append("Reply to your agent's receipt, or run `guesswork decide <id>=<option>` and push the ledger change.")
        lines.append("")
        lines.append("</details>")
        lines.append("")
    lines.append(f"<sub>Compared with `{base}` by Guesswork {__version__}. \U0001F534 high · \U0001F7E1 medium · ⚪ low stakes.</sub>")
    return "\n".join(lines) + "\n"


def cmd_pr(args: argparse.Namespace) -> int:
    project = project_from(args)
    base = resolve_base(project.root, args.base)
    text = render_pr(changed_guesses(project, base), base)
    if args.out:
        write_text_atomic(Path(args.out), text)
        print(f"Wrote {args.out}")
    else:
        print(text, end="")
    return 0


# ---------------------------------------------------------------------------
# HTML report

REPORT_CSS = """
:root {
  --bg: #f6f5f2; --panel: #ffffff; --ink: #1c1b19; --muted: #6a675f; --line: #e5e2db;
  --high: #c2410c; --high-bg: #fdeee4; --medium: #a16207; --medium-bg: #fbf3dc; --low: #5b6168; --low-bg: #efeeea;
  --ok: #15803d; --ok-bg: #e7f4ec; --accent: #4338ca; --accent-bg: #eceefe;
  --sans: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #121211; --panel: #1b1a18; --ink: #ecebe7; --muted: #a29f97; --line: #2d2b27;
    --high: #fb923c; --high-bg: #3b1f0f; --medium: #facc15; --medium-bg: #342c0c; --low: #a29f97; --low-bg: #262522;
    --ok: #4ade80; --ok-bg: #102a1a; --accent: #a5b4fc; --accent-bg: #20213d;
  }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 15px/1.55 var(--sans); -webkit-font-smoothing: antialiased; }
.wrap { max-width: 1140px; margin: 0 auto; padding: 28px 20px 64px; }
.top { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; flex-wrap: wrap; }
.brand { font-weight: 750; font-size: 18px; letter-spacing: -0.01em; }
.brand span { color: var(--muted); font-weight: 500; }
.meta { color: var(--muted); font-size: 13px; }
h1 { font-size: clamp(28px, 4vw, 40px); line-height: 1.1; letter-spacing: -0.025em; margin: 26px 0 10px; }
.lede { color: var(--muted); margin: 0 0 24px; max-width: 72ch; font-size: 16px; }
.stats { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.stat { background: var(--panel); border: 1px solid var(--line); border-radius: 16px; padding: 16px 18px; }
.stat .n { font-size: 32px; font-weight: 750; letter-spacing: -0.03em; line-height: 1.1; }
.stat .l { color: var(--muted); font-size: 13px; margin-top: 4px; }
.stat.alert .n { color: var(--high); }
.stat.good .n { color: var(--ok); }
.meter { height: 8px; background: var(--line); border-radius: 99px; overflow: hidden; margin-top: 10px; }
.meter i { display: block; height: 100%; background: var(--ok); border-radius: 99px; }
.toolbar { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin: 28px 0 0; }
.toolbar input { flex: 1 1 240px; min-width: 0; font: inherit; padding: 9px 12px; border-radius: 12px; border: 1px solid var(--line); background: var(--panel); color: var(--ink); }
.chip { font: inherit; font-size: 13px; padding: 7px 12px; border-radius: 99px; border: 1px solid var(--line); background: var(--panel); color: var(--ink); cursor: pointer; }
.chip[aria-pressed="true"] { background: var(--ink); color: var(--bg); border-color: var(--ink); }
.layout { display: grid; grid-template-columns: minmax(0, 1.9fr) minmax(0, 1fr); gap: 22px; margin-top: 22px; align-items: start; }
h2 { font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); margin: 0 0 12px; font-weight: 650; }
section { margin-bottom: 28px; }
.card { background: var(--panel); border: 1px solid var(--line); border-radius: 16px; padding: 16px 18px; margin-bottom: 12px; }
.card.high { border-left: 4px solid var(--high); }
.card.medium { border-left: 4px solid var(--medium); }
.card h3 { font-size: 17px; line-height: 1.35; margin: 8px 0 6px; letter-spacing: -0.01em; }
.why { color: var(--muted); margin: 0 0 10px; font-size: 14px; }
.tags { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; color: var(--muted); font-size: 12px; }
.pill { display: inline-block; font-size: 12px; font-weight: 650; padding: 2px 9px; border-radius: 99px; }
.pill.high { color: var(--high); background: var(--high-bg); }
.pill.medium { color: var(--medium); background: var(--medium-bg); }
.pill.low { color: var(--low); background: var(--low-bg); }
.pill.ok { color: var(--ok); background: var(--ok-bg); }
.pill.accent { color: var(--accent); background: var(--accent-bg); }
.gid { font-family: var(--mono); font-size: 11.5px; margin-left: auto; }
.opts { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0 8px; }
.opt { font: inherit; font-size: 13.5px; text-align: left; border: 1px solid var(--line); background: transparent; color: var(--ink); border-radius: 12px; padding: 7px 11px; cursor: pointer; }
.opt b { color: var(--accent); margin-right: 7px; }
.opt:hover, .opt:focus-visible { border-color: var(--accent); background: var(--accent-bg); outline: none; }
.opt.copied::after { content: "copied"; margin-left: 8px; color: var(--ok); font-size: 12px; font-weight: 600; }
code { font-family: var(--mono); font-size: 12px; background: var(--low-bg); padding: 1px 6px; border-radius: 6px; }
.where { display: flex; gap: 6px; flex-wrap: wrap; }
table { width: 100%; border-collapse: collapse; font-size: 14px; background: var(--panel); border: 1px solid var(--line); border-radius: 16px; overflow: hidden; }
th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--line); vertical-align: top; }
tr:last-child td { border-bottom: 0; }
th { color: var(--muted); font-weight: 650; font-size: 12px; text-transform: uppercase; letter-spacing: 0.06em; }
.side .box { background: var(--panel); border: 1px solid var(--line); border-radius: 16px; padding: 16px 18px; margin-bottom: 16px; }
.row { display: grid; grid-template-columns: minmax(0, 1fr) 110px 24px; gap: 10px; align-items: center; font-size: 13px; margin: 7px 0; }
.row .name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.row .count { text-align: right; color: var(--muted); font-variant-numeric: tabular-nums; }
.bar { height: 8px; background: var(--line); border-radius: 99px; overflow: hidden; display: flex; }
.bar i { display: block; height: 100%; }
.bar i.high { background: var(--high); } .bar i.medium { background: var(--medium); } .bar i.low { background: var(--low); }
.spark { display: flex; align-items: flex-end; gap: 4px; height: 64px; }
.spark i { flex: 0 1 26px; background: var(--accent); border-radius: 4px 4px 0 0; min-height: 3px; opacity: 0.85; }
.legend { display: flex; gap: 12px; color: var(--muted); font-size: 12px; margin-top: 8px; flex-wrap: wrap; }
.legend span::before { content: ""; display: inline-block; width: 8px; height: 8px; border-radius: 99px; margin-right: 6px; background: var(--c); }
.empty { color: var(--muted); padding: 22px; text-align: center; border: 1px dashed var(--line); border-radius: 16px; }
.hint { color: var(--muted); font-size: 13px; margin: -4px 0 12px; }
details summary { cursor: pointer; color: var(--muted); font-size: 14px; margin: 6px 0 12px; }
footer { color: var(--muted); font-size: 12.5px; margin-top: 36px; border-top: 1px solid var(--line); padding-top: 16px; }
.nowrap { white-space: nowrap; }
.gid { overflow-wrap: anywhere; }
[hidden] { display: none !important; }
@media (max-width: 880px) {
  .stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .layout { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  table, tbody, tr, td { display: block; width: 100%; }
  thead { display: none; }
  tr { border-bottom: 1px solid var(--line); padding: 10px 14px; }
  tr:last-child { border-bottom: 0; }
  td { border: 0; padding: 3px 0; }
}
"""

REPORT_JS = """
(function () {
  var search = document.getElementById("q");
  var state = { status: "all", stakes: "all" };
  function apply() {
    var text = (search.value || "").toLowerCase();
    document.querySelectorAll("[data-guess]").forEach(function (el) {
      var ok = (state.status === "all" || el.dataset.status === state.status)
        && (state.stakes === "all" || el.dataset.stakes === state.stakes)
        && (!text || el.dataset.text.indexOf(text) !== -1);
      el.hidden = !ok;
    });
  }
  document.querySelectorAll("[data-filter]").forEach(function (chip) {
    chip.addEventListener("click", function () {
      var group = chip.dataset.filter;
      state[group] = chip.dataset.value;
      document.querySelectorAll('[data-filter="' + group + '"]').forEach(function (other) {
        other.setAttribute("aria-pressed", other === chip ? "true" : "false");
      });
      apply();
    });
  });
  search.addEventListener("input", apply);
  function copy(text) {
    if (navigator.clipboard && window.isSecureContext) { return navigator.clipboard.writeText(text); }
    var area = document.createElement("textarea");
    area.value = text; document.body.appendChild(area); area.select();
    try { document.execCommand("copy"); } finally { document.body.removeChild(area); }
    return Promise.resolve();
  }
  document.querySelectorAll("[data-copy]").forEach(function (button) {
    button.addEventListener("click", function () {
      copy(button.dataset.copy).then(function () {
        button.classList.add("copied");
        setTimeout(function () { button.classList.remove("copied"); }, 1500);
      });
    });
  });
})();
"""


def render_report(project: Project, guesses: list[dict[str, Any]], title: Optional[str] = None) -> str:
    esc = html.escape
    name = title or project.root.name
    open_ = sort_by_risk(g for g in guesses if g["status"] == "open")
    needs = [g for g in open_ if g["stakes"] != "low"]
    small = [g for g in open_ if g["stakes"] == "low"]
    decided = sorted(
        (g for g in guesses if g["status"] == "decided"), key=lambda g: g["resolution"]["at"], reverse=True
    )
    testing = [g for g in guesses if g["status"] == "testing"]
    closed = [g for g in guesses if g["status"] in ("dismissed", "superseded")]
    active = [g for g in guesses if g["status"] in ACTIVE_STATUSES]
    ratio = coverage(guesses)
    reviewed = len(decided) + len(testing)

    if needs:
        headline = f"{plural(len(needs), 'decision')} {'needs' if len(needs) == 1 else 'need'} you"
    elif small:
        headline = f"Nothing urgent. {plural(len(small), 'small guess', 'small guesses')} still open."
    elif active:
        headline = "Every decision has an owner"
    else:
        headline = "No guesses recorded yet"
    if active:
        lede = (
            f"Agents recorded {plural(len(active), 'product decision')} in {name} that nobody specified. "
            f"The owner has answered {reviewed} of them."
        )
        if needs:
            lede += " The open ones below are ranked by what it costs if the guess is wrong."
    else:
        lede = "When an agent implements behavior nobody specified, it records the decision here with guesswork log."

    def text_blob(guess: dict[str, Any]) -> str:
        parts = [guess["id"], guess["title"], guess.get("why") or "", guess["category"], " ".join(guess["where"])]
        if guess["status"] == "decided":
            parts.append(guess["resolution"]["decision"])
        return esc(" ".join(parts).lower(), quote=True)

    def attrs(guess: dict[str, Any]) -> str:
        return f'data-guess data-status="{guess["status"]}" data-stakes="{guess["stakes"]}" data-text="{text_blob(guess)}"'

    def where_html(guess: dict[str, Any]) -> str:
        if not guess["where"]:
            return ""
        return '<div class="where">' + "".join(f"<code>{esc(item)}</code>" for item in guess["where"]) + "</div>"

    def card(guess: dict[str, Any]) -> str:
        tags = [f'<span class="pill {guess["stakes"]}">{guess["stakes"].capitalize()} stakes</span>', f"<span>{esc(guess['category'])}</span>"]
        if not guess["reversible"]:
            tags.append("<span>· hard to undo</span>")
        tags.append(f"<span>· {esc(guess['basis'])}</span>")
        tags.append(f'<span class="gid">{esc(guess["id"])}</span>')
        buttons = "".join(
            f'<button class="opt" type="button" data-copy="guesswork decide {esc(guess["id"])}={key}"><b>{key}</b>{esc(label)}</button>'
            for key, label in options_for(guess)
        )
        why = f'<p class="why">{esc(guess["why"])}</p>' if guess.get("why") else ""
        question = f'<p class="why"><strong>Question:</strong> {esc(guess["question"])}</p>' if guess.get("question") else ""
        return (
            f'<article class="card {guess["stakes"]}" {attrs(guess)}>'
            f'<div class="tags">{"".join(tags)}</div>'
            f"<h3>{esc(guess['title'])}</h3>{why}{question}"
            f'<div class="opts">{buttons}</div>{where_html(guess)}</article>'
        )

    def decided_row(guess: dict[str, Any]) -> str:
        resolution = guess["resolution"]
        badge = '<span class="pill accent">changed</span>' if resolution["choice"] != "a" else '<span class="pill ok">kept</span>'
        files = " ".join(f"<code>{esc(item)}</code>" for item in guess["where"][:3])
        note = f'<div class="why">{esc(resolution["note"])}</div>' if resolution.get("note") else ""
        return (
            f"<tr {attrs(guess)}><td><strong>{esc(resolution['decision'])}</strong>{note}"
            f'<div class="tags"><span class="gid" style="margin-left:0">{esc(guess["id"])}</span></div></td>'
            f"<td>{badge}</td><td>{esc(guess['category'])}</td>"
            f"<td>{esc(resolution['by'])} <span class='meta nowrap'>{day_of(resolution['at'])}</span></td><td>{files}</td></tr>"
        )

    def simple_row(guess: dict[str, Any], detail: str) -> str:
        return (
            f"<tr {attrs(guess)}><td><strong>{esc(guess['title'])}</strong>"
            f'<div class="tags"><span class="gid" style="margin-left:0">{esc(guess["id"])}</span></div></td>'
            f"<td>{esc(guess['category'])}</td><td>{detail}</td></tr>"
        )

    stats = [
        ("alert" if needs else "good", str(len(needs)), "decision needs you" if len(needs) == 1 else "decisions need you"),
        ("", str(len(decided)), "locked decision" if len(decided) == 1 else "locked decisions"),
        ("", str(len(small)), "small guess open" if len(small) == 1 else "small guesses open"),
        ("good" if ratio is not None and ratio >= 0.8 else "", "n/a" if ratio is None else f"{round(ratio * 100)}%", "of high and medium stakes reviewed"),
    ]
    stat_html = "".join(
        f'<div class="stat {kind}"><div class="n">{value}</div><div class="l">{label}</div>'
        + (f'<div class="meter"><i style="width:{round((ratio or 0) * 100)}%"></i></div>' if index == 3 else "")
        + "</div>"
        for index, (kind, value, label) in enumerate(stats)
    )

    def chips(group: str, values: list[tuple[str, str]]) -> str:
        return "".join(
            f'<button class="chip" type="button" data-filter="{group}" data-value="{value}" aria-pressed="{"true" if value == "all" else "false"}">{label}</button>'
            for value, label in values
        )

    toolbar = (
        '<div class="toolbar"><input id="q" type="search" placeholder="Search decisions, files, ids" aria-label="Search">'
        + chips("status", [("all", "All"), ("open", "Open"), ("decided", "Decided"), ("testing", "Testing")])
        + chips("stakes", [("all", "Any stakes"), ("high", "High"), ("medium", "Medium"), ("low", "Low")])
        + "</div>"
    )

    main: list[str] = []
    main.append("<section><h2>Needs your call</h2>")
    if needs:
        main.append('<p class="hint">Click an option to copy the command that records it, or reply to your agent\'s receipt.</p>')
        main.extend(card(g) for g in needs)
    else:
        main.append('<div class="empty">No open decisions with high or medium stakes.</div>')
    main.append("</section>")
    if small:
        main.append(f"<section><h2>Small guesses</h2><details><summary>{plural(len(small), 'low-stakes guess', 'low-stakes guesses')} that can wait</summary>")
        main.extend(card(g) for g in small)
        main.append("</details></section>")
    main.append("<section><h2>Locked decisions</h2>")
    if decided:
        main.append("<table><thead><tr><th>Decision</th><th></th><th>Category</th><th>Decided</th><th>Where</th></tr></thead><tbody>")
        main.extend(decided_row(g) for g in decided)
        main.append("</tbody></table>")
    else:
        main.append('<div class="empty">No decisions yet. Answers to receipts appear here and protect later sessions.</div>')
    main.append("</section>")
    if testing:
        main.append("<section><h2>Under test</h2><table><thead><tr><th>Guess</th><th>Category</th><th>Test</th></tr></thead><tbody>")
        main.extend(simple_row(g, esc(g["test"]["plan"])) for g in testing)
        main.append("</tbody></table></section>")
    if closed:
        main.append(f"<section><h2>Closed</h2><details><summary>{plural(len(closed), 'dismissed or superseded guess', 'dismissed or superseded guesses')}</summary>")
        main.append("<table><thead><tr><th>Guess</th><th>Category</th><th>Status</th></tr></thead><tbody>")
        main.extend(
            simple_row(g, esc(g["status"] + (f" by {g['superseded_by']}" if g.get("superseded_by") else ""))) for g in closed
        )
        main.append("</tbody></table></details></section>")

    side: list[str] = []
    by_category: dict[str, dict[str, int]] = {}
    for guess in active:
        bucket = by_category.setdefault(guess["category"], {"high": 0, "medium": 0, "low": 0})
        bucket[guess["stakes"]] += 1
    if by_category:
        widest = max(sum(bucket.values()) for bucket in by_category.values())
        rows = []
        for category, bucket in sorted(by_category.items(), key=lambda item: (-sum(item[1].values()), item[0])):
            total = sum(bucket.values())
            segments = "".join(
                f'<i class="{stakes}" style="width:{bucket[stakes] / widest * 100:.1f}%"></i>' for stakes in STAKES if bucket[stakes]
            )
            rows.append(f'<div class="row"><span class="name">{esc(category)}</span><span class="bar">{segments}</span><span class="count">{total}</span></div>')
        legend = '<div class="legend"><span style="--c:var(--high)">high</span><span style="--c:var(--medium)">medium</span><span style="--c:var(--low)">low</span></div>'
        side.append(f'<div class="box"><h2>By category</h2>{"".join(rows)}{legend}</div>')
    file_counts: dict[str, int] = {}
    for guess in active:
        for entry in {strip_anchor(item) for item in guess["where"]}:
            file_counts[entry] = file_counts.get(entry, 0) + 1
    if file_counts:
        top = sorted(file_counts.items(), key=lambda item: (-item[1], item[0]))[:8]
        widest = top[0][1]
        rows = [
            f'<div class="row"><span class="name" title="{esc(path)}"><code>{esc(path)}</code></span>'
            f'<span class="bar"><i class="medium" style="width:{count / widest * 100:.1f}%"></i></span><span class="count">{count}</span></div>'
            for path, count in top
        ]
        side.append(f'<div class="box"><h2>Hotspots</h2>{"".join(rows)}</div>')
    days: dict[str, int] = {}
    for guess in guesses:
        day = day_of(guess["created_at"])
        days[day] = days.get(day, 0) + 1
    if len(days) >= 3:
        recent = sorted(days.items())[-21:]
        tallest = max(count for _, count in recent)
        bars = "".join(f'<i title="{day}: {count}" style="height:{count / tallest * 100:.0f}%"></i>' for day, count in recent)
        span = f"{recent[0][0]} to {recent[-1][0]}" if len(recent) > 1 else recent[0][0]
        side.append(f'<div class="box"><h2>Guesses recorded</h2><div class="spark">{bars}</div><div class="legend">{esc(span)}</div></div>')
    side.append(
        '<div class="box"><h2>How this works</h2><p class="why" style="margin:0">Agents record each product decision they '
        "make without instructions. The owner answers the risky ones, and every later agent session, pull request, and "
        "CI run respects those answers.</p></div>"
    )

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return (
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>Guesswork: {esc(name)}</title><style>{REPORT_CSS}</style></head><body><div class=\"wrap\">"
        f'<div class="top"><div class="brand">guesswork <span>/ {esc(name)}</span></div>'
        f'<div class="meta">Generated {generated} · {plural(len(guesses), "guess", "guesses")} in the ledger</div></div>'
        f"<h1>{esc(headline)}</h1><p class=\"lede\">{esc(lede)}</p>"
        f'<div class="stats">{stat_html}</div>{toolbar}'
        f'<div class="layout"><div>{"".join(main)}</div><aside class="side">{"".join(side)}</aside></div>'
        f"<footer>Generated by Guesswork {__version__} from {LEDGER_DIR}/{GUESS_DIR}. "
        "Answer decisions in your agent session or with <code>guesswork decide</code>.</footer>"
        f"</div><script>{REPORT_JS}</script></body></html>\n"
    )


def cmd_report(args: argparse.Namespace) -> int:
    project = project_from(args)
    guesses, _ = load_or_fail(project)
    out = Path(args.out) if args.out else project.ledger / REPORT_NAME
    if not args.out:
        project.ensure()
    write_text_atomic(out, render_report(project, guesses, args.title))
    print(f"Wrote {out}")
    if args.open:
        webbrowser.open(out.resolve().as_uri())
    return 0


# ---------------------------------------------------------------------------
# Scan: find lines that often encode product decisions

LITERAL = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?![\w])|\b(?:true|false|True|False)\b|['\"][^'\"]{1,40}['\"]")
NUMBER = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?![\w])")
# Identifiers such as FREE_PLAN_LIMIT join words with underscores, so these rules use letter
# boundaries ((?<![a-z]) and (?![a-z])) where a plain \b would miss them.
SCAN_RULES: list[tuple[str, re.Pattern[str], Optional[re.Pattern[str]]]] = [
    ("money", re.compile(r"(?<![a-z])(?:price|pricing|amount|fees?|trial|discount|coupon|refund|tax|vat|currency|subscription|seats?|cents)(?![a-z])", re.I), LITERAL),
    ("data", re.compile(r"on_?delete|cascade|soft_?delete|deleted_?at|paranoid|purge|retention|keep_?for|archive_?after|hard_?delete|destroy_?all", re.I), None),
    ("access", re.compile(r"(?<![a-z])(?:roles?(?![a-z])|is_?admin|admin_?only|permission|authori[sz]|can_?(?:edit|view|delete|invite|manage)|is_?public|visibility|invit|share_?link|anyone_?with)", re.I), LITERAL),
    ("privacy", re.compile(r"analytics|tracking|track_?event|\.track\(|telemetry|mixpanel|posthog|segment\.(?:track|identify)|gtag|ip_?address|user_?agent|geoloc|fingerprint", re.I), None),
    ("security", re.compile(r"expir|(?<![a-z])ttl(?![a-z])|max_?age|session_?(?:timeout|length|duration|lifetime)|lockout|(?:max|login)_?(?:login_?)?attempts|password_?(?:min|max)|min_?length|rate_?limit|throttle|allow_?origin|samesite", re.I), LITERAL),
    ("notifications", re.compile(r"send_?(?:mail|email|sms)|sendmail|mailer|(?<![a-z])notif|digest|reminder|push_?notification", re.I), None),
    ("limits", re.compile(r"(?<![a-z])(?:max|min|limit|quota|threshold|timeout|page_?size|per_?page|retries|upload_?size)", re.I), NUMBER),
    ("defaults", re.compile(r"default\w*\s*[:=]|is_?default|auto_?(?:renew|publish|accept|approve|join|subscribe|enroll)", re.I), LITERAL),
]
SCAN_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".rb", ".go", ".rs", ".java", ".kt", ".swift", ".php",
    ".cs", ".ex", ".exs", ".sql", ".prisma", ".vue", ".svelte", ".dart", ".scala", ".yaml", ".yml", ".toml",
}
SCAN_SKIP = re.compile(
    r"(^|/)(node_modules|vendor|dist|build|out|coverage|target|\.next|\.nuxt|\.venv|venv|__pycache__|\.git|\.guesswork|"
    r"tests?|specs?|__tests__|__mocks__|fixtures|mocks?|e2e|cypress|stories)(/|$)|\.min\.|\.lock$|(^|/)package-lock\.json$|"
    r"\.(test|spec|stories)\.",
    re.I,
)
SCAN_IMPORT = re.compile(r"^\s*(import\s|from\s+\S+\s+import\s|require\(|use\s|#include|using\s)")


def scan_files(project: Project) -> list[str]:
    listed = git(project.root, "ls-files", "--cached", "--others", "--exclude-standard")
    if listed is not None and listed.returncode == 0:
        candidates = listed.stdout.splitlines()
    else:
        candidates = [path.relative_to(project.root).as_posix() for path in project.root.rglob("*") if path.is_file()]
    return sorted(
        rel for rel in candidates if Path(rel).suffix.lower() in SCAN_EXTENSIONS and not SCAN_SKIP.search(rel)
    )


def scan(project: Project, limit: int, per_file: int = 12) -> tuple[list[tuple[str, str, int, str]], int]:
    """Return candidate lines, picked in category order so money and data outrank limits."""
    candidates: list[tuple[str, str, int, str]] = []
    for rel in scan_files(project):
        path = project.root / rel
        try:
            if path.stat().st_size > 400_000:
                continue
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for number, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or len(stripped) > 240 or SCAN_IMPORT.match(stripped):
                continue
            for category, keyword, needs in SCAN_RULES:
                if keyword.search(stripped) and (needs is None or needs.search(stripped)):
                    candidates.append((category, rel, number, stripped))
                    break
    priority = {rule[0]: index for index, rule in enumerate(SCAN_RULES)}
    found: list[tuple[str, str, int, str]] = []
    per_path: dict[str, int] = {}
    for item in sorted(candidates, key=lambda item: (priority[item[0]], item[1], item[2])):
        if len(found) >= limit:
            break
        if per_path.get(item[1], 0) >= per_file:
            continue
        per_path[item[1]] = per_path.get(item[1], 0) + 1
        found.append(item)
    found.sort(key=lambda item: (priority[item[0]], item[1], item[2]))
    return found, len(candidates)


def cmd_scan(args: argparse.Namespace) -> int:
    project = project_from(args)
    found, total = scan(project, args.limit)
    if args.json:
        print(json.dumps([{"category": c, "path": p, "line": n, "text": t} for c, p, n, t in found], indent=2, ensure_ascii=False))
        return 0
    if not found:
        print("guesswork scan: no candidate lines found")
        return 0
    files = len({path for _, path, _, _ in found})
    shown = f", showing {len(found)}" if total > len(found) else ""
    print(f"guesswork scan: {plural(total, 'candidate line')} in source files{shown} across {plural(files, 'file')}")
    print("These lines often encode product decisions. Read each one and log only real decisions nobody specified.")
    for category in [rule[0] for rule in SCAN_RULES]:
        rows = [item for item in found if item[0] == category]
        if not rows:
            continue
        print()
        print(f"{category}: {CATEGORIES[category].lower()}")
        for _, path, number, text in rows:
            snippet = text if len(text) <= 110 else text[:107] + "..."
            print(f"  {path}:{number}  {snippet}")
    return 0


# ---------------------------------------------------------------------------
# Demo: a fictional project to try Guesswork without an agent

DEMO_GUESSES = [
    {"id": "g-workspace-delete-permanent", "title": "Deleting a workspace erases it immediately with no restore", "why": "No retention rule was given, and a hard delete was the shortest path", "category": "data", "stakes": "high", "reversible": False, "where": ["src/workspaces/delete.ts:14"], "alternatives": ["30-day restore window", "Require typing the workspace name to confirm"]},
    {"id": "g-export-includes-emails", "title": "CSV exports include every member's email address", "why": "Export copies all member columns from the members table", "category": "privacy", "stakes": "high", "where": ["src/export/members.ts:8"], "alternatives": ["Only admins can export email addresses", "Leave email addresses out of exports"]},
    {"id": "g-trial-converts-silently", "title": "Trials convert to paid on day 14 without a reminder email", "category": "money", "stakes": "high", "where": ["src/billing/trial.ts:22"], "alternatives": ["Email a reminder 3 days before the trial ends", "Require an explicit upgrade"]},
    {"id": "g-any-member-invites", "title": "Any member can invite new members", "category": "access", "stakes": "medium", "where": ["src/invites/create.ts:5"], "alternatives": ["Only admins can invite", "Members invite, admins approve"]},
    {"id": "g-invite-links-expire-7-days", "title": "Invitation links expire after 7 days", "category": "security", "stakes": "medium", "where": ["src/invites/token.ts:3"], "alternatives": ["Links expire after 24 hours", "Links work until used"]},
    {"id": "g-comment-emails-everyone", "title": "Every new comment emails all workspace members", "category": "notifications", "stakes": "medium", "where": ["src/notifications/comments.ts"], "alternatives": ["Email only people who are mentioned", "Send a daily digest instead"]},
    {"id": "g-free-plan-50-members", "title": "A free workspace holds at most 50 members", "category": "limits", "stakes": "low", "where": ["src/billing/plans.ts:7"], "alternatives": ["10 members", "No member limit"]},
]
DEMO_ANSWERS = {"g-trial-converts-silently": "b", "g-any-member-invites": "b"}


def cmd_demo(args: argparse.Namespace) -> int:
    import tempfile

    target = Path(args.dir) if args.dir else Path(tempfile.mkdtemp(prefix="guesswork-demo-"))
    project = Project(target)
    if project.initialized and any(project.guess_dir.glob("*.json")):
        raise GuessworkError(f"{target} already has a ledger; pass an empty --dir")
    project.ensure()
    for data in DEMO_GUESSES:
        project.save(build_guess(project, data, set(), "agent"))
    guesses, _ = project.load()
    by_id = {guess["id"]: guess for guess in guesses}
    for guess_id, choice in DEMO_ANSWERS.items():
        guess = by_id[guess_id]
        guess["resolution"] = {"choice": choice, "decision": decision_for(guess, choice), "by": "owner", "at": now_iso(), "note": None}
        record(guess, "decided", "owner")
        project.save(guess)
    guesses, _ = project.load()
    report = project.ledger / REPORT_NAME
    write_text_atomic(report, render_report(project, guesses, "demo-workspace-app"))
    shown = receipt_items(guesses)[: project.config()["receipt_limit"]]
    low_open = sum(1 for g in guesses if g["status"] == "open" and g["stakes"] == "low")
    remember_receipt(project, shown)
    print("An agent was asked to \"add team workspaces with invites, a free trial, and CSV export\".")
    print(f"It made {len(DEMO_GUESSES)} product decisions nobody specified. The owner already answered 2.")
    print()
    print(render_receipt(shown, 0, low_open, "text"))
    print()
    print(f"Demo project: {target}")
    print(f"Report:       {report}")
    print()
    print("Try it:")
    print(f"  guesswork --root \"{target}\" decide 1b 2c      answer like the owner would")
    print(f"  guesswork --root \"{target}\" context src/billing/trial.ts")
    print(f"  guesswork --root \"{target}\" report --open")
    if args.open:
        webbrowser.open(report.resolve().as_uri())
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    project = project_from(args)
    if not project.initialized:
        print(f"No {LEDGER_DIR}/{GUESS_DIR}/ folder in {project.root}")
        return 0
    guesses, problems = project.load()
    config_path = project.ledger / CONFIG_NAME
    if config_path.is_file():
        try:
            loaded = json.loads(config_path.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                problems.append(f"{LEDGER_DIR}/{CONFIG_NAME}: must be a JSON object")
            else:
                unknown = sorted(set(loaded) - set(DEFAULT_CONFIG))
                if unknown:
                    problems.append(f"{LEDGER_DIR}/{CONFIG_NAME}: unknown settings {', '.join(unknown)}")
        except (OSError, ValueError) as exc:
            problems.append(f"{LEDGER_DIR}/{CONFIG_NAME}: not valid JSON ({exc})")
    ids = [g["id"] for g in guesses]
    for guess in guesses:
        target = guess.get("superseded_by")
        if target and target not in ids:
            problems.append(f"{guess['id']}: superseded_by points to {target}, which does not exist")
    if problems:
        print("guesswork validate: problems found")
        for problem in problems:
            print(f"- {problem}")
        return 2
    print(f"guesswork validate: {plural(len(guesses), 'guess', 'guesses')} valid")
    return 0


# ---------------------------------------------------------------------------
# Claude Code hooks


def hooks_disabled(project: Project) -> bool:
    if os.environ.get("GUESSWORK_DISABLE", "").strip().lower() in ("1", "true", "yes", "on"):
        return True
    return not project.config()["hooks"]


def hook_project(payload: dict[str, Any]) -> Project:
    candidates = [payload.get("cwd"), os.environ.get("CLAUDE_PROJECT_DIR")]
    roots = [find_root(Path(value)) for value in candidates if nonempty(value)]
    for root in roots:
        if (root / LEDGER_DIR / GUESS_DIR).is_dir():
            return Project(root)
    if os.environ.get("CLAUDE_PROJECT_DIR"):
        return Project(find_root(Path(os.environ["CLAUDE_PROJECT_DIR"])))
    return Project(roots[0] if roots else find_root(Path.cwd()))


def session_context(project: Project) -> str:
    lines: list[str] = []
    if project.initialized:
        guesses, problems = project.load()
        decided = sorted((g for g in guesses if g["status"] == "decided"), key=lambda g: (g["category"], g["id"]))
        testing = [g for g in guesses if g["status"] == "testing"]
        counts = summary_counts(guesses)
        lines.append(
            "Guesswork is active in this project. The ledger in .guesswork/ records product decisions "
            "that were made without explicit instructions."
        )
        if decided:
            lines.append("")
            lines.append("Locked decisions. The project owner chose these, and changing them needs the owner's approval:")
            for guess in decided[:SESSION_DECISION_LIMIT]:
                where = f" [{', '.join(strip_anchor(w) for w in guess['where'][:2])}]" if guess["where"] else ""
                lines.append(f"- {guess['id']} ({guess['category']}): {current_behavior(guess)}{where}")
            if len(decided) > SESSION_DECISION_LIMIT:
                lines.append(f"- {len(decided) - SESSION_DECISION_LIMIT} more are listed by `guesswork context`.")
        if testing:
            lines.append(f"Guesses under test, to leave as they are until the test settles them: {', '.join(g['id'] for g in testing)}.")
        if counts["open"]:
            lines.append(
                f"Open guesses waiting for the owner: {counts['open_high']} high, {counts['open_medium']} medium, "
                f"{counts['open_low']} low stakes. `guesswork receipt` lists them."
            )
        if problems:
            lines.append(f"{plural(len(problems), 'ledger problem')} found. `guesswork validate` lists them.")
    else:
        lines.append("Guesswork is installed for this project. It creates .guesswork/ when the first guess is logged.")
    lines.append("")
    lines.append(PROTOCOL_NOTE)
    return "\n".join(lines)


def hook_session_start(payload: dict[str, Any]) -> Optional[dict[str, Any]]:
    project = hook_project(payload)
    if hooks_disabled(project):
        return None
    return {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": session_context(project)}}


def hook_prompt(payload: dict[str, Any]) -> Optional[dict[str, Any]]:
    project = hook_project(payload)
    if hooks_disabled(project):
        return None
    state = load_state(project.root)
    entry = session_entry(state, payload.get("session_id"))
    entry["started_at"] = time.time()
    entry["touched"] = []
    entry["nudged"] = False
    save_state(project.root, state)
    receipt = state.get("receipt")
    pairs = parse_reply(str(payload.get("prompt") or ""), receipt)
    if not pairs or not project.initialized:
        return None
    guesses, _ = project.load()
    by_id = {guess["id"]: guess for guess in guesses}
    items = {item["n"]: item for item in receipt["items"] if isinstance(item, dict)}  # type: ignore[index]
    parts = []
    for number, key in pairs:
        guess = by_id.get(items[number].get("id"))
        if guess is None:
            continue
        labels = dict(options_for(guess))
        if key not in labels:
            parts.append(f"{number}{key} = {guess['id']}: there is no option {key}; ask the user which option they meant")
        elif key == "a":
            parts.append(f"{number}{key} = {guess['id']}: keep as built ({guess['title']})")
        else:
            parts.append(f"{number}{key} = {guess['id']}: change to \"{labels[key]}\" (needs a code change)")
    if not parts:
        return None
    command = " ".join(f"{number}{key}" for number, key in pairs)
    context = (
        "This message answers the latest Guesswork receipt. "
        + "; ".join(parts)
        + f". After the code matches every answer, the answers are recorded with: guesswork decide {command}"
    )
    return {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": context}}


def hook_post_edit(payload: dict[str, Any]) -> Optional[dict[str, Any]]:
    project = hook_project(payload)
    if hooks_disabled(project):
        return None
    tool_input = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
    raw_path = tool_input.get("file_path") or tool_input.get("notebook_path")  # type: ignore[union-attr]
    if not nonempty(raw_path):
        return None
    rel = project.relative(raw_path)
    ledger_prefix = f"{LEDGER_DIR}/{GUESS_DIR}/"
    if rel.startswith(ledger_prefix) and rel.endswith(".json"):
        errors = validate_file(project.root / rel)
        if errors:
            return {
                "decision": "block",
                "reason": f"Guesswork cannot read {rel}: " + "; ".join(errors)
                + ". Fix the file to match the ledger format in the guesswork skill, or record guesses with `guesswork log`.",
            }
        return None
    if rel.startswith(LEDGER_DIR + "/") or Path(rel).is_absolute() or re.match(r"^[A-Za-z]:/", rel):
        return None
    state = load_state(project.root)
    entry = session_entry(state, payload.get("session_id"))
    touched = entry.setdefault("touched", [])
    if rel not in touched and len(touched) < 500:
        touched.append(rel)
    announced = entry.setdefault("announced", [])
    context = None
    if project.initialized and rel not in announced:
        guesses, _ = project.load()
        related = related_guesses(guesses, [rel])
        locked = [g for g in related if g["status"] == "decided"]
        pending = [g for g in related if g["status"] in ("open", "testing") and g["stakes"] != "low"]
        if locked or pending:
            announced.append(rel)
            lines = []
            if locked:
                lines.append(f"Guesswork: {rel} implements decisions the project owner made:")
                lines.extend(f"- {g['id']}: {current_behavior(g)} (decided {day_of(g['resolution']['at'])})" for g in locked)
                lines.append("A change to one of these behaviors needs the owner's approval, so it should be raised with the user before it stays.")
            if pending:
                lines.append(f"Open guesses that cover {rel} and still wait for the owner:")
                lines.extend(f"- {g['id']} ({g['stakes']} stakes, {g['status']}): {g['title']}" for g in pending)
            context = "\n".join(lines)
    save_state(project.root, state)
    if context:
        return {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": context}}
    return None


def git_changed_since(root: Path, since: float) -> list[str]:
    result = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all", timeout=10)
    if result is None or result.returncode != 0:
        return []
    entries = result.stdout.split("\0")
    paths: list[str] = []
    skip = False
    for item in entries:
        if skip:
            skip = False
            continue
        if len(item) < 4:
            continue
        code, path = item[:2], item[3:]
        if code[0] in "RC":
            skip = True
        full = root / path
        try:
            if full.is_file() and full.stat().st_mtime >= since:
                paths.append(path)
        except OSError:
            continue
    return paths


def changed_files(project: Project, entry: dict[str, Any], since: float, config: dict[str, Any]) -> list[str]:
    candidates = set(entry.get("touched") or [])
    candidates.update(git_changed_since(project.root, since))
    patterns = DEFAULT_STOP_IGNORE + list(config["ignore"])
    result = []
    for rel in sorted(candidates):
        if rel.startswith((LEDGER_DIR + "/", ".git/")) or Path(rel).is_absolute() or re.match(r"^[A-Za-z]:/", rel):
            continue
        if is_ignored(rel, patterns):
            continue
        result.append(rel)
    return result


def hook_stop(payload: dict[str, Any]) -> Optional[dict[str, Any]]:
    if payload.get("stop_hook_active"):
        return None
    project = hook_project(payload)
    if hooks_disabled(project):
        return None
    config = project.config()
    mode = config["stop_check"]
    if mode == "off":
        return None
    state = load_state(project.root)
    entry = state["sessions"].get(payload.get("session_id") if nonempty(payload.get("session_id")) else "default")
    if not isinstance(entry, dict) or "started_at" not in entry or entry.get("nudged"):
        return None
    since = float(entry["started_at"]) - CLOCK_SLACK
    guesses = project.load()[0] if project.initialized else []
    activity = [g for g in guesses if (parse_time(g.get("updated_at")) or 0) >= since]
    reason = None
    if activity:
        unseen = sort_by_risk(g for g in activity if g["status"] == "open" and g["stakes"] != "low")
        message = str(payload.get("last_assistant_message") or "")
        if unseen and "guesswork" not in message.lower():
            ids = ", ".join(g["id"] for g in unseen[:5])
            reason = (
                f"Guesswork check: this turn recorded {plural(len(unseen), 'decision')} the owner has not seen yet ({ids}). "
                "End the reply with the output of `guesswork receipt` so the owner can answer them."
            )
    elif mode == "nudge":
        changed = changed_files(project, entry, since, config)
        if changed:
            listed = ", ".join(changed[:5]) + (f", and {len(changed) - 5} more" if len(changed) > 5 else "")
            reason = (
                f"Guesswork check: this turn changed {plural(len(changed), 'file')} ({listed}) and recorded no guesses. "
                "If the work implemented behavior the user did not specify (defaults, limits, permissions, data handling, "
                "money, notifications, or wording that makes promises), record each decision with `guesswork log` and end "
                "the reply with the output of `guesswork receipt`. If the user specified all of it, end the reply with the "
                "line: Guesswork: no new guesses."
            )
    if not reason:
        return None
    entry["nudged"] = True
    save_state(project.root, state)
    return {"decision": "block", "reason": reason}


HOOKS = {
    "session-start": hook_session_start,
    "prompt": hook_prompt,
    "post-edit": hook_post_edit,
    "stop": hook_stop,
}


def cmd_hook(args: argparse.Namespace) -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        if not isinstance(payload, dict):
            payload = {}
        output = HOOKS[args.event](payload)
    except Exception:  # A hook must never break the agent session.
        if os.environ.get("GUESSWORK_DEBUG"):
            raise
        return 0
    if output:
        print(json.dumps(output))
    return 0


# ---------------------------------------------------------------------------
# Command line


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="guesswork",
        description="Keep a ledger of the product decisions your agent made without instructions.",
    )
    parser.add_argument("--version", action="version", version=f"guesswork {__version__}")
    parser.add_argument("--root", help="project root (default: nearest folder with .guesswork/ or .git)")
    commands = parser.add_subparsers(dest="command", metavar="command")

    def add(name: str, handler: Any, help_text: str) -> argparse.ArgumentParser:
        sub = commands.add_parser(name, help=help_text, description=help_text)
        sub.add_argument("--root", default=argparse.SUPPRESS, help=argparse.SUPPRESS)
        sub.set_defaults(func=handler)
        return sub

    sub = add("init", cmd_init, "create the .guesswork/ ledger")
    sub.add_argument("--agents-md", action="store_true", help="add the Guesswork convention to AGENTS.md for agents without hooks")

    sub = add("log", cmd_log, "record guesses (flags for one, or a JSON object or array on stdin)")
    sub.add_argument("--title", help="the decision as built, in plain language")
    sub.add_argument("--why", help="why this choice was made")
    sub.add_argument("--category", choices=list(CATEGORIES))
    sub.add_argument("--stakes", choices=STAKES)
    sub.add_argument("--irreversible", action="store_true", help="hard to undo once people rely on it")
    sub.add_argument("--basis", choices=BASIS, help="what the guess rests on (default: assumed)")
    sub.add_argument("--where", action="append", help="file that implements it (repeatable)")
    sub.add_argument("--alt", action="append", help="a credible alternative (repeatable, up to 4)")
    sub.add_argument("--question", help="the question the owner should answer")
    sub.add_argument("--id", help="explicit id like g-short-slug")
    sub.add_argument("--supersedes", help="id of a guess this one replaces")
    sub.add_argument("--by", help="who recorded it (default: $GUESSWORK_AGENT or agent)")
    sub.add_argument("--file", help="read guesses from a JSON file, or - for stdin")
    sub.add_argument("--receipt", action="store_true", help="print the receipt after logging")

    sub = add("list", cmd_list, "list guesses")
    sub.add_argument("--status", default="active", choices=["active", "all", *STATUSES])
    sub.add_argument("--stakes", choices=STAKES)
    sub.add_argument("--category", choices=list(CATEGORIES))
    sub.add_argument("--where", help="only guesses that cover this path")
    sub.add_argument("--json", action="store_true")

    sub = add("show", cmd_show, "show one guess")
    sub.add_argument("ref", help="guess id, unique id prefix, or receipt number")
    sub.add_argument("--json", action="store_true")

    sub = add("receipt", cmd_receipt, "show the open decisions that need the owner")
    sub.add_argument("--limit", type=int, help="most items to show (default from config, 5)")
    sub.add_argument("--format", choices=["md", "text", "json"], default="md")
    sub.add_argument("--all", action="store_true", help="include low-stakes guesses")
    sub.add_argument("--since", help="only guesses recorded since this ISO date or datetime")

    sub = add("decide", cmd_decide, "record the owner's answers, like: guesswork decide 1b 2a")
    sub.add_argument("choices", nargs="*", help="answers like 1b, 2a, or g-some-guess=b")
    sub.add_argument("--all", metavar="OPTION", help="apply one option to every item in the latest receipt")
    sub.add_argument("--custom", help="the owner's own answer for one guess given without an option letter")
    sub.add_argument("--note", help="context for the decision")
    sub.add_argument("--by", help="who decided (default: owner)")

    sub = add("test", cmd_test, "mark a guess as needing evidence before anyone decides")
    sub.add_argument("ref")
    sub.add_argument("--plan", required=True, help="the smallest test that will settle it")
    sub.add_argument("--by")

    sub = add("dismiss", cmd_dismiss, "close a guess that is not a real product decision")
    sub.add_argument("ref")
    sub.add_argument("--note")
    sub.add_argument("--by")

    sub = add("reopen", cmd_reopen, "reopen a decided, tested, or dismissed guess")
    sub.add_argument("ref")
    sub.add_argument("--note")
    sub.add_argument("--by")

    sub = add("context", cmd_context, "show the decisions that cover some files")
    sub.add_argument("paths", nargs="*")
    sub.add_argument("--json", action="store_true")

    sub = add("status", cmd_status, "one-line summary")
    sub.add_argument("--format", choices=["line", "statusline", "json"], default="line")

    sub = add("check", cmd_check, "fail when open guesses reach a stakes level (for CI)")
    sub.add_argument("--fail-on", choices=FAIL_LEVELS)
    sub.add_argument("--base", help="only check guesses changed since this git ref")

    sub = add("pr", cmd_pr, "write a Markdown summary of the decisions in this branch")
    sub.add_argument("--base", help="git ref to compare with (default: the pull request base or origin/HEAD)")
    sub.add_argument("--out", help="write to a file instead of standard output")

    sub = add("report", cmd_report, "write an HTML overview of the ledger")
    sub.add_argument("--out", help=f"output file (default: {LEDGER_DIR}/{REPORT_NAME})")
    sub.add_argument("--title", help="project name to show")
    sub.add_argument("--open", action="store_true", help="open the report in a browser")

    sub = add("scan", cmd_scan, "list code lines that often hide product decisions")
    sub.add_argument("--limit", type=int, default=60)
    sub.add_argument("--json", action="store_true")

    add("validate", cmd_validate, "check every ledger file")

    sub = add("demo", cmd_demo, "create a fictional project with guesses to try Guesswork in seconds")
    sub.add_argument("--dir", help="empty folder for the demo (default: a new temporary folder)")
    sub.add_argument("--open", action="store_true", help="open the demo report in a browser")

    sub = add("hook", cmd_hook, "handle a Claude Code hook event (reads JSON on stdin)")
    sub.add_argument("event", choices=sorted(HOOKS))
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    configure_streams()
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    try:
        return int(args.func(args) or 0)
    except GuessworkError as exc:
        print(f"guesswork: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
