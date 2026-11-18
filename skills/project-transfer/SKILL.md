---
name: project-transfer
description: >-
  One-time, on-demand harvest of proven lessons from any project (SOURCE) —
  owned or not — into a learnings store or another project (TARGET). Mines git
  history (commits, PRs, review comments, issues, closed branches) plus code,
  dot files, dot folders and agent session logs, then files the reviewed PACK
  or adapts lessons into the target. Trigger on "transfer lessons", "harvest
  this project", "reuse what worked from X", "collate learnings from X".
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Project Transfer

Transfer proven developer and agent lessons from a completed project (`SOURCE`)
into a learnings store or a new or existing target project (`TARGET`), adapting
across different languages, frameworks, and agent harnesses. `SOURCE` may be a
repo Bryan does not own; `TARGET` may differ from the store.

Work proceeds in discrete phases with a human-reviewable PACK file in between:
- **Phase 1 (Harvest)**: Mines git history plus code, dot files and agent session logs; writes only the PACK.
- **Phase 2 (File and Adopt)**: Files the reviewed PACK into `STORE` (default
  `hongyime/theprawnlearnings`, one folder per source repo), and optionally
  adapts lessons into `TARGET`.

Different agents or sessions can run Phase 1 and Phase 2 independently.

## Inputs & Defaults

| Input | Required | Default | Notes |
|---|---|---|---|
| `SOURCE` path or repo slug | Yes (Phase 1) | Prompt user if missing | Local path, or `owner/repo` — clone read-only to a temp dir if no local copy exists |
| `STORE` path | Optional | `hongyime/theprawnlearnings` (private) | Where the reviewed PACK is filed; one folder per source repo. Overridable per run |
| `PACK` path | Optional | `<source-folder>-lessons.md` next to `SOURCE` | Intermediate review file |
| `TARGET` path | Only for Adopt | Prompt user before Adopt | Destination repository for adapted lessons. May differ from `STORE`; needs write access |

Ask only for missing inputs. Never prompt for `TARGET` during Phase 1. Never prompt for `STORE` — the default applies unless the user names another.

## Ground Rules

- **Zero Target Writes in Phase 1**: Phase 1 reads `SOURCE` and home agent folders, writing *only* to the PACK file.
- **No-ownership mode**: `SOURCE` may be a repo Bryan does not own. Never commit, push, open a PR, or write anything in `SOURCE`. Read-only: `git log`, `gh pr` / `gh issue` reads, local clone reads. If the remote is gone or unreachable, harvest from the local clone only and record the access level in the PACK. If there is no local clone and no `gh` access, stop and report — do not guess.
- **STORE is not TARGET**: filing the PACK into `STORE` is not adopting. Adopt writes into `TARGET` only when Bryan names it and has write access.
- **Strict Boundary in Phase 2**: Phase 2 writes *only* inside `STORE` (filing) and `TARGET` (adopting).
- **Absolute Secret Exclusion**: Never copy secrets, keys, or credentials. Skip `.env*`, `*.pem`, `*.key`, `auth.json`, `tokens.json`, and cookies. Variable names are allowed. Scrub any credential-like string from session logs.
- **Graceful Permission Degradation**: If a folder cannot be read (sandbox, permissions), report the path and continue without aborting.
- **Evidence Requirement**: No evidence, no entry. Speculative or unverified rules must not be added to the PACK.

---

## Phase 1: Harvest (in SOURCE)

### 1.1 Codebase & Dot-File Inventory

Inspect all files in `SOURCE`, including hidden dot-files and folders.
Skip `node_modules/`, `.venv/`, `venv/`, `dist/`, `build/`, `target/`, and `.git/` internals.

Read in this prioritized order:

1. **Agent instructions & skills**:
   - Instruction files: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `QWEN.md`, `.cursorrules`, `.windsurfrules`, `.clinerules`, `.github/copilot-instructions.md`.
   - Tool/agent directories: `.agents/`, `.agent/`, `.claude/`, `.gemini/`, `.codex/`, `.opencode/`, `.cursor/`, `.kiro/`, `.windsurf/`, `.github/`.
