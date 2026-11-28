---
name: postgres-mcp-onboarding
description: >-
  When to read: setting up Postgres MCP — local Docker Postgres, Supabase, Railway, Neon, or
  managed Postgres URLs. Use for: enabling PostgreSQL MCP correctly across providers. Does:
  configures the MCP connection per provider. Not for SQL query optimization itself.
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Postgres MCP Onboarding

## Purpose
Get Postgres MCP connected with minimal errors.

## Required Input
A valid Postgres URL, supplied via the `POSTGRES_MCP_URL` env var (never paste the URL into a command or file).

## Steps
1. Set env var (preferred): `POSTGRES_MCP_URL`.
2. Configure command argument to read URL from env placeholder.
3. Keep server disabled by default until URL exists.
4. Validate and run `/status` or `opencode mcp list`.

## Provider Notes
- Supabase/Neon/Railway: use pooled or direct DB URL from dashboard.
- Local Docker: map host port and use `localhost:<port>`.

## Common Failures
- Missing URL arg -> `Connection closed`
- Wrong sslmode or firewall block -> timeout/auth failures
