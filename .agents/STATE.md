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
