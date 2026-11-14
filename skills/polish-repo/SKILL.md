---
name: polish-repo
description: >-
  Polish a somewhat-done repo with one command: map what it really does with
  user stories, stress-test it, fix what is wrong with tests, improve the
  frontend, and prove the result. Use when the user says polish this repo,
  give this project another pass, review and improve this project, second
  pass over this repo, or opens a repo wanting a full review-and-improve run.
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Polish Repo

One entry point for giving a finished-ish project another pass. You say
"polish this repo" once; this skill chains the library's review skills in
order — user-stories → interrogate → correct + tdd → modernize, unslop,
sharpen → security-best-practices → design-taste-frontend / impeccable →
verification-loop → file-pr — and stops where a human decision is needed.
One feature at a time, nothing fixed without approval, nothing polished
that was not first mapped.

## Ground rules

- The code is the source of truth for what the system DOES. The user is the
  source of truth for what it SHOULD do. Never assume intent; if unsure, ask.
- Write from the user's point of view (what they see, do and get back), not
  in terms of functions or classes. Cite file paths/lines for where each
  behavior lives.
- If you cannot tell how something behaves from reading the code, say so
  instead of guessing, and offer to run it or write a quick test to find out.
- Do not change any code until the user approves a specific fix. Do not
  refactor unrelated code. Do not commit or push unless the user says so.
- Keep the running record in `docs/user-stories.md` (create it if missing).
  If it already exists, read it first and resume where it left off.

## Phase 1: Map

Load `user-stories` and run its Phase 1: explore the repo (README, entry
points, routes/pages/screens, API endpoints, CLI commands, background jobs,
data models, auth/permissions, config, existing tests) and deliver the
project map — what kind of project it is and how a user interacts with it,
user roles, feature map with main files, and red flags (half-built features,
TODOs, dead code, backend features with no UI and the reverse,
inconsistencies between features). Then STOP and ask the user which feature
to start with.

## Phase 2: Challenge

For the feature the user picks, load `user-stories` Phase 2 steps 1–2 and
`interrogate`:

- Draft stories from the code ("As a [role], I want to [action], so that
  [outcome]"), with Given / When / Then acceptance criteria describing what
  the code ACTUALLY does, with file references.
- Review ONE story at a time with the user. Do not move on until the current
  story is confirmed, corrected, or marked unclear.
- `interrogate` each story adversarially: try to break it, prove claims by
  running the code, find blind spots. Mark every edge case handled / not
  handled / unclear, with what actually happens. Consider: empty, invalid
  or extreme input; missing permissions or unauthenticated access;
  double-submit and concurrent edits; network or third-party failures;
  partial failure mid-flow.
- When a bug resists explanation, dig deeper before fixing: `why` for
  root-cause chains, `figure-it-out` for autonomous investigation. Do not
  patch a symptom you cannot explain.

## Phase 3: Fix

Build the mismatch log from Phase 2 (user-stories Phase 2 step 3): every
place the code does something other than what the user expects, with a fix
proposal per item. Present the log and ask which fix to do first.

For each approved fix, in order:

- `blast-radius` first: map what else the change touches before touching
  code — callers, dependents, shared state, migrations. If the blast
  radius is bigger than the fix, say so and ask.
- `correct`: fix the fault, not the surface point. A guard is a fix only
  when the handled state is legitimate; check the pattern, not just the
  instance; suspect persisted state after a restart.
- `tdd`: write the failing regression test FIRST, testing behavior not
  implementation, then make the smallest fix that passes it.
- Re-run the affected stories after each fix and update the mismatch log.
  One fix at a time. STOP if a fix needs a product decision the user has
  not made.

## Phase 4: Tighten

After the fixes land, one code-quality pass over what changed (not the
whole repo):

- `modernize`: bring outdated patterns and dependencies up to current
  practice. Do not chase every new release — modernize what the feature
  touches.
- `unslop` then `sharpen`: remove slop and tighten the code — dead code,
  duplicated logic, vague names, over-commented obvious lines.
- `security-best-practices`: security pass over the feature — auth and
  permissions, input validation, secrets handling, injection and
  data-exposure risks. Security findings go back into the mismatch log and
  are fixed the same way (Phase 3), not silently patched here.

## Phase 5: Looks

Only when the feature has a user-facing surface. Skip entirely for
backend-only, CLI-only, or library features.

- Landing, company, or marketing surface: load `design-taste-frontend`.
- App UI, dashboard, or design system: load `impeccable`. Async review is
  the default — work from the code plus screenshots the user supplies, or
  one batched screenshot round, findings in one batch. Never start a dev
  server, open a browser extension, or run a poll loop unless the user
  explicitly asks for live mode.

## Phase 6: Verify

Load `verification-loop` and follow its evidence contract, with the
`skill-judge` verification discipline: prove-it-works against the real
artifact, not proxies or self-reports; a deterministic re-runnable script
is the strongest proof; judge tests by behavior, not implementation.
Verify in bounded passes, not a loop, and stop polishing when the passes
are clean.

Then wrap up in chat, in this order:

- What changed (files, with one line each on why).
- What was checked and how it was proven.
- What is still open (unfixed mismatches, unclear edge cases).
- What was deliberately left alone, and why.

## Phase 7: Ship

Do not stop at the wrap-up. Ask the user whether to open a pull request
for the changes. On yes, load `file-pr` and follow it. On no, leave the
changes uncommitted on the branch and say so.

## What this skill does not do

- It does not decide product direction; the user does, one feature at a
  time.
- It does not auto-fix, auto-commit, or auto-push anything. The PR step
  (Phase 7) asks first.
- It does not run the live browser loop; that is opt-in per feature.
- It does not touch other repos; one repo per run.
