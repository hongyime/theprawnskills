# Installed skill refresh — 2026-09-27

The owner requested installed skills on E14, L390, and T14 be refreshed from
main. The 65-skill profile is unchanged. All seven registered agent roots pass
file verification against skill content from `74355d2`; 216 separate skill
copies were refreshed, and all 213 replaced copies have verified backups.

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
  the combined report. Replaced copies remain under `~/Backups/2026-09-27/skills/`.

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
