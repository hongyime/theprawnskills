---
name: agent-machine-bootstrap
description: >-
  Bootstrap a new or rebuilt machine into a working coding-agent environment:
  base tooling, OpenCode and other agent CLIs, cloud model auth, agent config,
  plugins, MCP servers, and the skill library. Use for "set up a new machine",
  "fresh install", "replicate my setup", "move my agents to another machine",
  "install opencode on this box", or reprovisioning after a wipe. Works driven
  remotely from a working machine or run locally on the target itself.
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Windows, macOS, Linux targets; any CLI agent as the driver"
---

# Agent Machine Bootstrap

Bring a bare machine to a verified coding-agent environment. Detect before
installing, and prove the result with real usage rather than version strings.

## When to use

Use for a new, rebuilt, or freshly wiped machine that should match an existing
agent setup, and for adding a VM or remote host to the fleet. Use
`virtualbox-kali-vm` for the access mechanics of a VirtualBox guest and
`opencode-bedrock-config` for provider auth detail. This skill installs
software and must not invent credentials; every secret is supplied by the user
or minted fresh on the target.

## Execution modes

| Mode | When | Driver |
|---|---|---|
| Remote-driven | Target reachable from a working machine | Run the agent on the working machine; reach the target over SSH, or a hypervisor guest channel while SSH is still absent |
| Local self-bootstrap | Target has a terminal and an agent already, or you are at its console | Run on the target; paste the kickoff prompt below |

A cold target has no skill library yet, so this file will not be discoverable
there. Either drive from a working machine, or fetch this file first:

```bash
gh api repos/<owner>/<repo>/contents/skills/agent-machine-bootstrap/SKILL.md \
  --jq '.content' | base64 -d > /tmp/bootstrap.md
```

## Kickoff prompt

Paste this, filling the bracketed fields. Keep the verification clause; it is
what stops a premature "done".

```text
Bootstrap <target machine/host> into a working coding-agent environment,
matching my existing setup.

Access: <ssh alias | host+user+key | hypervisor guest channel>
Agents wanted: <opencode | claude-code | codex | cursor | all>
Model provider: <e.g. AWS Bedrock, region <region>, model <model-id>>
Credentials: <how I will supply them; mint fresh on the target if possible>
Skill library: <git remote> via clone, then the repo's own installer

Follow the agent-machine-bootstrap skill. Detect the target's OS, shell,
architecture and existing tooling BEFORE installing anything, and tell me
what you found. Batch work per phase. Do not mark this complete until you
have run one real end-to-end request through an installed agent and shown me
its actual output. Report per phase: what succeeded, what failed, and any
step that needs me.
```

## Phase 0 — Preflight

Detect first. Most bootstrap failures are wrong assumptions, not bad commands.

| Detect | Why it changes the plan |
|---|---|
| OS, distro, architecture | Selects install method and binary variant |
| Login shell (`getent passwd <user>`, `$SHELL`) | Decides which rc file receives `PATH` and env exports. A zsh user never reads `~/.bashrc` |
| Existing node/python/git and versions | Avoids reinstalling, and reveals version managers |
| Node version manager present (nvm, fnm, volta, asdf) | A managed node injects its own `PATH`, which can win over later exports and shadow a standalone binary |
| Privilege model (`sudo -n true`) | Passwordless sudo vs password-per-call changes every script |
| Outbound network path (VPN, proxy, killswitch) | A default-drop VPN firewall blocks inbound access and can throttle or reset downloads |
| Free disk and RAM | Agent binaries and dependency trees are large |
| Existing agent configs | Never clobber a working config; merge instead |

## Phase 1 — Base tooling

Install git, curl, unzip, a C toolchain, python3, and node. Prefer the
platform's current node rather than a distro default that is years stale.
Record the chosen node source; later phases depend on knowing it.

## Phase 2 — Agent CLIs

Install only the agents requested. Prefer each vendor's documented installer
over a hand-rolled path. For OpenCode, a standalone binary avoids coupling to
a version manager; a package-manager install is fine but then the agent lives
under that manager's prefix and inherits its `PATH` behavior.

