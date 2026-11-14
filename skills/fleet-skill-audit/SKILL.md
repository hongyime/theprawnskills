---
name: fleet-skill-audit
description: >-
  Generic, fault-tolerant audit of agent skills discovery and health across all
  fleet machines. Verifies that agents (OpenCode, Codex, Claude Code, Kiro, Cursor,
  DeepSeek) discover profile skills on disk with valid frontmatter, intact links,
  and zero secret leaks without requiring active agent logins. Gracefully skips
  unreachable hosts. Trigger on "audit fleet skills", "check all machine skills",
  "verify agent skills across machines".
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Fleet Skill Audit

Audit agent skill discovery, file integrity, and profile synchronization across all
developer workstations and agent harnesses (OpenCode, Codex, Claude Code, Kiro,
Cursor, DeepSeek).

The audit is:
- **Fault-Tolerant**: Dynamically discovers reachable nodes; unreachable or offline hosts are skipped within seconds without halting the audit.
- **Login-Agnostic**: Operates directly at the filesystem and frontmatter discovery layer. Requires zero active API keys, OAuth tokens, or paid subscriptions.
- **Privacy-Safe**: Masks hostnames, user paths, and IP addresses in all audit outputs and logs by default.

---

## When to Use

- After pushing or updating skills to verify that all machines and agent roots discover them.
- When an agent on a machine cannot find an installed skill.
- Routine fleet health inspection across mixed Linux, macOS, and Windows workstations.
- Trigger on: `"audit fleet skills"`, `"check all machine skills"`, `"verify agent skills across machines"`.

---

## Agent Discovery Architecture

Different coding agents discover skills through standardized filesystem directories:

| Agent Harness | Discovery Path (POSIX) | Discovery Path (Windows) | Nature of Integration |
|---|---|---|---|
| **OpenCode** | `~/.agents/skills/` | `%USERPROFILE%\.agents\skills\` | Direct or via directory junction to shared library |
| **Codex CLI** | `~/.agents/skills/` or `~/.codex/skills/` | `%USERPROFILE%\.codex\skills\` | Shared symlinks (Linux) or profile copies (Windows) |
| **Claude Code** | `~/.claude/skills/` | `%USERPROFILE%\.claude\skills\` | Dedicated user-level discovery folder |
| **Kiro** | `~/.kiro/skills/` or `~/.agents/skills/` | `%USERPROFILE%\.kiro\skills\` | Dedicated directory symlinking shared library |
| **Cursor** | `~/.cursor/skills/` or `~/.agents/skills/` | `%USERPROFILE%\.cursor\skills\` | Shared symlinks or dedicated root |
| **DeepSeek / Custom** | `~/.agents/skills/` | `%USERPROFILE%\.agents\skills\` | Standard community shared skill folder |

---

## Running the Audit

The audit is executed via the bundled Python script:

```bash
# Standard fleet audit (anonymized names & IPs, dynamic network discovery)
python3 scripts/audit_fleet_skills.py

# Local machine only (zero network probes)
python3 scripts/audit_fleet_skills.py --local-only

# Machine-readable JSON output (for automated CI/monitoring pipelines)
python3 scripts/audit_fleet_skills.py --json

# Raw display (shows unmasked machine hostnames and IPs when authorized)
python3 scripts/audit_fleet_skills.py --unmask
```

On Windows machines:

```powershell
python scripts\audit_fleet_skills.py
```

---

## Dynamic Node Discovery & Fault Tolerance

1. **Host Source**:
   - Reads private inventory from `machines.local.toml` (if present and configured).
   - If missing, automatically inspects active nodes via `tailscale status --json` (filtering for developer OS platforms: Linux, macOS, Windows).
   - Local host is always audited in-process with 0 network latency.
2. **Network Timeouts**:
   - Remote probes use a strict 3-second SSH timeout (`-o BatchMode=yes -o ConnectTimeout=3`).
   - If a machine is offline or powered down, it is recorded as `OFFLINE` and skipped immediately.
3. **Execution Payload**:
   - Executes a compact, self-contained discovery payload (Base64-encoded PowerShell on Windows; Base64-encoded Python on POSIX).
   - Never writes or modifies files on target hosts; purely read-only inspection.

---

## Verification Criteria

For every discovered agent root, the audit verifies:
1. **Directory Presence**: Root exists and is accessible.
2. **Profile Completeness**: Number of matching skills from `default-profile.toml` present vs. expected (e.g. `66/66`).
3. **Frontmatter Integrity**: Every skill directory contains a readable `SKILL.md` with valid YAML frontmatter and a `name` tag. Broken skills (missing `SKILL.md` or unparseable headers) are flagged.
4. **Custom Skills Segregation**: Non-profile skills (e.g. local experimental tools or vendor plugins) are identified as `Custom (N skills)` without generating false missing-profile warnings.

---

## Output Format

The output produces a clear ASCII table:

```text
==================================================================================================
HOST                 OS         STATUS       DISCOVERY ROOT                         STATUS / SKILLS
--------------------------------------------------------------------------------------------------
node-1 (local)       linux      ONLINE       Shared (.agents: OpenCode/Codex/Cursor) OK (66/66)     
                                             Kiro                                   OK (66/66)     
                                             Claude Code                            Custom (26 skills)
node-2               windows    ONLINE       Shared (.agents: OpenCode)             OK (66/66)     
                                             Codex CLI                              OK (66/66)     
                                             Claude Code                            OK (66/66)     
node-3               linux      ONLINE       Shared (.agents: OpenCode/Codex/Cursor) OK (66/66)     
                                             Kiro                                   OK (66/66)     
node-4               windows    OFFLINE      -                                      (Ping / SSH timed out)
==================================================================================================
Fleet Summary: 3/4 nodes reachable. Fault-tolerant audit complete.
```
