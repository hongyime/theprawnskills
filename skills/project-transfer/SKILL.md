---
name: project-transfer
description: >-
  When to read: 'transfer lessons', 'harvest this project', or 'reuse what worked from X'. Use
  for: a one-time, on-demand harvest of proven lessons from any project (SOURCE) into a
  learnings store or another project (TARGET). Does: mines git history, code, dot files, and
  agent session logs, then files the reviewed PACK or adapts lessons into the target.
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
- **Phase 2 (File and Adopt)**: Files the reviewed PACK into `STORE` (default `hongyime/theprawnlearnings`, one folder per source repo), and optionally adapts lessons into `TARGET`.

**Execution Modes:**
- **Single-repo mode (default)**: Pause after Phase 1 for user review of the summary table before running Phase 2.
- **Sweep mode (multi-repo list, Phase 1 + 2.1 only)**: When the user authorizes a batch harvest into `STORE` with no `TARGET`:
  1. Maintain a persistent ledger (`<STORE>/_sweep-state.md` or user-specified path) recording `repo | status (done|thin|skipped|failed) | head_sha | lessons_count | date | note` after *each* repo so interrupted runs resume cleanly.
  2. Pre-flight via `gh repo view <slug> --json isEmpty,isArchived,isFork,parent,defaultBranchRef,pushedAt,diskUsage,hasIssuesEnabled` before cloning.
  3. Skip empty repos (`isEmpty: true`) and unmodified forks (`0` commits ahead of parent and `0` fork PRs/issues); log `skipped` in the ledger without creating a `STORE` folder.
  4. If cloning fails (retry once) or `SOURCE` yields `0` valid lessons, record `failed` or `skipped (0 lessons)` in the ledger, delete any temp clone, and continue to the next repo.
  5. Commit each repo to `STORE` as it finishes, push in batches of 5–10 repos, and report a batch summary. Skip Phases 2.2–2.6 and `postplan-upload` unless explicitly requested.

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
- **No-ownership mode**: `SOURCE` may be a repo Bryan does not own. Never commit, push, open a PR, or write anything in `SOURCE`. Read-only: `git log`, `gh pr` / `gh issue` reads, local clone reads. Remote gone/unreachable → harvest from the local clone only, record the access level in the PACK. No local clone and no `gh` access → stop and report, do not guess.
- **Temp clones are scratch**: when `SOURCE` was cloned to a temp dir (remote exists, no local copy), delete the temp clone after the PACK is filed — or after the run, if filing is skipped. The PACK in `STORE` is the durable record, not the clone. When the remote is gone, there is no temp clone: harvest from the local clone, which may be the only copy.
- **Strict Boundary in Phase 2**: Phase 2 writes *only* inside `STORE` (filing) and `TARGET` (adopting).
- **Absolute Secret Exclusion**: Never copy secrets, keys, tokens, or credentials from *any* source (working tree, git diffs/commits, PR/issue comments, session logs). Skip `.env*` (except `.env.example`), `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.session`, `auth.json`, `tokens.json`, `credentials*.json`, `service-account*.json`, `.npmrc`, `.pypirc`, `id_rsa*`, and cookies. Variable names are allowed; redact any token/password/URL-with-auth literal as `<REDACTED>` before writing `Original Form` or `Evidence`.
- **Graceful Permission Degradation**: If a folder cannot be read (sandbox, permissions), report the path and continue without aborting.
- **Evidence Requirement**: No evidence, no entry. Speculative or unverified rules must not be added to the PACK.

---

## Phase 1: Harvest (in SOURCE)

### 1.1 Codebase & Dot-File Inventory

Before reading files, check provenance:
- **Forks (`isFork: true`)**: fork-only delta first (`gh pr list`, fork-author commits, diff vs `parent` if reachable). Harvest *only* fork-specific changes; never mine upstream history or upstream-owned files.
- **Bulk-synced templates**: `git log -n 10 --stat` for sync commits (e.g. `theprawntemplate` / `sourcerepo`, mass `AGENTS.md` / `STANDARDS.md` / `.github/` drops). Ignore files touched *only* by template-sync commits unless the repo modified them or actively references them in its own code/PRs.

