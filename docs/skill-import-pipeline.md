# Skill-import pipeline

Date: 2026-11-28
Author: Muse (spec 14, Wave 2)
Status: APPROVED spec, pipeline live for the next import
Spec: `~/workspace/muse-upgrade-backlog/specs/14-pinned-audited-skill-import-pipeline.md`

Every skill import into `theprawnskills` passes this pipeline before it lands
on `main`. The pipeline produces evidence, not a verdict: a human (Bryan, or
a vet he names) makes the allowlist call. No skill lands without a decision
row. No import is rolled out fleet-wide before the quarantine-pane vet has
recorded its verdicts.

Precedent import: 38 security skills from 4 repos, 2026-11-25, commit
`dd6b658` in `hongyime/theprawnskills`. Its review files
(`~/workspace/skill-imports/review-{strix,ctf-skills,pentest-skills,awesome-skills-security}.md`)
are the template for the import record. The dry run that proved this
pipeline reproduces those 38 decisions is
`~/workspace/skill-imports/dry-run-20261127/dry-run-record.md`.

## Invariants (V1–V7)

- **V1.** No skill is committed without a pinned source SHA recorded in its
  import record.
- **V2.** No skill lands on `main` without an allowlist decision row
  (import / import-with-fixes / reject) in the import record.
- **V3.** No import is rolled out fleet-wide before the quarantine-pane vet
  has recorded its verdicts.
- **V4.** A skill with an unresolved grep finding (script / credential read /
  network call / callback URL) never lands as "import as-is".
- **V5.** Licence and authorship metadata of an imported skill are never
  relabelled; unlicensed or proprietary material is recorded as-is with
  Bryan's decision noted.
- **V6.** Installed copies under `~/.agents/skills` are never edited by hand;
  edits belong in the clone, then `install_skills.py --apply` + `--check`.
- **V7.** "Committed" and "rolled out" are recorded as separate states; a
  claim of rollout must name the per-machine `--check` evidence.

## Stages (in order, each leaves evidence)

### 1. Intake + pin

Clone the source repo read-only under `~/workspace/skill-imports/<repo>`
(existing convention). Record repo URL + exact commit SHA in the import
record. Verify the clone is at the pinned SHA before any further stage:

```bash
git -C ~/workspace/skill-imports/<repo> rev-parse HEAD
```

Pinned SHAs from the last import, verified live 2026-11-27:

| repo | SHA |
|---|---|
| strix | `935f82350782cdf15d70cbcb3e6d7e48f49071c2` |
| ctf-skills | `20d182d9377f0467830f314bb0f843cae4dbf55e` |
| pentest-skills | `616feed88d5340ae64a49fc0416861cf7ed648d2` |
| awesome-skills-security | `ae26985eb60c2b9e1f1b95f7af0e5c438ff85e6d` |

Evidence: the import record's pinned SHA + the `rev-parse` output.

### 2. Diff

If a previous pin exists, produce the diff between pins and review the diff,
not just the final tree. First import of a repo: mark "no previous pin" and
review the full skill set.

```bash
git -C ~/workspace/skill-imports/<repo> diff <old-sha> <new-sha> --stat
```

Evidence: diff summary in the import record (files changed, skill dirs
added/removed/changed).

### 3. Static grep audit

Run the deterministic audit over the pinned clone:

```bash
cd ~/workspace/theprawnskills
python3 scripts/skill_import_audit.py --source ~/workspace/skill-imports/<repo> \
  --json /tmp/audit-<repo>.json
# exit 1 while any finding is undispositioned; exit 0 when all are dispositioned
```

Six pattern kinds, each a finding with file + line + disposition
(fix / waive-with-reason / reject):

| pattern | what it flags |
|---|---|
| `script` | executable scripts (`scripts/`, `*.py`, `*.sh`, `*.ps1`, `*.js`, `*.ts`) and binaries (ELF/PE/ZIP/SWF magic, or undecodable bytes) |
| `shell-bang` | lines starting with `!` in SKILL.md / reference Markdown (Claude-style `!command` execution) |
| `allowed-tools` | every `allowed-tools` entry in a SKILL.md frontmatter (values are listed for review; `quick_validate` only allows the key, it never vets the values) |
| `network` | network-call keywords (`curl`, `wget`, `fetch(`, `requests.*`, `urllib`, `socket`) and absolute URLs in Markdown |
| `credential` | credential reads (`os.environ` / `os.getenv` / `process.env` / credential-named `$VAR`s) and literal credential assignments (`api_key` / `token` / `secret` / `password = "..."`) |
| `callback` | absolute URLs inside script files — the exfiltration-callback pattern (a payload default that phones a third-party host) |

