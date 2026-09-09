# Linux skill maintenance

These instructions apply to a Linux Git clone. `ENVIRONMENT.md`,
`machines.toml`, and the original skill-management files describe the existing
Windows/OneDrive machines; do not execute their Windows propagation procedures
on Linux. Original files remain available and unchanged.

## Locate the library

Read the `library` key from `~/.config/theprawnskills/library.json`. The installer
writes it locally. For example:

```bash
library_root=$(python3 -c 'import json,pathlib; print(json.loads((pathlib.Path.home()/".config/theprawnskills/library.json").read_text())["library"])')
```

When inspecting a skill through a symlink, resolve the symlink before following
its relative references. For any requested skill, prefer
`$library_root/platforms/linux/skills/<name>/SKILL.md` if it exists, otherwise
read `$library_root/skills/<name>/SKILL.md`. Nested skills and supporting files
remain available in their original directories.

## Authoring conventions

- Read the existing skill fully before editing. Use `skills/<name>/SKILL.md`
  for shared instructions; use `platforms/linux/skills/<name>/SKILL.md` for a
  Linux-specific variant. Keep Windows behavior intact when editing shared text.
- Match the lowercase kebab-case folder name to frontmatter `name` (at most
  64 characters). Include a useful `description` of at least 40 characters,
  explaining what the skill does and when to use it.
- Preserve upstream attribution, licenses, supporting scripts, references,
  templates, and assets. Check relative references and actual prerequisites.
- Use the actual Linux shell, `python3`, and repository-relative paths.
  Do not copy authentication, tokens, environment secrets, or plugin caches.
- Search only the library and task-authorized project/configuration paths.
  Do not scan private agent session stores or credential directories.
- Keep `default-profile.toml` as the shared daily selection. New skills can
  remain on demand. Before changing profile membership, check both platforms.
- Update `INDEX.md` and the router when names or routing change. The existing
  index generator is PowerShell; if pwsh is unavailable, maintain affected
  index rows directly and verify them against the actual files.
- Run `scripts/install_skills.py --agents <selected agents> --dry-run`, then
  `--apply` and `--check` for the local Linux home. Correct symlinks need no
  copying. Existing conflicts must be reviewed and preserved separately.
- Do not run `dotagents sync` or use the Windows registry for Linux
  propagation. Do not register this machine as a Windows PowerShell SSH target.
- Review Git diffs and test affected behavior. Commit/push according to the
  user's authorized scope; never force-push or overwrite another checkout.

## Cleanup and removal

During migration, preserve every skill. Auditing is read-only: classify skills
as default, on-demand, duplicate, broken, or a candidate for later archiving.
Do not treat an on-demand skill as unused merely because it is not installed.

For a later removal request, establish the exact skill and whether the request
affects only installation or the source library. Present the affected links
and references. If already explicitly authorized, proceed within that scope;
otherwise get approval before archiving canonical content. Preserve recoverable
copies outside the checkout in a dated backup directory. Operate on symlinks
themselves when changing exposure; do not follow them and delete source files.
The installer intentionally has no removal or overwrite mode.

## Platform-dependent workflows

The installer makes instructions discoverable; it does not translate every
script or install tool dependencies. The original `codex`, `claude-code-cli`,
and `opencode-cli` skills include Windows paths. Inspect the actual Linux CLI
and translate those examples before use. Do not treat Windows credential paths
as migration input. `postplan-upload` needs Node/npm and its own setup; its
outputs are public when uploaded. Cloud, browser, document, and media skills
can require additional tools, credentials, or MCP connections.

Bundled Codex and plugin skills are owned by their corresponding applications.
Install plugins separately on Linux; do not copy Windows plugin caches into
this skill library. Duplicate names from plugins should be assessed separately.
