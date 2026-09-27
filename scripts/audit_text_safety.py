#!/usr/bin/env python3
"""Read-only check for hidden direction/control instructions in Git text.

Preserves normal Unicode, emoji, ZWJ/ZWNJ and variation selectors. Reports only
paths, positions and code points, never potentially sensitive line contents.
This is a narrow hygiene check, not a prompt-injection or secret-scan guarantee.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys

EXTENSIONS = {".md", ".mdx", ".txt", ".py", ".ps1", ".sh", ".js", ".mjs", ".cjs",
              ".ts", ".tsx", ".jsx", ".json", ".toml", ".yml", ".yaml", ".html", ".css"}

# Unicode RGI subdivision flags use otherwise invisible tag characters.
# Exempt only these complete sequences; arbitrary tags remain findings.
TAG_FLAGS = tuple("\U0001f3f4" + "".join(chr(0xE0000 + ord(c)) for c in code) + "\U000e007f"
                  for code in ("gbeng", "gbsct", "gbwls"))


def suspicious(code: int) -> bool:
    return (0x202A <= code <= 0x202E or 0x2066 <= code <= 0x2069
            or 0xE0000 <= code <= 0xE007F or code in {0x200B, 0x2060, 0xFEFF})


def findings(text: str) -> list[tuple[int, int, int]]:
    results = []
    for number, line in enumerate(text.removeprefix("\ufeff").splitlines(), 1):
        allowed = {i for flag in TAG_FLAGS for match in re.finditer(re.escape(flag), line)
                   for i in range(match.start(), match.end())}
        for column, char in enumerate(line, 1):
            if suspicious(ord(char)) and column - 1 not in allowed:
                results.append((number, column, ord(char)))
    return results


def audit(root: Path) -> list[str]:
    root = root.resolve()
    result = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                            cwd=root, capture_output=True, check=True)
    errors = []
    for name in sorted(set(result.stdout.decode("utf-8").split("\0")) - {""}):
        path = root / name
        display = repr(name)[1:-1]
        for _, column, code in findings(name):
            errors.append(f"{display}: filename column {column}: suspicious U+{code:04X}")
        if path.suffix.lower() not in EXTENSIONS or not path.exists():
            continue
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            errors.append(f"{display}: linked text requires explicit review")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError:
            errors.append(f"{display}: text must be UTF-8")
            continue
        for line, column, code in findings(text):
            errors.append(f"{display}:{line}:{column}: suspicious U+{code:04X}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    try:
        errors = audit(args.root)
    except (OSError, subprocess.CalledProcessError, UnicodeError):
        print("Text safety audit could not read the Git worktree.", file=sys.stderr)
        return 2
    for error in errors:
        print(error)
    print(f"Text safety findings: {len(errors)}. No files changed.")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
