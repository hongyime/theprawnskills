# Standalone installation and transfer documentation

Extending the published Linux setup to standalone Windows and macOS, without
OneDrive. Preserve the original skill library and daily profile.

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
- Recovery and installer published as `62cbd1f` on main. GitHub's recursive
  tree confirms 2,165 original skill files and 216 skill definitions.
- Fresh-checkout Linux CI passed:
  https://github.com/hongyime/theprawnskills/actions/runs/34293975375
- `README.md` contains clone/install/update commands and the Codex prompt.
  Actual installation on the user's target VM is performed with those commands;
  validation here used Linux containers and GitHub CI.
- Existing installed skills and OneDrive skill contents remain unchanged.
  Both local checkout remotes now point directly to hongyime/theprawnskills;
  the OneDrive checkout's origin was corrected and verified after the transfer.
- Added Windows managed copies, preserving unmanaged skills and local edits.
  Copy updates move the old copy to a dated backup before replacement.
  macOS/Linux keep symlinks; existing installation types remain supported.
- Generalized the seven maintenance variants to standalone use on all three
  OSes, retaining their platforms/linux paths for existing symlink compatibility.
- README now includes Windows/macOS/Linux setup and updates without OneDrive,
  an any-machine Codex prompt, transfer remediation, and an optional private
  visibility procedure. The repo remains public; no visibility change was made.
- Native Windows tests passed: 9 executed, 13 POSIX symlink cases skipped.
  CI now covers Windows, macOS, and Linux; fresh-checkout results pending.
- Next: publish this extension, verify the three CI jobs, and record the result.
