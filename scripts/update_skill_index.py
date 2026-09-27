#!/usr/bin/env python3
"""Generate or check INDEX.md without inspecting installed agent directories."""
import argparse
from pathlib import Path
import sys

from skill_catalog import CatalogError, render_index


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--check", action="store_true", help="Read-only check; fail if INDEX.md is stale.")
    args = parser.parse_args()
    try:
        expected = render_index(args.root)
        target = args.root / "INDEX.md"
        if args.check:
            if not target.exists() or target.read_text(encoding="utf-8-sig") != expected:
                print("INDEX.md is stale. Run python scripts/update_skill_index.py", file=sys.stderr)
                return 1
            print("Skill metadata, profile and INDEX.md agree.")
        else:
            target.write_text(expected, encoding="utf-8", newline="\n")
            print("INDEX.md regenerated from validated source metadata.")
    except (CatalogError, OSError, UnicodeError) as exc:
        print(f"Catalog error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
