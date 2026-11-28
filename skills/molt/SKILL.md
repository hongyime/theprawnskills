---
name: molt
description: >-
  When to read: 'save progress', 'create handoff', 'resume from state', 'switch agents', or
  'what were we doing'. Use for: carrying work across agents and machines with MOLT-style
  persistent state in a repo's .agents/ folder. Does: keeps STATE.md for now, JOURNAL.md for
  history, and handoff docs for deep recovery — any agent on any machine resumes from files, not
  chat.
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# MOLT — carry work across harnesses

Alias for the MOLT continuity system: `cross-harness-state` +
`session-handoff`. MOLT keeps durable, harness-agnostic work state as plain
Markdown inside a repo's `.agents/` folder, so the next session — any agent,
any machine that syncs the repo — resumes from files, not from a chat
transcript.

## When to use it

- Starting or ending significant work in a repo.
- The user says save progress, update the state, journal this, resume from
  state, what were we doing, or pause this task.
- Switching agents or machines mid-task (including running out of credits)
  and continuity must survive.

## How it works

Load `cross-harness-state` for the file contracts and `session-handoff`
when pausing mid-task:

- `.agents/STATE.md` — NOW: current task + latest progress, with
  verification evidence per bullet. Read it first on resume.
- `.agents/JOURNAL.md` — HISTORY: dated one-line decisions, newest first.
- `.agents/handoffs/` — deep recovery docs, one per paused task, created
  via `session-handoff` (scaffold, validate, check staleness on resume).

Rules: save at every phase boundary or stop point, so a credit-out loses
at most one phase. Commit `.agents/` together with related code and push
before switching agents — but only when the user has authorized commit/push;
without that approval, keep the state local and say the code is uncommitted
(a handoff file alone does not transfer uncommitted code). Never write secrets into state files; reference them by
name only.

## Provenance

Adapted from the MOLT system (README + harness-agnostic agent prompt +
AGENTS stanza + STATE.md templates). The `_molt/` folder holds the source
system; this skill is the library's alias for it.
