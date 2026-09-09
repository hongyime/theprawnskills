# Standalone skill maintenance

These instructions apply to standalone Git clones on Windows, macOS, and
Linux, including Kali. The `platforms/linux/` directory keeps its original
name so existing symlinks continue to work. `ENVIRONMENT.md`, `machines.toml`,
and the original skill-management files describe the existing Windows/OneDrive
machines; their propagation procedures do not apply to standalone clones,
including Windows machines without OneDrive. Original skills remain unchanged.

## Locate the library

Read the `library` key from `~/.config/theprawnskills/library.json`. The installer
writes it locally. On macOS/Linux:

```bash
library_root=$(python3 -c 'import json,pathlib; print(json.loads((pathlib.Path.home()/".config/theprawnskills/library.json").read_text())["library"])')
```

On Windows, in PowerShell:

```powershell
$libraryRoot = (Get-Content -Raw -LiteralPath (Join-Path $env:USERPROFILE '.config/theprawnskills/library.json') | ConvertFrom-Json).library
```

When inspecting a skill through a symlink, resolve the symlink before following
its relative references. For any requested skill, prefer
`$library_root/platforms/linux/skills/<name>/SKILL.md` if it exists, otherwise
read `$library_root/skills/<name>/SKILL.md`. Nested skills and supporting files
remain available in their original directories.

## Authoring conventions

- Read the existing skill fully before editing. Use `skills/<name>/SKILL.md`
  for shared instructions; use `platforms/linux/skills/<name>/SKILL.md` for a
  standalone variant. Preserve the existing OneDrive workflows in shared text.
- Match the lowercase kebab-case folder name to frontmatter `name` (at most
  64 characters). Include a useful `description` of at least 40 characters,
  explaining what the skill does and when to use it.
- Preserve upstream attribution, licenses, supporting scripts, references,
  templates, and assets. Check relative references and actual prerequisites.
- Use the machine's native shell and repository-relative paths: PowerShell
  with `py -3` (or a verified `python`) on Windows, bash/zsh with `python3` on
  macOS/Linux. Python must be 3.11 or newer.
  Do not copy authentication, tokens, environment secrets, or plugin caches.
- Search only the library and task-authorized project/configuration paths.
  Do not scan private agent session stores or credential directories.
- Keep `default-profile.toml` as the shared daily selection. New skills can
  remain on demand. Before changing profile membership, check all supported OSes.
- Update `INDEX.md` and the router when names or routing change. The existing
  index generator is PowerShell; if pwsh is unavailable, maintain affected
  index rows directly and verify them against the actual files.
- Invoke `scripts/install_skills.py --agents <selected agents> --dry-run` with
  the appropriate Python command, then `--apply` and `--check` for the current
  user's home. Default auto mode uses copies on Windows and symlinks on
  macOS/Linux. Links follow source edits; managed copies need `--apply` after
  changes. Updates back up unchanged managed copies to
  `~/Backups/<date>/theprawnskills/<run>/...`; local edits or unmanaged targets
  are preserved as conflicts. Never manually edit an installed copy when the
  intended change belongs in the Git clone.
- Do not run `dotagents sync` or use the existing Windows machine registry for
  standalone propagation. Do not register this machine as a PowerShell SSH target.
- Review Git diffs and test affected behavior. Commit/push according to the
  user's authorized scope; never force-push or overwrite another checkout.

## Cleanup and removal

During migration, preserve every skill. Auditing is read-only: classify skills
as default, on-demand, duplicate, broken, or a candidate for later archiving.
Do not treat an on-demand skill as unused merely because it is not installed.

For a later removal request, establish the exact skill and whether the request
affects only installation or the source library. Present the affected links/copies
and references. If already explicitly authorized, proceed within that scope;
otherwise get approval before archiving canonical content. Preserve recoverable
copies outside the checkout in a dated backup directory. On Windows, verify
resolved source and backup paths stay inside the intended user home before
moving a directory. Operate on symlinks
themselves when changing exposure; do not follow them and delete source files.
The installer never prunes installations or overwrites unmanaged directories.
For an interrupted copy update, retain the printed backup and inspect/restore
it before resolving a partial installation. Do not delete files to silence a conflict.

## Platform-dependent workflows

The installer makes instructions discoverable; it does not translate every
script or install tool dependencies. The original `codex`, `claude-code-cli`,
and `opencode-cli` skills include machine-specific Windows paths. Inspect the
actual local CLI and adapt those examples before use, including on another
Windows machine. Do not treat Windows credential paths
as migration input. `postplan-upload` needs Node/npm and its own setup; its
outputs are public when uploaded. Cloud, browser, document, and media skills
can require additional tools, credentials, or MCP connections.

Bundled Codex and plugin skills are owned by their corresponding applications.
Install plugins separately on each machine; do not copy another machine's caches into
this skill library. Duplicate names from plugins should be assessed separately.
