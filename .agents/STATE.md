# Current work

Preparing Linux installation while preserving the original Windows library.

- Base library: commit `0c6ba7f`, 206 top-level skills, 64 profile entries.
- Upstream `ae84bdb` removed all 2,165 tracked files in `skills/` during
  organisation config sync; newer upstream commits retain that deletion.
- Recovery branch preserves the original library and integrates upstream
  configuration without checking out the deleted tree.
- Use repository topic `no-config-sync` to prevent repeated deletion.
- Visibility is a separate decision; the source settings workflow defaults
  repositories to public unless `repos.yml` specifies private.
- Applied and verified the `no-config-sync` topic; current remote sync code
  checks that topic before cleanup. Visibility remains an owner decision.
- Added Linux installer, seven management/discovery variants, setup commands,
  Codex handoff prompt, and a Linux CI workflow.
- All 14 Linux container tests pass. All 2,165 original skill files match the
  OneDrive content; 445 differ only in line endings. The default profile is
  unchanged. A bounded token/private-key pattern scan found no matches; this
  is not a full historical security audit.
- Next: commit and publish the recovery, then verify GitHub's main branch and
  provide the setup commands. No Windows installation or OneDrive files have
  been changed. Visibility remains public pending an explicit owner choice.
