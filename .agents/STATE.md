# Daily visual explanations rollout

- User approved a new daily skill: restrained dark theme with one accent;
  use HTML for most explanations where a visual helps, even short answers;
  predictable visual overview -> details -> next steps.
- Created visual-explainer with a dark/cyan template, accessible context and
  sequence views, diagram guidance, Mermaid examples/config, and an HTML checker.
- Connected Postplan and both routers; daily profile is now 65 skills. Existing
  Windows installation copies will be backed up before the selected updates.
- Native Windows standalone installation tests pass with the new skill assets.
  Browser/diagram checks, publication, OneDrive delivery, and remote installs
  are in progress. Both registered remote Windows machines are reachable.
- Added a targeted Windows sync script: default preview, source hash checks,
  dated backups outside OneDrive, no remote canonical writes, no skill pruning.

## Earlier migration and audit context

Standalone Windows, macOS, and Linux setup is published without requiring
OneDrive. The original skill library and daily profile are preserved.

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
- Published the standalone extension as `6d6b0d9`. Fresh-checkout CI passed on
  Windows, macOS, and Linux:
  https://github.com/hongyime/theprawnskills/actions/runs/34296940092
  Windows executes 9 tests and skips 13 POSIX symlink cases; macOS/Linux run
  all 22 cases. Native Windows verification also passed in an isolated home.
- Original skills tree still matches 0c6ba7f exactly; the daily profile is
  unchanged. Target machines can now follow README.md; no target VM or other
  physical machine was configured during this work.
- Optional next step only if the owner chooses: private visibility plus a
  matching override in sourcerepo's repos.yml. Do not run org-wide sync.

## Postplan reference audit

- Searched all 216 canonical skill definitions, matching repo sources,
  installed Codex/Claude/Cursor skills, and 106 cached plugin definitions.
- Seven skills name Postplan: postplan-upload, to-spec, to-tickets, wayfinder,
  competitive-upgrade, skill-router, and skill-cleanup. The uploader additionally
  names repo-standardization as a source of compliance reports.
- The uploader creates standalone HTML and invokes npx postplan upload; its
  broad planning/audit/review triggers can match without an explicit handoff.
  Router/default-profile/cleanup rules keep it in the daily installation.
- Followed indirect planning references; distinguish workflow handoffs from
  related-skill lists and unrelated HTML generators. Installed routers have
  older non-Postplan entries, but their Postplan guidance matches canonical.
- Audit only: no skill changes, installations, or uploads were performed.