After install, resolve the binary explicitly (`command -v`, or a bounded
`find` under the home directory) and export `PATH` in the rc file the detected
shell actually reads.

## Phase 3 — Cloud model auth

Configure credentials on the target. Mint fresh, separately revocable
credentials for each machine; do not copy secrets between hosts. Where a
provider supports both a long-lived API key and a full credential chain,
prefer whichever the agent reads natively with no custom code.

Verify identity with the provider's own whoami-style call before touching
agent config, so a later failure is unambiguous.

## Phase 4 — Agent configuration

Write the agent's config, then confirm the file parses. Config is typically
read once at startup, so restart the agent after any change.

| Setting | Why it matters |
|---|---|
| Provider credential selector (for example a named profile) | Some providers do not read an on-disk credentials file without being told which profile to use |
| Region or endpoint | Cross-region or global model routing is anchored to a specific region |
| Per-agent model overrides | Plugin-contributed subagents can carry their own hardcoded model; a global default does not override them |
| Permissions | Match the source machine rather than loosening defaults |

## Phase 5 — Plugins and MCP servers

Pin plugin versions rather than floating ranges, so the target matches the
source machine exactly. Install, then confirm the package actually landed in
the expected directory — a timed-out installer can leave a partial tree.

Register MCP servers in the agent's own native config shape. A config shape
copied from a different harness may be silently ignored.

## Phase 6 — Skill library

Clone the library with git and run the repository's own installer. Do not
depend on a cloud-sync client, and do not mount or symlink another machine's
synced folder. Use the installer's dry-run first, then apply, then its check.

Keep the installer's own rules: never run a command the library documents as
forbidden, and let it choose copies or symlinks per platform.

## Phase 7 — Verification gates

Version strings prove installation, not function. Required evidence:

| Gate | Evidence |
|---|---|
| Agent runs | Version output from the resolved binary |
| Credentials valid | Provider identity call returning an account/principal |
| Config loads | Agent starts without a config error |
| Model reachable | One real request returning expected text |
| Plugin layer active | Agent reports its expected persona/agent name, not a bare default |
| Skills present | Expected skill count in the installed location |
| Shell persistence | A fresh interactive shell resolves the binary and env vars |

The model-reachable gate is the one that catches almost every real
misconfiguration. Run it before reporting success.

## Known traps

Each of these has produced a confusing, time-consuming failure.

| Trap | Handling |
|---|---|
| Exports written to the wrong rc file | Detect the login shell first; zsh ignores `~/.bashrc` |
| Login vs interactive shell differences | A login shell may skip `~/.zshrc`; verify with an interactive shell |
| Version manager shadowing a standalone binary | Order `PATH` deliberately, and confirm which path actually resolves |
| A CLI hanging with no output over SSH | It is reading stdin with no PTY; use `ssh -n` or redirect from `/dev/null` |
| Long install killed when the client times out | Detach on the target (`nohup ... > log 2>&1 &`) and poll the log |
| Installer appears stuck | Compare accumulating CPU time between samples; a deadlocked process accumulates none |
| Global package install permission denied | Use the platform's documented elevation, or set a user-writable prefix |
| Package manager blocks install/postinstall scripts | Approve the specific packages, then reinstall so the scripts run |
| Transient download resets mid-transfer | Retry before re-diagnosing; a constrained network path can reset long transfers |
| Unattended upgrades reboot the target mid-run | An orderly shutdown entry in the prior boot log confirms a reboot; resume, do not restart from scratch |
| Generated files conflict on merge | Regenerate with the project's authoritative generator rather than hand-merging |
| Multiple generators for one artifact | Use whichever the project's CI validates with |
| Copying secrets between machines | Mint per-machine credentials; rotate anything that passed through a chat or log |

## Report

State the detected environment, the phases completed, the exact evidence for
each verification gate, and anything still requiring the user. Name any
credential that must be rotated. A completed install with no successful real
request is an incomplete bootstrap, and should be reported as such.

## Prerequisites and provenance

Requires network access on the target, privilege to install software, and
user-supplied or freshly minted credentials. Derived from a live
end-to-end bootstrap of a Linux guest from a Windows host. Contains no
credentials, hostnames, or machine-specific paths. Load companions through
`skill-router`.
