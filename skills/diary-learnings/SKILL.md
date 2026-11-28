---
name: diary-learnings
description: >-
  When to read: Bryan corrects something, says 'that was wrong', or a mistake
  needs recording the same day. Use for: writing the same-day diary entry and
  keeping the learnings loop honest. Does: appends a WRONG / CAUSE / OWED /
  RULE entry to ~/memory/diary.md, mirrors the mistake to
  ~/workspace/.learnings/ERRORS.md, and tracks promotion against the
  3-corroboration gate — never auto-promotes.
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Diary & Learnings Loop

A correction made twice is a skill waiting to be written — but only if the
first correction was written down the same day. This skill is the loop that
makes sure it was.

## Files

- `~/memory/diary.md` — same-day mistakes, corrections, owed items.
  Main agent writes only, same day as the event. Append-only.
- `~/workspace/.learnings/ERRORS.md` — mistakes + real cause. Append-only,
  never deleted. Main agent only, on diary entry.
- `~/workspace/.learnings/LEARNINGS.md` — rules that worked, promoted
  only. Main agent only, on promotion from the diary.

Fleet agents never write these files: they report corrections in their
handoffs, and the main agent logs them.

## Write the diary entry — same day, fixed format

One dated section per day. One entry per correction, four lines in order,
one line each, greppable:

```text
## YYYY-MM-DD
- WRONG: <what was wrong, in Bryan's words where he gave them>
- CAUSE: <the real cause, not the symptom>
- OWED: <what is still owed to Bryan, or "none — <fixed same turn>">
- RULE: <the rule that would have prevented it, one line>
```

Worked example (real correction, 2026-11-25):

```text
## 2026-11-25
- WRONG: Long prose reply in Main, Bryan: "too much mumbo jumbo" — give short version only
- CAUSE: No pre-send format check existed; caveman rule lived in SOUL/MEMORY/skill but nothing checked output before sending
- OWED: none — short version given same turn
- RULE: Talk caveman — answer first, bullets over prose, no greeting/hedging/recap
```

What counts: every user correction, mistake, or owed item gets an entry
the same day. Caveman style — terse, four lines, no essay. If the entry
was written at file creation rather than on the day itself (as the
2026-11-25 example was), say so in a note under the section heading.

## Mirror to ERRORS.md

One line per mistake, `|`-separated:

```text
- <date> | <chat> | <mistake> | cause: <cause> | fixed by: <rule or "pending — <what is not yet built>">
```

A fixed mistake gets a `fixed by <rule>` note, not a deletion. Nothing is
ever deleted from ERRORS.md — a fix is a note, not an erasure.

## Promotion gate — never auto-promote

A rule goes to SOUL / AGENTS / TOOLS / MEMORY only at **3+
corroborations** (same rule, different dates or chats) or **one explicit
user correction**. No auto-promotion, no one-offs.

- LEARNINGS.md format, one line per rule, `|`-separated: rule, first-seen
  date, corroboration count, status (`already in <file> — do not
  re-promote`, or `promoted to <file>`).
- A rule already in a standing file is marked as such — never re-promoted.
- A promoted rule is not re-logged as a new RULE. If it breaks again, log
  it as WRONG with a pointer to the standing file — that is a regression,
  not a new rule.

This skill never edits SOUL / AGENTS / TOOLS / MEMORY itself. Promotion is
Bryan's per-rule call; the agent prepares the candidate list and waits.

## Weekly check — manual until a cron is approved

Sample the past week's chats for user corrections, verify each has a
same-day diary entry, report misses. Manual spot-check until a cron is
approved — **do NOT create the weekly-check cron**; that needs Bryan's
separate approval.

First promotion pass: scheduled 2026-12-11 (cron
`wave3-03-10-dec11-check`). That job reports the candidate list only; it
must NOT promote anything itself.

## What this skill is not

- `reflect`: mines the current session for reusable lessons and routes
  each to a concrete edit on an existing skill. Diary-learnings records
  corrections in the diary loop; it never edits skills.
- `correct`: diagnoses a recurring error pattern and fixes the cause in
  the code. Diary-learnings records the mistake; `correct` fixes the
  system that produced it.

Cross-reference, do not merge.
