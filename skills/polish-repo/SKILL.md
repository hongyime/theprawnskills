---
name: polish-repo
description: >-
  Polish a somewhat-done repo with one command: map it, stress-test it, fix
  it with tests, tighten and secure it, improve the frontend, prove it,
  optionally climb the weakest area until it scores 9/10, and open a PR.
  Use when the user says polish this repo, give this project another pass,
  or review and improve this project. Also works on an early-stage repo
  with PRD/TDD docs and little code yet — Phases 1–2 give the second
  opinion and log the gaps in docs/user-stories.md.
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Polish Repo

One entry point for giving a finished-ish project another pass. You say
"polish this repo" once; this skill chains the library's skills in
order — user-stories → interrogate + security-best-practices →
blast-radius + tdd → refactor + ponytail-review →
design-taste-frontend / impeccable → verification-loop →
hill-climb (optional) → file-pr — and stops where a human decision is
needed. One feature at a time, nothing fixed without approval, nothing
polished that was not first mapped. One repo per run.

## Early-stage repos

Also works on a repo that is mostly docs so far (PRD, TDD/design docs,
little or no code yet). Say "second opinion only" and the run stops after
Phase 2: Phase 1 maps what the docs claim, Phase 2 challenges the claims
and logs the gaps in docs/user-stories.md. Phases 3–5 mostly
skip until there is code to fix, refactor, or show. The baseline test/build
check in Phase 1 just reports what is missing when there is nothing to run
yet.

## Ground rules

- The code is the source of truth for what the system DOES. The user is the
  source of truth for what it SHOULD do. Never assume intent; if unsure, ask.
- Decide, don't ask, for anything that is not a product decision or an
  approval gate: pick the reasonable option, log the decision in the running
  record, and keep going. Questions about what the system SHOULD do are
  product decisions — ask those. Questions about how to do it — decide and log.
- Pacing: a polish run can span the active provider's limit window. Budget usage
  (~20% of that window per hour, never 100%) and check the remaining budget
  at each phase boundary; slow down before the window is exhausted. The window
  belongs to whichever agent is running (Codex, agy, OpenCode, Muse) — agy's
  is 5h; use the active provider's own window.
- Write from the user's point of view (what they see, do and get back), not
  in terms of functions or classes. Cite file paths/lines for where each
  behavior lives.
- If you cannot tell how something behaves from reading the code, say so
  instead of guessing, and offer to run it or write a quick test to find out.
- Do not change any code until the user approves a specific fix. Do not
  refactor unrelated code. Do not commit or push unless the user says so.
- Keep the running record in `docs/user-stories.md` — create it only with the user's approval (repo rule: no new Markdown files without an explicit request); if the user has not approved a new file, keep the record in the conversation instead.
  If it already exists, read it first and resume where it left off.
- Annotation packets are the human feedback channel: the user annotates
  the render in plain words, the agent turns each note into a packet
  (see Phase 5). Every packet is resolved or explicitly dismissed by the
  user before ship — the agent never dismisses a packet on its own.

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

Too-fast check: if Phase 2 finds zero mismatches on a non-trivial repo, the
bar was read too low. Re-read the weakest area at full depth — the largest
file, the least-tested path, the oldest code — before declaring it clean. A
clean bill on the first pass is a signal to look harder, not to stop.

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

Then run one annotation round:

- Present the render (screenshot, live page, or postplan page) alongside
  the recommendations and ask the user to annotate it — plain words are
  fine ("header nav feels tight").
- Build one packet per note (see below) and record it in
  `docs/annotations.md` — create that file only with the user's approval (same rule as `docs/user-stories.md`: no new Markdown files without an explicit request); if not approved, keep the packets in the conversation instead. Fix the packets in severity order, then
  re-render once so the user can confirm. One round per feature by
  default — a second round only if the user asks for it.

### Annotation packet

Format adapted from the Agentation annotation packet (no dependency —
the Agentation tool itself is not adopted).

- Element: selector / path to the element the user pointed at.
- File: file:line where it lives.
- Component tree: the component ancestry around the element.
- Computed styles: the relevant ones only — the values the note is about.
- Intent: what is wrong / what to change, in the user's words.
- Severity: High (blocks ship), Medium (fix this pass), Low (deferrable —
  park in the mismatch log with a reason).
- Status: open → acknowledged → resolved, or dismissed. The agent
  acknowledges a packet when it starts the fix and resolves it when the
  fix is verified in the re-render. Only the user dismisses a packet,
  with a reason.

