# The Prawn Skills

A full skill library plus the daily profile in `default-profile.toml`.
The library contains 207 top-level skills (217 `SKILL.md` files including
nested skills), with 65 selected for daily use. The recovered originals remain
available alongside the new daily `visual-explainer` skill.

## Your daily visual standard

[`visual-explainer`](skills/visual-explainer/SKILL.md) stores the standing HTML
preferences: restrained dark styling, one cyan accent, and **visual overview ->
details -> next steps**. Use it for most answers where a visual helps, including
short explanations. Choose useful flows, UML sequence/class diagrams, C4 views,
comparisons, charts, and small interactions instead of defaulting to text/tables.

- [Reusable HTML template and example](skills/visual-explainer/templates/explainer.html)
- [Design tokens and accessibility rules](skills/visual-explainer/references/design-system.md)
- [Mermaid rendering and diagram guidance](skills/visual-explainer/references/diagrams.md)

Download/open the template locally to see the design; GitHub's file view displays
its source. `postplan-upload` reads this skill before preparing hosted documents.
The template needs no network at viewing time. Node/npm is only needed for the
optional Mermaid authoring CLI or Postplan upload, not for reading the HTML.
Task-specific generated reports stay in the task's output directory, outside
the shared skill library. Change the shared assets to change the default style.

The skill is included in `default-profile.toml`, so every new standalone install
receives its instructions, template, diagram examples, configuration, and checker.

## Install on any machine

Use a normal Git clone on Windows, macOS, or Linux. OneDrive and the existing
Windows machine registry are not required. Installation is per OS user, so it
also works on another machine where you have permission to install your tools.