Inspect repo-native files in `SOURCE`, including hidden dot-files and folders. Skip `node_modules/`, `.venv/`, `venv/`, `dist/`, `build/`, `target/`, `vendor/`, `__pycache__/`, `.next/`, `.pytest_cache/`, binary/media/dataset blobs, and `.git/` internals.

Read in this prioritized order:

1. **Agent instructions & skills**: instruction files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `QWEN.md`, `.cursorrules`, `.windsurfrules`, `.clinerules`, `.github/copilot-instructions.md`); tool/agent directories (`.agents/`, `.agent/`, `.claude/`, `.gemini/`, `.codex/`, `.opencode/`, `.cursor/`, `.kiro/`, `.windsurf/`, `.github/`).
2. **Hooks & automation**: `.claude/settings*.json` (hooks), `.husky/`, `.pre-commit-config.yaml`; build/task files (`Makefile`, `justfile`, `Taskfile`, CI workflows, `package.json` scripts, `pyproject.toml` tool sections, `scripts/`).
3. **Quality & lint configuration**: linters, formatters, type checkers, strict compiler flags, `.editorconfig`, test runner configurations.
4. **Docs, notes, & ADRs**: `README.md`, `docs/`, `notes/`, ADRs, `TODO`/`FIXME` trends, `CHANGELOG.md`.
5. **Environment & Editor configs**: `.env.example` (variable names only), `.vscode/settings.json`, `.vscode/tasks.json`.

### 1.2 Git history (commits, PRs, issues, closed branches)

Mine the history, not just the current tree. Work read-only; prefer `gh` for anything GitHub holds and `git log` for what the clone holds.

When cloning for harvest, use a treeless clone (`git clone --filter=blob:none --no-single-branch <url>`) so `git log --all` is complete without downloading historical binary blobs. If `git log --all` fails (0 commits), classify `Source Access` as `empty`.

```bash
git log --oneline --all --no-merges -n 200      # recent/bounded commit subjects; drop -n 200 only for deep audit
git log --all -i --grep="revert" --oneline      # case-insensitive reverts (matches "Revert ...")
gh pr list --state all --limit 100              # PRs (ignore gracefully if 403/disabled)
gh issue list --state all --limit 100           # skip if hasIssuesEnabled == false
git branch -a                                   # live + remote-tracking branches
```

Cap deep inspection to protect context: inspect comments (`gh pr view <N> --comments` / `gh issue view <N> --comments`) on at most the **20 most relevant PRs/issues** (closed/merged PRs with review comments, reverts, and bugs first — not dependency bumps).

Extract, with evidence cited as `commit <sha>`, `PR #N`, or `issue #N`:
- **Decisions**: what was chosen, who decided, when — from merged PR titles/bodies and review comments that settled an argument.
- **Reverts**: a reverted commit is evidence a direction failed; record what was tried and why it was undone.
- **Recurring bugs**: the same failure fixed in more than one PR or commit.
- **Review corrections**: "don't do X", "use Y instead" in review comments — the same class as user corrections in session logs.
- **Closed branches**: a deleted branch survives through its PR (branch name, merged/closed state, discussion). A branch with no PR leaves only its commits in `git log --all` until pruned.
- **Per-author ownership**: always use `git log --all` — one branch undercounts (trial: Ben 157 commits on one branch vs 312 across all refs). Per author, record commit count, date range, top files, and representative subjects: an ownership map of who owns which area. Branch-only authors (never on main) still count.

```bash
git log --all --no-merges --format="%an <%ae>" | grep -vE '\[bot\]|dependabot|renovate|github-actions' | sort | uniq -c | sort -rn
git log --all --no-merges --author="<name>" --format="%ad %s" --date=short | head -8
git log --all --no-merges --author="<name>" --pretty=format: --name-only | sort | uniq -c | sort -rn | head -5
git for-each-ref --format="%(refname:short) | %(committerdate:short) | %(authorname) | %(subject)" refs/remotes/origin/ | grep -v HEAD
```
Note email aliases belonging to the same person in `Authors` rather than splitting them, and on forks list fork-only author counts separately from upstream.

