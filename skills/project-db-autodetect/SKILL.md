---
name: project-db-autodetect
description: >-
  When to read: auto-detecting Postgres/SQLite settings from a project. Use for: detecting
  project database settings and mapping them to MCP runtime env. Does: reads .env,
  docker-compose, Prisma, and project folders. Not for provisioning cloud databases.
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Project DB Autodetect

## Purpose
Auto-resolve DB config per project so MCP can switch contexts without manual edits.

## Detection Order
1. `.env*` keys: `DATABASE_URL`, `POSTGRES_URL`, etc.
2. `docker-compose*.yml` postgres service and port mappings.
3. `prisma/schema.prisma` datasource providers + env reference.
4. local sqlite files: `*.db`, `*.sqlite*` under common folders.

## Output Contract
Return normalized object:
- `postgresUrl`
- `sqlitePath`
- `source`
- `confidence`

## Runtime Policy
Precedence: explicit user env > detected values > safe fallback > disable unresolved server.
