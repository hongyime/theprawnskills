# The Prawn Skills

A full skill library plus the daily profile in `default-profile.toml`.
The recovered snapshot contains 206 top-level skills (216 `SKILL.md` files
including nested skills), with 64 selected for daily use.

## Install on Kali / Linux

Requires Git and Python 3.11 or newer. This installs skill instructions and
their supporting files; tools, MCP servers, credentials, and plugins used by
individual skills need their own setup. No npm install is needed for this
library's installer; the legacy root package.json is not its dependency list.

If the repo is private, authenticate with GitHub first, for example using
`gh auth login` followed by `gh auth setup-git`, or use an authenticated SSH URL.

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
If Python is too old or absent, install a supported Python through Kali's
package manager before continuing.

The installer creates individual symlinks for the selected skills. It validates
the whole selection before writing and stops on conflicts, preserving existing
files. Running it again keeps correct links. It never prunes other skills or
overwrites an existing installation. Preview is the default mode.

| Agent argument | Linux installation location |
|---|---|
| `codex` | `~/.agents/skills/<skill>` |
| `opencode` | Same shared `~/.agents/skills/<skill>` location |
| `claude` | `~/.claude/skills/<skill>` |
| `cursor` | Same shared `~/.agents/skills/<skill>` location |

For example, use `--agents codex claude opencode` to select those agents.
Codex, OpenCode, and Cursor share one set of links. The full library remains in the
clone for on-demand use. Do not symlink the entire clone into `~/.agents` or
install the same profile again into Codex's legacy `~/.codex/skills` folder.
The router uses `~/.config/theprawnskills/library.json` to locate the clone.
OpenCode and Cursor also scan Claude's directory; when Claude is selected,
both directories point to the same source variants. Inspect pre-existing
agent-specific installations separately if those agents report duplicate names.

Original skill sources are preserved in `skills/`. Seven Linux variants under
`platforms/linux/skills/` provide portable discovery and maintenance instructions;
six of those names are in the existing daily profile. On-demand lookup prefers
a Linux variant when one exists. See [Linux maintenance](platforms/linux/README.md).

## Update on Kali

```bash
cd "$HOME/repos/theprawnskills"
git status --short
git pull --ff-only
python3 scripts/install_skills.py --agents codex --dry-run
python3 scripts/install_skills.py --agents codex --apply
python3 scripts/install_skills.py --agents codex --check
```

Review or commit local edits before pulling; do not reset them. Linked skill
content follows the checkout, so pulling updates changes the installed content.
The installer adds newly selected entries, but does not remove skills dropped
from the profile. Review such changes separately. Restart Codex if needed and
use `/skills` to inspect discovery. A profile check verifies paths and links;
it does not prove every third-party tool used by every skill is configured.

## Prompt for Codex on Kali

```text
Set up my skills from hongyime/theprawnskills on this Kali machine.
Use ~/repos/theprawnskills, cloning it if absent. If present, verify the remote
and preserve local changes before attempting git pull --ff-only. If GitHub
authentication is required, use the normal interactive login; do not ask me
to paste a token into chat or store credentials in the repo.
Read AGENTS.md, README.md, and platforms/linux/README.md in the clone.
Use Python 3.11+ and scripts/install_skills.py with --agents codex.
Run --dry-run first. If it reports conflicts, inspect and report them while
preserving all existing files. If the preview succeeds, run --apply and
--check. Confirm that the 64 daily skills resolve, including the Linux
skill-router, and that the router can locate an on-demand skill such as pdf.
Keep the full library in the clone and use only the profile in agent discovery.
Do not delete any skills, run dotagents sync, copy Windows authentication or
plugin caches, or alter the Windows/OneDrive machine registry. Report any
missing Linux tools or agent integrations separately.
```

## Windows and Git

Windows continues to use the existing OneDrive library and
`scripts/Install-DefaultSkillProfile.ps1`. The Linux installer does not change
OneDrive or propagate through `machines.toml`.

Use GitHub as the transfer point to Kali. Review and commit Windows library
changes in the OneDrive checkout, then integrate them into this repository;
Kali pulls from GitHub. Changes made in the repository do not automatically
flow back into OneDrive: review and integrate them there separately. Keep one
machine responsible for shared-library edits at a time. Never run the Windows
propagation script on Kali or blindly copy one checkout over another.

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

## Verification

```bash
python3 -m unittest discover -s tests -v
```

Tests use isolated homes and verify first installation, repeat installation,
conflict preservation, profile validation, Linux variants, shared agent roots,
and router discovery. No real agent home is changed by the test suite.

Agent locations: [Codex](https://learn.chatgpt.com/docs/build-skills),
[Claude Code](https://code.claude.com/docs/en/skills),
[OpenCode](https://opencode.ai/docs/skills/),
[Cursor](https://cursor.com/docs/context/skills).
