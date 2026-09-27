---
name: cli-agent-router
description: Choose and launch an available CLI agent for authorized delegation, independent review or isolated implementation. Use for agent selection, host adapters, bounded parallel work, and tmux/dmux worktree coordination.
---

# CLI agent router

First honor the user's selected agent. Otherwise choose by verified local
capability, authentication, tool access and task scope. Use configured model
defaults unless the task specifies a model; check current CLI help instead of
guessing model IDs, context sizes, prices or flags.

## Route the work

| Need | Route |
|---|---|
| Small change within the current agent's abilities | Complete it here |
| Independent review with native host subagents available | Use the host's review role when delegation is authorized |
| Explicit Codex execution | Read `codex`; check `codex --version` and `codex exec --help` |
| Explicit Claude execution | Check `claude --version` and `claude --help`; inspect local authentication status |
| Provider/MCP tools configured in OpenCode | Read `opencode-cli`; verify the actual provider and tools |
| Another installed CLI, such as Gemini | Inspect its local help and authentication; no assumed skill or free quota |
| Repeated repair with acceptance commands | Read `bounded-agent-loop` |
| Persistent terminal or isolated multi-worktree pilot | Read [terminal workflows](references/terminal-workflows.md) |

Availability is not readiness: a command can exist but lack credentials, a
provider, network access or compatible filesystem paths. Never copy auth files
through this repository. Never print credentials during readiness checks.

PowerShell: `Get-Command codex,claude,gemini,opencode -ErrorAction SilentlyContinue`.
POSIX: `command -v codex claude gemini opencode`. Inspect resolved shims in WSL:
a Windows executable may require Windows paths and use Windows authentication.
A successful version command does not prove its working directory or tools work.

## Delegate explicitly

Give the worker a concrete task, root/branch, instructions, exact file ownership,
acceptance command, deadline and output format. Separate read-only exploration
from implementation. Reuse the portable prompts in `bounded-agent-loop` or
`cavecrew`; these prompt roles are not universally registered agent names.

Use separate worktrees for independent writers and one integrator. Do not run
multiple writers against the same checkout. Serialize dependent work. Preserve
the worker's actual exit, stderr and test evidence; a completion sentence alone
is not proof. Review its diff and run acceptance independently.

Keep argument arrays as arrays; do not interpolate user prompts into shell code.
Use stdin or a private prompt file when supported. Give each run a unique local
log directory. Background PowerShell helpers use `Start-Process -WindowStyle
Hidden`; interactive windows are only for a user-requested visible session.

## Stop and hand off

Apply only the permissions required by the authorized task. Do not silently
enable permission bypass, autopilot, schedules, automatic commits or merging.
A preauthorized edit does not need another confirmation at each iteration.
On unavailable tools, cancellation, repeated failure or exhausted budget, record
the exact limitation and remaining work using `session-handoff` and
`cross-harness-state`. Resume a specific task/session after checking its root,
branch and remaining budget; never choose an unrelated "last" session.