Access ladder — record the level in the PACK and degrade, never guess: **full** = local clone + `gh` access; **clone-only** = local clone, remote gone/unreachable (no PRs/issues; branches and log only); **gh-only** = no local clone, `gh` reads work (no working-tree or session-log harvest); **empty** = 0 commits — record `skipped (empty)` in the sweep ledger, do not create a `STORE` folder; **none** = no clone and no `gh` access — stop and report.

### 1.3 Working tree (uncommitted work)

If inspecting an existing local developer checkout, capture uncommitted work (skip and record `N/A — fresh temp clone` for a fresh remote clone):

```bash
git status --porcelain | wc -l
git diff --stat | tail -3
git status --porcelain | grep "^??" | head -20
```

Record the diff stat and untracked inventory (paths only, not contents, unless a file is itself the lesson, e.g. an analysis doc). Flag every uncommitted item as machine-local — it exists only on that machine's clone until committed; note which machine's tree was captured. If clones exist on several machines, compare working trees: same HEAD with different dirt means divergent local work — record both. A large uncommitted change (new modules, guides, test suites) is itself a finding: work never committed is work with no review trail.

### 1.4 Agent Session Logs (Home Folders)

See [Session logs](reference/session-logs.md) for agent log locations and grep patterns.

### 1.5 Extract, Filter, and Generalize

Apply a strict inclusion bar before keeping a candidate:
- **Drop routine hygiene**: standard `.gitignore` entries, boilerplate READMEs, default framework scaffolding, unmotivated style configs are *not* lessons unless linked to a concrete bug, revert, review correction, or 2+ recurrences.
- **Check staleness**: verify the pattern is not contradicted or deleted later in `git log` and still applies (archived/legacy repos: tag the era/version in `Intent` if tied to an old runtime).
- **Budget**: target 5–10 high-signal lessons for active repos, 1–4 for small/thin repos, and `0` (stop and skip `STORE` filing) if nothing passes the bar.

For every kept lesson, record four attributes: **Intent** — what this rule prevents or makes easy; generalize universal practices into stack-agnostic terms, keep concrete library/API gotchas explicitly named (e.g. rate limits, TLS/SDK quirks) rather than bleaching them into vague platitudes; drop pure domain/business logic with no reusable engineering lesson. **Original Form** — the concrete code snippet, config flag, script, or instruction from `SOURCE` (scrubbed of any secrets). **Evidence** — exact file path, `commit <sha>`, `PR #N`, `issue #N`, or session timestamp + recurrence count proving this was needed. **Verification** — how an agent or tool can verify adherence in a target repository.

### 1.6 Classification Rubric

Categorize each generalized item into one of six standard types:

| Category | Definition | Target Destination |
|---|---|---|
| `convention` | Style or architectural preference | `AGENTS.md` (TARGET) or filed learning (STORE) |
| `procedure` | Step-by-step workflow used 2+ times | Agent skill (`.agents/skills/<name>/SKILL.md`) — theprawnskills or TARGET, decided at review |
| `rule` | Hard constraint that must never break | Automated check script or strict linter rule |
| `hook` | Triggered event (pre-commit, tool hook) | Check script wired to agent hook / git hook |
| `workflow` | CI, release, build, or review pipeline | CI action, Makefile, or runner recipe |
| `mistake-to-avoid` | Recurrent trap or anti-pattern | `AGENTS.md` "Avoid" bullet with rationale |

### 1.7 Write the PACK File

Write the output file (for local `SOURCE`: `<source-folder>-lessons.md` next to `SOURCE`; for temp clones: directly to a staging path outside the temp clone or `<STORE>/<owner>-<repo>/packs/<YYYY-MM-DD>-lessons.md` so deleting the clone never deletes the PACK). Include `Source HEAD` and omit/set `Target Recommendation` to `Filed learning (STORE)` when no `TARGET` is given:

````markdown
# Lessons PACK: <SOURCE_NAME>

- **Date:** <YYYY-MM-DD>
- **Source Path:** `<SOURCE_PATH>`
- **Source HEAD:** `<short-sha>` (`<default-branch>`) | `N/A (gh-only)` | `empty`
- **Source Stack:** <Language, framework, tools>
- **Source Access:** full | clone-only | gh-only | empty
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

