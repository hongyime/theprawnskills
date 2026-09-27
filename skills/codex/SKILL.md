---
name: codex
description: Run the installed Codex CLI for user-requested analysis, review, implementation or resuming a specific task, using verified local flags and configured model defaults.
---

# Codex CLI adapter

Read repository instructions and durable state before delegation. Confirm the
task root and whether the user authorized analysis or edits. Carry that
authorization forward without adding a confirmation after every command.

## Check the installed interface

Run `codex --version`, `codex exec --help` and, for continuation,
`codex exec resume --help`. Use `codex login status` to check readiness without
reading authentication files. Local help is authoritative for this installation;
flags and available model names change. Preserve diagnostics on failure.

Use the configured model/reasoning defaults unless the task names an override.
Do not hardcode model prices, benchmark scores or an invented model suffix.
Use `--sandbox read-only` for inspection and `--sandbox workspace-write` for
authorized repository edits when supported. A CLI flag is not proof of the
effective sandbox; inspect launch diagnostics and the host's actual enforcement.

## Launch a bounded task

Current example, verify flags against the installed CLI first:

```powershell
Get-Content -LiteralPath $promptPath -Raw |
  codex exec --cd $repoPath --sandbox read-only --ephemeral --json --output-last-message $resultPath -
```

POSIX equivalent:

```bash
codex exec --cd "$repoPath" --sandbox read-only --ephemeral --json \
  --output-last-message "$resultPath" - < "$promptPath"
```

Choose a unique private result/log path outside a public repository. Capture the
process exit and stderr as well as JSON events; do not suppress errors with
`2>/dev/null`. A final answer is not evidence that tests passed or edits stayed
in scope. Inspect tool events, changed files and independent acceptance results.

For edits, change the sandbox mode to match the authorized task. Use the
supervisor in `bounded-agent-loop` when repetition/deadlines are needed.
The supervisor accepts executable argument arrays, so Windows npm `.cmd` shims
may need Node plus the CLI's actual JavaScript entrypoint or a native binary.
Do not use a shell just to interpolate a prompt. Keep foreground workers alive
until their children finish; detached processes need explicit lifecycle ownership.

Do not copy legacy `--full-auto`, `--cwd` or `--task-file` examples into a
command unless this installed version advertises them. Do not bypass the Git
repository check for a normal repository. Broader filesystem/network access
must fit the task's actual authority and host rules, not an automatic fallback.

## Continue or report failure

An ephemeral run is not a resumable saved session. For a persistent session,
record its explicit ID and repository/branch; use the installed resume help to
build the continuation command. Avoid `resume --last` when multiple agents or
projects are active. Recheck scope and remaining budget before resuming.

Retry a transient failure within the already authorized bounds. Missing
credentials or a required user choice becomes a concise handoff, not a claim
of success. Summarize changes, actual checks, remaining risks and the precise
next step. Use `requesting-code-review` before integration.
