---
description: Central configuration and documentation for all AI coding agents across repositories
---

# AI Agents Configuration

This file defines how AI coding agents (Cursor, Antigravity, Claude Code, GitHub Copilot, etc.) should behave across all repositories in this workspace.

## Cross-Session State (Read This First)

Before doing anything else, read `.agents/STATE.md` if it exists. It is the
handover from whoever worked here last, possibly from a different tool or
machine.

This workspace is worked on by multiple agents: Gemini CLI, Antigravity, Mistral
CLI, Kiro, Codex, Pi, Hermes, opencode, Claude Code, Cursor, and others. Sessions
can end abruptly when a free-tier limit is hit. No harness can read every other
harness's private session store, so durable state lives in plain files that all
of them can read.

The state directory is:

```text
.agents/
  STATE.md      current task, progress, next steps
  JOURNAL.md    append-only decisions and rationale
  handoffs/     detailed handoff documents
```

`.agents/` is committed deliberately so state reaches the other machines. Never
write secrets or personal details there. These files are permanent and
world-readable in public repositories.

Treat `.agents/` as shared project state, not personal scratch space. In team
repos, write only what another teammate or agent needs to resume the work:
current task, decisions, blockers, linked issues or PRs, and safe next steps.
Do not write private notes, credentials, customer data, local machine paths that
should stay private, or anything that would be unsafe in a public repository.

Your obligations:

1. On start, read `.agents/STATE.md` if it exists.
2. As you work, update `.agents/STATE.md` after each meaningful step.
3. For durable decisions, append one dated line to `.agents/JOURNAL.md`.
4. Before a long or risky stretch, write a handoff in `.agents/handoffs/`.

Keep `STATE.md` short and current. Put durable decisions in `JOURNAL.md`. Put
detailed resume notes in timestamped files under `.agents/handoffs/` so multiple
people do not overwrite one another.

Memory tools such as cognee or cavemem are optional local aids. Trust
`.agents/STATE.md` and `git log` over an empty memory-tool result.

## Agent Types and Roles

### 1. Primary Coding Agent (Cursor/Claude Code)
**Purpose**: Main development assistant for code changes
**Capabilities**: Full codebase access, file editing, terminal commands
**Behavior**: Follows all conventions in this file

### 2. Review Agent (GitHub PR Review)
**Purpose**: Automated code review on pull requests
**Capabilities**: Read-only access to PR changes
**Behavior**: Strict adherence to coding standards

### 3. Documentation Agent
**Purpose**: Maintains and updates documentation
**Capabilities**: Can modify markdown files
**Behavior**: Never creates new docs without explicit request

### 4. Security Agent (TruffleHog, CodeQL)
**Purpose**: Security scanning and vulnerability detection
**Capabilities**: Full codebase scan
**Behavior**: Blocks PRs on security issues

## Universal Rules (Apply to All Agents)

### 1. File Operations
- **NEVER** create new markdown files without explicit user request
- **ALWAYS** update existing documentation when possible
- **NEVER** delete files without confirmation
- **ALWAYS** preserve file history and git history

### 2. Code Style
- Follow language-specific conventions (see skill files)
- Use consistent naming patterns
- Keep functions small and focused
- Add type hints for Python, TypeScript interfaces for JS

### 3. Git Conventions
- Commit messages: `type: description`
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `style`
- Keep commits atomic and focused
- Never force push to main branches

### 4. Communication
- Be concise and direct
- Explain complex changes briefly
- Admit uncertainty when present
- Ask for clarification when requirements are ambiguous

## Repository-Specific Overrides

### source-repo-code (Template/Source)
- **Purpose**: Source of truth for shared configurations
- **Special Rules**: Changes here should be synced to all repos

## Skill System

This repository is the skill library itself. Preserve `skills/` and its
references, scripts, assets, and licenses. The GitHub topic `no-config-sync`
opts this repo out of the organisation's downstream configuration cleanup,
which previously removed the library. Do not remove this topic or run that
cleanup here. Visibility is managed separately by sourcerepo's `repos.yml`.

The existing Windows machines may keep their OneDrive library and PowerShell
installer. Standalone Windows, macOS, and Linux machines use a Git clone plus
`scripts/install_skills.py`; see `README.md` and `platforms/linux/README.md`.
Auto mode uses managed copies on Windows and symlinks on macOS/Linux.
The shared profile is `default-profile.toml`. Portable management variants
retain their original `platforms/linux/skills/` paths for existing symlinks.
Do not propagate standalone installation changes through the Windows registry.

Shared repo instructions live in `AGENTS.md`; shared handoff state lives under
`.agents/`. Never put authentication files, tokens, or machine-local install
state in this repository. Do not prune or delete skills during migration.

### MCP Configuration

MCP support varies by harness. Use local MCP configuration if present, but do
not assume one shared MCP config is read by every agent.

## Syncing Strategy

### Source of Truth

This repository owns the skill library and standalone installers. Review and
integrate changes from the existing OneDrive library through Git. The separate
`hongyime/sourcerepo` controls organisation settings, but this repository opts
out of its file cleanup and configuration replacement using `no-config-sync`.

The organisation settings workflow runs on its configured schedule or manual
dispatch. Its visibility settings apply independently of the content opt-out.
If the owner chooses private visibility, also set this repo's visibility to
private in sourcerepo's `repos.yml`. Never re-enable destructive config cleanup
for this library or dispatch an organisation-wide sync as an installation step.

For a new machine, follow README.md using the organisation Git URL and that
machine's own GitHub authentication. No OneDrive access is required.

## Maintenance

### Quarterly Reviews
- Review and update skill files
- Check for outdated action versions
- Verify agent behavior consistency
- Update this configuration as needed

### Automated Monitoring
- Use Dependabot for dependency updates
- Use TruffleHog for secret scanning
- Use custom scripts to detect outdated GitHub Actions

## Troubleshooting

### Agent Not Following Conventions
1. 检查仓库特定覆盖在 AGENTS.md 中
2. 检查 `.agents/STATE.md` 中是否有最新任务上下文
3. 审阅近期约定变更
4. Review this repository's own instructions; do not run source config cleanup here.

### Sync Failures
1. Inspect the existing workflow logs; do not dispatch organisation-wide sync for this library.
2. 检查目标仓库中的 git 冲突
3. 验证文件权限
4. 查看同步日志中的具体错误

## References

- [GitHub Skills Documentation](https://docs.github.com/en/contributing/collaborating-with-github-docs/using-skills)
- [Cursor AI Documentation](https://docs.cursor.com/)
- [Claude Code Documentation](https://docs.anthropic.com/claude/code)
- [Dependabot Configuration](https://docs.github.com/en/code-security/dependabot)
