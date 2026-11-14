#!/usr/bin/env python3
"""Audit SKILL.md platform lines against the agent-agnostic contract.

Every skill must declare the full contract platform line (or a superset
of it), unless it carries a documented exception in
scripts/skill-platform-exceptions.json. The checker rejects stale
exception entries (the file now complies, the path no longer exists,
or the path is not a scanned skill file).

Required tokens (all must appear in the platform value):
  Codex, Antigravity (agy), OpenCode, Muse, Windows, macOS, Linux (Debian)

Exit 0 when clean, 1 when violations or stale exceptions are found.
Run in CI (see .github/workflows/skills.yml) and locally before pushing.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIRED_TOKENS = (
    "Codex",
    "Antigravity (agy)",
    "OpenCode",
    "Muse",
    "Windows",
    "macOS",
    "Linux (Debian)",
)
EXCEPTIONS_PATH = os.path.join(ROOT, "scripts", "skill-platform-exceptions.json")
PLATFORM_RE = re.compile(r"^\s*platform:\s*[\"']?(.*?)[\"']?\s*$", re.M)


def to_posix(path):
    """Path with forward slashes, so exception keys match on Windows too."""
    return path.replace(os.sep, "/")


def platform_of(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    parts = text.split("---", 2)
    if len(parts) < 3 or not text.startswith("---"):
        return None
    m = PLATFORM_RE.search(parts[1])
    return m.group(1).strip() if m else None


def missing_tokens(platform):
    if platform is None:
        return list(REQUIRED_TOKENS)
    return [t for t in REQUIRED_TOKENS if t not in platform]


def main():
    with open(EXCEPTIONS_PATH, encoding="utf-8") as f:
        exceptions_doc = json.load(f)
    exceptions = {
        e["source"]: e.get("reason", "") for e in exceptions_doc.get("exceptions", [])
    }

    files = sorted(
        glob.glob(os.path.join(ROOT, "skills", "**", "SKILL.md"), recursive=True)
        + glob.glob(os.path.join(ROOT, "platforms", "**", "SKILL.md"), recursive=True)
    )

    violations = []
    seen_exception_paths = set()
    for path in files:
        rel = to_posix(os.path.relpath(path, ROOT))
        missing = missing_tokens(platform_of(path))
        if not missing:
            continue
        if rel in exceptions:
            seen_exception_paths.add(rel)
            continue
        violations.append((rel, missing))

    stale = []
    for source in exceptions:
        full = os.path.join(ROOT, source)
        if not os.path.exists(full):
            stale.append((source, "path does not exist"))
        elif source not in seen_exception_paths:
            if not missing_tokens(platform_of(full)):
                stale.append((source, "file now complies"))
            else:
                stale.append((source, "not a scanned skill file"))

    print(f"checked {len(files)} SKILL.md files, "
          f"{len(exceptions)} documented exceptions")
    if violations:
        print(f"FAIL: {len(violations)} violation(s):")
        for rel, missing in violations:
            print(f"  {rel}: missing {', '.join(missing)}")
    if stale:
        print(f"FAIL: {len(stale)} stale exception(s):")
        for source, reason in stale:
            print(f"  {source}: {reason}")
    if violations or stale:
        return 1
    print("OK: all platform lines declare the contract (or carry an exception).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
