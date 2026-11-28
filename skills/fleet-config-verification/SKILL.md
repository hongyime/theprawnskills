---
name: fleet-config-verification
description: >-
  Verify a fleet configuration change with deterministic scripts, not LLM
  judgement: host identity, Herdr live state, tool versions, config-file
  hashes, live resolved models, git drift, and fresh-session proof across
  the VM, L390, 3410, T14, and E14, emitting machine-readable JSON lines
  per machine. Use for "verify the fleet", "check the fleet change", "is
  the fleet in sync", or before reporting any fleet change done.
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Fleet-Config Verification

Deterministic verification for fleet configuration changes. Scripts check;
LLM judgement does not. A fleet change is not reported done unless these
checks pass per machine.

Version match: hc 0.1.20 / herdr 0.9.5, verified live 2026-11-27 on L390 and
3410. Updating a fleet tool without updating this line is a bug.

## When to use

After any fleet configuration change (model slot, provider gate, fallback
entry, disabled-provider flag, git identity, skills install, Herdr change),
before reporting it done. Also for a periodic fleet parity check. For the
human-readable playbook behind these rules, read
`~/workspace/custom-skills/fleet_config_verification/SKILL.md` — this skill
is the deterministic layer under it, not a replacement. Where the two
conflict, the custom skill wins and the conflict is flagged, never silently
resolved.

## Rules (invariants — do not weaken)

- V1: Every fleet-done claim names the machine, the checks run, and the
  evidence (hash / resolved model / fresh-session result) — never "fleet
  verified" with no per-machine breakdown.
- V2: Host identity (hostname + Tailscale address) is confirmed in the same
  session as the checks; a check run without it is reported as unproven,
  never passed. A piped or jump-host command is unproven until the hostname
  matches the intended machine.
- V3: A config difference is reported per machine and per field; differences
  are never averaged away and one machine's result is never fleet proof.
- V4: File checks, resolved-config checks, and fresh-session checks are
  labelled separately; a file check is never described as runtime proof.
- V5: A zero-change re-run is reported as "no changes detected by these
  checks", never as proof the fleet is correct.
- V6: No credential, token, or key material appears in any check output,
  report, or digest entry. Scripts emit hashes and model names only — never
  file contents.
- V7: Read-only. Scripts change no config, restart no service, and write
  nothing outside their own report output. 3410 NEVER reboots.

## Transport (baked in, not left to the agent)

- Linux (VM/L390/3410): pipe the script via stdin, never `ssh 'a; b'`
  (that splits across the jump host — the second command runs on L390).
  Environment does NOT cross ssh: set vars in the remote command itself.
  `cat scripts/<name>.sh | <host>-ssh 'EXPECTED_HOST=<h> MACHINE=<m> bash -s'`
  or `cat scripts/<name>.py | <host>-ssh 'EXPECTED_HOST=<h> MACHINE=<m> python3 -'`.
  Pass `-F /home/hatch/.ssh/config` explicitly (exec runs as root and ssh
  otherwise ignores it). Use the wrappers `~/workspace/bin/l390-ssh` and
  `~/workspace/bin/3410-ssh` where they exist. Verified 2026-11-27: env
  exported locally is silently lost across ssh — every record came back
  unproven until the vars moved into the remote command.
- Windows (T14/E14): stdin piping is unreliable — scp the `.ps1` to the
  host, run it with `powershell -NoProfile -ExecutionPolicy Bypass -File`,
  then delete it. Never leave the script on the host. Keep stderr out of
  the JSONL (redirect to a `.err` file) — PowerShell error text is not
  JSON and corrupts the file. PowerShell quirks: quote
  `HEAD...@{upstream}` as a string, never use a bare `(if ...)` as an
  expression value.
- Every script takes `EXPECTED_HOST=<hostname>` and `MACHINE=<label>` in
  the environment. A hostname mismatch makes every record unproven.

## Workflow

Run in this order, one JSONL file per machine (name it `<machine>.jsonl`):

1. Host + Herdr — `check-host-herdr.sh` (Linux) / `.ps1` (Windows).
   Host identity, `hc ls` JSON (machines connected, live terminals).
2. Versions + hashes — `check-versions-hashes.sh` / `.ps1`.
   codex/agy/opencode/hc/herdr/strix/kiro/gh versions; sha256 of
   opencode.jsonc, model-fallback.json, codex config.toml, omo.jsonc,
   library.json, FORGE AGENTS.md (`/home/bryan/Projects/forge/AGENTS.md`
   on 3410 only), skills-dir entry count.
3. Resolved config — `check-resolved-config.py` / `.ps1`.
   Codex model + reasoning + live models catalog (slugs, fetched_at);
   opencode model/small_model/disabled_providers/provider models; agent
   primary slots counted deepseek vs other; fallback models/depth/triggers;
   omo models/fallback_models/disabled_providers. No dump subcommand
   exists for codex or opencode — parsing the files they resolve from is
   the resolved check, and it is labelled resolved, not file.
4. Git drift — `check-git-drift.sh` / `.ps1`.
   `EXPECTED_NAME` / `EXPECTED_EMAIL` from `expected.json`. Global
   identity plus a per-repo local-identity sweep (`REPO_ROOT`: VM
   `~/workspace`, Linux `~/Projects`, Windows `%USERPROFILE%\Projects`).
   A repo-local identity that differs from global is a FAIL (unswept
   override) until a human confirms it intentional.
