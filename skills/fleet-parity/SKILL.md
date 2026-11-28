---
name: fleet-parity
description: >-
  Turn any fleet configuration change into the same three-part proof before
  reporting it done: cross-machine diff, live resolved-config check, and
  fresh-session end-to-end check per machine (VM, L390, 3410, T14, E14),
  with a per-machine done/not-done report. Use for "is the fleet in sync",
  "verify the fleet change", "parity check", or before claiming any fleet
  change done.
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Fleet Parity

A reusable playbook for proving a fleet configuration change, not a new
checker. The deterministic checks live in `fleet-config-verification`
(library skill + scripts); the human-readable rules live in the custom
skill `fleet_config_verification`. This skill adds the parity checklist,
the per-machine report shape, and the one-command diff runner around
them. It references those skills; it does not copy them. Where they
conflict, the custom skill wins and the conflict is flagged, never
silently resolved.

Version match: `scripts/diff-fleet-config.sh` + `fleet-config-verification`
scripts, verified live 2026-11-28. Updating a fleet tool without updating
this line is a bug.

## When to use

After any fleet configuration change (model slot, provider gate, fallback
entry, disabled-provider flag, git identity, skills install, Herdr change),
before reporting it done. Also for a periodic fleet parity check. Never
for a change itself — this skill only verifies; the change is a separate
task. Not a loop: on-demand only, no cron, no dashboard.

## Rules (invariants — do not weaken)

- V1: No fleet change is reported done unless all three checks (diff,
  resolved config, fresh session) have passed on every machine in scope,
  or the machines that did not pass are named as not-done.
- V2: A file check is never described as runtime proof; the three check
  types are always labelled separately in the report.
- V3: A command's result is never attributed to a machine whose hostname
  was not proven in the same session (hostname + Tailscale address).
- V4: A zero-change re-run is never treated as proof of parity. It is
  reported as "no changes detected by these checks".
- V5: The previous provider stays staged as backup until fresh-session
  proof passes; it is removed only on an explicit direction from Bryan.
- V6: The skill contains no credentials, tokens, or machine-local install
  state. Scripts emit hashes and model names only — never file contents.

## Before the change: state side effects, scope slots

Per `fleet_config_verification`: state what stops before editing shared
config (service, port, access path), the interim state, and the exact
reversal step plus the check after reversal. Scope every model slot the
change touches: main model, plan agents, categories, subagent models,
provider gates, fallback entries, disabled-provider flags — never primary
fields alone. Treat any machine that diverged in an earlier change as
suspect and check its full configuration first.

## The three-part proof, per machine

Run in this order. Machines: VM (`htch-runtime`, no Tailscale IP), L390
(`prawn-l390`, 100.101.72.18), 3410 (`prawn-3410`, 100.108.40.55), T14
(`Prawn-T14`, 100.87.34.38), E14 (`PRAWN-E14`, 100.92.164.125).

1. **Diff** — `scripts/diff-fleet-config.sh [file ...]` from the VM
   (default set below; `--git-identity` adds the repo-override sweep).
   Hash/byte-compare the changed files across all five machines; report
   each outlier by machine and field; never average a difference away.
   Exit 0 = no outliers, exit 2 = outliers found. For the full record
   set (versions, hashes, resolved config, git drift) use the
   `fleet-config-verification` scripts and `diff-reports.py` instead;
   this runner is the quick diff for one change.
2. **Live resolved config** — run the tool's resolved-config output on
   each machine and read the model it actually resolves (`fleet-config-
   verification` step 3: `check-resolved-config.py` / `.ps1`). Count
   old-provider primaries and old-provider backups separately. A
   provider disabled in plugin config is unavailable even if a file
   still lists it as primary. Never treat an estimated count as a live
   count (run `COUNT(*)` before calling a Postgres table empty).
3. **Fresh session** — close and reopen the agent on each machine in a
   visible Herdr pane, start a new session, confirm it runs on the
   intended model; validate the verbatim reply with
   `fleet-config-verification/scripts/check-fresh-session.py`. Opening
   the pane is agent dispatch, not a script step — the report labels
   fresh-session proof separately and never claims it from a file check.

## Host-truth guard

Every remote command runs with the true host proven in-session
(hostname + Tailscale address). SSH from the VM passes `-F
/home/hatch/.ssh/config` explicitly (exec runs as root; `~` resolves to
`/root/.ssh`) or explicit proxy/key flags. Complex commands are piped via
stdin (`cat script.sh | 3410-ssh 'bash -s'`), never `3410-ssh 'a; b'`.

Negative test, verified live 2026-11-28: `3410-ssh 'hostname; hostname'`
printed `prawn-3410` then `prawn-l390` — the second command ran on the
jump host, not the target. Any result collected that way is unproven
until the hostname in the same session matches the intended machine.