Placeholder hosts and placeholder credential values are never findings:
`example.com/.org/.net`, `*.example.*`, `localhost`, `127.0.0.1`, RFC1918
addresses, and values like `<token>`, `redacted`, `changeme`, `CHANGE THIS`.

Dispositions live in a JSON file (`{id: {action: fix|waive|reject, reason}}`),
one per repo import, kept with the import record. Finding IDs are a stable
hash of (relative path, kind, normalized match) — line numbers are NOT in
the ID, so a disposition survives edits that shift lines. Re-run with
`--dispositions` until exit 0:

```bash
python3 scripts/skill_import_audit.py --source ~/workspace/skill-imports/<repo> \
  --dispositions ~/workspace/skill-imports/dry-run-20261127/dispositions-<repo>.json \
  --json /tmp/audit-<repo>-disposed.json
```

Determinism: two runs over the same tree produce byte-identical JSON
reports (verified 2026-11-28 on ctf-skills, 945 findings). The audit is
stdlib-only, no network.

Known limitation (recorded 2026-11-28, do not work around by hand): the
stage-3 patterns do NOT catch an unpinned package-manager invocation in
Markdown, e.g. `npx @playwright/mcp@latest` found by the ctf review in
2026-11-25. The quarantine-pane vet (stage 5) is the backstop for that
class; a future audit extension would add an `unpinned-install` pattern.

Evidence: the audit JSON + the dispositions file, both referenced from the
import record. An unresolved finding never lands as "import as-is" (V4).

#### T2 gap audit (2026-11-28, why this script exists)

Stage-3 patterns vs the pre-existing scripts, read from source:

| pattern | covered by existing script? |
|---|---|
| executable scripts / binaries | GAP — `audit_skill_resources` checks references exist, not content |
| shell-execution `!` markers | GAP |
| `allowed-tools` entries | PARTIAL — `quick_validate` (`skills/skill-creator/scripts/quick_validate.py`) allows the key, never vets the values |
| network calls | GAP |
| credential reads | GAP |
| exfiltration callbacks | GAP — resources audit ignores URLs |

Covered elsewhere: `audit_text_safety` (hidden Unicode only),
`audit_skill_platforms` (platform-line tokens only),
`audit_fleet_skills` (fleet install state, not import content),
`quick_validate` (frontmatter keys, name kebab ≤64, description).
The new script fills only the gaps above.

### 4. House audits + SkillEvaluator

Run the existing gates and record results. Commands as run in CI:

```bash
cd ~/workspace/theprawnskills
for d in skills/<each-imported-skill>; do
  python3 skills/skill-creator/scripts/quick_validate.py "$d"
done
python3 scripts/audit_text_safety.py
python3 scripts/audit_skill_resources.py
python3 scripts/audit_skill_platforms.py
python3 scripts/update_skill_index.py --check
python3 -m unittest discover -s tests
```

SkillEvaluator Tier 1, with the house policy overlay and PII waivers
(security + dependency checks are EXCLUDED until SkillSpector is
provisioned — see `skill-checks.yml`):

```bash
skillevaluator validate ./skills --type skill --tiers 1 --no-llm \
  --checks schema,version,quality,harness,pii,license,unicode,lint,code-integrity \
  --policy ./skillevaluator-policy.yaml \
  --pii-waivers ./skillevaluator-pii-waivers.yaml \
  --continue-on-failure -r json -o <reports-dir>
```

SkillEvaluator findings are evidence, not an automatic block: its known
scanner-variance limits (documented 2026-11-22: 116/220 failing on the
security scan only through incompleteness) must be recorded, not silently
overridden. Credential checks cannot be waived (policy: remove or rotate
instead) — see `skillevaluator-pii-waivers.yaml` header.

Evidence: the command outputs + the SkillEvaluator report dir, summarized
in the import record (per-skill pass/fail, failing check names).

### 5. Quarantine-pane vet

A fresh agent session (never the session that did the import work) vets the
import in a Herdr pane, read-only on the source, against the findings list.
Vet verdict per skill: import / import-with-fixes / reject, with reasons.
This is the stage that catches what the grep patterns miss (e.g. the
unpinned `npx` invocation above) and makes the licence / live-shell /
unlicensed-repo judgement calls a scanner cannot make.

