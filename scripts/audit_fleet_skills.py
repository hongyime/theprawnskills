#!/usr/bin/env python3
"""Generic, fault-tolerant audit of agent skills discovery and health across fleet machines.

Scans local and remote hosts (via Tailscale or private machine registry) for standard
agent skill discovery roots (OpenCode, Codex, Claude Code, Kiro, Cursor, DeepSeek).
Operates purely at the filesystem and frontmatter discovery layer without requiring
active agent sessions, subscriptions, or interactive logins.
"""
from __future__ import annotations

import argparse
import base64
import concurrent.futures
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib
from typing import Any

# Standard skill roots scanned per platform
STANDARD_ROOTS_POSIX = [
    (".agents/skills", "Shared (.agents: OpenCode/Codex/Cursor)"),
    (".kiro/skills", "Kiro"),
    (".claude/skills", "Claude Code"),
    (".codex/skills", "Codex CLI (Dedicated)"),
    (".cursor/skills", "Cursor (Dedicated)"),
    (".config/opencode/skills", "OpenCode (Dedicated)"),
]

STANDARD_ROOTS_WINDOWS = [
    (".agents\\skills", "Shared (.agents: OpenCode Junction)"),
    (".codex\\skills", "Codex CLI"),
    (".claude\\skills", "Claude Code"),
    (".cursor\\skills", "Cursor"),
    (".config\\opencode\\skills", "OpenCode (Dedicated)"),
    (".kiro\\skills", "Kiro"),
    ("OneDrive\\01 SKILLS\\.agents\\skills", "Canonical OneDrive Shared"),
]


@dataclass
class RootAuditResult:
    path: str
    label: str
    exists: bool = False
    is_link: bool = False
    skill_count: int = 0
    profile_present: int = 0
    profile_total: int = 0
    missing_skills: list[str] = field(default_factory=list)
    broken_skills: list[str] = field(default_factory=list)


@dataclass
class HostAuditResult:
    host_id: str
    display_name: str
    os_name: str
    status: str  # "ONLINE", "OFFLINE", "UNREACHABLE", "ERROR"
    roots: list[RootAuditResult] = field(default_factory=list)
    message: str = ""


def load_profile_skills(library_root: Path) -> list[str]:
    profile_path = library_root / "default-profile.toml"
    if not profile_path.is_file():
        return []
    with profile_path.open("rb") as f:
        data = tomllib.loads(f.read().decode("utf-8-sig"))
    return [str(s) for s in data.get("skills", [])]


