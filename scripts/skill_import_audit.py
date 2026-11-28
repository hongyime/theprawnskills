#!/usr/bin/env python3
"""Static grep audit for skill imports (spec 14, stage 3).

Scans a pinned source tree (skill dirs only) for the six stage-3 pattern
groups and reports every finding with file + line + disposition status:

  script       executable scripts (scripts/, *.py, *.sh, *.ps1, *.js, *.ts, ...)
               and binaries (ELF/PE/ZIP/SWF magic, or undecodable bytes)
  shell-bang    shell-execution markers: lines starting with ``!`` in SKILL.md
               / reference Markdown (Claude-style ``!command`` execution)
  allowed-tools every ``allowed-tools`` entry in a SKILL.md frontmatter
               (values are listed for review; quick_validate only allows
               the key, it never vets the values)
  network      network-call keywords (curl, wget, fetch(, requests.*, urllib,
               socket) and absolute URLs in Markdown
  credential   credential reads (os.environ / os.getenv / process.env /
               credential-named $VARs such as $TAVILY_API_KEY in scripts)
               and literal credential assignments
               (api_key / token / secret / password = "...")
  callback     absolute URLs inside script files (.py/.sh/.ps1/.js/.ts) --
               the exfiltration-callback pattern (a payload default that
               phones a third-party host)

Placeholder hosts and placeholder credential values are never findings:
example.com/.org/.net, *.example.*, localhost, 127.0.0.1, RFC1918
addresses, and values like <token>, redacted, changeme, "CHANGE THIS".

Deterministic: findings are sorted by (file, line, kind, match) and finding
IDs are a stable hash of (relative path, kind, normalized match) -- line
numbers are NOT in the ID, so a disposition survives edits that shift
lines. Two runs over the same tree produce byte-identical JSON reports.

Dispositions (JSON file, --dispositions):
  {"dispositions": {"<finding-id>": {"action": "fix|waive|reject",
                                      "reason": "..."}}}
Every disposition needs a non-empty reason. Exit code is 0 when every
finding has a disposition (or there are no findings), 1 when any finding
is undispositioned, 2 on usage errors. A "fix" disposition means the fix
must land before import and the audit must be re-run until the finding is
gone; the import record's allowlist row (not this script) is what enforces
that -- see V4 in docs/skill-import-pipeline.md.

No network. Read-only on the source tree (never writes into it).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

TEXT_EXTS = {".md", ".mdx", ".txt", ".py", ".sh", ".ps1", ".js", ".mjs",
            ".cjs", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml", ".toml"}
SCRIPT_EXTS = {".py", ".sh", ".ps1", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx"}
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}

URL_RE = re.compile(r"https?://[^\s\"'<>`\)\]]+")
NETWORK_KW_RE = re.compile(
    r"\b(curl|wget)\b|fetch\s*\(|requests\s*\.\s*(get|post|put|delete|request)\s*\(|"
    r"\burllib\b|\bsocket\s*\.")
ENV_READ_RE = re.compile(
    r"os\s*\.\s*environ|os\s*\.\s*getenv|process\s*\.\s*env|getenv\s*\(|"
    r"ENV\s*\[\s*[\"'][A-Z_]+[\"']\s*\]")
SHELL_ENV_RE = re.compile(r"\$[A-Z_]*(TOKEN|KEY|SECRET|PASS|CRED|AUTH)[A-Z0-9_]*\b")
PHP_SUPERGLOBALS = {"$_GET", "$_POST", "$_SERVER", "$_FILES", "$_COOKIE",
                     "$_REQUEST", "$_SESSION", "$_ENV", "$GLOBALS"}
CRED_LITERAL_RE = re.compile(
    r"(?i)(api[_-]?key|access[_-]?token|secret|password|passwd)\s*[:=]\s*"
    r"([\"'][^\"'\s<>]{4,}[\"']|[^\s\"'<>]{8,})")
KEYFILE_RE = re.compile(r"~\/\.ssh|\.pem\b|\.key\b|credentials\.json|client_secret|vault\b")
SHELL_BANG_RE = re.compile(r"^\s*!(?![\(\[])(\S.*)?$")
BINARY_MAGICS = (b"\x7fELF", b"MZ", b"PK\x03\x04", b"PK\x05\x06", b"CWS", b"FWS")

PLACEHOLDER_HOSTS = {"example.com", "example.org", "example.net", "localhost",
                     "127.0.0.1", "0.0.0.0", "::1"}
PLACEHOLDER_VALUES = ("<", "redacted", "example", "changeme", "change this",
                      "your-", "xxx", "here", "placeholder", "todo")


def is_placeholder_host(host: str) -> bool:
    host = host.lower().split("/")[0].split(":")[0].split("@")[-1]
    if host in PLACEHOLDER_HOSTS or host.endswith(".example.com") \
            or host.endswith(".example.org") or host.endswith(".example.net"):
        return True
    # Single-label stand-ins for a user-supplied target in pentest/CTF docs.
    if host in {"target", "challenge", "victim"}:
        return True
    if host.startswith(("10.", "192.168.")):
        return True
    if re.match(r"172\.(1[6-9]|2[0-9]|3[01])\.", host):
        return True
    return False


def is_placeholder_value(value: str) -> bool:
    lowered = value.strip().strip("\"'").lower()
    return any(token in lowered for token in PLACEHOLDER_VALUES)


def is_binary(path: Path) -> bool:
    try:
        head = path.read_bytes()[:4]
    except OSError:
        return False
    if any(head.startswith(magic) for magic in BINARY_MAGICS):
        return True
    try:
        path.read_text(encoding="utf-8")
    except UnicodeError:
        return True
    return False


def finding_id(relpath: str, kind: str, match: str) -> str:
    digest = hashlib.sha1(f"{relpath}\0{kind}\0{match}".encode("utf-8")).hexdigest()
    return digest[:12]


def make_finding(source: Path, relpath: str, line: int, kind: str,
                 match: str, detail: str = "") -> dict:
    return {"id": finding_id(relpath, kind, match), "file": relpath,
            "line": line, "kind": kind, "match": match[:200], "detail": detail}


def parse_allowed_tools(text: str) -> list[tuple[int, str]]:
    """Return (line, value) pairs for allowed-tools entries in frontmatter."""
    entries: list[tuple[int, str]] = []
    if not text.startswith("---"):
        return entries
    parts = text.split("---", 2)
    if len(parts) < 3:
        return entries
    front = parts[1]
    in_tools = False
    for offset, line in enumerate(front.splitlines(), 1):
        stripped = line.strip()
        if re.match(r"allowed-tools\s*:", stripped):
            value = stripped.split(":", 1)[1].strip().strip("\"'")
            if value.startswith("["):
                for item in re.findall(r"[\"']([^\"']+)[\"']", value):
                    entries.append((offset, item))
            elif value:
                entries.append((offset, value))
            in_tools = True
            continue
        if in_tools:
            item = re.match(r"-\s*[\"']?([^\"'\s]+)[\"']?", stripped)
            if item and not re.match(r"[a-zA-Z0-9_-]+\s*:", stripped):
                entries.append((offset, item.group(1)))
            elif stripped and not stripped.startswith("-"):
                in_tools = False
    return entries


def scan_file(path: Path, source: Path) -> list[dict]:
    relpath = path.relative_to(source).as_posix()
    findings: list[dict] = []
    suffix = path.suffix.lower()
    if suffix in SCRIPT_EXTS or (path.parent.name == "scripts"
                                 and suffix not in TEXT_EXTS):
        findings.append(make_finding(source, relpath, 1, "script",
                                     path.name, "executable script in skill dir"))
    if is_binary(path):
        findings.append(make_finding(source, relpath, 1, "binary",
                                     path.name, "non-text or binary-magic file"))
        return findings
    if path.suffix.lower() not in TEXT_EXTS:
        return findings
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return findings
    is_script = path.suffix.lower() in SCRIPT_EXTS
    is_md = path.suffix.lower() in {".md", ".mdx"}
    if is_md:
        for line_no, value in parse_allowed_tools(text):
            findings.append(make_finding(source, relpath, line_no,
                                         "allowed-tools", value,
                                         "frontmatter allowed-tools entry"))
    in_fence = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
        if is_md and SHELL_BANG_RE.match(line):
            findings.append(make_finding(source, relpath, number, "shell-bang",
                                         line.strip()[:120],
                                         "line starts with ! (shell execution)"))
        for match in NETWORK_KW_RE.finditer(line):
            findings.append(make_finding(source, relpath, number, "network",
                                         match.group(0), "network-call keyword"))
        for match in URL_RE.finditer(line):
            url = match.group(0).rstrip(".,;")
            host = url.split("://", 1)[1].split("/")[0] if "://" in url else ""
            if is_placeholder_host(host):
                continue
            kind = "callback" if is_script else "network"
            findings.append(make_finding(source, relpath, number, kind, url,
                                         f"absolute URL, host {host}"))
        if is_script or path.suffix.lower() in {".sh", ".ps1"}:
            for match in ENV_READ_RE.finditer(line):
                findings.append(make_finding(source, relpath, number,
                                             "credential", match.group(0),
                                             "credential read (env var)"))
            for match in SHELL_ENV_RE.finditer(line):
                if match.group(0) in PHP_SUPERGLOBALS:
                    continue
                findings.append(make_finding(source, relpath, number,
                                             "credential", match.group(0),
                                             "environment variable reference"))
            for match in KEYFILE_RE.finditer(line):
                findings.append(make_finding(source, relpath, number,
                                             "credential", match.group(0),
                                             "key file / vault reference"))
        for match in CRED_LITERAL_RE.finditer(line):
            value = match.group(2)
            if is_placeholder_value(value):
                continue
            findings.append(make_finding(source, relpath, number, "credential",
                                         match.group(0)[:120],
                                         "literal credential assignment"))
    return findings


def discover_skill_dirs(source: Path) -> list[Path]:
    """Dirs containing SKILL.md, plus the source root itself if it has scripts."""
    found: list[Path] = []
    for path in sorted(source.rglob("SKILL.md")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        found.append(path.parent)
    return found


def audit(source: Path) -> list[dict]:
    source = source.resolve()
    if not source.is_dir():
        raise ValueError(f"source is not a directory: {source}")
    findings: list[dict] = []
    for skill_dir in discover_skill_dirs(source):
        for path in sorted(skill_dir.rglob("*")):
            if not path.is_file() or path.is_symlink():
                continue
            if any(part in SKIP_DIRS for part in path.relative_to(skill_dir).parts):
                continue
            findings.extend(scan_file(path, source))
    for path in sorted(source.iterdir()):
        if path.is_file() and path.suffix.lower() in SCRIPT_EXTS:
            findings.extend(scan_file(path, source))
    seen: set[tuple[str, int, str, str]] = set()
    unique: list[dict] = []
    for finding in findings:
        key = (finding["file"], finding["line"], finding["kind"], finding["match"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(finding)
    unique.sort(key=lambda f: (f["file"], f["line"], f["kind"], f["match"]))
    return unique


def load_dispositions(path: Path | None) -> dict:
    if path is None:
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    dispositions = data.get("dispositions", {})
    for finding_id_, entry in dispositions.items():
        if entry.get("action") not in {"fix", "waive", "reject"}:
            raise ValueError(f"disposition {finding_id_}: bad action {entry.get('action')!r}")
        if not str(entry.get("reason", "")).strip():
            raise ValueError(f"disposition {finding_id_}: reason required")
    return dispositions


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True,
                        help="Pinned source tree (clone root or staging dir of skill dirs).")
    parser.add_argument("--dispositions", type=Path,
                        help="JSON file mapping finding IDs to {action, reason}.")
    parser.add_argument("--json", type=Path, help="Write the full JSON report here.")
    args = parser.parse_args(argv)
    try:
        findings = audit(args.source)
        dispositions = load_dispositions(args.dispositions)
    except (OSError, ValueError) as exc:
        print(f"audit error: {exc}", file=sys.stderr)
        return 2
    unresolved = [f for f in findings if f["id"] not in dispositions]
    by_kind: dict[str, int] = {}
    for finding in findings:
        by_kind[finding["kind"]] = by_kind.get(finding["kind"], 0) + 1
    report = {"source": str(args.source.resolve()), "findings_total": len(findings),
              "by_kind": by_kind, "unresolved": len(unresolved),
              "dispositioned": len(findings) - len(unresolved),
              "findings": [{**f,
                            "disposition": dispositions.get(f["id"])} for f in findings]}
    if args.json:
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{len(findings)} findings ({len(unresolved)} unresolved) in {args.source}")
    for kind in sorted(by_kind):
        print(f"  {kind}: {by_kind[kind]}")
    for finding in unresolved:
        print(f"UNRESOLVED {finding['id']} {finding['file']}:{finding['line']} "
              f"[{finding['kind']}] {finding['match']}")
    return 1 if unresolved else 0


if __name__ == "__main__":
    raise SystemExit(main())
