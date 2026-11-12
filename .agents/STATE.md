# Hill-climb skill created (on demand, uncommitted) — 2026-11-11

- New skill `hill-climb` in `skills/hill-climb/SKILL.md`, based on Theo's
  `council` (t3dotgg/tstack), generalised from UI-only to any scoreable
  goal. Judges: agy (implementer first) + Codex (critic), 3rd judge
  deterministic. Defaults: threshold 9/10, max 8 rounds, plateau 2.
- Debian/Linux addendum in the skill: library clone paths resolve from library.json; `~/.agents/skills`, Python installer.
  Windows/OneDrive text preserved. Not added to `default-profile.toml`.
- INDEX.md regenerated (227 top-level, 244 definitions), router route
  added, validations pass: quick_validate, index check, text safety 0,
  resource audit Missing 0, installer dry-run 66 selected / 0 changes.
- v1.1.0 (2026-11-12): fallback ladder + walkthrough mode added per
  the user's concern — see skill. No scores invented, no silent substitution.
- v1.2.0 (2026-11-12): Codex audit verdict NEEDS FIXES 7.5/10, 4 blockers
  fixed (score aggregation, no-delegate self-review, fleet paths,
  walkthrough defaults). Report: ~/workspace/hill-climb-audit-codex-20261112.md.
- v1.3.0 (2026-11-12): de-fleeted per the user — no machine names, personal
  paths, provider balances, or "Bryan"/"fleet" in the skill. Grep clean.
- v1.4.0 (2026-11-12): agy audit NEEDS FIXES 8.0/10, all findings fixed
  (ONE model judge, not two; plateau = stop, escape is a user menu; git
  checkpoint/revert; baseline must be scored; drift every 3rd round;
  headless ban scoped to fleet work). Reports in ~/workspace.
- v1.5.0 (2026-11-12): Codex third check NEEDS FIXES 8.2/10, all fixed
  (baseline gate-first, drift re-anchor, degraded exception, scoped git
  commands, stale wording). Report: ~/workspace/hill-climb-audit-codex-v140-20261112.md.
- STATE.md / JOURNAL.md scrubbed 2026-11-12 (machine names → generic
  roles, personal paths removed, grep clean).
