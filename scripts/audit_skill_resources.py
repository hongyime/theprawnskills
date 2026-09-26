#!/usr/bin/env python3
"""Check local Markdown links and explicit bundled resource paths without running skills.

Scans all Markdown under skills/ and platforms/*/skills/. Dynamic paths, URLs,
anchors, and bare prose filenames are outside the automated check. Contextual
exceptions are exact source/target pairs with a documented reason, never globs.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

LINK = re.compile(r"!?\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+['\"][^\n]*?['\"])?\s*\)")
DEFINITION = re.compile(r"^\s{0,3}\[[^\]\n]+\]:\s*(<[^>]+>|\S+)")
RESOURCE = re.compile(
    r"(?<![\w:/\\.-])((?:\.{1,2}[\\/])*(?:scripts|references|reference|assets|templates|agents|hooks|eval-viewer|examples|tests)"
    r"[\\/][A-Za-z0-9_./\\-]+\.(?:md|mdx|py|sh|ps1|js|mjs|cjs|ts|tsx|jsx|json|yaml|yml|html|css|png|svg|toml))"
    r"(?![\w.-])"
)


@dataclass(frozen=True)
class Reference:
    source: str
    line: int
    target: str
    kind: str


def documents(root: Path) -> list[Path]:
    folders = [root / "skills", *sorted((root / "platforms").glob("*/skills"))]
    return sorted({p for folder in folders if folder.is_dir() for p in folder.rglob("*.md")})


def references(root: Path, doc: Path) -> list[Reference]:
    result = []
    seen = set()
    fence = None
    for number, line in enumerate(doc.read_text(encoding="utf-8-sig").splitlines(), 1):
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            if fence is None:
                fence = marker.group(1)
            elif marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence):
                fence = None
        matches = []
        links = list(LINK.finditer(line)) if fence is None and not marker else []
        if fence is None and not marker:
            matches.extend((m.group(1), "link") for m in links)
            definition = DEFINITION.match(line)
            if definition:
                matches.append((definition.group(1), "link"))
        matches.extend((m.group(1), "resource") for m in RESOURCE.finditer(line)
                       if not any(link.start() <= m.start() < link.end() for link in links))
        for value, kind in matches:
            target = unquote(value.strip("<>").split("#", 1)[0]).replace("\\", "/")
            if not target or re.match(r"^[a-z][a-z0-9+.-]*:|^/|^~", target, re.I):
                continue
            if any(char in target for char in "{}$*<>"):
                continue
            key = (target, kind)
            if key in seen:
                continue
            seen.add(key)
            result.append(Reference(doc.relative_to(root).as_posix(), number, target, kind))
    return result


def bases(root: Path, ref: Reference) -> list[Path]:
    doc = root / ref.source
    result = [doc.parent]
    if ref.kind == "resource":
        for parent in doc.parents:
            if parent == root:
                break
            if (parent / "SKILL.md").is_file():
                result.append(parent)
                break
    return list(dict.fromkeys(result))


def audit(root: Path, policy: Path | None = None) -> dict:
    root = root.resolve()
    docs = documents(root)
    if not root.is_dir() or not any(doc.name == "SKILL.md" for doc in docs):
        raise ValueError("Audit root must contain at least one skill definition under skills/ or platforms/*/skills/.")
    exceptions = {}
    if policy and policy.exists():
        data = json.loads(policy.read_text(encoding="utf-8"))
        for entry in data["exceptions"]:
            key = (entry["source"], entry["target"], entry["kind"])
            if key in exceptions or not entry.get("reason", "").strip():
                raise ValueError("Exceptions must be unique and include a reason.")
            exceptions[key] = entry
    missing, excluded = [], []
    used = set()
    count = 0
    for doc in docs:
        for ref in references(root, doc):
            count += 1
            candidates = [(base / ref.target).resolve() for base in bases(root, ref)]
            if any(path.is_relative_to(root) and path.exists() for path in candidates):
                continue
            key = (ref.source, ref.target, ref.kind)
            if key in exceptions:
                used.add(key)
                excluded.append({**asdict(ref), "reason": exceptions[key]["reason"]})
            else:
                missing.append(asdict(ref))
    stale = [entry for key, entry in exceptions.items() if key not in used]
    return {"skill_definitions": sum(doc.name == "SKILL.md" for doc in docs),
            "markdown_files": len(docs), "references_checked": count,
            "missing": missing, "contextual_exceptions": excluded, "stale_exceptions": stale,
            "scope": "Static local links and explicit resource paths; no remote URL, external tool, model behavior, or arbitrary prose validation."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--exceptions", type=Path)
    parser.add_argument("--json", type=Path, help="Optional output report path.")
    args = parser.parse_args()
    try:
        result = audit(args.root, args.exceptions or args.root / "scripts/skill-resource-exceptions.json")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Audit error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        args.json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"{result['skill_definitions']} skill definitions; {result['markdown_files']} Markdown files; {result['references_checked']} references checked.")
    print(f"Missing: {len(result['missing'])}; contextual exceptions: {len(result['contextual_exceptions'])}; stale exceptions: {len(result['stale_exceptions'])}.")
    for item in result["missing"]:
        print(f"{item['source']}:{item['line']}: {item['target']} ({item['kind']})")
    return int(bool(result["missing"] or result["stale_exceptions"]))


if __name__ == "__main__":
    raise SystemExit(main())