The agent fills Element, File, Component tree, and Computed styles from
the code it already knows — the user only supplies the note and, if they
want, the severity.

## Phase 6: Verify

Load `verification-loop`. Prove changes against the real artifact with
deterministic tests/commands (testing behavior, not implementation). Stop
when clean.

Annotation gate: every packet in `docs/annotations.md` must be resolved
or user-dismissed before this phase passes. An open or acknowledged
packet fails verification — it is still-open human feedback, not a
passing check. Low packets the user deferred stay in the mismatch log
with their reason.

Then wrap up in chat, in this order:

- What changed (files, with one line each on why).
- What was checked and how it was proven.
- What is still open (unfixed mismatches, unclear edge cases).
- What was deliberately left alone, and why.

## Phase 7: Iterate (optional)

Only if the user says yes at the end of Phase 6 — never by default. The
point is to keep climbing the weakest area instead of stopping at the
first clean verification pass. Skip entirely for early-stage repos (no
code or tests yet — nothing scoreable to climb), and for any repo with no
executable test suite, build, or lint to serve as the deterministic gate.

- Pick the weakest area from the Phase 6 wrap-up ("still open") and the
  mismatch log: the most open mismatches, or the lowest verification
  confidence. Name it when asking — the user may pick a different area
  instead.
- Ask: "Run the hill-climb loop on <area>, or ship as-is?" On no, go to
  Phase 8. On yes, load `hill-climb` and fill its authorization form
  from the polish context — no fresh walkthrough, the eval already
  exists:
  - Goal: improve <area> until the judge scores it 9/10.
  - Eval: the feature's acceptance criteria from Phase 2 plus the
    coding row of hill-climb's Define the Eval table.
  - Deterministic gate: the repo's test suite + build + lint (the
    Phase 1 baseline commands).
  - Threshold 9/10, max 8 rounds, plateau 2 rounds with no gain.
  - Baseline: score the post-Phase-6 version first — gate, then judge.
    If the gate fails, propose the fix and get user approval before
    starting the loop, or abort Phase 7 and go to Phase 8.
  - Editable files: the files for <area> (by default, the files
    changed in Phases 3–5 for this feature). Immutable: tests, the
    eval, everything else.
  - Worktree/branch: the same disposable branch this polish run uses.
    The branch will have uncommitted changes from Phases 1–6 — code,
    the Phase 3 regression tests, and docs/user-stories.md. The
    baseline checkpoint commit stages all of them explicitly
    (`git add -- <editable files> <test files> docs/user-stories.md
    && git commit -m "hill-climb baseline"`); that is the baseline,
    not dirt to clean first. Do NOT use `git add -A` (hill-climb
    forbids it) and do NOT use `git reset --hard` anywhere in the
    loop — reverts use only the scoped `git restore -- <editable
    files>` plus `git clean -fd -- <editable files>`, so uncommitted
    tests are never wiped. During rounds 1–8, stage and restore ONLY
    the editable files. Saying yes to the loop authorizes autonomous
    per-round edits within Editable files and local checkpoint
    commits on that branch (`hill-climb baseline`,
    `hill-climb round N: <score>/10`); push still needs a separate
    yes — Phase 8 handles that.
  - Cost cap: none enforceable (subscription / local model).
  - Pacing: same rule as the ground rules — ~20% of the active
    provider's window per hour, never 100%, check at every round
    boundary.
  - Harness check: if only one model provider is available (e.g. agy
    without Codex), follow hill-climb's Degraded 1-model mode: tell
    the user which seat is missing and get a "go", cap at 4 rounds,
    label every score single-judge, low confidence — a 9/10 there is
    NOT consensus.
- Follow `hill-climb` as written: one small change per round, gate
  first, zero-context judge, keep only if the score rises, plateau is
  a decision point — present the escape options and wait for the user's
  pick, do not auto-branch or restructure. Fix only what moves the
  eval score; park the rest as follow-ups in the mismatch log.
- When the loop stops, report the rounds in a table, the best score,
  what changed, what stalled, and the branch / checkpoint — then go
  to Phase 8.

## Phase 8: Ship

Do not stop at the wrap-up. Ask the user whether to open a pull request
for the changes. On yes, load `file-pr` and follow it. On no, leave the
changes uncommitted on the branch and say so.

Then check the Phase 1 map: if other features remain, ask "Continue with
the next feature ([Name]), or wrap up here?" If the user picks the next
feature, return to Phase 2 with it. The next feature continues on the
same branch — Phase 7 checkpoints stay in its history; start a fresh
branch only if the user asks. If they wrap up, stop.
