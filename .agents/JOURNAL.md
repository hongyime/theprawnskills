# Decisions

- 2026-11-02: Replicated 66 daily skills to dedicated agent roots (Claude Code, OpenCode,
  Codex CLI, Cursor) across all Linux and Windows fleet nodes, achieving 100% OK (66/66)
  across all online agents while preserving existing custom skills.

- 2026-11-02: Resolved Windows junction traversal defects and fleet audit false positives.
  Updated Kiro discovery on Windows nodes to use a single directory junction directly
  to canonical OneDrive skills (matching OpenCode architecture, 0 broken skills).
  Filtered dot-directories (.system) in audit scripts and cleaned up orphan empty runtime directory.

- 2026-11-02: Added fleet-skill-audit skill and generic scripts/audit_fleet_skills.py.
  Supports dynamic fault-tolerant multi-agent skill verification with privacy masking.

- 2026-11-02: Pushed project-transfer to origin/main (363ac71). Deployed and
  verified across active fleet nodes.

- 2026-11-02: Added project-transfer skill to skills/project-transfer/SKILL.md,
  registered in default-profile.toml and skills/skill-router/SKILL.md, and updated
  INDEX.md. Validation suite, resource audit, and text safety checks all pass.

- 2026-09-27: Published executable ECC adoption in b9bb28c; all three OS jobs
  passed run 36298257310 after fixing the macOS loopback/zombie-group failure.
  Verified 2,236 canonical skill files with existing CRLF/LF normalization and
  exact SHA-256 equality for 41 files in six refreshed daily copies on the Windows daily laptop. Kept
  the profile at 65, created no backup copies, and preserved the existing shared
  links. Automatic approval review blocked three temporary-folder deletions.

- 2026-09-27: Implemented four approved ECC adaptations and in-place browser,
  evaluation, index and CI improvements from pinned revision e482e579. Preserved
  65 daily skills and upstream notices. Added real React/browser/helper probes,
  fixed independent review findings and recorded first-run failures honestly.
  Planned API contracts, onboarding, ADRs, bounded loops, tmux/dmux and 68 agent
  roles separately. Owner delegated other-machine delivery to OneDrive; this
  batch does not claim a new installed-copy or cloud-read verification on the Windows work laptop or the Debian dev machine.

- 2026-09-27: At the owner's request, reverified all seven installed agent roots
  and removed the 213 old copies created by the refresh (the Windows work laptop 99, the Debian dev machine 78, the Windows daily laptop 36).
  Exact deletion paths came from the rollout records and were checked before
  removal. Kept the verified working snapshots and evidence; the Windows work laptop's shared
  OneDrive issue remains a separate follow-up.

- 2026-09-27: Refreshed 65 daily skills across seven registered agent roots on
  the Windows work laptop, the Debian dev machine, and the Windows daily laptop from `74355d2`. Verified 216 updates and 213 retained backups.
  Used a hash-verified Git snapshot for separate copies because OneDrive was
  delayed; preserved shared links and remote canonical folders. the Windows work laptop's shared
  OneDrive handoff files still fail cloud reads. The local snapshot passes the
  resource audit and all four handoff command smoke checks on every machine.

- 2026-09-26: Published resource repairs in `b2d1a70` and project-path alias fix
  in `8fde37a`. CI run 36224710255 passed the resource gate and 53-test suite on
  Linux/macOS; Windows passed 37 with 16 POSIX skips. Independent review reproduced
  the alias defect and confirmed the fix. Machine installation copies were not
  refreshed; preserve the existing X-drive branch and damaged OneDrive checkout.

- 2026-09-26: Recreated portable handoff helpers and audited all 224 skill
  definitions after the owner requested repairs and publication to main. Added
  a static resource gate, exact contextual exceptions, and isolated runtime tests.
  Preserved external integration boundaries and used original local review guides
  where the retrieved upstream licence did not substantiate MIT redistribution.

- 2026-09-09: Preserve all original skill files and the existing 64-skill
  profile; provide Linux management variants separately. Protect the library
  using the existing no-config-sync topic rather than changing global cleanup.
- 2026-09-09: Linux container installation tests pass; original skill content
  is preserved. Keep visibility unchanged until the owner chooses; a private
  choice also requires an override in sourcerepo's repository settings map.
- 2026-09-09: Published recovery and Linux setup in `62cbd1f`. GitHub's fresh
  checkout passed the Linux installation suite, and the remote tree contains
  all 2,165 original skill files. Setup and handoff are documented in README.md.
