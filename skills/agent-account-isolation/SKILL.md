---
name: agent-account-isolation
description: >-
  Run two or more accounts of the same coding-agent CLI on one machine without
  cross-contamination. Use for "it used my other account", "wrong account",
  separating work and personal agent identities, WSL versus host isolation,
  per-account credentials, or proving which account a CLI is actually using.
  Covers browser-login CLIs and cloud-credential CLIs, which fail differently.
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Windows with WSL, macOS, Linux; any agent CLI"
---

# Agent Account Isolation

Keep two agent identities on one machine from drifting into each other, and be
able to prove at any moment which one is in use.

## When to use

Use when the same CLI must run under different accounts on one machine, when a
tool has silently used the wrong account, or when setting up a second identity
alongside an existing one. Use `agent-machine-bootstrap` for installing the CLIs
themselves, and `virtualbox-guest-access` when the second context is a VM.

Not for multi-tenant server access control, not for secret management, and not a
substitute for separate machines where policy requires them.

## Status

**Proposed, not yet verified end to end.** The reasoning and the individual
mechanisms are sound and documented, but this procedure has not been executed
and confirmed on a live two-account setup. Treat the verification commands as
the acceptance test, not as a formality, and correct this section once a run has
actually passed.

## The two credential classes

Isolation fails differently depending on how a CLI authenticates. Establish
which class each tool is in before designing anything.

| Class | Credential is | Isolation depends on | Failure mode |
|---|---|---|---|
| Browser login | A token written into a config directory after an interactive authorisation | A separate config directory, and the correct browser session **at login time** | Approving as the wrong account. There is at least a visible moment to get right |
| Cloud credential chain | Environment variables, or a shared credentials file on disk | Not inheriting those variables, and not sharing the credentials directory | Silent inheritance. There is **no login step to get wrong** — it simply works, wrongly |

The second class is the dangerous one. A tool that resolves credentials from the
environment gives no signal that it picked up the wrong identity.

## Isolation mechanisms, strongest to weakest

| Mechanism | Strength | Cost |
|---|---|---|
| Separate physical or virtual machine | Strongest. No shared filesystem, environment or process table | Another machine to build and maintain |
| Separate operating-system user account | Strong. File permissions are enforced by the OS | Switching users; awkward to use both at once |
| Container per account | Strong, provided the host filesystem is not bind-mounted in | Image and lifecycle management |
| Separate guest distribution, for example WSL | Good for accidents, but the host drive is usually mounted by default | Host-platform specific |
| Config-directory environment variables in one shell | **Weakest.** One unset variable puts you in the wrong account, with nothing enforcing it | None, which is exactly why it is tempting |

Anything below the container line prevents mistakes rather than access. Choose
deliberately and state which you chose.

## What isolation does and does not buy

Be precise about this. Overstating it is how people end up trusting a boundary
that is not there.

| Measure | Prevents | Does not prevent |
|---|---|---|
| Host programs kept off the guest `PATH` | Silently running the host's binary, under the host's identity | Reading host files through a mounted drive |
| Credential variables not forwarded | Silent inheritance of the other account's keys | A tool reading a shared credentials file on disk |
| Config directories kept local | Two contexts sharing one token store | Anything that deliberately walks the mounted drive |
| Authorising in the correct browser session | Binding a new CLI to the old account | A later re-authorisation drifting back |
| Host drive mount disabled | Reading host files at all | Nothing. This is the only actual boundary here |

The realistic risk is accidental misuse, and the measures above address it well.
A genuine boundary requires the last row, or a mechanism from the top of the
previous table. This matters more than usual because the process running in the
isolated context is an agent: asked to "find my config", it is exactly the thing
that would walk a mounted host drive and read the other account's credentials.

## Worked example: a WSL guest as the second context

Host keeps account A. The guest gets account B.

### 1. Keep host programs out of the guest PATH

Inside the guest, edit `/etc/wsl.conf`:

```ini
[interop]
appendWindowsPath=false
```

Then, from the host shell, restart the subsystem:

```powershell
wsl --shutdown
```

After this, the CLI name in the guest resolves to the guest's own installation
or to nothing at all, never to the host's copy. Install the Linux builds
afterwards, not before.

### 2. Do not forward credential variables

Inside the guest:

```bash
echo $WSLENV
```

