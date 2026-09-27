# tmux and dmux host adapter

tmux keeps a terminal process on its execution host. A laptop reconnects to that
host using its existing SSH/Tailscale access; OneDrive does not move the running
process. Git transfers committed work and `session-handoff` transfers context.
Do not store active worktrees in the canonical OneDrive skill library.

## Check the actual host

Native PowerShell, WSL Ubuntu and a remote Linux shell are different hosts for
paths, processes and credentials. Check `pwd`, `git status`, `git branch --show-current`,
`command -v` and version output inside the chosen environment. A Windows npm shim
on WSL's PATH can launch a Windows executable: verify actual file reads and edits
in the intended worktree before calling that adapter ready.

Use the installed tmux documentation (`tmux list-commands`, `man tmux`). The
pilot used tmux 3.4, Git 2.43.0 and Node 20.20.2 in Ubuntu 24.04 WSL. These are
observed pilot versions, not a requirement to replace working installations.

## tmux first

Use a unique socket/session for a pilot so server options cannot affect existing
sessions. In a POSIX shell, after choosing an absolute local `$repo`:

```bash
tmux -L prawn-pilot new-session -d -s work -c "$repo"
tmux -L prawn-pilot display-message -p -t work '#{pane_current_path} #{pane_pid}'
tmux -L prawn-pilot attach-session -t work
# Detach with Ctrl-b d; reconnect and run the same attach command.
```

`capture-pane` verifies an existing pane from another client; it is not evidence
of SSH disconnect/reconnect or interactive reattachment. Test the actual access
path before claiming that. Do not change SSH configuration for a local pilot.
Stop only the worker/session owned by the task, and check for surviving children.
A detached session is not a scheduler or a bound on cost/runtime.

## dmux is an optional external runtime

Primary source: [dmux v5.11.1](https://github.com/standardagents/dmux/tree/v5.11.1).
Its package, agent CLIs and optional inference provider are external dependencies;
this skill does not bundle or silently install them. Use a user-owned isolated
prefix for an authorized pilot, never `sudo npm install -g`:

```bash
npm install --prefix "$pilotRoot/tools" --ignore-scripts --no-audit --no-fund dmux@5.11.1
```

Inspect the pinned package's lifecycle scripts and requirements first. Skipping
install scripts can disable optional native features; test the features used.
Do not assume `dmux --help` is read-only: v5.11.1 enters application startup and
can create `.dmux/` and a `.gitignore` entry in the current directory. Start it
only from the disposable Git repository, inside the pilot tmux server.

Before startup, create project-local `.dmux/settings.json` with:

```json
{
  "permissionMode": "",
  "enableAutopilotByDefault": false,
  "enableGoalModeByDefault": false,
  "enableNotifications": false
}
```

The pinned release defaults to permission bypass and autopilot. Project settings
override its global settings; verify the effective values before creating workers.
For a pinned pilot, also disable `updateSettings.autoUpdateEnabled` in the
project's generated `.dmux/dmux.config.json`, then verify the package version.
Pinning the npm install alone does not disable dmux's runtime updater.
An empty permission mode leaves the agent's own default in force. It does not
prove a sandbox exists. Decline optional global tmux configuration and inference
provider setup unless needed and already authorized. No credentials in Git.

dmux provides panes plus Git worktrees/branches. Each worker owns its worktree;
the integrator owns shared files and acceptance checks. The `m` key opens a menu:
merge actions can commit and clean up worktrees. Inspect changes/tests first and
use only the merge authority granted for the task. Do not interpret merge as
copying a transcript, and do not automatically resolve an intentional conflict.

Pilot checklist: two independent tasks; an intentional overlapping edit; failed
acceptance; cancellation and child cleanup; reconnect and state recovery; a
handoff to another CLI with the correct root/branch. Record which were exercised
through dmux itself versus directly through Git/tmux or a controlled test worker.
Missing inference/auth or a broken host adapter is a bounded failed pilot, not a
reason to turn on bypass permissions or change global configuration.

Keep reusable task state in the existing STATE/JOURNAL/handoff convention and
private runtime logs outside public Git. For runtime limits use
`bounded-agent-loop`; dmux's pane UI alone does not enforce those limits.