def mask_string(val: str) -> str:
    """Mask hostnames or IP addresses for privacy."""
    if not val:
        return "unknown"
    # If IPv4: mask middle octets
    if re.fullmatch(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", val):
        parts = val.split(".")
        return f"{parts[0]}.***.***.{parts[3]}"
    # If text name: keep prefix/suffix
    if len(val) <= 4:
        return "***"
    return f"{val[:2]}***{val[-2:]}"


def inspect_directory_skills(root: Path, profile_skills: list[str]) -> tuple[int, int, list[str], list[str]]:
    """Scan a local directory for valid skills against the profile."""
    if not root.is_dir():
        return 0, 0, [], []

    skill_folders = [p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")]
    skill_count = len(skill_folders)
    valid_names = set()
    broken_skills = []

    for folder in skill_folders:
        skill_md = folder / "SKILL.md"
        if not skill_md.is_file():
            broken_skills.append(f"{folder.name} (no SKILL.md)")
            continue
        try:
            head = skill_md.read_text(encoding="utf-8-sig", errors="replace")[:500]
            if not head.startswith("---"):
                broken_skills.append(f"{folder.name} (missing frontmatter)")
                continue
            match = re.search(r"name:\s*([a-z0-9-]+)", head)
            if match:
                valid_names.add(match.group(1))
            else:
                valid_names.add(folder.name)
        except Exception as exc:
            broken_skills.append(f"{folder.name} ({exc})")

    present_profile = [s for s in profile_skills if s in valid_names]
    missing_profile = [s for s in profile_skills if s not in valid_names]
    return skill_count, len(present_profile), missing_profile, broken_skills


def audit_local_host(library_root: Path, profile_skills: list[str], mask: bool = False) -> HostAuditResult:
    home = Path.home()
    is_win = sys.platform == "win32"
    os_name = "windows" if is_win else ("darwin" if sys.platform == "darwin" else "linux")
    raw_name = os.environ.get("HOSTNAME") or "localhost"
    display_name = f"{mask_string(raw_name)} (local)" if mask else f"{raw_name} (local)"

    roots_to_scan = STANDARD_ROOTS_WINDOWS if is_win else STANDARD_ROOTS_POSIX
    results: list[RootAuditResult] = []

    for subpath, label in roots_to_scan:
        full_path = home / subpath
        if not full_path.exists():
            continue
        count, present, missing, broken = inspect_directory_skills(full_path, profile_skills)
        display_path = f"~/{subpath}" if not is_win else f"%USERPROFILE%\\{subpath}"
        results.append(RootAuditResult(
            path=display_path,
            label=label,
            exists=True,
            is_link=full_path.is_symlink(),
            skill_count=count,
            profile_present=present,
            profile_total=len(profile_skills),
            missing_skills=missing,
            broken_skills=broken,
        ))

    return HostAuditResult(
        host_id="localhost",
        display_name=display_name,
        os_name=os_name,
        status="ONLINE",
        roots=results,
    )


def audit_remote_host(
    host_target: str,
    raw_label: str,
    os_hint: str,
    profile_skills: list[str],
    mask: bool = False,
    timeout: int = 3,
) -> HostAuditResult:
    display_name = mask_string(raw_label or host_target) if mask else (raw_label or host_target)
    is_win = os_hint.lower() == "windows"

    if is_win:
        # Base64 encoded UTF-16LE powershell command avoids all OpenSSH escaping issues
        skills_csv = "','".join(profile_skills)
        ps_code = """
$ErrorActionPreference = 'SilentlyContinue'
$profileSkills = @('__SKILLS_CSV__')
$roots = @(
  @{ Path = (Join-Path $HOME '.agents\\skills'); Label = 'Shared (.agents: OpenCode)' },
  @{ Path = (Join-Path $HOME '.codex\\skills'); Label = 'Codex CLI' },
  @{ Path = (Join-Path $HOME '.claude\\skills'); Label = 'Claude Code' },
  @{ Path = (Join-Path $HOME '.cursor\\skills'); Label = 'Cursor' },
  @{ Path = (Join-Path $HOME '.config\\opencode\\skills'); Label = 'OpenCode (Dedicated)' },
  @{ Path = (Join-Path $HOME '.kiro\\skills'); Label = 'Kiro' },
  @{ Path = (Join-Path $HOME 'OneDrive\\01 SKILLS\\.agents\\skills'); Label = 'OneDrive Shared' }
)
$out = @()
foreach ($r in $roots) {
  if (Test-Path -LiteralPath $r.Path) {
    $dirs = Get-ChildItem -LiteralPath $r.Path -Directory -ErrorAction SilentlyContinue | Where-Object { -not $_.Name.StartsWith('.') }
    $count = ($dirs | Measure-Object).Count
    $names = @()
    $broken = @()
    foreach ($d in $dirs) {
      $sk = Join-Path $d.FullName 'SKILL.md'
      if (Test-Path -LiteralPath $sk) {
        $names += $d.Name
      } else {
        $broken += $d.Name
      }
    }
    $present = ($profileSkills | Where-Object { $names -contains $_ }).Count
    $missing = @($profileSkills | Where-Object { $names -notcontains $_ })
    $out += @{
      path = $r.Path
      label = $r.Label
      exists = $true
      count = $count
      present = $present
      missing = $missing
      broken = $broken
    }
  }
}
$out | ConvertTo-Json -Compress
""".replace("__SKILLS_CSV__", skills_csv)
        encoded_ps = base64.b64encode(ps_code.encode("utf-16le")).decode("ascii")
        remote_cmd = f"powershell.exe -NoProfile -EncodedCommand {encoded_ps}"
    else:
        # POSIX Python one-liner encoded in base64
        py_code = f"""
import json, os, pathlib
profile = set({profile_skills!r})
roots = [
  ('.agents/skills', 'Shared (.agents: OpenCode/Codex/Cursor)'),
  ('.kiro/skills', 'Kiro'),
  ('.claude/skills', 'Claude Code'),
  ('.codex/skills', 'Codex CLI (Dedicated)'),
  ('.cursor/skills', 'Cursor (Dedicated)'),
  ('.config/opencode/skills', 'OpenCode (Dedicated)'),
]
home = pathlib.Path.home()
out = []
for rel, label in roots:
    p = home / rel
    if p.is_dir():
        dirs = [d for d in p.iterdir() if d.is_dir() and not d.name.startswith('.')]
        valid = set()
        broken = []
        for d in dirs:
            sk = d / 'SKILL.md'
            if sk.is_file():
                valid.add(d.name)
            else:
                broken.append(d.name)
        present = len(profile.intersection(valid))
        missing = sorted(list(profile - valid))
        out.append({{
            'path': str(p),
            'label': label,
            'exists': True,
            'count': len(dirs),
            'present': present,
            'missing': missing,
            'broken': broken
        }})
print(json.dumps(out))
"""
        encoded_py = base64.b64encode(py_code.encode("utf-8")).decode("ascii")
        remote_cmd = f"python3 -c \"import base64; exec(base64.b64decode('{encoded_py}').decode('utf-8'))\""

    ssh_args = [
        "ssh",
        "-o", "BatchMode=yes",
        "-o", f"ConnectTimeout={timeout}",
        "-o", "StrictHostKeyChecking=accept-new",
        host_target,
        remote_cmd,
    ]

    try:
        proc = subprocess.run(ssh_args, capture_output=True, text=True, timeout=timeout + 5)
        if proc.returncode != 0:
            return HostAuditResult(
                host_id=host_target,
                display_name=display_name,
                os_name=os_hint,
                status="UNREACHABLE",
                message="SSH probe failed",
            )
        stdout = proc.stdout.strip()
        json_line = next((line for line in stdout.splitlines() if line.startswith("[") or line.startswith("{")), None)
        if not json_line:
            return HostAuditResult(
                host_id=host_target,
                display_name=display_name,
                os_name=os_hint,
                status="UNREACHABLE",
                message="No response",
            )
        raw_roots = json.loads(json_line)
        if isinstance(raw_roots, dict):
            raw_roots = [raw_roots]

        root_results = []
        for r in raw_roots:
            raw_path = r.get("path", "")
            # Privacy mask user paths on remote machines
            clean_path = re.sub(r"^[A-Za-z]:\\Users\\[^\\]+", "%USERPROFILE%", raw_path)
            clean_path = re.sub(r"^/home/[^/]+", "~", clean_path)

            root_results.append(RootAuditResult(
                path=clean_path,
                label=r.get("label", ""),
                exists=bool(r.get("exists", False)),
                skill_count=int(r.get("count", 0)),
                profile_present=int(r.get("present", 0)),
                profile_total=len(profile_skills),
                missing_skills=list(r.get("missing", [])),
                broken_skills=list(r.get("broken", [])),
            ))

        return HostAuditResult(
            host_id=host_target,
            display_name=display_name,
            os_name=os_hint,
            status="ONLINE",
            roots=root_results,
        )
    except subprocess.TimeoutExpired:
        return HostAuditResult(
            host_id=host_target,
            display_name=display_name,
            os_name=os_hint,
            status="OFFLINE",
            message="Ping / SSH timed out",
        )
    except Exception as exc:
        return HostAuditResult(
            host_id=host_target,
            display_name=display_name,
            os_name=os_hint,
            status="ERROR",
            message="Probe exception",
        )


def discover_tailscale_hosts() -> list[tuple[str, str, str]]:
    """Dynamically discover candidate coding nodes from Tailscale status without hardcoding."""
    try:
        proc = subprocess.run(["tailscale", "status", "--json"], capture_output=True, text=True, timeout=3)
        if proc.returncode != 0:
            return []
        data = json.loads(proc.stdout)
    except Exception:
        return []

    peers = data.get("Peer", {})
    candidates: list[tuple[str, str, str]] = []

    for peer in peers.values():
        os_type = (peer.get("OS") or "").lower()
        # Only probe developer machine OSes (Linux, Windows, macOS)
        if os_type not in {"linux", "windows", "darwin"}:
            continue
        ips = peer.get("TailscaleIPs", [])
        if not ips:
            continue
        ip = ips[0]
        hostname = peer.get("HostName", ip)
        candidates.append((ip, hostname, os_type))

    return candidates


def discover_registry_hosts(library_root: Path) -> list[tuple[str, str, str]]:
    """Discover hosts from private machines.local.toml if present."""
    config_path = library_root / "machines.local.toml"
    if not config_path.is_file():
        explicit = os.environ.get("THEPRAWNSKILLS_MACHINE_CONFIG")
        if explicit and Path(explicit).is_file():
            config_path = Path(explicit)
        else:
            return []

    try:
        with config_path.open("rb") as f:
            data = tomllib.loads(f.read().decode("utf-8-sig"))
        machines = data.get("machines", [])
        results = []
        for m in machines:
            if not m.get("enabled", True) or m.get("local", False):
                continue
            target = m.get("ssh") or m.get("tailscale_ip")
            if target:
                label = m.get("label") or m.get("id", target)
                os_guess = "windows" if "\\" in m.get("canonical_root", "") else "linux"
                results.append((target, label, os_guess))
        return results
    except Exception:
        return []


def run_fleet_audit(library_root: Path, mask: bool = True, local_only: bool = False) -> list[HostAuditResult]:
    profile_skills = load_profile_skills(library_root)
    results: list[HostAuditResult] = []

    # 1. Local host audit (always runs, 0 network latency)
    results.append(audit_local_host(library_root, profile_skills, mask=mask))

    if local_only:
        return results

    # 2. Discover remote fleet nodes dynamically
    remote_hosts = discover_registry_hosts(library_root)
    if not remote_hosts:
        remote_hosts = discover_tailscale_hosts()

    # Filter out local address from remote targets
    local_ips = {"127.0.0.1", "::1", "localhost"}
    unique_remotes = []
    seen = set()
    for target, label, os_hint in remote_hosts:
        if target in local_ips or target in seen:
            continue
        seen.add(target)
        unique_remotes.append((target, label, os_hint))

    # 3. Probe remote hosts concurrently with strict timeout
    if unique_remotes:
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(unique_remotes), 8)) as executor:
            future_to_host = {
                executor.submit(audit_remote_host, target, label, os_hint, profile_skills, mask): target
                for target, label, os_hint in unique_remotes
            }
            for future in concurrent.futures.as_completed(future_to_host):
                try:
                    res = future.result()
                    results.append(res)
                except Exception:
                    target = future_to_host[future]
                    display = mask_string(target) if mask else target
                    results.append(HostAuditResult(
                        host_id=target,
                        display_name=display,
                        os_name="unknown",
                        status="ERROR",
                        message="Probe error",
                    ))

    return results