- Pulled 2026-11-12 15:42 SGT: HEAD 04477d5 (Bryan's hardening commit).
- Verified READY by Muse 2026-11-12 against the Codex third-check
  findings (all 5 fixed, full consistency sweep clean). Committed to
  main and pushed to origin/main on the user's word.

# Full fleet agent replication and dedicated root rollout — 2026-11-02

- Replicated all 66 profile skills to dedicated agent roots across the entire fleet:
  - Linux: symlinked 66 profile skills into `~/.claude/skills`, `~/.codex/skills`,
    and `~/.config/opencode/skills`, while preserving existing custom skills (`arkcli-*`)
    and internal system directories (`.system`).
  - Windows: copied 66 profile skills into `.cursor\skills` and `.config\opencode\skills`
    across all nodes, matching existing `.claude` and `.codex` roots.
- Updated `audit_fleet_skills.py` to audit dedicated OpenCode roots on Windows.
- Verified fleet-wide audit: all 4 online nodes show 100% OK (66/66) across all
  agents (Shared, Codex CLI, Claude Code, Cursor, OpenCode, Kiro).
- 0 broken skills, 0 missing profile skills across all nodes.

# Fleet skill verification and Windows Kiro junction repair — 2026-11-02

- Repaired Kiro skill discovery on Windows fleet nodes: replaced individual per-skill
  junctions with a single direct junction to the canonical OneDrive skills library
  (`OneDrive\01 SKILLS\.agents\skills`), matching OpenCode's architecture.
- Resolved NTFS "untrusted mount point" errors and corrupted reparse point issues.
- Filtered internal agent dot-directories (e.g. `.system`) in `audit_fleet_skills.py`
  and removed orphan empty directory under `.codex/skills`.
- Verified all online fleet nodes: 0 broken skills, 66/66 daily profile skills
  present and valid across OpenCode, Codex CLI, Claude Code, and Kiro.
- All repositories fast-forwarded to main (`aa5a527`).

# Fleet skill audit and generic verification — 2026-11-02

Delivered `fleet-skill-audit` skill and portable `scripts/audit_fleet_skills.py`.
Provides generic, fault-tolerant verification of agent discovery roots (OpenCode,
Codex, Claude Code, Kiro, Cursor, DeepSeek) without requiring agent logins.
Supports dynamic network discovery and anonymizes node names and IPs by default.
Registered in `skills/skill-router/SKILL.md` and updated `INDEX.md`.

# Add project-transfer skill — 2026-11-02

Delivered new canonical skill `project-transfer` under `skills/project-transfer/SKILL.md`.
Added to `default-profile.toml` (under core coding workflow) so machines running
`scripts/install_skills.py` deploy it automatically to configured agent roots.
Added discovery route in `skills/skill-router/SKILL.md` and regenerated `INDEX.md`.
Verified with `quick_validate.py`, `update_skill_index.py --check`, `audit_text_safety.py`
and `audit_skill_resources.py` (242 definitions, 1,682 Markdown files checked, 0 errors).
Fleet rollout complete: pushed to origin/main (`363ac71`), deployed and verified across
active Linux and Windows fleet nodes.

# ECC second wave — 2026-09-27

Skills delivered; live-agent pilot limitations remain recorded. Owner approved
proceeding with the reviewed second-wave plan:
API contracts, codebase onboarding, detailed ADRs, then a bounded orchestration
pilot and selective agent review lenses. Keep 65 daily skills; publish tested
source through main and OneDrive, with local copy verification on the Windows daily laptop. Other-machine
delivery continues under the owner's OneDrive assumption.

Implementation starts from 38b8bb5 and preserves the intervening privacy fix.
Four on-demand additions and CLI/routing integrations are delivered at e0479fc.
Three-OS CI 36302727616 passed: 99 Python cases with platform/browser skips,
plus four React and four Chromium cases per OS. Security jobs passed.
OneDrive: 2,256 tracked skill files match tested Git content after line-ending
normalization; its router matches plus the separately added local Orca row.
Windows daily laptop: 12 affected daily skills refreshed (12 files exact, one router merge
verified); all 65 profile entries resolve. Preserved 12 local Orca files and
their uncommitted state/index changes. Private machine inventory moved to its
ignored override. No new backup copies; temporary merge stash removed.
tmux/dmux launched in isolated Ubuntu WSL. Live Codex repair stopped no-progress
after a host command-runner failure; Claude handoff is blocked by expired OAuth.
No unattended schedules or blanket agent registration. See
docs/audits/2026-09-27-ecc-second-wave.md for pilot boundaries and delivery status.

# Orca skill installation — 2026-09-27

Owner requested four official Orca skills and preservation of the existing
library conventions. Added computer-use, orchestration, orca-per-workspace-env,
and orca-cli from stablyai/orca revision
90bae01db930f11951f75cb28f2da54c2b8b4b9b, with original discovery stubs,
MIT licenses and source hashes. All four version-matched guides respond in the
installed Orca runtime. Keep the 65-skill daily profile and existing links;
this is a targeted local addition, not a fleet refresh. Local Codex copies and
the existing shared-library links verify against the staged source hashes.
The 2,228 pre-existing skill files other than the router are unchanged; the
router adds one Orca route. All three registry files are byte-identical.
Metadata/index validation passes; text safety finds zero issues; the resource
audit checks 232 definitions, 1,664 Markdown files and 2,569 references with
zero missing references and zero stale exceptions. Other-machine delivery is
not verified. Preserve all prior handoff records below.

# ECC selective adoption — 2026-09-27

Completed and delivered. Owner approved four on-demand additions (verification-loop,
python-testing, react-testing, homelab-pihole-dns), browser-testing improvements,
skill evaluation/discovery improvements, and index/CI fixes. Keep the daily
profile at 65. Adapt from ECC revision e482e579415fde18357cafce70f177ae19fd7f03;
preserve attribution and validate all bundled dependencies.

Publish tested changes to main and the local OneDrive library. The owner's
latest instruction delegates other-machine delivery to OneDrive: do not retry
remote installs or claim a new remote verification. API contracts, onboarding,
ADRs, autonomous loops, tmux/dmux and the agent roster were research/plan only
in the first wave; the later second-wave authorization above supersedes that.

Four skills and three improvement batches are implemented; daily profile is 65.
Executable revision b9bb28c passed three-OS CI run 36298257310: 74 Python cases
on Linux/macOS, 58 on Windows with 16 POSIX skips, plus four React and four real
Chromium cases on each OS. Metadata/index/text/resource and security jobs pass.
Independent review repairs include malformed YAML handling, async assertions,
server cleanup and macOS loopback fixture startup.
See docs/audits/2026-09-27-ecc-adoption.md for exact failures and test boundaries.
See docs/plans/2026-09-27-ecc-second-wave.md for the three next skill proposals,
bounded loop/tmux/dmux pilot and all 68 upstream agent role mappings.

OneDrive source: 2,236 tracked skill files match tested content after existing
CRLF/LF normalization. Six affected daily copies on the Windows daily laptop: 41 files match source
SHA-256 exactly. Four new skills are readable on demand through the shared
library; no new backup copies were created. Automatic approval review blocked
cleanup of three temporary test folders. Earlier Chromium shutdown delays on the Windows daily laptop
remain recorded separately from the clean final Windows CI result.

First-wave next step was owner review; the owner has now approved proceeding.

# Installed skill refresh — 2026-09-27

The owner requested installed skills on the Windows work laptop, the Debian dev machine, and the Windows daily laptop be refreshed from
main. The 65-skill profile is unchanged. All seven registered agent roots pass
file verification against skill content from `74355d2`; 216 separate skill
copies were refreshed. After another successful installed-file verification,
the owner requested cleanup and all 213 old backup copies were removed.

- Windows work laptop: Codex, Claude, and Cursor pass. Debian dev machine: Codex and Claude pass. Windows daily laptop: Codex
  passes; Claude's existing shared-library link is preserved and verified.
- Full Git snapshots outside OneDrive pass all 2,219 skill-file hashes and the
  resource audit on each machine. All four handoff commands start successfully.
- the Windows daily laptop's missing Git object was recovered by a fresh fetch, and its OneDrive
  checkout was fast-forwarded without discarding local files. the Debian dev machine's eight
  shared handoff files match the updated source. the Windows work laptop's shared OneDrive copy
  returns cloud-read errors for the new files; do not mark that source synced.
- Installed-copy refreshes used the verified Git snapshot when OneDrive was
  delayed. No remote canonical folders or existing shared-library links were
  replaced. For the Windows work laptop handoffs, use the verified snapshot until OneDrive is fixed.
- Local evidence and snapshot on each machine:
  `~/Backups/2026-09-27/skills-main-refresh/`. The initiating machine retains
  the combined report and per-machine cleanup records. Working Git snapshots
  remain available; the obsolete copies under the separate `skills/` backup
  directory were deleted at the owner's request.

# Skill resource repair — 2026-09-26

Current task: complete. Repairs are published to main (`b2d1a70`, `8fde37a`).

- Audited 224 skill definitions and 1,631 baseline bundled Markdown files (plus
  the platform overview in independent review). Addressed 60
  findings; current scan checks 1,650 files and 2,551 references with zero unresolved
  missing references, 16 documented contextual exceptions, and zero stale entries.
- Implemented four handoff commands, supporting code and guides, six preset helper
  copies, and three portable Cavecrew prompts. Restored 12 MIT-licensed upstream
  resources and authored four local review guides. External Caveman/OpenCode setup
  remains a documented prerequisite rather than an implied installed capability.
- Verification: 53 local tests, 37 passed and 16 platform-specific skips, zero
  failures. Native PowerShell and Git Bash wrappers use fake CLIs; handoff tests
  use real disposable Git projects. Independent reviewers cleared the repairs;
  the handoff reviewer passed 14 extra assertions and eight alias-fix checks.
  CI found a temporary-directory alias bug on macOS/Windows, now fixed.
  Final CI passed all 53 tests on Linux/macOS and 37 with 16 POSIX skips on Windows:
  https://github.com/hongyime/theprawnskills/actions/runs/36224710255
- Report: `docs/audits/2026-09-26-skill-resources.md`; all baseline findings have
  dispositions in the adjacent JSON register. Resource audit and three-OS CI pass.
  Existing X-drive and OneDrive checkouts and machine installations are preserved.

# Portfolio review — 2026-09-10

Installer/profile source review and both core Python syntax checks passed. The current Windows suite ran 22 tests: nine passed and thirteen Unix symlink cases were skipped. Verification used temporary homes, including install/update/repeat checks for the actual 65-skill profile; installed agent directories were not changed. The repository still has the `no-config-sync` topic. Keep its library and current opt-out intact.

The older remote-machine rollout notes below remain unresolved; this portfolio check did not retry remote installation or validate every referenced provider tool. Current source is a local skill library/installer, not a Supabase or Vercel application.

# Daily visual explanations

- Published `visual-explainer` in commit `254f727`: restrained dark/cyan style,
  proactive visuals even for short explanations, and visual overview -> details
  -> next steps. Shared assets own the style; Postplan and both routers use it.
- Library now contains 207 top-level skills, 217 skill definitions, and 65 daily
  selections. All 2,165 original skill files remain; no skills were deleted.
- The OneDrive source checkout received the new skill through Git. The current
  Windows machine's Codex, Claude, and Cursor copies match the four selected
  sources; each installed daily profile contains 65 skills. Previous copies
  were archived in dated backups outside OneDrive.
- Remote rollout is incomplete: one registered machine has not received the new
  OneDrive source; the other times out over SSH. Neither remote installation
  was changed. Retry the documented selected-skill sync after source delivery
  and connectivity recover. Do not overwrite remote canonical folders.
- Fixed Windows SSH helper transport using SCP plus SHA256 verification instead
  of waiting for stdin EOF. Remote execution reports missing source cleanly;
  local preview, repeat application, and backup preservation were verified.
- Native Windows and fresh-checkout Windows/macOS/Linux installation tests pass:
  https://github.com/hongyime/theprawnskills/actions/runs/34305986010
  Windows runs 9 tests and skips 13 POSIX cases; macOS/Linux run all 22.
- HTML structure, desktop/mobile rendering, switcher, no-JavaScript fallback,
  and absence of external runtime resources were checked. Axe reported no
  violations with SVG contrast requiring manual review. Three Mermaid examples
  rendered; a separate class-example browser check encountered local launch issues.
- Standalone machines use Git pull plus the Python installer. OneDrive carries
  shared source files and the Windows helper refreshes separate agent copies.
  No scheduled background updater was installed. README contains setup, update,
  and Codex handoff instructions for Windows, macOS, and Linux.

## Repository protection and earlier work

- Recovery `62cbd1f` restored the original library after organisation cleanup.
  Preserve the GitHub topic `no-config-sync`; never run that cleanup here.
- Standalone installation on all three operating systems was added in `6d6b0d9`.
  Original management variants remain in platforms/linux for link compatibility.
- Both local checkout remotes point to hongyime/theprawnskills. Repository
  visibility is unchanged; changing it requires a matching sourcerepo override.
- Earlier Postplan audit found seven direct skill references and a reverse
  reference to repo-standardization. This task adds visual-explainer integration.
- JOURNAL.md and Git history retain the earlier migration and audit decisions.

---
## 2026-09-16 - baseline review batch-a
- Health: main HEAD 08f16d5 after fast-forward. git status clean.
- Open PRs: #5 (Dependabot: trufflehog action bump). Open issues: 0.
- pnpm audit: 26 vulns (1 critical vitest <3.2.6, 15 high, 9 moderate, 1 low) - ALL in dev-only paths (vitest tree, esbuild). Runtime deps (graphology*) clean. Critical vitest advisory GHSA-5xrq-8626-4rwp requires UI server exposed to attacker; not applicable in CI/local test runs.
- Semver ranges (^3.1.0) already permit patched vitest >=3.2.6; lockfile is stale. Deferred: lockfile is sourcerepo-managed (last touched by post-recovery snapshot 5c8ef90). Update should flow through sourcerepo, not this target.
- Free-tier surface: none. Skill library, no Vercel/Supabase.
- Next safe steps: file issue in sourcerepo to refresh pnpm-lock.yaml (bumps vitest, postcss/nanoid, esbuild transitives).

## Privacy-safe machine examples - 2026-09-27

Keep machine-specific inventory in an ignored private override, with disabled public examples and packaging exclusions. Preserve the current skill catalog, profile and newer provider-auth instructions. No fleet installation or registry-based synchronization ran.

## Current task — 2026-11-12

Hardened the fleet audit, legacy PowerShell installer, and bot merge gates. The
audit copies remain byte-identical; local host naming and remote path masking
are corrected; linked installer roots/destinations are skipped. Bot workflows
now wait for `Skill library` and use protected auto-merge. Focused regressions,
library integrity gates, and a fresh read-only 4/4 fleet audit pass.

<!-- MOLT_AUTO_START -->
## Auto State

- Updated: 2026-11-12 15:13:23 +08:00
- Machine: Windows daily laptop
- Harness: codex
- Event: session-start
- Branch: main
- HEAD: 6e61c4a
- Dirty files: 0
- Resume hint: Read .agents/STATE.md, then the latest file in .agents/handoffs/ if present.
<!-- MOLT_AUTO_END -->