Evidence: the vet's verdicts, recorded per skill in the import record.

### 6. House-standard rewrite

Imported skills get the house treatment proven on 2026-11-25:

- metadata rewritten to house standard (`author: Local setup`,
  `version: 1.0.0`, platform line);
- licence noted as-is, never relabelled (e.g. Anthropic proprietary
  skills; unlicensed repos used as-is per Bryan's explicit call);
- live-shell / binary notes recorded (e.g. `nc.exe` was the only binary
  in the last import);
- callback URLs neutralised (e.g. blind-XSS default `evil.com` →
  `https://callback.invalid`);
- CJK / non-English content translated to English;
- installer scripts included manual-only, never auto-run (e.g.
  `scripts/install_ctf_tools.sh` — sudo + system packages).

Evidence: the commit diff itself (stage 8), reviewed before landing.

### 7. Allowlist decision

One import record per repo import, listing every skill with its decision:
import / import-with-fixes / reject, with reasons. No skill lands without a
decision row (V2). Rejects stay in the record so a later import does not
re-litigate them silently.

### 8. Commit + fleet rollout

Commit to `theprawnskills` — one commit per import (as `dd6b658` was) — push,
then roll out to all 5 machines (VM, L390, 3410, T14, E14) via the installer
and verify with `--check` on each. Rollout is a separate, recorded step —
"committed" is not "rolled out" (V7).

```bash
python3 scripts/install_skills.py --apply
python3 scripts/install_skills.py --check   # per machine
```

Do NOT run `--apply` as part of the import work itself; the fleet rollout
is a separate step after the allowlist decision. Never hand-copy into
`~/.agents/skills` (V6).

### 9. Index update

Regenerate the skill index and update `skill-router` route rows for the new
skills (as done 2026-11-14: index 228 → 257 rows for 29 new skills), so
imported skills are actually reachable:

```bash
python3 scripts/update_skill_index.py
python3 scripts/update_skill_index.py --check   # must agree before landing
```

Evidence: `--check` output ("Skill metadata, profile and INDEX.md agree.")
in the import record.

## T5 decision: `install_skills.py` needs no import mode

Assessed 2026-11-28 (read-only): `install_skills.py` accepts
`--agents/--home/--profile/--mode/--apply/--check/--dry-run` only — no
import mode, and none is added. The installer stays the rollout step only
(stage 8). Intake, pin, diff, audit, vet, and rewrite happen in the clone
and in `~/workspace/skill-imports/`; the installer never touches a source
repo. Decision: **no change** (spec default).

## T7: CI wiring

The import audit itself runs locally at import time against the pinned
clone — CI has no pinned source clone, so there is no CI path for stages
1–3, 5–6, 8. CI is the gate for stages 4 and 9:

| workflow | trigger | covers |
|---|---|---|
| `.github/workflows/skills.yml` | push to `main` on `skills/**`, `platforms/linux/**`, `scripts/**`, `tests/**`, `default-profile.toml`, `INDEX.md` | `update_skill_index.py --check`, `audit_text_safety`, `audit_skill_resources`, `audit_skill_platforms`, `unittest discover`, browser tests |
| `.github/workflows/skill-checks.yml` | PR and push to `main` on `skills/**`, policy/waivers files | SkillEvaluator Tier 1 with the house policy overlay + PII waivers (security/dependency EXCLUDED until SkillSpector) |

`unittest discover` picks up `tests/test_skill_import_pipeline.py`
automatically. The pipeline is otherwise a manual checklist (this doc +
the import-record template); CI does not run the stage-3 audit because
there is no source clone in CI to audit. Do not invent a CI path for it.

## Import-record template

`~/workspace/skill-imports/import-record-template.md` — one Markdown file
per repo import. Fields: repo, SHA, diff summary, grep findings +
dispositions, audit results, vet verdicts, allowlist decisions, commit SHA,
per-machine rollout evidence.

## Manual verification (spec check)

A reviewer who was not the author follows this doc on a fresh clone of one
of the four pinned repos and reaches the same allowlist decisions. The
2026-11-28 dry run (`dry-run-20261127/dry-run-record.md`) is the worked
example: it reproduces the 38/38 decisions from `dd6b658` with the evidence
above, and lists its divergences as pipeline bugs, not as reasons to
re-import.
