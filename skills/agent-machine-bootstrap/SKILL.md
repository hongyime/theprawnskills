---
name: agent-machine-bootstrap
description: >-
  Bootstrap any new, rebuilt or virtual machine into a working coding-agent
  environment: sizing, base tooling, runtimes, agent CLIs, model credentials,
  agent config, plugins, MCP servers, skill library, remote access and
  verification. Use for "set up a new machine", "fresh install", "replicate my
  setup", "move my agents to another machine", "what do I need on a new box",
  or reprovisioning after a wipe. OS-agnostic; covers physical, VM and VPS
  targets, driven remotely or run locally.
license: MIT
metadata:
  author: Local setup
  version: "2.0.0"
  platform: "Windows, macOS, Linux and VM/VPS targets; any CLI agent as driver"
---

# Agent Machine Bootstrap

Bring a bare machine to a verified coding-agent environment. Detect before
installing, install in dependency order, and prove the result with real usage
rather than version strings.

## When to use

Use for a new, rebuilt or freshly wiped machine, a new VM or VPS, or adding a
host to an existing fleet. Use `virtualbox-guest-access` for hypervisor guest
access mechanics and `opencode-bedrock-config` for one provider's auth detail.
This skill installs software. It must never invent credentials: every secret is
supplied by the operator or minted fresh on the target.

## Privacy contract

This file is generic on purpose. It names publicly documented products, and
never hosts, addresses, usernames, account identifiers, hardware inventory,
private project names or credentials.

Machine-specific values belong in a local, version-control-ignored inventory on
the driving machine, following the same pattern as any private machine registry
the library already ignores. Never commit the filled-in inventory, and never
paste secrets into a chat or issue.

### Inventory the agent needs

Supply these per target. Anything omitted becomes a detection step or a
question, not an assumption.

| Field | Example shape | Notes |
|---|---|---|
| Target identity | `<alias>` | Alias only; keep real hostnames local |
| Access method | ssh alias, host+user+key, hypervisor guest channel, console | Determines whether remote-driven is possible |
| Elevation | passwordless sudo, password-per-call, admin account | Changes every install script |
| Agents wanted | subset of the agent CLIs you use | Install only what is asked |
| Model provider + region + model id | provider, region, model identifier | Region matters for cross-region routing |
| Credential source | mint fresh on target, operator-supplied, existing SSO | Prefer mint-fresh |
| Skill library remote | git remote | Clone, never sync-mount |
| MCP servers wanted | server names | Each may need its own auth |
| Container runtime needed | yes/no | Large disk and RAM impact |
| Fleet integration | mesh VPN, SSH inbound, shares | Often blocked by a VPN killswitch |

## Kickoff prompt

Paste this and fill the bracketed fields from your private inventory. Keep the
final clause: it is what prevents a premature completion claim.

```text
Bootstrap <target alias> into a working coding-agent environment.

Access:            <ssh alias | host+user+key | guest channel | console>
Elevation:         <passwordless sudo | password per call | admin>
Agents wanted:     <list>
Model provider:    <provider>, region <region>, model <model-id>
Credentials:       <mint fresh on target | I will supply | existing SSO>
Skill library:     <git remote>
MCP servers:       <list or none>
Container runtime: <yes | no>
Fleet access:      <mesh VPN | SSH inbound | none>

Follow the agent-machine-bootstrap skill.

Detect the target's OS, distro, architecture, login shell, existing runtimes,
version managers, privilege model and outbound network path BEFORE installing
anything, and report what you found before proceeding.

Work in the skill's layer order. Batch each layer into one operation where the
transport is slow. Never copy secrets between machines.

Do not report completion until every verification gate in the skill passes,
including one real end-to-end model request whose actual output you show me.
Report per layer: what succeeded, what failed, what needs me, and any
credential I must rotate.
```

## Sizing

Agent processes, not the OS, dominate resource use on these machines. A single
long-running agent session can hold well over a gigabyte of resident memory,
and several agents plus a build will outweigh everything else present.

Plan capacity from concurrency rather than from installed tool count:

| Component | Reserve | Notes |
|---|---|---|
| OS, shell, base tooling | 1–2 GiB RAM | Higher on a desktop environment |
| Each concurrent agent session | ~2 GiB RAM | Observed resident sets range widely; long sessions grow |
| Each concurrent build or test run | ~4 GiB RAM | Compilers and bundlers spike |
| Container runtime, if used | 1–2 GiB RAM | Excludes the containers themselves |
| Headroom | +25% | On top of the sum |
| vCPU | 2 baseline, +1 per concurrent agent, +2 per concurrent build | Not benchmarked; a planning heuristic |