2. **Hooks & automation**:
   - `.claude/settings*.json` (hooks), `.husky/`, `.pre-commit-config.yaml`.
   - Build/task files: `Makefile`, `justfile`, `Taskfile`, CI workflows (`.github/workflows/`), `package.json` scripts, `pyproject.toml` tool sections, `scripts/`.
3. **Quality & lint configuration**:
   - Linters, formatters, type checkers, strict compiler flags, `.editorconfig`, test runner configurations.
4. **Docs, notes, & ADRs**:
   - `README.md`, `docs/`, `notes/`, Architecture Decision Records (ADRs), `TODO`/`FIXME` trends, `CHANGELOG.md`.
5. **Environment & Editor configs**:
   - `.env.example` (variable names only), `.vscode/settings.json`, `.vscode/tasks.json`.

### 1.2 Git history (commits, PRs, issues, closed branches)

Mine the history, not just the current tree. Work read-only; prefer `gh` for
anything GitHub holds and `git log` for what the clone holds.

```bash
git log --oneline --all --since=<window>        # commit subjects, authors, dates
git log --all --grep="revert" --oneline         # reverts: a direction that failed
gh pr list --state all --limit 200              # every PR: open, merged, closed
gh pr view <N> --comments                       # review discussion and decisions
gh issue list --state all --limit 200           # every issue: open and closed
git branch -a                                   # live + remote-tracking branches
```

Extract, with evidence cited as `commit <sha>`, `PR #N`, or `issue #N`:
- **Decisions**: what was chosen, who decided, when — from merged PR titles/bodies and review comments that settled an argument.
- **Reverts**: a reverted commit is evidence a direction failed; record what was tried and why it was undone.
- **Recurring bugs**: the same failure fixed in more than one PR or commit.
- **Review corrections**: "don't do X", "use Y instead" in review comments — the same class as user corrections in session logs.
- **Closed branches**: a deleted branch survives through its PR (branch name, merged/closed state, discussion). A branch with no PR leaves only its commits in `git log --all` until pruned.
- **Per-author ownership**: always use `git log --all` — a single branch's log undercounts contributors (in the trial, Ben showed 157 commits on one branch vs 312 across all refs). For each author, record commit count, date range, top files, and representative subjects. The result is an ownership map: who owns which area. Authors who appear only on branches (never on the main branch) still count.

```bash
git log --all --format="%an" | sort | uniq -c | sort -rn
git log --all --author="<name>" --format="%ad %s" --date=short | head -8
git log --all --author="<name>" --pretty=format: --name-only | sort | uniq -c | sort -rn | head -5
git for-each-ref --format="%(refname:short) | %(committerdate:short) | %(authorname) | %(subject)" refs/remotes/origin/ | grep -v HEAD
```

Access ladder — record the level in the PACK and degrade, never guess:
- **full**: local clone + `gh` access (PRs, issues, comments available).
- **clone-only**: local clone, remote gone or unreachable (no PRs/issues; branches and log only).
- **gh-only**: no local clone, `gh` reads work (PRs/issues available; no working-tree or session-log harvest).
- **none**: no clone and no `gh` access — stop and report.

### 1.3 Working tree (uncommitted work)

`git log` cannot see uncommitted work, and uncommitted work exists on one
machine only. Capture it or it is lost to the harvest:

```bash
git status --porcelain | wc -l
git diff --stat | tail -3
git status --porcelain | grep "^??" | head -20
```

- Record the diff stat and the untracked inventory (paths only, not file contents unless a file is the lesson itself, e.g. an analysis doc).
- Flag every uncommitted item as machine-local: it exists only on that machine's clone until committed. Note which machine's tree was captured.
- If clones exist on several machines, compare working trees: same HEAD with different dirt means divergent local work — record both.
- A large uncommitted change (new modules, guides, test suites) is itself a finding: work that was never committed is work with no review trail.

### 1.4 Agent Session Logs (Home Folders)

Search agent session logs for mentions of `SOURCE`'s absolute path or folder name.
Because session logs can be massive, use `rg` (ripgrep) or targeted file searches first.
Do not read entire log files into context without filtering.

#### Known Cross-Platform Locations