- 2026-09-09: Added standalone Windows/macOS instructions at the user's request.
  Windows uses managed copies without symlink privileges; preserve local edits
  and back up old copies during updates. Keep existing variant paths compatible.
- 2026-09-09: Corrected the local OneDrive checkout's origin to the organisation
  URL and verified reachability. Document transfer, content-sync opt-out, and
  optional private visibility procedure; visibility remains unchanged.
- 2026-09-09: Published standalone installer/docs in 6d6b0d9. Fresh-checkout
  Windows, macOS, and Linux CI passed; original skills tree and profile match
  the preserved baseline. Actual remote machine installation remains user-run.
- 2026-09-09: Audited Postplan references across canonical, installed, and plugin
  skills. Found seven direct mentions and repo-standardization as a reverse
  handoff source. Reported broader planning routes without treating ordinary
  related-skill links as mandatory uploads; no skills changed or content uploaded.
- 2026-09-09: User approved visual-explainer as a daily skill: dark/cyan styling,
  proactive visual explanations including short answers, and overview/details/
  next steps. Store preferences in reusable skill assets; Postplan uses them.
- 2026-09-09: Add targeted Windows propagation with source hashes and local
  backups outside OneDrive. Standalone machines continue using Git plus the
  Python installer. Preserve originals and avoid rewriting unrelated skills.
- 2026-09-09: Published daily visual-explainer in 254f727; three-OS installation
  CI passed. Verified 65 daily skills on the current Windows machine and all
  2,165 original skill files preserved. Shared source was fast-forwarded through
  Git; replaced agent copies have dated backups outside OneDrive.
- 2026-09-09: Windows SSH stdin hung, so targeted sync now transfers and hashes
  a helper file. Real remote execution confirms missing OneDrive source stops
  before agent updates. The other registered target timed out. Report these
  pending machines honestly; retry after OneDrive and connectivity recover.

- 2026-09-10: Portfolio installer review passed nine applicable Windows tests with thirteen Unix skips and isolated temporary homes. Preserve the library and verified no-config-sync topic; remote rollout was not retried.

- 2026-09-16: Baseline review batch-a. pnpm audit surfaced 26 dev-only vulns; deferred remediation to sourcerepo since lockfile flows via sync-repo-settings. Recorded critical (vitest <3.2.6, dev-only) for the sync-source owner.

- 2026-09-27: Prepared reviewed private-inventory selection, packaging exclusions and public documentation examples without changing installed agent profiles or newer upstream skills.
- 2026-09-27: Owner approved ECC second wave: four on-demand skills, existing CLI/routing improvements and a bounded terminal/agent pilot; daily profile stays 65. Keep supervisor scope detection distinct from sandbox enforcement, preserve failed host-pilot evidence, and deliver through main/OneDrive without claiming new remote-machine verification.

- 2026-09-27: Added four official Orca discovery skills at upstream 90bae01db930f11951f75cb28f2da54c2b8b4b9b with MIT license and provenance; preserved the 65-skill profile, all three registries and existing links. Installed local Codex copies, added one router entry, and passed metadata, text-safety, resource and preservation checks. No fleet rollout.
- 2026-11-11: Added on-demand skill `hill-climb` (Theo council, generalised; agy implementer, Codex critic, deterministic 3rd judge; plateau default). Debian/Linux addendum included; Windows/OneDrive preserved. INDEX regenerated (227/244), router route added, all validations pass. Uncommitted; no fleet rollout.

- 2026-11-12: hill-climb v1.1.0 — added fallback ladder (full / 1-model degraded / 0-model / no-delegate-tool) and walkthrough mode (max 5 questions, suggested defaults, fill auth form for user, explicit go). No scores invented, no silent substitution. Validations pass.

- 2026-11-12: hill-climb v1.2.0 — Codex audit (VM, 86,651 tokens) verdict NEEDS FIXES 7.5/10; all 4 blockers fixed (score aggregation, no-delegate self-review, fleet paths, walkthrough defaults). Codex could not write its report (sandbox: only repo + /tmp writable) — Muse saved reconstructed report at ~/workspace/hill-climb-audit-codex-20261112.md. Validations pass.

- 2026-11-12: hill-climb v1.3.0 — de-fleeted per the user: no machine names, no personal clone paths, no provider credit/balance state, no "Bryan"/"Muse VM"/"fleet" in the skill. Generic wording only; library paths resolve from library.json. Grep clean, validations pass. Standing rule: skills must not expose fleet config or machine names.

