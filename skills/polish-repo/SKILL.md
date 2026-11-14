---
name: polish-repo
description: >-
  Polish a somewhat-done repo with one command: map it, stress-test it, fix
  it with tests, tighten and secure it, improve the frontend, prove it, and
  open a PR. Use when the user says polish this repo, give this project
  another pass, or review and improve this project. Also works on an
  early-stage repo with PRD/TDD docs and little code yet — Phases 1–2 give
  the second opinion and Phase 7 turns gaps into tasks.
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Polish Repo

One entry point for giving a finished-ish project another pass. You say
"polish this repo" once; this skill chains the library's review skills in
order — user-stories → interrogate + security-best-practices →
blast-radius + tdd → refactor + ponytail-review →
design-taste-frontend / impeccable → verification-loop → file-pr — and
stops where a human decision is needed. One feature at a time, nothing
fixed without approval, nothing polished that was not first mapped. One
repo per run.

## Early-stage repos

Also works on a repo that is mostly docs so far (PRD, TDD/design docs,
little or no code yet). Say "second opinion only" and the run stops after
Phase 2: Phase 1 maps what the docs claim, Phase 2 challenges the claims
and records the gaps, Phase 7 turns the gaps into tasks. Phases 3–5 mostly
skip until there is code to fix, refactor, or show. The baseline test/build
check in Phase 1 just reports what is missing when there is nothing to run
yet.

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

Load `user-stories` and run Phase 1 to deliver the project map and red
flags. Then STOP and ask the user which feature to start with.

Before starting on the feature, run the repo's test suite and build once
and record the baseline. If it is already broken, say so before fixing
anything — do not let pre-existing breakage blur with polish regressions.
If there is no code or no test suite yet, record that and move on — do not
invent a baseline.

## Phase 2: Challenge

For the feature the user picks, load `user-stories` Phase 2 steps 1–2,
`interrogate`, and `security-best-practices`:

- Draft stories from the code with Given / When / Then acceptance criteria
  describing what the code ACTUALLY does, with file references.
- `interrogate` each story adversarially: try to break it, prove claims by
  running the code, find blind spots. Mark every edge case handled / not
  handled / unclear, with what actually happens.
- `security-best-practices`: audit auth, permissions, input validation,
  secrets handling, injection and data-exposure risks up front. Security
  findings join the mismatch log like any other defect.
- When a bug resists explanation, dig deeper before fixing: `why` for
  root-cause chains, `figure-it-out` for autonomous investigation. Do not
  patch a symptom you cannot explain.

Present the drafted stories, edge cases, and security findings in a single
summary table for user review. STOP for approval before proceeding to fixes.

## Phase 3: Fix

Build the mismatch log from Phase 2 (user-stories Phase 2 step 3): every
place the code does something other than what the user expects, with a fix
proposal per item, ordered by severity. Present the prioritized queue and
proceed in order unless the user reorders.

For each fix, in order:

- `blast-radius` first: map what else the change touches before touching
  code — callers, dependents, shared state, migrations. If the blast
  radius is bigger than the fix, say so and ask.
- Fix the fault, not the surface point. A guard is a fix only when the
  handled state is legitimate; check the pattern, not just the instance;
  suspect persisted state after a restart.
- `tdd` when the bug has an obvious cheap local test target: write the
  failing regression test FIRST, testing behavior not implementation, then
  make the smallest fix that passes it.
- Re-run the affected stories after each fix and update the mismatch log.
  One fix at a time. STOP if a fix needs a product decision the user has
  not made.

## Phase 4: Tighten

After the fixes land, one code-quality pass over what changed (not the
whole repo). Present the proposals first and STOP for approval — do not
change code here until the user approves:

- `refactor`: surgical behavior-preserving cleanup — extract functions,
  rename, break down god functions, remove dead code and duplication.
- `ponytail-review`: quality review of the change — is the logic right, is
  it safe, is risky code tested, is every line needed.

## Phase 5: Looks

Only when the feature has a user-facing surface. Skip entirely for
backend-only, CLI-only, or library features.

- Landing, company, or marketing surface: load `design-taste-frontend`.
- App UI, dashboard, or design system: load `impeccable`. Async review is
  the default — work from the code plus screenshots the user supplies, or
  one batched screenshot round, findings in one batch. Never start a dev
  server, open a browser extension, or run a poll loop unless the user
  explicitly asks for live mode.

Present UI recommendations first and get the user's approval before editing
any frontend files.

## Phase 6: Verify

Load `verification-loop`. Prove changes against the real artifact with
deterministic tests/commands (testing behavior, not implementation). Stop
when clean.

Then wrap up in chat, in this order:

- What changed (files, with one line each on why).
- What was checked and how it was proven.
- What is still open (unfixed mismatches, unclear edge cases).
- What was deliberately left alone, and why.

## Phase 7: Ship

Do not stop at the wrap-up. Ask the user whether to open a pull request
for the changes. On yes, load `file-pr` and follow it. On no, leave the
changes uncommitted on the branch and say so.

Then check the Phase 1 map: if other features remain, ask "Continue with
the next feature ([Name]), or wrap up here?" If the user picks the next
feature, return to Phase 2 with it. If they wrap up, stop.
