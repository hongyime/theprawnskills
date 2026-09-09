# Decisions

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
