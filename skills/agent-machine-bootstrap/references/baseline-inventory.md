# Baseline inventory and per-machine template

Companion to the `agent-machine-bootstrap` skill. This file is **committed and
public**: it carries the baseline list, the layer mapping, sizing guidance and
an empty template.

**Filled-in per-machine values do not belong here.** Copy the template below
into a gitignored sibling — any `*.local.md` name is already ignored — and keep
aliases, access methods, providers, regions and the rotation log there. Never
record a credential value in either file.

## Baseline must-haves

Present on every machine unless a target cannot support it. The layer column is
sequence, not priority: a must-have can still be installed last.

| Category | Item | Layer | Notes |
|---|---|---|---|
| Agent CLI | opencode | 3 | Standalone binary preferred over a version-manager install |
| Agent CLI | codex | 3 | |
| Agent CLI | claude | 3 | |
| Agent CLI | agy | 3 | |
| Agent CLI | kiro | 3 | |
| Agent CLI | gemini | 3 | |
| Fleet | Tailscale | 8 | Join the tailnet, then confirm reachability both directions |
| Desktop | Beeper | 9 | Desktop session only; nothing to install on a headless target |
| Sync | Cloud file-sync client | 9 | See platform notes |
| Container | Docker | 10 | **Must-have, installed last.** Largest disk and RAM cost of anything here |

Optional per machine: MCP servers, databases, language toolchains, anything
workload-specific.

## Sizing before committing to a machine or paid tier

OS and base 1–2 GiB. **Roughly 2 GiB per concurrent agent session.** About
4 GiB per concurrent build. 1–2 GiB for a container runtime, excluding the
containers themselves. Then add 25%.

Container images alone commonly occupy 20–40 GiB, and build caches grow
unbounded — budget for pruning.

Decide intended concurrency first, then size. Never install layer 10 before the
agent environment has passed its verification gates: a failed bootstrap is much
cheaper to diagnose without tens of gigabytes of images in the way.

## Platform notes that bite

| Item | Platform | Note |
|---|---|---|
| Cloud file-sync client | Linux | Some proprietary services ship no first-party Linux client. Use a maintained third-party client or an object-storage bridge, and a device-code or remote authorisation flow on headless targets |
| Desktop messaging client | Headless | Nothing to install; skip layer 9 entirely rather than forcing it |
| Container runtime | Windows | Runs on a Linux VM backend, so it consumes host RAM beyond the containers themselves |
| Container runtime | Linux | Adding the user to the runtime group requires a new login session before it takes effect |
| Mesh VPN | Any | If a killswitch is active, allow the management subnet through the VPN's own allowlist. Do not hand-edit firewall rules the client regenerates |
| Agent CLIs | Headless | Prefer device-code auth; browser-redirect flows fail with no display |
| Agent CLIs | Any | Confirm which binary wins `PATH` when a version manager is also present |

## Per-machine template

Copy into a gitignored `*.local.md` file. Do not fill this in here.

```text
Alias:             <alias>
Role:              <driver | target | both>
OS / arch:         <os> / <arch>
Session type:      <headless | desktop>
Login shell:       <shell>            # detect, never assume
Access method:     <ssh alias | host+user+key | guest channel | console>
Elevation:         <passwordless sudo | password per call | admin>
Agents installed:  <subset of baseline>
Model provider:    <provider>, region <region>, model <model-id>
Credential source: <mint fresh on target | operator supplies | existing SSO>
Skill library:     <git remote>       # clone, never sync-mount
MCP servers:       <list or none>
Desktop apps:      <subset or none>
Sync client:       <service + client, or none>
Container runtime: <yes | no>
Fleet access:      <mesh VPN | SSH inbound | none>
```

## Rotation log template

Also for the gitignored copy. Record the identifier or a description, never the
value. Anything that has appeared in a transcript, log, screenshot or commit
message must be rotated.

| Date | What | Where exposed | Rotated |
|---|---|---|---|
| | | | |
