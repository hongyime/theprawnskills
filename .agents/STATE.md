# ECC second wave — 2026-09-27

Skills delivered; live-agent pilot limitations remain recorded. Owner approved
proceeding with the reviewed second-wave plan:
API contracts, codebase onboarding, detailed ADRs, then a bounded orchestration
pilot and selective agent review lenses. Keep 65 daily skills; publish tested
source through main and OneDrive, with local T14 copy verification. Other-machine
delivery continues under the owner's OneDrive assumption.

Implementation starts from 38b8bb5 and preserves the intervening privacy fix.
Four on-demand additions and CLI/routing integrations are delivered at e0479fc.
Three-OS CI 36302727616 passed: 99 Python cases with platform/browser skips,
plus four React and four Chromium cases per OS. Security jobs passed.
OneDrive: 2,256 tracked skill files match tested Git content after line-ending
normalization; its router matches plus the separately added local Orca row.
T14: 12 affected daily skills refreshed (12 files exact, one router merge
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
CRLF/LF normalization. Six affected T14 daily copies: 41 files match source
SHA-256 exactly. Four new skills are readable on demand through the shared
library; no new backup copies were created. Automatic approval review blocked
cleanup of three temporary test folders. Earlier T14 Chromium shutdown delays
remain recorded separately from the clean final Windows CI result.

First-wave next step was owner review; the owner has now approved proceeding.

# Installed skill refresh — 2026-09-27

The owner requested installed skills on E14, L390, and T14 be refreshed from
main. The 65-skill profile is unchanged. All seven registered agent roots pass
file verification against skill content from `74355d2`; 216 separate skill
copies were refreshed. After another successful installed-file verification,
the owner requested cleanup and all 213 old backup copies were removed.

- E14: Codex, Claude, and Cursor pass. L390: Codex and Claude pass. T14: Codex
  passes; Claude's existing shared-library link is preserved and verified.
- Full Git snapshots outside OneDrive pass all 2,219 skill-file hashes and the
  resource audit on each machine. All four handoff commands start successfully.
- T14's missing Git object was recovered by a fresh fetch, and its OneDrive
  checkout was fast-forwarded without discarding local files. L390's eight
  shared handoff files match the updated source. E14's shared OneDrive copy
  returns cloud-read errors for the new files; do not mark that source synced.
- Installed-copy refreshes used the verified Git snapshot when OneDrive was
  delayed. No remote canonical folders or existing shared-library links were
  replaced. For E14 handoffs, use the verified snapshot until OneDrive is fixed.
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