Transport gotchas, verified live 2026-11-28 (see the T5 dry-run file
for the full record):
- Windows `cmd`: `set VAR=value & command` puts a trailing space in
  the value — write `set VAR=value&command`, `&` immediately after the
  value, or every record fails host-truth as unproven.
- `ssh` inside a `while read` loop consumes the loop's stdin and kills
  the loop before the last machine runs — give `scp`/`ssh` there
  `< /dev/null`.
- `cmd` does not split on `;` — use `&` as the separator.
- Windows probe output is CRLF — strip `\r` before comparing hostnames.

## Config paths (resolved live 2026-11-28, hostname-proven)

Paths are relative to `$HOME` (Linux) / `%USERPROFILE%` (Windows).
`MISSING` means measured absent on that date, not guessed.

| File | VM | L390 | 3410 | T14 | E14 |
|---|---|---|---|---|---|
| `.config/opencode/opencode.jsonc` | present | MISSING | MISSING | present | present |
| `.config/opencode/model-fallback.json` | present | present | present | present | present |
| `.codex/config.toml` | present | present | present | present | present |
| `.codex/models_cache.json` | present | present | present | present | present |
| `.codex/AGENTS.md` | MISSING | MISSING | MISSING | present, 0 bytes (empty) | present, 161 bytes |
| `.omo/omo.jsonc` | present | present | present | present | present |
| `.config/theprawnskills/library.json` | present | present | present | MISSING | MISSING |
| `Projects/forge/AGENTS.md` | MISSING | MISSING | present | present | MISSING |
| `AGENTS.md` (home) | present | present | present | present | present |
| `.gemini/config/` | present | present | UNKNOWN | present | present |
| `.gemini/skills/` | present (25 arkcli-*) | MISSING | UNKNOWN | MISSING | MISSING |

Corrections to the spec: `~/.gemini/config/skills/` exists on NO machine
(measured all five); the real skills dir is `~/.gemini/skills/` (VM
only) and the real config dir is `~/.gemini/config/`. `~/.codex/AGENTS.md`
exists only on Windows, and T14's copy is empty. `opencode.jsonc` is
missing on L390 and 3410 (binary is present there) — a MISSING file is
an outlier, never a pass. Full hashes: see the T2 record in
`~/workspace/muse-upgrade-backlog/specs/18-fleet-parity-dryrun.md`.

## Report template

```text
Fleet parity — <change> — <date>
- DONE — VM: <resolved primary>, fallbacks <...>, fresh session <model>
- NOT DONE — L390: <field> differs: <value> vs <baseline>
- NOT DONE — 3410: <field> <reason>
- BLOCKED — T14: <reason>
Still open: <list, or "nothing open">
Checks run: diff <files> / resolved config / fresh session.
Zero-change wording: "no changes detected by these checks".
```

Lead with done/not-done per machine, then resolved primary, fallback
entries, fresh-session result. Partial results are labelled incomplete,
never presented as a gate.

## Dry run (T5, GitHub identity 5/5)

Reconstructed 2026-11-28 against the 25 Nov change: global identity
passes on all five machines; the repo-level local overrides surface as
NOT DONE, not hidden (VM `theprawnskills` email without the 66017805+
prefix; L390 `patreonalive` name "b"; L390 `healthkaki-pov` name
"Bryan"). Fresh-session proof was never run for that change, so no
machine is marked DONE in the dry run. Full per-machine report:
`~/workspace/muse-upgrade-backlog/specs/18-fleet-parity-dryrun.md`.

## Known not-covered

- Fresh-session proof needs a visible Herdr pane per machine — manual
  dispatch, not scripted. A file-check-only report never claims it.
- Windows version records carry `value: null` when the tool is a
  wrapper with no FileVersion (present, version not probed).
- Codex model has no fleet standard on file (live 2026-11-27: VM
  luna/medium, L390 terra/high, 3410 terra/high, T14 luna/low, E14
  terra/xhigh) — the differ reports cross-machine outliers only; do not
  invent an expected value.
- `models_cache.json` is a live cache, not config — its hash drifts
  between runs (observed 2026-11-28: L390 and 3410 hashes changed
  between two runs minutes apart). A models_cache-only diff is
  informational, not a parity failure.
- 3410 repo drive lives under /media, not ~/Projects — the default
  git-drift sweep covers only ~/Projects; pass REPO_ROOT=<drive path>
  to sweep the repo drive (read-only; never fix bugs there).
- Live divergences are reported, not fixed, by this skill. The
  2026-11-27 full-fleet run found 14 diff fields; see
  `fleet-config-verification` SKILL.md "Known not-covered".

## Evidence contract

Per `verification-loop`: PASS / FAIL / SKIPPED (reason) / UNAVAILABLE
(prerequisite) / NOT APPLICABLE (reason) per check. A required check that
is SKIPPED or UNAVAILABLE leaves readiness unverified; it is never turned
into PASS. Verify against the real artifact, not a proxy, a self-report,
or "it compiles". A zero exit code with zero collected checks is not
coverage.
