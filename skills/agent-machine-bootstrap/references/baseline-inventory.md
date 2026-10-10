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

Optional per machine: extra MCP servers, databases, language toolchains,
anything workload-specific. The OpenCode plugin and model baseline below is
not optional on a machine that runs OpenCode.

## OpenCode plugin and model baseline

Layer 5 writes both config files. Layer 6 installs the plugin. Quit and
restart OpenCode after either change. An already-open session keeps the model
it was created with, so prove this on a new session.

No hosts, account ids, or credentials belong in this file. The operator
supplies IAM credentials on the target. Do not copy them from another machine.

| Piece | Value |
|---|---|
| Agent | opencode only, unless the operator asks for more |
| Provider | `amazon-bedrock` |
| Region | `us-east-1` |
| Auth | IAM via the process environment: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION=us-east-1`. Not `opencode auth login`. A bearer token in `AWS_BEARER_TOKEN_BEDROCK`, if set, overrides IAM |
| Plugin | `oh-my-openagent` pinned at `4.19.4`, listed in both `opencode.jsonc` and `tui.json` |
| Default model | `amazon-bedrock/global.anthropic.claude-fable-5-1` |
| Thinking cap | `variant`, `reasoning`, and `reasoningEffort` all `xhigh`. Never `max` |

Write the same model on every named agent in both files. The status bar reads
the top-level `model` in `opencode.jsonc`. The agent picker reads
`agent.<name>.model` there. The plugin reads `oh-my-openagent.json` when it
spawns a subagent. Setting only one file leaves the other path on the old
default.

| Agents | Model id, after `amazon-bedrock/` |
|---|---|
| sisyphus, prometheus, metis, plan | `global.anthropic.claude-fable-5-1` |
| atlas, sisyphus-junior | `global.anthropic.claude-sonnet-5` |
| hephaestus, oracle, librarian, explore, momus, multimodal-looker | `global.openai.gpt-6-astra` |

Categories live only in `oh-my-openagent.json`. They do not appear in the
agent picker.

| Categories | Model id, after `amazon-bedrock/` |
|---|---|
| visual-engineering, artistry, unspecified-high | `global.anthropic.claude-fable-5-1` |
| quick, writing | `global.anthropic.claude-sonnet-5` |
| ultrabrain, deep, unspecified-low | `global.openai.gpt-6-astra` |

Do not set `fallback_models`. The plugin uses that list at spawn time as
"first model present in the local catalog", not only after an error. An older
catalog model in the list replaces the configured model immediately.

Other switches in `opencode.jsonc`: set `"autoupdate": false`, and set
`permission.webfetch` to `allow`.

Claude Code user plugins, only when that CLI is requested: context7,
frontend-design, code-review, code-simplifier, playwright, claude-md-management,
ralph-loop, security-guidance, typescript-lsp, explanatory-output-style,
learning-output-style, pr-review-toolkit, commit-commands, feature-dev.
A machine that is OpenCode-only skips this list.

Prove it: a new Sisyphus session must call Fable 5.1, and an explore subagent
it spawns must call Astra, not an older default.

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
