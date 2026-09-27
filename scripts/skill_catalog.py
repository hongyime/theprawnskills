"""Parse the library's YAML once for metadata validation and a portable index."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import tomllib

try:
    import yaml
except ImportError as exc:
    raise SystemExit("Install check dependencies: python -m pip install -r requirements-skill-checks.txt") from exc


class CatalogError(ValueError):
    """Invalid metadata or profile; diagnostics never echo document contents."""


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader: UniqueLoader, node: yaml.MappingNode, deep: bool = False) -> dict:
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str) or key in result:
            raise CatalogError("YAML mapping keys must be unique strings")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


@dataclass(frozen=True)
class Skill:
    path: Path
    name: str
    description: str


def read_skill(path: Path) -> Skill:
    text = path.read_text(encoding="utf-8-sig")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    if not match:
        raise CatalogError("missing leading YAML frontmatter")
    try:
        meta = yaml.load(match.group(1), Loader=UniqueLoader)
    except CatalogError:
        raise
    except Exception as exc:
        # SafeLoader constructors may raise ValueError/AttributeError, not only
        # YAMLError. Do not echo a malformed scalar through a traceback.
        mark = getattr(exc, "problem_mark", None)
        location = f" at frontmatter line {mark.line + 1}" if mark else ""
        raise CatalogError("invalid YAML" + location) from None
    if not isinstance(meta, dict):
        raise CatalogError("frontmatter must be a mapping")
    name, description = meta.get("name"), meta.get("description")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
        raise CatalogError("name must be a nonempty kebab-case string of at most 64 characters")
    if name != path.parent.name:
        raise CatalogError("name does not match its folder")
    if not isinstance(description, str) or len(description.strip()) < 40:
        raise CatalogError("description must be a string with at least 40 characters")
    return Skill(path, name, " ".join(description.split()))


def skill_paths(root: Path) -> list[Path]:
    folders = [root / "skills", *sorted((root / "platforms").glob("*/skills"))]
    return sorted(p for folder in folders for p in folder.rglob("SKILL.md"))


def catalog(root: Path) -> list[Skill]:
    paths = skill_paths(root)
    if not paths:
        raise CatalogError("no skill definitions found")
    skills, errors = [], []
    for path in paths:
        try:
            skills.append(read_skill(path))
        except (CatalogError, OSError, UnicodeError) as exc:
            detail = str(exc) if isinstance(exc, CatalogError) else type(exc).__name__
            display = repr(path.relative_to(root).as_posix())[1:-1]
            errors.append(f"{display}: {detail}")
    if errors:
        raise CatalogError("\n".join(errors))
    return skills


def profile(root: Path, skills: list[Skill]) -> set[str]:
    try:
        data = tomllib.loads((root / "default-profile.toml").read_text(encoding="utf-8-sig"))
    except tomllib.TOMLDecodeError as exc:
        raise CatalogError("invalid default-profile.toml") from exc
    names = data.get("skills")
    if not isinstance(names, list) or not names or not all(isinstance(n, str) for n in names):
        raise CatalogError("profile skills must be a nonempty array of names")
    if len(names) != len(set(names)):
        raise CatalogError("duplicate profile entry")
    primary = {s.name for s in skills if s.path.parent.parent == root / "skills"}
    if set(names) - primary:
        raise CatalogError("profile names a missing top-level skill")
    return set(names)


def render_index(root: Path) -> str:
    root = root.resolve()
    skills = catalog(root)
    daily = profile(root, skills)
    primary = sorted((s for s in skills if s.path.parent.parent == root / "skills"), key=lambda s: s.name)
    portable = sum(s.path.is_relative_to(root / "platforms") for s in skills)
    lines = [
        "# Skills Index", "",
        "Generated from source metadata; independent of the machine generating it.", "",
        "The full library lives in this Git checkout or the OneDrive library. "
        "`default-profile.toml` selects the daily profile; `skill-router` finds on-demand skills. "
        "Never run `dotagents sync`.", "",
        "See [README.md](README.md) for installation and "
        "[standalone conventions](platforms/linux/README.md) for Windows, macOS and Linux. "
        "Profile membership below is desired exposure, not proof of installation on any machine.", "",
        "| Source inventory | Count |", "|---|---:|",
        f"| Top-level skills | {len(primary)} |",
        f"| All definitions, including nested skills and portable variants | {len(skills)} |",
        f"| Portable variants | {portable} |",
        f"| Daily profile | {len(daily)} |", "",
        "## Skills", "", "| Skill | Purpose | Default status |", "|---|---|---|",
    ]
    for skill in primary:
        description = skill.description
        if len(description) > 180:
            description = description[:177] + "..."
        description = description.replace("|", "\\|")
        status = "DAILY" if skill.name in daily else "ON-DEMAND"
        lines.append(f"| `{skill.name}` | {description} | {status} |")
    return "\n".join(lines) + "\n"
