"""Portable handoff helpers. Git operations are read-only; output is project-local."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote

SECTIONS = (
    "Current State Summary", "Important Context", "Decisions Made",
    "Completed Work and Verification", "Pending Work", "Immediate Next Steps",
    "Critical Files", "Potential Gotchas",
)
META = re.compile(r"<!-- handoff-metadata\s*\n(.*?)\n-->", re.S)
LINK = re.compile(r"\[[^\]\n]*\]\(\s*(<[^>\n]+>|(?:[^\s()]|\([^()]*\))+)(?:\s+['\"][^\n]*?['\"])?\s*\)")
SENSITIVE = re.compile(r"(?i)(?:^|/)(?:\.env(?:\.[^/]*)?|\.ssh|\.aws|credentials)(?:/|$)|\.(?:pem|key)$")
SECRET_PATTERNS = (
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("access token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-(?:proj-)?[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16})\b")),
    ("credential assignment", re.compile(r"(?im)\b(?:api[_-]?key|access[_-]?token|password|client[_-]?secret)\s*[:=]\s*[\"']?([^\s\"'`,;]+)")),
    ("credential URL", re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s/:]+:[^\s/@]+@", re.I)),
)


def git(project: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(project), *args], capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=15, check=False,
    )
    if result.returncode:
        # Git diagnostics can include local paths; callers need the operation only.
        raise ValueError(f"Git {args[0]} failed; verify the selected project and Git history.")
    return result.stdout.rstrip("\r\n")


def project_root(value: str | Path) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_dir():
        raise ValueError("Project must be an existing directory.")
    try:
        return Path(git(path, "rev-parse", "--show-toplevel")).resolve()
    except (ValueError, FileNotFoundError):
        return path


def inside(project: Path, relative: str) -> Path:
    project = project.resolve()
    candidate = Path(relative)
    if candidate.is_absolute() or re.match(r"^[A-Za-z]:|^\\", relative):
        raise ValueError("Use a project-relative path, not a machine-specific absolute path.")
    path = (project / candidate).resolve()
    if not path.is_relative_to(project):
        raise ValueError("Referenced path escapes the project.")
    return path


def snapshot(project: Path) -> dict:
    project = project.resolve()
    try:
        head = git(project, "rev-parse", "--verify", "HEAD")
    except (ValueError, FileNotFoundError):
        return {"head": None, "branch": None, "dirty": {}, "recent_commits": [], "index_sha256": None, "incomplete": []}
    branch = git(project, "rev-parse", "--abbrev-ref", "HEAD")
    status = git(project, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    records = iter(status.split("\0"))
    dirty = {}
    incomplete = []
    for record in records:
        if not record:
            continue
        state, name = record[:2], record[3:]
        original_name = next(records, None) if "R" in state or "C" in state else None
        if name.startswith(".agents/handoffs/") and (not original_name or original_name.startswith(".agents/handoffs/")):
            continue
        if SENSITIVE.search(name):
            incomplete.append("Sensitive working file omitted from content snapshot.")
            continue
        digest = None
        kind = "missing"
        executable = False
        path = project / name
        # Inspect the link itself; do not follow a final-component symlink.
        if not path.parent.resolve().is_relative_to(project):
            incomplete.append("Working-file parent redirects outside the project.")
        elif path.is_symlink():
            kind = "symlink"
            digest = hashlib.sha256(os.readlink(path).encode("utf-8")).hexdigest()
        elif path.is_file():
            kind = "regular"
            executable = bool(path.stat().st_mode & 0o111) if os.name != "nt" else False
            with path.open("rb") as stream:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
        elif path.is_dir():
            kind = "directory"
            incomplete.append("Directory or submodule content is outside the file snapshot.")
        dirty[name] = {"status": state, "sha256": digest, "original_name": original_name,
                       "kind": kind, "executable": executable}
    index_records = git(project, "ls-files", "--stage", "-z").split("\0")
    # Fingerprint staged entries for dirty paths, not the entire index: a new
    # clean commit should be reported as new history rather than dirty drift.
    index = "\0".join(record for record in index_records
                       if "\t" in record and record.split("\t", 1)[1] in dirty)
    return {"head": head, "branch": branch, "dirty": dirty,
            "index_sha256": hashlib.sha256(index.encode("utf-8")).hexdigest(), "incomplete": incomplete,
            "recent_commits": git(project, "log", "-5", "--format=%h").splitlines()}


def read_handoff(path: Path) -> tuple[str, dict]:
    text = path.read_text(encoding="utf-8-sig")
    match = META.search(text)
    if not match:
        raise ValueError("Missing handoff metadata; use the current scaffold or review this legacy handoff manually.")
    data = json.loads(match.group(1))
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("Unsupported handoff metadata version.")
    try:
        stamp = datetime.fromisoformat(data["created_utc"])
    except (KeyError, TypeError, ValueError):
        raise ValueError("Invalid creation timestamp.") from None
    if stamp.tzinfo is None:
        raise ValueError("Creation timestamp must include a timezone.")
    head = data.get("head")
    if head is not None and (not isinstance(head, str) or not re.fullmatch(r"[a-f0-9]{40,64}", head)):
        raise ValueError("Invalid recorded Git commit.")
    if not isinstance(data.get("dirty"), dict) or not isinstance(data.get("incomplete", []), list):
        raise ValueError("Invalid working-tree snapshot.")
    if data.get("continues_from") is not None and not isinstance(data["continues_from"], str):
        raise ValueError("Invalid continuation path.")
    return text, data


def local_references(text: str) -> list[str]:
    """Explicit Markdown links and backticked paths in Critical Files are repo-relative."""
    refs = []
    for match in LINK.finditer(text):
        destination = match.group(1).strip().strip("<>")
        if re.match(r"^[a-z][a-z0-9+.-]*://|^mailto:|^#", destination, re.I):
            continue
        path = unquote(destination.split("#", 1)[0])
        if path:
            refs.append(path)
    match = re.search(r"(?ms)^## Critical Files\s*\n(.*?)(?=^## |\Z)", text)
    if match:
        refs += [p for p in re.findall(r"`([^`\n]+)`", match.group(1)) if "/" in p or "." in p]
    return sorted(set(refs))


def secret_findings(text: str) -> list[str]:
    findings = []
    for label, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            if label == "credential assignment":
                value = match.group(1)
                if value.startswith(("$", "<", "[")) or value.lower() in {"none", "redacted", "example", "placeholder"}:
                    continue
            findings.append(f"Possible {label} at line {text[:match.start()].count(chr(10)) + 1}; value withheld.")
    return findings


def validate(path: Path, project: Path) -> dict:
    project = project.resolve()
    text = path.read_text(encoding="utf-8-sig")
    errors, warnings = [], []
    score = 100
    try:
        _, metadata = read_handoff(path)
    except (ValueError, KeyError, TypeError) as exc:
        metadata = {}
        errors.append(f"Invalid metadata: {exc}")
        score -= 20
    for title in SECTIONS:
        match = re.search(r"(?ms)^## " + re.escape(title) + r"\s*\n(.*?)(?=^## |\Z)", text)
        body = re.sub(r"<!--.*?-->", "", match.group(1), flags=re.S).strip() if match else ""
        if not body or not re.search(r"[A-Za-z0-9]", body):
            errors.append(f"Missing or empty section: {title}")
            score -= 10
    if re.search(r"\[TODO\b|\bTBD\b", text, re.I):
        errors.append("Unfinished TODO/TBD placeholders remain.")
        score -= 20
    errors.extend(secret_findings(text))
    references = local_references(text)
    if metadata.get("continues_from"):
        references.append(metadata["continues_from"])
    for reference in sorted(set(references)):
        try:
            if not inside(project, reference).is_file():
                safe_reference = "[possible secret withheld]" if secret_findings(reference) else reference
                errors.append(f"Missing referenced file: {safe_reference}")
                score -= 10
        except ValueError as exc:
            errors.append(str(exc))
            score -= 10
    if metadata.get("head") is None:
        warnings.append("No recorded Git commit; Git staleness cannot be established.")
    warnings.append("Secret detection and completeness scoring are heuristics; manually review before sharing.")
    score = max(0, score)
    return {"file": path.name, "score": score, "passed": not errors and score >= 70,
            "errors": errors, "warnings": warnings}


def create(project: Path, slug: str, previous: str | None) -> Path:
    project = project.resolve()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", slug):
        raise ValueError("Task slug must use 1-64 lowercase letters, digits, or hyphens.")
    folder = inside(project, ".agents/handoffs")
    # Prevent redirecting generated documents even to another in-project directory.
    for parent in [project / ".agents", project / ".agents/handoffs"]:
        if parent.is_symlink() or getattr(parent, "is_junction", lambda: False)():
            raise ValueError("Handoff directory must not be a symlink or junction.")
    prior = None
    if previous:
        prior_path = inside(project, previous if "/" in previous or "\\" in previous else ".agents/handoffs/" + previous)
        if not prior_path.is_file() or not prior_path.is_relative_to(folder):
            raise ValueError("Previous handoff must be an existing file in this project's .agents/handoffs directory.")
        prior = prior_path.relative_to(project).as_posix()
    stamp = datetime.now(timezone.utc)
    metadata = {"version": 1, "created_utc": stamp.isoformat(),
                "project_name": project.name, **snapshot(project), "continues_from": prior}
    template = (Path(__file__).resolve().parent.parent / "references/handoff-template.md").read_text(encoding="utf-8")
    text = "# Handoff: " + slug + "\n\n<!-- handoff-metadata\n" + json.dumps(metadata, indent=2, ensure_ascii=True) + "\n-->\n\n"
    text += "Created (UTC): " + stamp.isoformat() + "\n\n"
    text += "Git branch: `" + str(metadata["branch"] or "unavailable") + "`\n\n"
    if prior:
        text += "Continues from: [previous handoff](" + prior + ")\n\n"
    text += template
    # Refuse to persist metadata if a branch or filename itself resembles a secret.
    if secret_findings(text):
        raise ValueError("Potential secret in generated metadata; use safe branch/file names before creating a shared handoff.")
    folder.mkdir(parents=True, exist_ok=True)
    prefix = stamp.strftime("%Y-%m-%d-%H%M%S") + "-" + slug
    for number in range(1000):
        path = folder / (prefix + (f"-{number}" if number else "") + ".md")
        try:
            with path.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(text)
            return path
        except FileExistsError:
            continue
    raise ValueError("Too many handoffs with the same timestamp and slug.")


def staleness(path: Path, project: Path) -> dict:
    project = project.resolve()
    text, recorded = read_handoff(path)
    now = datetime.now(timezone.utc)
    age = (now - datetime.fromisoformat(recorded["created_utc"])).total_seconds() / 86400
    reasons = []
    level = 0
    if age < -0.01:
        return {"level": "UNKNOWN", "reasons": ["Creation timestamp is in the future."]}
    if age > 30:
        level = 3
        reasons.append("Handoff is more than 30 days old.")
    elif age > 7:
        level = 2
        reasons.append("Handoff is more than seven days old.")
    current = snapshot(project)
    if not recorded.get("head") or not current.get("head"):
        return {"level": "UNKNOWN", "reasons": ["A recorded and current Git commit are required to establish freshness."]}
    if recorded.get("incomplete") or current.get("incomplete") or not recorded.get("index_sha256"):
        return {"level": "UNKNOWN", "reasons": ["File snapshot is incomplete; inspect sensitive files, submodules, and legacy metadata manually."]}
    try:
        git(project, "cat-file", "-e", recorded["head"] + "^{commit}")
        git(project, "merge-base", "--is-ancestor", recorded["head"], current["head"])
    except ValueError:
        return {"level": "VERY_STALE", "reasons": ["Recorded commit is missing or is not an ancestor of the current checkout."]}
    commits = int(git(project, "rev-list", "--count", recorded["head"] + "..HEAD"))
    if recorded.get("branch") != current.get("branch"):
        level = max(level, 2)
        reasons.append("Git branch differs from the handoff.")
    if commits:
        level = max(level, 1)
        reasons.append(f"{commits} commit(s) since the handoff.")
    if current["dirty"] != recorded["dirty"] or current["index_sha256"] != recorded["index_sha256"]:
        level = max(level, 2)
        reasons.append("Uncommitted file state differs from the recorded snapshot.")
    changed = git(project, "diff", "--name-only", "-z", recorded["head"], "HEAD", "--").split("\0")
    for ref in local_references(text):
        try:
            missing = not inside(project, ref).is_file()
        except ValueError:
            missing = True
        if missing:
            level = max(level, 2)
            reasons.append("A referenced file is missing or outside the project.")
    return {"level": ("FRESH", "SLIGHTLY_STALE", "STALE", "VERY_STALE")[level],
            "age_days": round(age, 2), "commits_since": commits,
            "changed_files": [x for x in changed if x], "reasons": reasons}


def main(command: str, argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=".", help="Target project directory (defaults to current directory).")
    parser.add_argument("--json", action="store_true", help="Print machine-readable results.")
    if command == "create":
        parser.add_argument("slug")
        parser.add_argument("--continues-from")
    elif command == "list":
        parser.add_argument("path", nargs="?", help="Optional project directory; overrides --project.")
    else:
        parser.add_argument("file", help="Project-relative handoff file path.")
    args = parser.parse_args(argv)
    try:
        project = project_root(args.path if command == "list" and args.path else args.project)
        code = 0
        if command == "create":
            path = create(project, args.slug, args.continues_from)
            result = {"file": path.relative_to(project).as_posix(), "status": "DRAFT", "next": "Fill in every section and run validate_handoff.py."}
        elif command == "list":
            result = []
            folder = inside(project, ".agents/handoffs")
            for path in sorted(folder.glob("*.md"), reverse=True):
                try:
                    safe = inside(project, path.relative_to(project).as_posix())
                    report = validate(safe, project)
                    result.append({"file": path.name, "status": "COMPLETE" if report["passed"] else "DRAFT", "score": report["score"]})
                except (OSError, ValueError, KeyError, TypeError):
                    result.append({"file": path.name, "status": "INVALID", "score": 0})
        else:
            path = inside(project, args.file)
            if command == "validate":
                result = validate(path, project)
                code = 0 if result["passed"] else 1
            else:
                result = staleness(path, project)
                code = 0 if result["level"] == "FRESH" else 1
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=True))
        elif command == "create":
            print(result["file"])
            print(result["next"])
        else:
            print(json.dumps(result, indent=2, ensure_ascii=True))
        return code
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        # Do not echo parsed file contents or credential-bearing JSON errors.
        detail = "Malformed handoff metadata." if isinstance(exc, (json.JSONDecodeError, KeyError, TypeError)) else str(exc)
        print(json.dumps({"error": detail}) if args.json else "Error: " + detail, file=sys.stderr)
        return 2
