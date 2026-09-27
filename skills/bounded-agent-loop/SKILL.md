---
name: bounded-agent-loop
description: Run a user-authorized, bounded repair loop with explicit acceptance commands, isolated ownership, attempt and time limits, failure stop conditions, and a resumable handoff. Use for repeated agent repair work, not routine one-pass edits or unattended scheduling.
license: MIT
---

# Bounded agent loop

Choose this only when a task has a concrete deliverable and runnable acceptance
criteria. Reuse the current host's native agent facilities when they suffice.
For a separate CLI, resolve `cli-agent-router` and inspect its installed help.
Use the configured model unless the task specifies one; never invent model IDs,
prices, permissions, or flags. Existing task authorization carries forward.

## Define the run

1. Read project instructions and `.agents/STATE.md`. Identify a clean disposable
   branch/worktree, a single writer, exact editable files and immutable tests.
   Keep active worktrees and private transcripts outside the OneDrive library.
2. Record the task, baseline commit, acceptance command, scope, maximum three
   attempts, wall-clock deadline, and per-command timeout. If the CLI exposes an
   enforceable cost limit, set it; otherwise report that there is no hard cost cap.
3. Run acceptance once before editing. Give the worker the failure, constraints,
   file ownership and remaining budget. Do not weaken tests to obtain a pass.
4. After each attempt, inspect changed files, test exits and remaining budget.
   Stop on success, timeout/cancellation, scope or Git-history changes, missing
   tools/credentials, exhausted budget, or a repeated failure without progress.
   The helper conservatively treats the same nonzero acceptance exit with an
   unchanged file snapshot as no progress, even if log text/timings differ.
5. Independently review the final patch using `requesting-code-review` and run
   project CI. Report a patch/branch; merge or deployment follows that task's
   actual authorization. Do not silently enable schedules or automatic merging.

## Optional bundled supervisor

`scripts/run_loop.py` is a standard-library process supervisor for a clean Git
worktree. It runs argument arrays without a shell. It checks tracked and visible
untracked files plus HEAD/index after commands, and writes private logs and a
JSON checkpoint to a caller-selected new directory outside the worktree.
Repositories containing Git submodules are rejected before launch: this helper
does not recursively supervise submodule content/history.
Git metadata and process cleanup have bounded grace periods beyond command
execution deadlines (Windows tree cleanup retries at most twice, 45 seconds
each). A `cleanup-failed` result requires inspecting/stopping surviving children
before resuming; it is not an ordinary task timeout or a successful stop.
These checks detect scope changes; **they are not a security sandbox**. They do
not monitor ignored files, outside paths, transient changes or external effects.
Use host permissions and a disposable worktree for containment. Workers must run
foreground children; detached daemons are outside this helper's contract.

Copy `examples/plan.json` to a private location and replace every placeholder.
Use absolute executable paths when PATH differs across hosts. On Windows, npm
`.cmd` shims need an explicit interpreter; prefer the CLI's native executable or
Node plus its JavaScript entrypoint. Do not add `shell=True` to work around it.

Resolve `$skillDir` to the directory containing the loaded `SKILL.md`; an
on-demand skill may live in a library clone rather than an installed agent root.

```powershell
$skillDir = Split-Path -Parent $loadedSkillPath
python (Join-Path $skillDir 'scripts/run_loop.py') --plan $planPath --run-dir $newRunDirectory
```

POSIX: `python3 "$skillDir/scripts/run_loop.py" --plan "$planPath" --run-dir "$newRunDirectory"`.
The plan owns a worker command and an acceptance command; no agent CLI is bundled.
Both receive the worktree as their working directory. Each worker invocation gets
`PRAWN_LOOP_ATTEMPT` and `PRAWN_LOOP_FEEDBACK` (previous verifier-log path).
Nonzero worker exit stops the run. An acceptance failure allows another attempt.

An interrupted checkpoint is deliberately not auto-replayed. Read its logs,
inspect all changes and child processes, then create a handoff with elapsed time,
attempts consumed and remaining budget. A human/agent resumer must explicitly
carry those remaining limits into a new plan; restarting is not a budget reset.
The helper refuses an existing run directory to avoid overwriting evidence.
Use `session-handoff` and existing STATE/JOURNAL; do not add a memory database.

See `references/roles.md` for portable role prompts and `cli-agent-router` for
the tmux/dmux host adapter. Review failure tests under the repository's `tests/`
before changing supervisor behavior; those are maintainer tests, not installed
runtime dependencies.

## Provenance

Adapted from ECC `continuous-agent-loop`, `loop-design-check` and
`team-agent-orchestration` at revision
`e482e579415fde18357cafce70f177ae19fd7f03`. The Python supervisor is a local
implementation, not ECC runtime code. MIT notice: `LICENSE.txt`.
