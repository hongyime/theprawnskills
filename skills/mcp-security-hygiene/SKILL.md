---
name: mcp-security-hygiene
description: >-
  When to read: securing MCP configuration — inline secrets, env-var migration, log redaction,
  or least-privilege defaults. Use for: hardening MCP configuration security. Does: removes
  inline secrets, migrates to env vars, redacts logs, and sets least-privilege MCP defaults. Not
  for unrelated auth implementations.
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# MCP Security Hygiene
Matches OpenCode CLI 1.18.34 (verified on the VM, 2026-11-18)

## Purpose
Reduce accidental secret leakage and risky MCP defaults.

## Checklist
1. Move API keys/passwords from config files to env vars.
2. Redact URLs in logs (`user:****@host`).
3. Disable servers that lack required credentials.
4. Restrict file-system MCP roots to minimum needed scope.
5. Keep backups and rollback scripts outside shared/public repos.

## Don’ts
- Don’t commit real secrets in `opencode.json`.
- Don’t keep failing credentialed MCPs enabled.