def render_table(results: list[HostAuditResult]) -> str:
    lines = [
        "=" * 98,
        f"{'HOST':<20} {'OS':<10} {'STATUS':<12} {'DISCOVERY ROOT':<38} {'STATUS / SKILLS':<15}",
        "-" * 98,
    ]

    for host in sorted(results, key=lambda h: (h.status != "ONLINE", h.display_name)):
        if host.status != "ONLINE":
            reason = f"({host.message})" if host.message else ""
            lines.append(f"{host.display_name:<20} {host.os_name:<10} {host.status:<12} {'-':<38} {reason:<15}")
            continue

        if not host.roots:
            lines.append(f"{host.display_name:<20} {host.os_name:<10} {'ONLINE':<12} {'(no roots found)':<38} {'-':<15}")
            continue

        first = True
        for r in host.roots:
            h_col = host.display_name if first else ""
            os_col = host.os_name if first else ""
            st_col = "ONLINE" if first else ""
            first = False

            if r.profile_present > 0:
                score = f"OK ({r.profile_present}/{r.profile_total})"
            elif r.skill_count > 0:
                score = f"Custom ({r.skill_count} skills)"
            else:
                score = "Empty (0)"

            lines.append(f"{h_col:<20} {os_col:<10} {st_col:<12} {r.label:<38} {score:<15}")
            if r.broken_skills:
                lines.append(f"  └── Broken: {', '.join(r.broken_skills[:3])}")
            if r.missing_skills and r.profile_present > 0 and r.profile_present < r.profile_total:
                lines.append(f"  └── Missing profile: {', '.join(r.missing_skills[:3])}")

    lines.append("=" * 98)
    online_count = sum(1 for h in results if h.status == "ONLINE")
    total_count = len(results)
    lines.append(f"Fleet Summary: {online_count}/{total_count} nodes reachable. Fault-tolerant audit complete.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="Path to the repository root")
    parser.add_argument("--unmask", action="store_true", help="Display raw hostnames and IPs instead of masking them")
    parser.add_argument("--local-only", action="store_true", help="Audit only the local host")
    parser.add_argument("--json", action="store_true", help="Output audit results as JSON")
    args = parser.parse_args()

    results = run_fleet_audit(args.root, mask=not args.unmask, local_only=args.local_only)

    if args.json:
        data = [
            {
                "host_id": h.host_id if args.unmask else mask_string(h.host_id),
                "display_name": h.display_name,
                "os": h.os_name,
                "status": h.status,
                "message": h.message,
                "roots": [
                    {
                        "path": r.path if args.unmask else mask_string(r.path),
                        "label": r.label,
                        "skill_count": r.skill_count,
                        "profile_present": r.profile_present,
                        "profile_total": r.profile_total,
                        "missing": r.missing_skills,
                        "broken": r.broken_skills,
                    }
                    for r in h.roots
                ],
            }
            for h in results
        ]
        print(json.dumps(data, indent=2))
    else:
        print(render_table(results))

    return 0


if __name__ == "__main__":
    sys.exit(main())