Disk, additive: OS 15–25 GiB; runtimes and global packages ~5 GiB; each agent
binary up to ~0.5 GiB; skill library well under 1 GiB; repository clones and
agent worktrees per your own footprint; container images 20–40 GiB if a runtime
is installed; then +25%. Build caches grow unbounded — budget for pruning.

Treat all of the above as planning estimates, not measurements. Measure the
real machine before committing to a paid tier.

## Layer order

Later layers depend on earlier ones. Installing out of order is the most common
cause of confusing failure.

```text
0 preflight → 1 base tooling → 2 runtimes → 3 agent CLIs → 4 credentials
→ 5 agent config → 6 plugins + MCP → 7 skill library → 8 remote access
→ 9 optional workload tooling → verification
```

### Layer 0 — Preflight detection

| Detect | Why it changes the plan |
|---|---|
| OS, distro, version, architecture | Selects install method and binary variant |
| Login shell | Decides which rc file receives `PATH` and env exports; a zsh user never reads a bash rc |
| Existing runtimes and versions | Avoids reinstalling; reveals what is already depended on |
| Version manager present | A managed runtime injects its own `PATH` and can shadow a standalone binary |
| Privilege model | Passwordless elevation versus password-per-call changes every script |
| Outbound path: VPN, proxy, killswitch | A default-drop VPN firewall blocks inbound access and can reset long downloads |
| Free disk and RAM against the sizing table | Decide before installing, not after |
| Existing agent configs | Merge; never clobber a working config |
| Desktop versus headless | Affects browser-based auth flows and any GUI tooling |

### Layer 1 — Base tooling

Version control, a downloader, an archive extractor, and a C toolchain for
native modules. Without the toolchain, later native builds fail confusingly.

### Layer 2 — Runtimes

Install the runtimes your agents and MCP servers need, at current versions
rather than a stale distro default. Decide deliberately between a system
package, a vendor repository, and a version manager — then record the choice,
because later `PATH` resolution depends on it.

### Layer 3 — Agent CLIs

Install only the requested agents, each via its vendor's documented installer.
A standalone binary avoids coupling to a version manager; a package-manager
install is fine but the binary then lives under that manager's prefix and
inherits its `PATH` behaviour.

Afterwards resolve each binary explicitly and export `PATH` in the rc file the
detected shell actually reads. Confirm which path wins when more than one
install of the same agent exists.

### Layer 4 — Credentials and model access

Mint fresh, separately revocable credentials per machine. Do not copy secrets
between hosts, and rotate anything that has passed through a chat, log or
screenshot.

Prefer whichever credential source the agent reads natively with no custom
code. Verify identity with the provider's own caller-identity call before
writing agent config, so a later failure is unambiguous.

### Layer 5 — Agent configuration

Write config, confirm it parses, then restart the agent — config is typically
read once at startup.

| Setting | Why it matters |
|---|---|
| Credential selector, such as a named profile | Some providers ignore an on-disk credentials file unless told which profile to use |
| Region or endpoint | Cross-region and global model routing is anchored to a specific region |
| Per-agent model overrides | Plugin-contributed subagents can carry a hardcoded model; a global default does not override them |
| Permissions | Mirror the source machine rather than loosening defaults |
| Instruction and memory files | Agents read different filenames; place each where that agent looks |

### Layer 6 — Plugins and MCP servers

Pin plugin versions rather than floating ranges so the target matches the
source. Install, then confirm the package actually landed — a timed-out
installer leaves a partial tree that looks installed.

Register MCP servers in the agent's own native config shape; a shape copied
from a different harness may be silently ignored. Each server may need its own
credentials and its own verification.

### Layer 7 — Skill library

Clone with version control and run the repository's own installer: dry-run,
apply, then its check. Do not depend on a cloud-sync client, and do not mount
or symlink another machine's synced folder. Respect any command the library
documents as forbidden, and let the installer choose copies or links per
platform.

### Layer 8 — Remote access and fleet integration

If this machine will be driven remotely, install the SSH server, deploy a key,
and confirm from the driving machine. Generate keys with a genuinely empty
passphrase, or non-interactive automation cannot sign with them.

