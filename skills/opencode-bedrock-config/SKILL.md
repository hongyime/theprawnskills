---
name: opencode-bedrock-config
description: >-
  Configure OpenCode to use AWS Bedrock models, and fix subagents pinned to a
  dead or unfunded provider. Use for "SigV4 authentication requires AWS
  credentials", Bedrock provider setup, region pinning for global inference
  profiles, per-agent model overrides, "no credits remaining" from a subagent,
  and replicating an OpenCode Bedrock setup onto a new machine.
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "OpenCode on Windows, macOS, Linux"
---

# OpenCode With AWS Bedrock

Two settings cause most Bedrock failures: a missing `profile` and an
unpinned region. A third causes confusing subagent failures: plugin-supplied
agents carrying their own hardcoded model.

## When to use

Use when configuring, replicating, or debugging OpenCode's `amazon-bedrock`
provider, or when a subagent fails with a provider error while the main agent
works. Use `mcp-health-repair` for MCP server failures unrelated to model
auth. This skill holds no credentials and does not create AWS identities.

## Config location and reload

| Scope | Path |
|---|---|
| Global | `~/.config/opencode/opencode.json` or `.jsonc` |
| Project | `./opencode.json`, `.jsonc`, or `.opencode/opencode.json` |

Config is read once at startup and is not hot-reloaded. After any change,
tell the user to quit and restart OpenCode; the running session keeps the old
config. Always keep `"$schema": "https://opencode.ai/config.json"`.

## Credentials: the profile requirement

The provider does not read `~/.aws/credentials` on its own. Without an
explicit `profile`, valid credentials on disk still produce:

```text
AWS SigV4 authentication requires AWS credentials
```

Set the profile explicitly:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "amazon-bedrock": {
      "options": {
        "region": "us-east-1",
        "profile": "default"
      }
    }
  }
}
```

| Option | Purpose |
|---|---|
| `profile` | Named profile from the shared credentials file. Required unless credentials come from environment variables |
| `region` | Target region. Config value takes precedence over `AWS_REGION`, then `AWS_DEFAULT_REGION`, then a built-in default |
| `endpoint` | VPC endpoint URL; alias for the generic `baseURL` and takes precedence over it |

Supported credential sources, in the provider's own precedence order:

1. `AWS_BEARER_TOKEN_BEDROCK` — a long-lived Bedrock API key. Overrides every
   other method, including a configured profile.
2. The AWS credential chain — `profile`, `AWS_ACCESS_KEY_ID` /
   `AWS_SECRET_ACCESS_KEY`, web identity, container and instance credentials.

`opencode auth list` does not cover Bedrock; it authenticates through the
environment and credentials file, not stored API-key accounts.

## Region pinning for global inference profiles

A `global.`-prefixed model id is a cross-Region inference profile, not a plain
foundation model. Its routing is anchored to a specific source Region, so the
provider `region` must match that source Region rather than the user's normal
working Region. A regional-only region value yields access errors even with
correct credentials.

Cross-Region profiles also need broader IAM than a single model. Grant, in one
policy: the inference-profile ARN in the requesting Region, the foundation
model in that Region, and the Region-less global foundation-model ARN. Scope
with the `bedrock:InferenceProfileArn` condition key, and include
`bedrock:GetInferenceProfile` plus `bedrock:InvokeModelWithResponseStream`
alongside `bedrock:InvokeModel`.

For a custom application inference profile, key the model by name and set its
`id` to the profile ARN so caching stays correct.

## Subagents pinned to a dead provider

A plugin that contributes its own agents can hardcode each one's model. When
that provider is unfunded or unavailable, only those agents fail while the
main agent keeps working — often as a retry loop onto an equally dead
fallback model.

Override the specific agent by name, using the model already proven working
on that machine:

```json
{
  "agent": {
    "<agent-name>": { "model": "<provider>/<model-id>" }
  }
}
```

| Detail | Note |
|---|---|
| The top-level `model` field does not fix this | Agent-level `model` intentionally overrides the global default |
| Fix only the agents that actually fail | Categories are deliberately routed to different specialist models |
| Match the machine, not the fleet | Confirm that machine's own working model before copying a string across hosts |

## Replicating onto another machine

| Item | Action |
|---|---|
| `opencode.json` / `.jsonc` | Copy, then re-verify `profile` and `region` resolve on the new host |
| Plugins in `plugin[]` | Pin the exact version in the config directory's `package.json`, then install |
| Credentials | Create fresh, separately revocable credentials for the new machine; do not copy secrets between hosts |
| Custom auth plugins | Usually unnecessary. Prefer a supported native credential source before porting bespoke refresh code |
| `PATH` and env exports | Write to the file the login shell actually reads; confirm the shell first |

## Verify with real inference

Configuration that parses is not configuration that works. Run one real
request and confirm both the model line and the response:

```powershell
opencode run "Reply with exactly: BEDROCK_OK"
```

Report the resolved model, whether the response returned, and the identity
the call authenticated as. Do not report success from a config diff alone.

## Prerequisites and provenance

Requires OpenCode installed, Bedrock model access granted in the target AWS
account, and credentials resolvable on the host. Reflects behavior observed
against the published OpenCode provider documentation and AWS cross-Region
inference guidance. Load companions through `skill-router`.