It should be empty, or contain only names that carry no identity. Never add any
provider key or cloud credential variable to it. See the matrix below for the
specific names per CLI.

### 3. Keep configuration directories local

Leave each CLI's configuration directory as an ordinary directory inside the
guest. Do not symlink any of them onto the mounted host drive, and do not point
a config-directory or home-directory override at a host path.

### 4. Authorise in the correct browser session

The login link opens the host's default browser, which is probably still signed
in as account A. Clicking Authorize there binds the CLI to account A.

Instead, paste the login URL into a private window, or into a browser profile
signed in as account B. Do this once per CLI, and verify immediately afterwards
rather than assuming it worked.

Where a CLI offers a device-code flow, prefer it: the code is entered in a
browser you choose explicitly, which removes this whole failure mode.

### 5. Optional: make it an actual boundary

To stop the guest reading host files at all, disable the mount in
`/etc/wsl.conf`:

```ini
[automount]
enabled=false
```

This is the only measure here that is a real boundary. It also removes host file
access entirely, which is a significant loss of convenience. Decide explicitly;
do not enable it by accident.

## Per-CLI credentials and verification

Confirm each row against the CLI's own current documentation before relying on
it; paths and flags change.

| CLI | Class | Config location | Never forward | Identity check |
|---|---|---|---|---|
| `claude` | Browser login | `~/.claude/` | `ANTHROPIC_API_KEY`, `CLAUDE_CONFIG_DIR` | `/status` inside the CLI |
| `codex` | Browser login | `~/.codex/` | `OPENAI_API_KEY`, `CODEX_HOME` | `codex login status` |
| `gemini` | Browser login | `~/.gemini/` | `GEMINI_API_KEY`, `GOOGLE_API_KEY` | account shown in the header |
| `kiro-cli` | Browser login | `~/.local/share/kiro-cli/` | `KIRO_API_KEY` | `kiro-cli whoami` |
| `agy` | Browser login | **confirm before relying on it** | provider key, if it accepts one | account shown in the header |
| `opencode` | Cloud credential chain | `~/.config/opencode/` **and** `~/.aws/` | `AWS_BEARER_TOKEN_BEDROCK`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `AWS_PROFILE`, and any key-pool file variable | provider caller-identity call, plus one real request showing the resolved model |

Two things follow from that last row. A shared cloud-credentials directory
defeats isolation even when every other measure is in place, so give each
context its own directory and its own separately revocable identity. And because
there is no login step, the only proof is a caller-identity call: run it, do not
infer it.

## Verify after setup

Inside the isolated context:

```bash
command -v claude codex gemini kiro-cli agy opencode
```

No result should resolve to a host path. Then run each CLI's identity check from
the matrix and confirm every one reports account B.

Optionally label the shell so the context is visible at a glance. For bash:

```bash
PS1="\[\e[35m\][<label>]\[\e[0m\] $PS1"
```

For zsh, prepend the same label to `PROMPT`. Use a label that identifies the
context, not the account holder.

## Verify again later

Treat the identity checks as recurring, not one-off. A token expiring and being
re-authorised months later can silently rebind to whichever account the browser
happens to be signed into — the same failure as the original setup, with none of
the original attention. Re-run the checks after any re-authentication, any CLI
upgrade, and any change to the shell profile or `/etc/wsl.conf`.

## Known unknowns

| Unknown | Why it matters |
|---|---|
| Whether an authorisation callback reaches a listener inside the guest from a host browser | Recent WSL releases mirror localhost and this generally works; older networking modes may not. Untested here. If it fails, use a device-code flow or authorise from a browser inside the guest |
| `agy` configuration directory | Listed as unconfirmed above rather than guessed. Establish it before trusting isolation for that CLI |
| Whether every listed CLI honours a config-directory override | Some ignore it, or read a second location as well. Verify per CLI rather than assuming |

## Report

State the chosen mechanism and why, which measures were applied, and the actual
output of every identity check. Name any credential variable found forwarded, and
any configuration directory found pointing at a host path. If the boundary is
accident-prevention rather than enforcement, say so plainly rather than implying
containment.

## Prerequisites and provenance

Requires administrative access in the isolated context, and a browser session or
device-code flow for the target account. Contains no accounts, hostnames,
credentials or machine-specific paths. Load companions through `skill-router`.
