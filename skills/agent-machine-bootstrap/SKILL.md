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
  version: "2.1.0"
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

Machine-specific values belong in a local inventory held outside this
repository, or at minimum ignored by version control. Keep the operator's
baseline application list, per-machine records and credential-rotation log
there, not here. Never commit a filled-in inventory, and never paste secrets
into a chat, issue or commit message.

Commit messages are as public and as permanent as the files themselves. Apply
the same rule to them.

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
| Desktop apps wanted | messaging, communication and GUI utilities | Requires a desktop session; skip on headless targets |
| Sync client wanted | which service, and the client to use per platform | Some services have no first-party client on every platform |
| Headless or desktop | headless, desktop | Decides whether layer 9 applies at all, and whether browser auth flows work |

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
Desktop apps:      <list or none>
Sync client:       <service + client, or none>
Session type:      <headless | desktop>

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
→ 9 desktop and sync apps → 10 workload tooling → verification
```

| # | Layer | What goes in | Why it sits here | Gate | Classic failure |
|---|---|---|---|---|---|
| 0 | Preflight detection | OS, distro, version, architecture, login shell, existing runtimes, version managers, privilege model, outbound path including VPN or proxy, free RAM and disk, existing agent configs, desktop versus headless | Every later choice branches on these. Detecting costs seconds; a wrong assumption costs an hour | Findings reported before any install | Assuming one shell when another is the login shell, so every `PATH` export lands in a file nothing reads |
| 1 | Base tooling | Version control, a downloader, an archive extractor, a C/C++ toolchain | Native modules in later layers compile against the toolchain; absent, they fail with misleading errors | Each binary resolves | No compiler, so a native plugin or MCP dependency fails deep inside an install log |
| 2 | Runtimes | Language runtimes the agents and MCP servers need, at current versions. Choose deliberately between a system package, a vendor repository and a version manager, then record the choice | Agent CLIs and MCP servers are runtime-hosted. The install method sets the prefix, which decides `PATH` precedence in layer 3 | Version output, and which path resolves | A distro default years stale, or a version manager silently winning `PATH` later |
| 3 | Agent CLIs | Only the requested agents, each via its vendor's documented installer. Then resolve each binary and export `PATH` in the rc file layer 0 detected | Needs runtimes. Must precede config because you must know which binary wins before configuring it | Version from the winning path | Two installs of one agent, with the unintended one shadowing |
| 4 | Credentials and model access | Mint fresh, per-machine, separately revocable credentials. Prefer the source the agent reads natively with no custom code. Verify caller identity before writing config. If this machine will hold a second account alongside an existing one, see `agent-account-isolation` | Before config, so a later failure is unambiguous: auth is already proven | Provider identity call returns a principal | Copying secrets between hosts, or debugging "auth broken" when the real fault was a config typo |
| 5 | Agent configuration | Credential selector such as a named profile, region or endpoint, per-agent model overrides, permissions, instruction and memory files | Needs a working binary and proven credentials. Config is read once at startup, so restart after every change | Parses, and the agent starts clean | A provider ignoring an on-disk credentials file because no profile was named, or editing config without restarting |
| 6 | Plugins and MCP servers | Pin exact plugin versions. Confirm the package actually landed. Register MCP servers in the agent's own native config shape | These load into the agent, so it must already run and be configured | Each server reports connected; plugin layer active | A timed-out installer leaving a partial tree that looks installed, or a config shape copied from another harness being ignored |
| 7 | Skill library | Clone with version control, then run the repository's own installer: dry-run, apply, check | Skills are consumed by a working agent, so this is pointless earlier | Expected skill count present | Depending on a cloud-sync client instead of a clone, or running a command the library documents as forbidden |
| 8 | Remote access and fleet | SSH server, key deployment, mesh VPN join, reachability confirmed in both directions | After the machine is useful, so transport and setup are not debugged simultaneously | Driving machine connects non-interactively | A VPN killswitch dropping the management subnet, or a key whose passphrase is not genuinely empty and so cannot sign non-interactively |
| 9 | Desktop and sync apps | Messaging and communication clients, cloud storage or file-sync clients, and any GUI utilities the operator expects | Needs base tooling and often a desktop session; irrelevant to proving the agent environment works, so it comes after verification-critical layers | Each launches, and any sync client completes one successful sync | Installing a GUI app on a headless target, or a proprietary sync service with no first-party client for the target platform, needing a third-party client or an object-storage bridge instead |
| 10 | Workload tooling | Container runtimes, databases, language toolchains, and anything specific to the work this machine will do | Deliberately last: none of it is needed to prove the agent environment works, and it competes for the resources sized above | Only what the workload needs | Installing tens of gigabytes of container images before discovering the agent never authenticated |

The **order** is fixed; **membership is not**. Which items appear in layers 3,
9 and 10 is defined by the operator's baseline, not by this skill — a container
runtime may be a hard requirement on every machine and still belongs last in
sequence, because it does not gate whether the agent environment works.

Layers 0 to 8 are structurally required for a remotely driven machine. A purely
local machine can stop at 7. See
[baseline inventory](references/baseline-inventory.md) for the operator's own
must-have list, the OpenCode plugin and model baseline, and the per-machine
template.

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
