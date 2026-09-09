#!/usr/bin/env python3
"""Install a profile using links or managed copies, preserving existing user files."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tomllib
import uuid


AGENT_ROOTS = {
    "codex": Path(".agents/skills"),
    "opencode": Path(".agents/skills"),
    "claude": Path(".claude/skills"),
    "cursor": Path(".agents/skills"),
}
COPY_MARKER = ".prawn-install.json"


def is_redirect(path: Path) -> bool:
    """Include Windows directory junctions, also on Python 3.11."""
    if path.is_symlink():
        return True
    try:
        return getattr(path.lstat(), "st_reparse_tag", 0) == 0xA0000003
    except FileNotFoundError:
        return False


def tree_digest(folder: Path) -> str:
    """Hash content and relative paths; the root ownership marker is excluded."""
    digest = hashlib.sha256()
    for path in sorted(folder.rglob("*")):
        if path == folder / COPY_MARKER:
            continue
        if is_redirect(path):
            raise ValueError(f"Copy mode does not follow linked content: {path}")
        relative = path.relative_to(folder).as_posix().encode("utf-8")
        digest.update((b"D" if path.is_dir() else b"F") + relative + b"\0")
        if path.is_file():
            digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


@dataclass(frozen=True)
class Link:
    source: Path
    destination: Path
    exists: bool
    mode: str = "symlink"
    digest: str | None = None
    previous_digest: str | None = None
    backup: Path | None = None


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
        if is_redirect(parent):
            raise ValueError(f"Parent is a symlink or junction; inspect it before installing: {parent}")
        if parent.exists() and not parent.is_dir():
            raise ValueError(f"Parent is not a directory: {parent}")


def make_plan(library: Path, home: Path, agents: list[str], profile: Path | None = None, mode: str = "auto") -> Plan:
    library, home = library.resolve(), home.resolve()
    if mode not in {"auto", "copy", "symlink"}:
        raise ValueError("Installation mode must be auto, copy, or symlink.")
    selected_mode = ("copy" if os.name == "nt" else "symlink") if mode == "auto" else mode
    backup_root = home / "Backups" / datetime.now(timezone.utc).strftime("%Y-%m-%d") / "theprawnskills" / uuid.uuid4().hex
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
        source_digest = None
        for root in roots:
            destination = root / name
            exists = destination.is_symlink() and destination.resolve() == source
            if exists:
                links.append(Link(source, destination, True))
                continue
            present = destination.exists() or is_redirect(destination)
            marker = destination / COPY_MARKER
            managed_copy = present and not is_redirect(destination) and destination.is_dir() and marker.is_file()
            if present and not managed_copy:
                raise ValueError(f"Existing skill preserved; resolve this conflict first: {destination}")
            item_mode = "copy" if managed_copy else selected_mode
            if item_mode == "symlink":
                links.append(Link(source, destination, False))
                continue
            if (source / COPY_MARKER).exists():
                raise ValueError(f"Source contains local installation metadata: {source}")
            source_digest = source_digest or tree_digest(source)
            previous_digest = None
            backup = None
            if managed_copy:
                if is_redirect(marker):
                    raise ValueError(f"Installation marker is a link: {marker}")
                saved = json.loads(marker.read_text(encoding="utf-8"))
                if not isinstance(saved, dict) or saved.get("version") != 1 or saved.get("source") != str(source):
                    raise ValueError(f"Existing skill preserved; ownership does not match: {destination}")
                previous_digest = tree_digest(destination)
                if previous_digest != saved.get("digest"):
                    raise ValueError(f"Local edits preserved; review before updating: {destination}")
                exists = previous_digest == source_digest
                if not exists:
                    backup = backup_root / destination.relative_to(home)
                    validate_parent(backup.parent, home)
            links.append(Link(source, destination, exists, "copy", source_digest, previous_digest, backup))

    # Codex can also see legacy user installs. Avoid adding another copy.
    if "codex" in agents:
        legacy = home / ".codex/skills"
        overlaps = [name for name in names if (legacy / name / "SKILL.md").is_file()]
        if overlaps:
            raise ValueError("Legacy Codex skills would be duplicated; preserve and review them first: " + ", ".join(overlaps))

    pointer = home / ".config/theprawnskills/library.json"
    validate_parent(pointer.parent, home)
    plan = Plan(library, home, tuple(links), pointer, pointer.exists())
    if is_redirect(pointer):
        raise ValueError(f"Library pointer is a symlink; inspect it first: {pointer}")
    if pointer.exists():
        if not pointer.is_file() or json.loads(pointer.read_text(encoding="utf-8")) != plan.metadata:
            raise ValueError(f"Existing library configuration preserved: {pointer}")
    return plan


def apply_plan(plan: Plan) -> None:
    """Keep user edits; archive managed copies before replacing their content."""
    for link in plan.links:
        validate_parent(link.destination.parent, plan.home)
        if link.mode == "copy":
            if tree_digest(link.source) != link.digest:
                raise ValueError(f"Source changed since preview: {link.source}")
            if link.previous_digest is not None:
                if is_redirect(link.destination) or tree_digest(link.destination) != link.previous_digest:
                    raise ValueError(f"Local edits preserved; skill changed since preview: {link.destination}")
                if link.exists:
                    continue
                if link.backup is None:
                    raise ValueError(f"Managed copy update requires a backup: {link.destination}")
                validate_parent(link.backup.parent, plan.home)
                # Both resolved targets must stay in the chosen home before moving.
                if not link.destination.resolve().is_relative_to(plan.home) or not link.backup.resolve().is_relative_to(plan.home):
                    raise ValueError("Backup move would escape the selected home.")
                link.backup.parent.mkdir(parents=True, exist_ok=True)
                link.destination.rename(link.backup)
                print(f"BACKUP {link.backup}")
            link.destination.parent.mkdir(parents=True, exist_ok=True)
            # copytree creates the destination exclusively and refuses racing files.
            shutil.copytree(link.source, link.destination)
            if tree_digest(link.destination) != link.digest:
                raise ValueError(f"Source changed during copying; inspect this preserved copy: {link.destination}")
            with (link.destination / COPY_MARKER).open("x", encoding="utf-8") as stream:
                json.dump({"version": 1, "source": str(link.source), "digest": link.digest}, stream, indent=2)
                stream.write("\n")
            continue
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
    parser.add_argument("--mode", choices=["auto", "copy", "symlink"], default="auto", help="New installs: auto uses copies on Windows and symlinks on macOS/Linux")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Install/update after validating the entire plan; managed copy updates are backed up")
    mode.add_argument("--check", action="store_true", help="Check that every selected skill and the library pointer are installed")
    mode.add_argument("--dry-run", action="store_true", help="Preview only (the default)")
    args = parser.parse_args(argv)
    try:
        plan = make_plan(Path(__file__).resolve().parents[1], args.home, args.agents, args.profile, args.mode)
        missing = sum(not link.exists for link in plan.links)
        for link in plan.links:
            action = "KEEP" if link.exists else "COPY" if link.mode == "copy" else "LINK"
            print(f"{action} {link.destination} <- {link.source}")
            if link.backup:
                print(f"  Existing managed copy will be backed up to: {link.backup}")
        print(f"{len(plan.links)} selected skills; {missing} installations/updates; existing unrelated skills are preserved.")
        if args.check:
            if missing or not plan.pointer_exists:
                print("Installation is incomplete. Run the preview, then --apply.", file=sys.stderr)
                return 1
            print("Installation verified.")
        elif args.apply:
            apply_plan(plan)
            print("Installed. Restart your agent if the skills are not visible yet.")
        else:
            print("Preview only. Use --apply to install these skills.")
        return 0
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
