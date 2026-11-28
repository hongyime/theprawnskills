---
name: web-design-guidelines
description: >-
  When to read: checking a site against Vercel's Web Interface Guidelines. Use for: reviewing UI
  code for compliance with Vercel's Web Interface Guidelines (fetched live from the source URL).
  Does: checks the live guidelines against the code. For general design review use
  design-taste-frontend; for accessibility audits use better-accessibility.
metadata:
  author: vercel
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
  argument-hint: file-or-pattern
---

# Web Interface Guidelines

Review files for compliance with Web Interface Guidelines.

## How It Works

1. Fetch the latest guidelines from the source URL below
2. Read the specified files (or prompt user for files/pattern)
3. Check against all rules in the fetched guidelines
4. Output findings in the terse `file:line` format

## Guidelines Source

Fetch fresh guidelines before each review:

```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

Use the agent's available web tool (e.g. `curl`, the harness's web fetch) to retrieve the latest rules — do not assume a `WebFetch` tool exists. The fetched content contains all the rules and output format instructions. If offline or the fetch fails, do not guess the rules: route design review to `design-taste-frontend` and accessibility checks to `better-accessibility` instead.

## Usage

When a user provides a file or pattern argument:
1. Fetch guidelines from the source URL above
2. Read the specified files
3. Apply all rules from the fetched guidelines
4. Output findings using the format specified in the guidelines

If no files specified, ask the user which files to review.