5. Fresh session — procedure, then `check-fresh-session.py`.
   Open a fresh agent session in a visible Herdr pane on the target
   machine, ask it to state the model it runs on, capture the verbatim
   reply, then validate:
   `python3 scripts/check-fresh-session.py --machine <m> --pane <p>
   --agent <agy|codex|opencode> --expected-model <m> --reported-model <r>`
   A file-check-only report never claims runtime proof.
6. Diff — `python3 scripts/diff-reports.py [--expected expected.json]
   vm.jsonl l390.jsonl 3410.jsonl t14.jsonl e14.jsonl`.
   Cross-machine diff (baseline = most common value, outliers named by
   machine and field) plus expected-value checks. Ends with a summary
   record whose verdict is "no changes detected by these checks" when
   nothing differs — never "fleet correct".
7. Report — per machine, done-or-not first, then resolved primary,
   fallback entries, fresh-session result, with check types labelled.
   Then the digest summary (below).

## Record schema

One JSON object per line: `machine`, `check`, `field`, `type`, `status`,
`evidence`, `value`. Types: `host`, `file`, `resolved`, `fresh-session`,
`version`, `diff`, `expected`. Statuses: `pass`, `fail`, `unproven`,
`not-covered`, `unavailable`. `not-covered` means the tool/file does not
exist on that machine (e.g. library.json on T14/E14) — never pass, never
fail on its own. `unavailable` means the check could not run; `unproven`
means host identity was not confirmed in-session.

## Report template

```text
Fleet verification — <change> — <date>
- DONE — VM: <resolved primary>, fallbacks <...>, fresh session <model>
- NOT DONE — L390: <field> differs: <value> vs <baseline>
- NOT DONE — 3410: <field> <reason>
- BLOCKED — T14: <reason>
Still open: <list, or "nothing open">
Checks run: <list>. Zero-change wording: "no changes detected by these checks".
```

## Digest summary

Append to the digest as one block (manual paste — no automated digest
feed exists; do not invent one):

```text
[Fleet verification] <change>: VM <done/not>, L390 <done/not>,
3410 <done/not>, T14 <done/not>, E14 <done/not>.
Outliers: <machine>: <field> <value> vs <baseline>; or "none".
```

## Known not-covered (T1 inventory, 2026-11-27 — live reads)

- opencode.jsonc missing on L390 and 3410 (binary IS present there,
  v1.19.3 at `~/.local/bin/opencode` — T1 correction #2). model-fallback.json
  still checked.
- `~/.config/theprawnskills/library.json` missing on T14/E14.
- Codex models_cache path on Windows not verified live — script reports
  not-covered if absent.
- VM has no Tailscale IP (tailscale not up) — recorded UNAVAILABLE, never
  a run failure.
- Digest ingestion format UNKNOWN — manual paste only (see above).
- Codex model has no fleet standard on file (live: VM luna/medium, L390
  terra/high, 3410 terra/high, T14 luna/low, E14 terra/xhigh) — the
  differ reports cross-machine outliers only for it; do not invent an
  expected value. `expected.json` covers only fleet-agreed fields: git
  identity, opencode model/small_model/disabled_providers, fallback
  models, fallback depth.
- hc lists T14 as machine name `prawn-t4` — accepted as an alias.
- Windows version records carry `value: null` when the tool is a
  .ps1/.cmd wrapper with no FileVersion (present, version not probed) —
  the differ skips nulls instead of diffing a path against a version.
- 3410 repo drive lives under /media, not ~/Projects — the default
  REPO_ROOT sweep covers only ~/Projects (7 repos); pass
  REPO_ROOT=<drive path> to sweep the repo drive (read-only; never fix
  bugs there — sync only).
- Live divergences found by T1 + the first full run 2026-11-27 (report,
  do not fix here): omo.jsonc L390==3410 but T14≠E14≠Linux (all use
  beam-free/glm-free fallbacks); gh 2.46.0 vs 2.101.0 vs 2.81.0; agy
  1.5.13 vs 1.5.18; codex 0.164.0-alpha.9 vs 0.170.0 vs 0.171.0; opencode
  1.18.34 (VM) vs 1.19.3 (L390/3410); strix 1.7.1 on 3410 only (bash
  wrapper); library.json VM differs from L390/3410; model-fallback Linux
  vs Windows differ only by logPath; opencode primary slots VM 19/19 vs
  Windows 12/12; FORGE AGENTS.md hash differs 3410 vs T14; skills-dir
  entries 70 (Linux) vs 259 (Windows, OneDrive-backed); repo-local git
  identity overrides: VM theprawnskills (email without 66017805+ prefix),
  L390 patreonalive (name "b") and healthkaki-pov (name "Bryan").

## Evidence contract

Per `verification-loop`: PASS / FAIL / SKIPPED (reason) / UNAVAILABLE
(prerequisite) / NOT APPLICABLE (reason) per check. A required check that
is SKIPPED or UNAVAILABLE leaves readiness unverified; it is never turned
into PASS. Verify against the real artifact, not a proxy, a self-report,
or "it compiles". A zero exit code with zero collected checks is not
coverage.