On a mesh VPN, join the network and confirm reachability in both directions. If
a VPN killswitch is active, allow the management subnet through the VPN's own
allowlist rather than editing firewall rules it will regenerate.

### Layer 9 — Optional workload tooling

Container runtimes, databases, language toolchains and anything specific to the
work this machine will do. Deliberately last: none of it is needed to prove the
agent environment works, and it competes for the resources sized above.

## OS differences that actually matter

| Concern | Windows | macOS | Linux | VM or VPS guest |
|---|---|---|---|---|
| Shell and env persistence | Profile script; user versus machine scope | Login versus interactive shell files | Login shell may not read the interactive rc | Same as its distro |
| Path separators and quoting | Backslashes; nested quoting through layers breaks easily | POSIX | POSIX | POSIX |
| Elevation | Administrator prompt | `sudo`, plus signed-binary prompts | `sudo` policy varies | Often passwordless by image default |
| Package source | Per-vendor installers or a package manager | Package manager or vendor installer | Distro repo, vendor repo, or upstream installer | As distro, minus GUI |
| Native builds | Toolchain is a separate install | Command-line tools package | Build-essential equivalent | Same as distro |
| Browser auth flows | Available | Available | May be headless — use device-code flows | Frequently headless |
| Network | Host firewall profiles | Host firewall | Host firewall plus any VPN killswitch | Hypervisor networking mode decides reachability |
| Clock skew | Rare | Rare | Rare | Common after suspend; breaks signed API calls |

## Verification gates

Version strings prove installation, not function. All of these, with evidence:

| Gate | Evidence |
|---|---|
| Agent resolves | Version output from the path that actually wins |
| Credentials valid | Provider caller-identity call returning a principal |
| Config parses | Agent starts with no config error |
| Model reachable | One real request returning expected text |
| Plugin layer active | Agent reports its expected persona or agent name, not a bare default |
| Subagent routing | A delegated task runs on the intended model, not a fallback |
| MCP servers connect | Each server appears connected at startup |
| Skills present | Expected skill count in the installed location |
| Shell persistence | A fresh interactive shell resolves binaries and env vars |
| Remote access | Driving machine connects non-interactively |
| Resources adequate | Free RAM and disk exceed the sizing table for intended concurrency |

The model-reachable and subagent-routing gates catch almost every real
misconfiguration. Run them before claiming success.

## Known traps

Each has produced a confusing, time-consuming failure.

| Trap | Handling |
|---|---|
| Exports written to the wrong rc file | Detect the login shell first |
| Login versus interactive shell divergence | Verify with an interactive shell, not only a login one |
| Version manager shadowing a standalone binary | Order `PATH` deliberately; confirm which path resolves |
| Two installs of one agent | Decide which wins and remove or ignore the other |
| A CLI hanging with no output over SSH | It is reading stdin with no PTY; close stdin explicitly |
| Long install killed when the client times out | Detach on the target and poll a log file |
| Installer appears stuck | Compare accumulating CPU time between samples; a deadlocked process accumulates none |
| Global package install permission denied | Use documented elevation or set a user-writable prefix |
| Package manager blocks install scripts | Approve the specific packages, then reinstall so the scripts run |
| Transient download reset mid-transfer | Retry once before re-diagnosing; constrained paths reset long transfers |
| Unattended upgrades reboot mid-run | An orderly shutdown entry in the prior boot log confirms a reboot; resume rather than restart |
| Key rejected despite correct contents | A key with a passphrase cannot sign non-interactively; confirm the passphrase is genuinely empty |
| Server accepts key then connection closes | Client-side signing failure, not server rejection; read both sides' logs |
| Generated file conflicts on merge | Regenerate with the project's authoritative generator |
| Several generators for one artifact | Use whichever the project's CI validates with |
| Copying secrets between machines | Mint per-machine credentials; rotate anything exposed |
| Config edited but behaviour unchanged | Most agents read config once; restart |

## Report

State the detected environment, the layers completed, explicit evidence per
verification gate, and anything still requiring the operator. Mark unverified
items as unverified rather than omitting them. Name any credential that must be
rotated. An install with no successful real request is an incomplete bootstrap
and must be reported as such.

## Prerequisites and provenance

Requires network access on the target, privilege to install software, and
operator-supplied or freshly minted credentials. Distilled from live
end-to-end bootstraps. Contains no credentials, hosts, addresses, account
identifiers or hardware inventory by design. Load companions through
`skill-router`.
