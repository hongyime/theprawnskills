# Decisions

- 2026-09-27: Refreshed 65 daily skills across seven registered agent roots on
  E14, L390, and T14 from `74355d2`. Verified 216 updates and 213 retained backups.
  Used a hash-verified Git snapshot for separate copies because OneDrive was
  delayed; preserved shared links and remote canonical folders. E14's shared
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