After the user reviews the PACK, file it into `STORE` (default `hongyime/theprawnlearnings`):

1. Clone or update `STORE` (`git pull --ff-only` on `main`); verify clean working tree before editing.
2. Folder per source repo: `<owner>-<repo>/` (e.g. `bchuminx-healthkaki-pov/`).
3. Copy the reviewed PACK to `<owner>-<repo>/packs/<YYYY-MM-DD>-lessons.md`. Same-day rerun collision: overwrite only if re-harvesting the same `HEAD`, else write `<YYYY-MM-DD>-r2-lessons.md`.
4. Merge into `<owner>-<repo>/lessons.md`: update header metadata (`Date`, `Source HEAD`, `History Inspected`, `Working Tree`); match existing items by title/intent — add new items, update changed evidence/details with an `Updated <YYYY-MM-DD> (packs/<file>)` note, and for retired items keep the heading with status **`[SUPERSEDED <YYYY-MM-DD> — see packs/<file>: <reason>]`** instead of deleting it.
5. Commit and push. The commit message names the source repo and the PACK date.

Filing needs no `TARGET`. If the user wants PACK-only (no filing), stop after 1.7. If the user wants STORE-filing only (no `TARGET`), stop here — do not inspect `TARGET` or run 2.2–2.6.

### 2.2 Inspect TARGET

Before modifying: identify `TARGET` stack (language, package managers, test runners, linters, CI, task runners); read its instruction files, scripts (`scripts/`, `checks/`, `bin/`), and skills (`.agents/skills/`, `.claude/skills/`); note which PACK items are already covered or partially addressed.

### 2.3 Decide for Each Item: Adopt, Adapt, or Skip

- **adopt**: Apply directly as-is (e.g. universal markdown guidelines, stack-independent git practices).
- **adapt**: Translate the item's *intent* and *verification* into `TARGET`'s native tooling (e.g. a Python flake8 rule → an ESLint plugin, or a bash script → a PowerShell / npm script).
- **skip**: Already satisfied by existing configuration or conflicts with `TARGET`'s explicit architecture. Document the reason.

Never copy raw syntax from `SOURCE` if `TARGET` uses a different paradigm. Translate the underlying intent.

### 2.4 Present Plan and Write

Present a decision table to the user:

| Item | Decision | Adaptation Details | Target Location |
|---|---|---|---|
| `<Item>` | `adapt` | Converted to Vitest check | `checks/check-api-contract.sh` |
| `<Item>` | `adopt` | Added to project rules | `AGENTS.md` |
| `<Item>` | `skip` | Already enforced by tsconfig | - |

Wait for user approval before writing. Once approved:

1. **Rules & Conventions**: append under `## Lessons from <source-folder>` in `TARGET/AGENTS.md`. If `CLAUDE.md` or `GEMINI.md` exist, add a reference pointing to `AGENTS.md` rather than duplicating content.
2. **Skills (`procedure`)**: save to `TARGET/.agents/skills/<name>/SKILL.md`. If Claude Code is used, notify the user that it reads `.claude/skills/`, and offer to create a symlink or copy.
3. **Checks & Rules (`rule`, `hook`)**: place executable scripts in `TARGET/checks/` (or the existing script directory); wire checks into `package.json`, `Makefile`, or task runner; add a notice to `TARGET/AGENTS.md`: `"Before finishing a task, run <check-command>."`
4. **Hooks**: configure only for specific agents requested by the user, having the hook invoke the check script.
5. **Conflict Prevention**: never overwrite existing files without confirmation. Merge additions cleanly.

### 2.5 Verification

Execute each newly introduced check script once within `TARGET`: confirm it runs and reports pass/fail without syntax errors, fix any environment setup issues, and do not modify existing codebase logic in `TARGET` unless explicitly instructed.

### 2.6 Handoff Report

Conclude with an adoption summary: files created/modified in `STORE` and `TARGET`, items adapted and their new locations, items skipped and reasons, and next steps / manual decisions required from the user.

Also publish this PACK lessons as a hosted page: hand the finished file to `postplan-upload` and return the Postplan URL next to the local path. Confirm with the user before uploading — see the Postplan rule's gated list.