- [Kali / Linux / macOS](#kali--linux--macos)
- [Windows without OneDrive](#windows-without-onedrive)
- [Existing clone after the organisation transfer](#repository-transfer-to-hongyime)
- [Prompt for Codex on any machine](#prompt-for-codex-on-any-machine)

Requires Git and Python 3.11 or newer. This installs skill instructions and
their supporting files; tools, MCP servers, credentials, and plugins used by
individual skills need their own setup. No npm install is needed for this
library's installer; the legacy root package.json is not its dependency list.

If the repo is private, authenticate with GitHub first, for example using
`gh auth login` followed by `gh auth setup-git`, or use an authenticated SSH URL.
The authenticated GitHub account must have read access. Keep authentication
local to that machine; do not copy credentials from the Windows/OneDrive setup.

### Kali / Linux / macOS

Check `python3 --version` first; it must be 3.11 or newer.

```bash
mkdir -p "$HOME/repos"
git clone https://github.com/hongyime/theprawnskills.git "$HOME/repos/theprawnskills"
cd "$HOME/repos/theprawnskills"
python3 scripts/install_skills.py --agents codex --dry-run
python3 scripts/install_skills.py --agents codex --apply
python3 scripts/install_skills.py --agents codex --check
```

The clone command is for a new checkout. If that path already exists, inspect
its Git remote and working tree, then follow the update instructions below.
If Python is too old or absent, install Python 3.11+ using your OS package
manager or the [official Python downloads](https://www.python.org/downloads/).
On macOS, do not assume the system's bundled Python meets this requirement.

### Windows without OneDrive

Install Git and Python 3.11+ first. In PowerShell:

```powershell
py -3 --version
$skillsRepo = Join-Path $env:USERPROFILE 'repos\theprawnskills'
git clone https://github.com/hongyime/theprawnskills.git $skillsRepo
if ($LASTEXITCODE -ne 0) { throw 'Clone failed; inspect any existing checkout before continuing.' }
Set-Location -LiteralPath $skillsRepo
py -3 scripts/install_skills.py --agents codex --dry-run
py -3 scripts/install_skills.py --agents codex --apply
py -3 scripts/install_skills.py --agents codex --check
```

If `py` is unavailable but `python --version` reports Python 3.11+, replace
`py -3` with `python`. Install the relevant agent separately on the new machine.
Do not run `Install-DefaultSkillProfile.ps1` for this standalone setup: that
script is for the existing OneDrive-connected Windows machines.

### What installation changes

The default mode uses symlinks on macOS/Linux and ordinary copies on Windows.
Windows therefore does not require administrator rights or Developer Mode for
symlinks. `--mode copy` also works on macOS/Linux; `--mode symlink` is available
where symlink permissions are already configured. Existing correct links or
managed copies retain their installation type.

The installer validates the whole selection before writing. Unmanaged skills
and locally edited copies cause a conflict and are preserved. An unchanged
managed copy can be updated after its previous version is moved to
`~/Backups/<date>/theprawnskills/<run>/...` (under the user profile on Windows).
The backup path is printed. If copying is interrupted, keep the backup and
inspect/restore it before resolving the partial installation; the installer
will not blindly overwrite that directory. Preview is the default mode.
No installation mode prunes other skills or removes source files.

| Agent argument | Installation location under the current user's home |
|---|---|
| `codex` | `~/.agents/skills/<skill>` |
| `opencode` | Same shared `~/.agents/skills/<skill>` location |
| `claude` | `~/.claude/skills/<skill>` |
| `cursor` | Same shared `~/.agents/skills/<skill>` location |

For example, use `--agents codex claude opencode` to select those agents.
Codex, OpenCode, and Cursor share one installed set. The full library remains in the
clone for on-demand use. Do not symlink the entire clone into `~/.agents` or
install the same profile again into Codex's legacy `~/.codex/skills` folder.
The router uses `~/.config/theprawnskills/library.json` to locate the clone.
OpenCode and Cursor also scan Claude's directory; when Claude is selected,
both directories contain the same source variants. Inspect pre-existing
agent-specific installations separately if those agents report duplicate names.

Original skill sources are preserved in `skills/`. Seven standalone variants under
`platforms/linux/skills/` provide portable discovery and maintenance instructions;
six of those names are in the existing daily profile. On-demand lookup prefers
a standalone variant when one exists. The directory keeps its original Linux
name so previously installed symlinks continue to work; its instructions now
cover Windows, macOS, and Linux. See [standalone maintenance](platforms/linux/README.md).

## Update on Kali / Linux / macOS

```bash
cd "$HOME/repos/theprawnskills"
git status --short
git pull --ff-only
python3 scripts/install_skills.py --agents codex --dry-run
python3 scripts/install_skills.py --agents codex --apply
python3 scripts/install_skills.py --agents codex --check
```

For Windows, use PowerShell in the clone:

```powershell
Set-Location -LiteralPath (Join-Path $env:USERPROFILE 'repos\theprawnskills')
git status --short
git pull --ff-only
if ($LASTEXITCODE -ne 0) { throw 'Pull failed; preserve and resolve local changes before installing.' }
py -3 scripts/install_skills.py --agents codex --dry-run
py -3 scripts/install_skills.py --agents codex --apply
py -3 scripts/install_skills.py --agents codex --check
```

Review or commit local edits before pulling; do not reset them. Linked skill
content follows the checkout. Managed copies are refreshed by `--apply`, with
the old copy backed up first; local edits are never silently discarded.
The installer adds newly selected entries, but does not remove skills dropped
from the profile. Review such changes separately. Restart Codex if needed and
use `/skills` to inspect discovery. A profile check verifies paths and links;
it does not prove every third-party tool used by every skill is configured.

## Prompt for Codex on Kali

The following prompt also covers other operating systems.

## Prompt for Codex on any machine

```text
Set up my skills from hongyime/theprawnskills on this machine without OneDrive.
Detect Windows, macOS, or Linux and use its native shell and Python 3.11+.
Use repos/theprawnskills under my current OS user home, cloning it if absent.
If present, verify the remote
and preserve local changes before attempting git pull --ff-only. If GitHub
authentication is required, use the normal interactive login; do not ask me
to paste a token into chat or store credentials in the repo.
Read AGENTS.md, README.md, and platforms/linux/README.md in the clone.
Use scripts/install_skills.py with --agents codex and the default auto mode:
copies on Windows, symlinks on macOS/Linux. No administrator rights are needed
for the default copy installation. Do not change symlink privileges or require OneDrive.
Run --dry-run first. If it reports conflicts, inspect and report them while
preserving all existing files. If the preview succeeds, run --apply and
--check. Confirm that the 65 daily skills resolve, including the standalone
skill-router and visual-explainer with its template, and that the router can
locate an on-demand skill such as pdf.
Keep the full library in the clone and use only the profile in agent discovery.
Do not delete any skills, run dotagents sync, copy Windows authentication or
plugin caches, or alter the Windows/OneDrive machine registry. Report any
missing platform tools or agent integrations separately.
```

## Existing OneDrive machines and Git

The existing OneDrive-connected Windows machines can continue using their library
and `scripts/Install-DefaultSkillProfile.ps1`. The standalone installer does not
change OneDrive or propagate through `machines.toml`. Other Windows machines
use the standalone setup above.

Use GitHub as the transfer point between machines. Review and commit library
changes in the OneDrive checkout, then integrate them into this repository;
Standalone machines pull from GitHub. Changes made in the repository do not automatically
flow back into OneDrive: review and integrate them there separately. Keep one
machine responsible for shared-library edits at a time. Never run the Windows
propagation script on a standalone machine or blindly copy one checkout over another.

For a targeted daily-skill update on the existing OneDrive machines, use
PowerShell 7 from the library checkout after OneDrive has finished syncing.
Invoke the script directly so PowerShell preserves the skill-name array:

```powershell
& ./scripts/Sync-SelectedSkills.ps1 -SkillNames visual-explainer,postplan-upload,skill-router,skill-cleanup
& ./scripts/Sync-SelectedSkills.ps1 -SkillNames visual-explainer,postplan-upload,skill-router,skill-cleanup -Apply
```

Preview is the default. The script reads enabled machines and their installed
agent roots from `machines.toml`, checks each machine's shared source against
the initiating checkout, and updates only the named daily skills. Already
matching copies are skipped. Replaced copies are backed up under that machine's
user home at `Backups/<date>/skills/<run>/...`, outside OneDrive. Review those
backups before merging any local customization. Unreachable machines or source
mismatches are reported; they are not marked synchronized. Use `-LocalOnly`
to operate only on the current registered machine. No remote canonical files
are written by this script. The older full-profile installer remains available
for existing workflows; targeted updates avoid rewriting unrelated skills.

OneDrive transports the shared files; this script refreshes the separate agent
copies. Standalone Kali/macOS/Windows machines use Git and the Python installer
from the update section above. Pulling Git alone refreshes existing symlinks,
but adding a newly selected skill or refreshing Windows copies needs `--apply`.
Neither method silently sets up a scheduled background sync. Restart the agent
after installation if the new daily skill is not visible yet.

## Repository transfer to hongyime

The current repository is `hongyime/theprawnskills`. It was transferred from
the previous personal account; it is the same repository and Git history.
GitHub redirects old clone/fetch/push URLs, but recommends updating existing
clones. Creating a new repository at the old location would remove that
redirect. See [GitHub's transfer documentation](https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository).

Inside each existing clone, on any OS:

```text
git remote set-url origin https://github.com/hongyime/theprawnskills.git
git remote -v
git ls-remote origin HEAD
```

The working checkout and the local OneDrive library checkout were both updated
to the organisation URL. Other machines should verify their own remotes with
the commands above. New clones in this README already use the new URL.

The observed skill deletion came from organisation configuration automation.
The library was restored and protected with `no-config-sync`; the transfer
redirect itself is working. Organisation settings and access policies still
apply, including the visibility sync described below.

## Recovery and repository visibility

The organisation config-sync commit `ae84bdb` removed all 2,165 tracked files
under `skills/`. They are recovered from `0c6ba7f` without changing their
contents. Keep the GitHub topic `no-config-sync` on this repository: the
organisation's `sourcerepo` cleanup otherwise deletes `skills/` and `docs/`
and adds them to `.gitignore`.

That topic does not control visibility. The source settings workflow defaults
repositories to public unless `repos.yml` contains a private override.
Visibility should be an explicit owner decision. A personal library can be
private and still be cloned by authenticated machines. For public sharing,
publish selected portable skills with their attribution and license files,
without personal machine configuration. Changing visibility does not retract
copies already downloaded or public forks.

For this personal working library, private visibility is recommended; publish
selected portable skills separately if public sharing is desired. If the owner
chooses private visibility, keep it consistent in both places:

1. In `hongyime/sourcerepo`'s `repos.yml`, add or merge this entry, preserving
   any existing description, homepage, and topics, then commit and push it:

   ```yaml
   hongyime/theprawnskills:
     visibility: private
   ```

2. Change only this repository's visibility:

   ```text
   gh repo edit hongyime/theprawnskills --visibility private --accept-visibility-change-consequences
   ```

3. Verify the setting and retain the content-sync opt-out:

   ```text
   gh repo view hongyime/theprawnskills --json nameWithOwner,isPrivate
   gh api repos/hongyime/theprawnskills/topics
   ```

These are instructions for an owner-approved change, not a change applied by
the installer. Do not run an organisation-wide sync just to update this repo.
Private clones require an account or SSH key with access on each machine.

## Verification

```bash
python3 -m unittest discover -s tests -v
```

On Windows, use `py -3 -m unittest discover -s tests -v` instead.
CI runs on Windows, macOS, and Linux. Tests use isolated homes and verify first
installation, repeat installation, conflict preservation, profile validation,
standalone variants, shared agent roots, managed copy backups and local-edit
protection, and router discovery. Symlink tests run on macOS/Linux; Windows
tests verify the default copy mode without symlink privileges. No real agent
home is changed by the test suite.

Agent locations: [Codex](https://learn.chatgpt.com/docs/build-skills),
[Claude Code](https://code.claude.com/docs/en/skills),
[OpenCode](https://opencode.ai/docs/skills/),
[Cursor](https://cursor.com/docs/context/skills).