- 2026-11-12: hill-climb v1.4.0 — agy audit (second opinion) verdict NEEDS FIXES 8.0/10; all findings fixed (1 model judge, not 2 — score = judge score + gate; plateau = stop, escape is a user menu; git checkpoint/revert commands; baseline must be scored, no "unscored"; drift re-score every 3rd round, >1 = report + re-anchor; headless ban scoped to fleet work only). Report: ~/workspace/hill-climb-audit-agy-20261112.md. Validations pass.
- 2026-11-12 15:01:03 +08:00 [Windows daily laptop/codex/session-start] branch=main head=6e61c4a dirty=0
- 2026-11-12 15:13:23 +08:00 [Windows daily laptop/codex/session-start] branch=main head=6e61c4a dirty=0
- 2026-11-12: Fleet-audit paths now remain readable JSON values, and legacy profile installation preserves reparse-point roots and skills. Bot merges wait for Skill library through protected auto-merge rather than bypassing branch protection.

- 2026-11-12: hill-climb v1.5.0 — Codex re-audit (third check) verdict NEEDS FIXES 8.2/10; all 4 moderate + 1 minor fixed (baseline gate-first ordering, drift re-anchor = reset baseline + best kept, degraded same-model exception qualified, git commands scoped to editable files with clean-worktree check, stale "two providers" wording). Report: ~/workspace/hill-climb-audit-codex-v140-20261112.md. Validations pass.

- 2026-11-12: hill-climb v1.5.0 verified READY by Muse (self-verification on the user's word): all 5 Codex third-check findings confirmed fixed in the file, full consistency sweep clean (single-judge everywhere, threshold / plateau / max rounds agree, no stale wording, de-fleeting clean). Committed to main on the user's word; push pending.

- 2026-11-13: Removed Orca skills from the repo (Bryan approved scope: orca-cli, orca-emulator-android, orca-per-workspace-env, orchestration, computer-use — 13 files, 5 dirs). Router rows removed (2), INDEX regenerated (227 -> 222 top-level, 244 -> 239 definitions). Validations pass (index check, text safety 0, resource audit Missing 0). Fleet-wide Orca removal now matches the repo; converges all clones on next pull. E14 pull.rebase=false set locally in both clones; stray root JOURNAL.md/STATE.md deleted on E14 + T14.
- 2026-11-14: Skill sourcing build done, uncommitted — 29 new on-demand skills (user-stories, pstack 14, design-taste-frontend, ponytail 6, tstack 7), impeccable updated 4.1.1 to 4.9.0 with async no-live default, 3 principles folded into 4 existing skills; all validations pass.
- 2026-11-14: Skill sourcing build committed + pushed as 48310f4 on the user's word; fleet sync verified (VM, L390, 3410, T14, E14 primary clones all at 48310f4, INDEX 257, clean). E14 second clone not located — open item, ask the user.
- 2026-11-14: Second clones found — live OneDrive clones at C:\Users\bryan\.agents (symlink to OneDrive\01 SKILLS\.agents) on T14 + E14. T14 OneDrive clone pulled clean to 2993050. E14 OneDrive clone STUCK: files on disk are new but git cannot write its index file (pull + reset --hard fail), HEAD still b4c63e9; needs E14 hands (close agent using it or reboot, then retry pull).
- 2026-11-14: 3410 direct-SSH note corrected — direct works with explicit flags (verified login); old 'refuses connection' was root ignoring ssh-config. E14 OneDrive clone: rename test proved .git/index is held open by another process on E14 (codex.exe running, PID 21412, no visible window); fix is reboot E14 then pull.
- 2026-11-14: E14 reboot cleared the locked index; OneDrive clone pulled clean to 2993050 then b1f3d38. Fleet fully converged: all 7 clones (VM, L390, 3410, T14 x2, E14 x2) at b1f3d38, clean. 3410 direct SSH re-verified (pull over direct connection).
- 2026-11-14: polish-repo entry-point skill built (on-demand, uncommitted) — one command chains user-stories → interrogate → correct + tdd → design-taste-frontend/impeccable → verification-loop. kun/headless checked first, neither fits. Validations pass.
- 2026-11-14: polish-repo made DEFAULT on the user's word — added to default-profile.toml (67 selected), INDEX regenerated (DAILY), installed on the VM (opencode, symlink verified). Uncommitted; fleet install pending commit + push.
