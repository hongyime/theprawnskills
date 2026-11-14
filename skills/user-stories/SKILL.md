---
name: user-stories
description: >-
  Review a finished project with the user through user stories: map what a
  user can actually do, find edge cases, and reconcile the user's mental model
  with what the code really does, fixing mismatches with their approval. Use
  when the user says user stories, review this project, is this what I built,
  or wants a second pass over a somewhat-done project before polishing it.
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# User Stories

The user has finished building a project but is not confident it behaves the
way they think it does. Go through it together using user stories, so you can
(1) spell out what a user can actually do, (2) find edge cases, and (3)
reconcile their mental model with what is actually built, fixing anything
that is wrong.

## Ground rules

- The code is the source of truth for what the system DOES. The user is the
  source of truth for what it SHOULD do. Never assume intent; if unsure, ask.
- Write stories from the user's point of view (what they see, do, and get
  back), not in terms of functions or classes. Cite file paths and lines for
  where each behavior lives.
- If you cannot tell how something behaves from reading the code, say so
  instead of guessing, and offer to run it or write a quick test to find out.
- Do not change any code until the user approves a specific fix. Do not
  refactor unrelated code.
- Keep a running record in `docs/user-stories.md` (create it if missing). If
  it already exists, read it first and resume where you left off.

## Phase 1: Map the project (no code changes)

Explore the repo: README, entry points, routes/pages/screens, API endpoints,
CLI commands, background jobs, data models, auth/permissions, config, and
existing tests. Then give the user:

1. What kind of project this is and how a user interacts with it.
2. User roles: every distinct actor (guest, logged-in user, admin, API
   client, scheduled job, external service).
3. Feature map: features/flows grouped logically, each with a one-line
   description, its main files, and which roles use it.
4. Red flags: half-built features, TODOs, dead code, backend features with no
   way to reach them from the UI (or the reverse), and inconsistencies between
   features.

Then stop and ask the user which feature to start with.

## Phase 2: One feature at a time

For the feature the user picks:

### Step 1: Draft stories from the code

For each story:

- "As a [role], I want to [action], so that [outcome]."
- Acceptance criteria (Given / When / Then) describing what the code
  ACTUALLY does, with file references.
- Edge cases, each marked handled / not handled / unclear, with what actually
  happens. Consider: empty, invalid, or extreme input; missing permissions or
  unauthenticated access; double-submit and concurrent edits; network or
  third-party failures; partial failure mid-flow; items deleted, expired, or
  changed by someone else; first-time vs returning user; large data; dates
  and time zones; plus anything specific to this project.

Work the edge cases adversarially (see `interrogate`): a finding survives
only when a run proves it. Do not claim an edge case is handled because the
code looks right; run it, or mark it unclear. For anything about why the
code is shaped the way it is, investigate the rationale with cited evidence
(see `why`) instead of guessing.

### Step 2: Review with the user ONE story at a time

Show the story, what actually happens, and its edge cases, then ask: "Is
this what you intended?" The user answers yes, no (and explains what they
meant), or not sure. If they are not sure, help them decide by laying out
the trade-offs. Do not move on until the current story is settled.

### Step 3: Handle mismatches

When the user says the behavior is wrong:

- Log it: expected vs actual, where in the code, severity (breaks things /
  wrong but harmless / cosmetic).
- Propose a fix: which files change, the approach, and which other stories or
  features it could affect. Check the blast radius first (see
  `blast-radius`): what else could this change break, and prove the one fact
  it is safe because of by running code. If what the user wants conflicts
  with another story or creates a new edge case, say so.
- Wait for approval, then make the change.

### Step 4: Tests

- For each confirmed story, write tests for its acceptance criteria and key
  edge cases, following the project's existing test framework and
  conventions. Tests assert what the code's users can observe, so a test
  fails when the behavior breaks and keeps passing when only the internals
  change: drive the code through its users' interface with a concrete input,
  derive the expected value from the requirement, not from a run of the code.
- For each fix, write a regression test first (see `tdd`), confirm it fails
  on the old behavior, then make the fix and confirm it passes.
- If the project has no test setup, propose a minimal one and ask before
  adding it.
- Run the relevant tests and report the results.

### Step 5: Wrap up the feature

Update `docs/user-stories.md` with the stories (status: confirmed / changed /
open), the mismatch log, tests added, and open questions. Give the user a
short summary, then ask which feature to do next.

## Provenance

Authored from the user's own prompt (2026-11-13). Edge-case discipline
adapted from cursor/plugins `pstack/interrogate` and `pstack/why`,
regression-test-first from `pstack/tdd`, behavior-not-implementation test
rule from `pstack/principle-test-behavior-not-implementation`, blast-radius
check from `pstack/blast-radius` (all MIT).