| Agent | Linux / macOS | Windows |
|---|---|---|
| Claude Code | `~/.claude/projects/` | `%USERPROFILE%\.claude\projects\` |
| Codex CLI | `~/.codex/sessions/` | `%USERPROFILE%\.codex\sessions\` |
| Gemini CLI / Antigravity | `~/.gemini/` | `%USERPROFILE%\.gemini\` |
| OpenCode | `~/.config/opencode/`, `~/.local/share/opencode/` | `%APPDATA%\opencode\`, `%LOCALAPPDATA%\opencode\` |
| Other Agents | `~/.cursor/`, `~/.kimi/`, `~/.qwen/`, `~/.windsurf/` | `%USERPROFILE%\.<agent>\` |

#### Fast Grep Patterns

```bash
# Linux / macOS
rg -l "SOURCE_NAME" ~/.claude/projects ~/.codex/sessions ~/.gemini -g "*.json" -g "*.jsonl" -g "*.md"
```

```powershell
# Windows PowerShell
$logs = "$HOME\.claude\projects", "$HOME\.codex\sessions", "$HOME\.gemini"
rg -l "SOURCE_NAME" $logs -g "*.json" -g "*.jsonl" -g "*.md"
```

From matched logs, extract surrounding context (3-5 lines) focusing on:
- **User corrections**: "no", "don't", "instead", "again", "I told you", "stop doing".
- **Recurring errors**: The same compilation, lint, or runtime bug encountered multiple times.
- **Loop-ending fixes**: The key breakthrough or fix that resolved a prolonged debugging session.
- **Repeated manual steps**: Commands or setup steps the user repeatedly ran or asked the agent to execute.

### 1.5 Extract and Generalize

For every potential lesson, record four attributes:

- **Intent**: What this rule prevents or makes easy, stated purely in stack-agnostic terms. If the intent cannot be expressed without project-specific names or domain logic, drop it.
- **Original Form**: The concrete code snippet, config flag, script, or instruction from `SOURCE`.
- **Evidence**: The file path, session timestamp, or recurrence count proving this was needed.
- **Verification**: How an agent or tool can verify adherence in a target repository.

### 1.6 Classification Rubric

Categorize each generalized item into one of six standard types:

| Category | Definition | Target Destination |
|---|---|---|
| `convention` | Style or architectural preference | `AGENTS.md` guidelines (TARGET) or filed learning (STORE) |
| `procedure` | Step-by-step workflow used 2+ times | Agent skill (`.agents/skills/<name>/SKILL.md`) — in theprawnskills or TARGET, decided at review |
| `rule` | Hard constraint that must never break | Automated check script or strict linter rule |
| `hook` | Triggered event (pre-commit, tool hook) | Check script wired to agent hook / git hook |
| `workflow` | CI, release, build, or review pipeline | CI action, Makefile, or runner recipe |
| `mistake-to-avoid` | Recurrent trap or anti-pattern | `AGENTS.md` "Avoid" bullet with rationale |

### 1.7 Write the PACK File

Write the output file (default `<source-folder>-lessons.md` next to `SOURCE`). Use this exact markdown structure:

````markdown
# Lessons PACK: <SOURCE_NAME>

- **Date:** <YYYY-MM-DD>
- **Source Path:** `<SOURCE_PATH>`
- **Source Stack:** <Language, framework, tools>
- **Source Access:** full | clone-only | gh-only
- **Store:** `<STORE path, default hongyime/theprawnlearnings>`
- **Logs Inspected:** <List of agents whose logs were reviewed>
- **History Inspected:** <Commit count, PR count, issue count reviewed>
- **Authors:** <Count, top authors with commit counts — always --all>
- **Working Tree:** <clean | N files changed + M untracked on <machine>>

## Summary Table

| # | Item | Category | Evidence Count | Target Recommendation |
|---|---|---|---|---|
| 1 | <Short Name> | convention | 3 sessions | AGENTS.md |
| 2 | <Short Name> | rule | Pre-commit hook | checks/ |

## Harvested Lessons

### 1. <Item Title>
- **Category:** `convention` | `procedure` | `rule` | `hook` | `workflow` | `mistake-to-avoid`
- **Intent:** <Stack-agnostic purpose>
- **Original Form:**
  ```text
  <Original code, config, or prompt snippet>
  ```
- **Evidence:** `<file-path-or-log-id>` (observed N times)
- **Verification:** <Concrete verification command or condition>

## Dropped Candidates
- `<Candidate Name>`: Dropped because <specific reason, e.g. project-specific domain logic, no reproducible evidence>.
````

Present the summary table to the user and prompt them to review, modify, or prune items before proceeding to Phase 2.

---

## Phase 2: File and Adopt (in STORE, optionally in TARGET)

### 2.1 File into STORE

After the user reviews the PACK, file it into `STORE` (default
`hongyime/theprawnlearnings`):

1. Clone `STORE` if not already present; work on main.
2. Folder per source repo: `<owner>-<repo>/` (e.g. `bchuminx-healthkaki-pov/`).
3. Copy the reviewed PACK to `<owner>-<repo>/packs/<YYYY-MM-DD>-lessons.md`.
4. Merge its items into `<owner>-<repo>/lessons.md` (one consolidated file per
   source repo): add new items, update changed ones, never silently drop an old
   item — supersede it with a dated note and a link to the newer PACK.
5. Commit and push. The commit message names the source repo and the PACK date.

Filing needs no `TARGET`. If the user wants no filing (PACK only), stop here.

### 2.2 Inspect TARGET

Before making any modifications:
1. Identify `TARGET` stack: language, package managers, test runners, linters, CI systems, and task runners.
2. Read existing instruction files: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, etc.
3. Check existing scripts (`scripts/`, `checks/`, `bin/`) and skills (`.agents/skills/`, `.claude/skills/`).
4. Note which PACK items are already covered or partially addressed in `TARGET`.

### 2.3 Decide for Each Item: Adopt, Adapt, or Skip

- **adopt**: Apply directly as-is (e.g. universal markdown guidelines, stack-independent git practices).
- **adapt**: Translate the item's *intent* and *verification* into `TARGET`'s native tooling (e.g. convert a Python flake8 rule to an ESLint plugin, or a bash script to a PowerShell / npm script).
- **skip**: Item is already satisfied by existing configuration or conflicts with `TARGET`'s explicit architecture. Document the reason.

Never copy raw syntax from `SOURCE` if `TARGET` uses a different paradigm. Translate the underlying intent.

### 2.4 Present Plan and Write

Present a decision table to the user:

| Item | Decision | Adaptation Details | Target Location |
|---|---|---|---|
| `<Item>` | `adapt` | Converted to Vitest check | `checks/check-api-contract.sh` |
| `<Item>` | `adopt` | Added to project rules | `AGENTS.md` |
| `<Item>` | `skip` | Already enforced by tsconfig | - |

Wait for user approval before writing. Once approved:

1. **Rules & Conventions**:
   - Append under `## Lessons from <source-folder>` in `TARGET/AGENTS.md`.
   - If `CLAUDE.md` or `GEMINI.md` exist, add a reference pointing to `AGENTS.md` rather than duplicating content.
2. **Skills (`procedure`)**:
   - Save to `TARGET/.agents/skills/<name>/SKILL.md`.
   - If Claude Code is used, notify the user that it reads `.claude/skills/`, and offer to create a symlink or copy.
3. **Checks & Rules (`rule`, `hook`)**:
   - Place executable scripts in `TARGET/checks/` (or the existing script directory).
   - Wire checks into `package.json`, `Makefile`, or task runner.
   - Add a notice to `TARGET/AGENTS.md`: `"Before finishing a task, run <check-command>."`
4. **Hooks**:
   - Configure only for specific agents requested by the user, having the hook invoke the check script.
5. **Conflict Prevention**:
   - Never overwrite existing files without confirmation. Merge additions cleanly.

### 2.5 Verification

Execute each newly introduced check script once within `TARGET`:
- Confirm the script runs and reports pass/fail without syntax errors.
- Fix any environment setup issues.
- Do not modify existing codebase logic in `TARGET` unless explicitly instructed.

### 2.6 Handoff Report

Conclude with a clear adoption summary:
- Files created and modified in `STORE` and `TARGET`.
- Items adapted and their new locations.
- Items skipped and reasons.
- Next steps or manual decisions required from the user.
