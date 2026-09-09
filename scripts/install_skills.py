#!/usr/bin/env python3
"""Expose a selected skill profile without overwriting or removing user files."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
import tomllib


AGENT_ROOTS = {
    "codex": Path(".agents/skills"),
    "opencode": Path(".agents/skills"),
    "claude": Path(".claude/skills"),
    "cursor": Path(".agents/skills"),
}


@dataclass(frozen=True)
class Link:
    source: Path
    destination: Path
    exists: bool


@dataclass(frozen=True)
class Plan:
    library: Path
    home: Path
    links: tuple[Link, ...]
    pointer: Path
    pointer_exists: bool

    @property
    def metadata(self) -> dict[str, str | int]:
        return {"version": 1, "library": str(self.library)}


def validate_parent(path: Path, home: Path) -> None:
    """Refuse redirects such as ~/.agents pointing at the full source library."""
    if not path.is_relative_to(home):
        raise ValueError(f"Installation destination is outside the selected home: {path}")
    for parent in (path, *path.parents):
        if parent == home:
            break
        if parent.is_symlink():
            raise ValueError(f"Parent is a symlink; inspect it before installing: {parent}")
        if parent.exists() and not parent.is_dir():
            raise ValueError(f"Parent is not a directory: {parent}")


def make_plan(library: Path, home: Path, agents: list[str], profile: Path | None = None) -> Plan:
    library, home = library.resolve(), home.resolve()
    profile = profile or library / "default-profile.toml"
    with profile.open("rb") as stream:
        # Existing Windows profile files may have a UTF-8 BOM.
        data = tomllib.loads(stream.read().decode("utf-8-sig"))
    names = data.get("skills")
    if not isinstance(names, list) or not names:
        raise ValueError("Profile must contain a non-empty skills array.")
    if any(not isinstance(name, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", name) for name in names):
        raise ValueError("Profile skill names must be simple lowercase folder names.")
    if len(set(names)) != len(names):
        raise ValueError("Profile contains duplicate skill names.")
    if not agents or any(agent not in AGENT_ROOTS for agent in agents):
        raise ValueError("Select a supported agent.")

    roots = list(dict.fromkeys(home / AGENT_ROOTS[agent] for agent in agents))
    for root in roots:
        validate_parent(root, home)
        if library == root or library.is_relative_to(root):
            raise ValueError("Clone the library outside an agent's skill discovery directory.")

    links = []
    for name in names:
        canonical = library / "skills" / name
        if not (canonical / "SKILL.md").is_file():
            raise ValueError(f"Missing canonical skill: {canonical / 'SKILL.md'}")
        variant = library / "platforms/linux/skills" / name
        source = (variant if (variant / "SKILL.md").is_file() else canonical).resolve()
        if not source.is_relative_to(library):
            raise ValueError(f"Skill source escapes the library: {source}")
        for root in roots:
            destination = root / name
            exists = destination.is_symlink() and destination.resolve() == source
            if not exists and (destination.exists() or destination.is_symlink()):
                raise ValueError(f"Existing skill preserved; resolve this conflict first: {destination}")
            links.append(Link(source, destination, exists))

    # Codex can also see legacy user installs. Avoid adding another copy.
    if "codex" in agents:
        legacy = home / ".codex/skills"
        overlaps = [name for name in names if (legacy / name / "SKILL.md").is_file()]
        if overlaps:
            raise ValueError("Legacy Codex skills would be duplicated; preserve and review them first: " + ", ".join(overlaps))

    pointer = home / ".config/theprawnskills/library.json"
    validate_parent(pointer.parent, home)
    plan = Plan(library, home, tuple(links), pointer, pointer.exists())
    if pointer.is_symlink():
        raise ValueError(f"Library pointer is a symlink; inspect it first: {pointer}")
    if pointer.exists():
        if not pointer.is_file() or json.loads(pointer.read_text(encoding="utf-8")) != plan.metadata:
            raise ValueError(f"Existing library configuration preserved: {pointer}")
    return plan


def apply_plan(plan: Plan) -> None:
    """Only create new entries. Exclusive creation also preserves racing writes."""
    for link in plan.links:
        validate_parent(link.destination.parent, plan.home)
        if link.exists:
            if not link.destination.is_symlink() or link.destination.resolve() != link.source:
                raise ValueError(f"Skill changed since preview: {link.destination}")
            continue
        link.destination.parent.mkdir(parents=True, exist_ok=True)
        link.destination.symlink_to(link.source, target_is_directory=True)
    if not plan.pointer_exists:
        validate_parent(plan.pointer.parent, plan.home)
        plan.pointer.parent.mkdir(parents=True, exist_ok=True)
        with plan.pointer.open("x", encoding="utf-8") as stream:
            json.dump(plan.metadata, stream, indent=2)
            stream.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agents", nargs="+", choices=AGENT_ROOTS, default=["codex"])
    parser.add_argument("--home", type=Path, default=Path.home(), help="Target home; useful for isolated verification")
    parser.add_argument("--profile", type=Path, help="Alternate TOML profile; default is default-profile.toml")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Create missing links after validating the entire plan")
    mode.add_argument("--check", action="store_true", help="Check that every selected skill and the library pointer are installed")
    mode.add_argument("--dry-run", action="store_true", help="Preview only (the default)")
    args = parser.parse_args(argv)
    try:
        plan = make_plan(Path(__file__).resolve().parents[1], args.home, args.agents, args.profile)
        missing = sum(not link.exists for link in plan.links)
        for link in plan.links:
            print(f"{'KEEP' if link.exists else 'LINK'} {link.destination} -> {link.source}")
        print(f"{len(plan.links)} selected links; {missing} new; existing unrelated skills are preserved.")
        if args.check:
            if missing or not plan.pointer_exists:
                print("Installation is incomplete. Run the preview, then --apply.", file=sys.stderr)
                return 1
            print("Installation verified.")
        elif args.apply:
            apply_plan(plan)
            print("Installed. Restart your agent if the skills are not visible yet.")
        else:
            print("Preview only. Use --apply to create these links.")
        return 0
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
