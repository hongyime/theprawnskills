---
name: reflect
description: >-
  Spawn three parallel review subagents over the active transcript, surface
  learnings, and route each to a concrete edit on an existing skill. Use when
  the user says reflect.
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Reflect

Mine the current conversation for durable learnings, then route them into skill edits.

Invoke when the user says "reflect" or "/reflect". Skip when the conversation is trivial, off-topic, or already covered by an existing skill the parent followed correctly. One-offs are not learnings.

## 1. Locate the active transcript

Use the current conversation as the source. If your environment keeps a transcript file for this session, read that; never read transcripts from other sessions or workspaces. If no transcript file is available, pass a tight digest of the session instead.

## 2. Spawn three reviewers in parallel

Delegate three reviewers in one message so they run in parallel, each as a fresh agent context with the strongest reasoning model available to you. If only one provider is available, use it for every role and say so; do not invent a second provider. If no delegation tool is available, run the three reviews as separate phases in sequence, keeping each one's findings separate until synthesis. Reviewers need read access to the tickets, chat threads, and observability traces the transcript references. They must not write anything.

| Lens | Prompt template |
|---|---|
| Judgment | `references/judgment-reviewer.md` |
| Tooling | `references/tooling-reviewer.md` |
| Divergent | `references/divergent-reviewer.md` |

Pass each template verbatim, substituting the transcript path or digest where marked. Reviewers return findings in their response body.

## 3. Synthesize

Delegate one synthesizer as a fresh agent context with the strongest reasoning model available. It spot-verifies citations through the evidence tools available to it. Pass `references/synthesizer.md` verbatim, with each reviewer's full output inlined where marked. It returns an Accepted / Rejected / Backlog list.

## 4. Structural enforcement check

Move any Accepted item that a lint rule, script, metadata flag, or runtime check would enforce more reliably to Backlog. Prefer enforcement in structure over a skill edit.

## 5. Apply

Present the synthesizer's full Accepted / Rejected / Backlog output and wait for explicit approval before applying any Accepted edit. The user picks the subset and may redirect routings. Skill changes affect every future agent in the org. Do not auto-apply.

File each Backlog item to your team's devex or backlog tracker without waiting. Only the Accepted list waits for approval.

Never edit an installed copy of a skill. Edit the skill in the library clone and validate it; the user decides when it is committed and pushed.

Follow each approved row's Routing exactly:

- Trivial existing-skill edit (a one-line bullet, a tightened sentence, a stale fact corrected): the parent does it directly.
- Substantive existing-skill edit (a new section, a new pattern table, more than ~10 lines): use the `skill-create` skill's draft / test / iterate loop.
- `tune description: <skill path>` (the skill exists but didn't trigger when it should have): use `skill-create` and run its description-optimization loop.
- `new skill via create-skill: <kebab-name>`: hand creation to `skill-create`. Do not invent the shape ad hoc.

Run `skills/skill-creator/scripts/quick_validate.py` on every touched skill before declaring done.

## 6. Summarize for the user

Short list, no preamble:

- Edits applied: `<skill path>`. What changed, one line each.
- New skills created: `<skill path>`. One line each (rare).
- Backlog filed to the devex tracker: `<issue title>` (`<tags>`). One line each.
- Dropped: one line per rejected finding + reason from the synthesizer.

## Provenance

Adapted from cursor/plugins `pstack/reflect` (MIT).

Library adaptation: transcript location, Task calls, and model routing generalized; skill edits go to the library clone, never installed copies.
