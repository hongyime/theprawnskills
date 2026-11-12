---
name: hill-climb
description: >-
  Hill climb any scoreable goal — code, research, or UI — by looping implement, judge, fix until a threshold or plateau. Use when the user says hill climb, hill climbing, climb the hill, iterate until it scores, or keep improving until it hits 9, or when they ask the agent to walk them through defining the goal and eval first. Generic, not UI-only.
license: MIT
metadata:
  author: Local setup
  version: "1.5.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Hill Climb

Turn a fuzzy goal into a score, then climb the score. One small change at a
time, keep it only if the score goes up, revert if it goes down. Stop at the
threshold, at a plateau, or at the round cap — whichever comes first.

Origin: Theo Browne (t3.gg), "Agents Sucked At UI (Until Today)", 2026-11-03,
and the `council` skill in t3dotgg/tstack. Theo's version scores UI with
three models from three providers. This skill generalises it: any goal that
can be scored, with one implementer provider, one model-judge provider,
and one deterministic gate.

## When To Use

- The goal has no single right answer, but quality can be scored 0-10:
  code quality, a research idea, a UI, docs, a prompt, a design.
- The user says "hill climb", "keep improving until it scores X", or
  "iterate until the judges are happy".
- A deterministic check exists (tests, build, lint, a checklist, counts)
  that can act as a hard gate alongside model judges.

## When NOT To Use

- One-pass edits, routine fixes, or a task with a binary pass/fail and no
  quality gradient — use `bounded-agent-loop` instead.
- No score can be defined even after the walkthrough below. If you cannot
  say what "better" means and how to measure it, stop and ask. No score,
  no hill. Do not guess an eval silently.
- Unattended scheduling. A hill climb is a supervised, bounded run, not a
  cron job. Do not merge, deploy, or enable a schedule from it.

## Judges

Only two model providers are assumed available. Do not invent a third.

| Seat | Provider | Role |
|---|---|---|
| Implementer, first | agy (Gemini) | Makes the change |
| Model judge / critic | Codex (OpenAI) | Scores it, lists fixes, never implements its own review |
| 3rd judge — deterministic | Tests / build / lint / checklist / counts | Hard gate. Must pass before any model score counts. No model, no cost, no bias. |

Full Mode has ONE model judge (Codex), not two. The deterministic gate
is the 3rd judge, pass/fail, never scored. There is no second model
judge in Full Mode — the implementer never scores its own work.

Do not assume any other provider is available. Check before using one;
if it is unavailable, report it instead of substituting. A third model
may be used only as a final tie-breaker if the user explicitly asks,
and say so in the report.

Swap implementer and critic on the next run if the user asks, or if one
model stalls. Never let the same model review its own work in the same
round: same family is the same person at a different time of day.
Exception: the explicitly labelled degraded 1-model and no-delegate
modes below, where the same model reviews in a fresh context and the
score is labelled single-judge / self-review, low confidence, never
consensus. That exception does not apply in Full Mode.

The orchestrator is not a judge in this loop. It drives the agent pane,
reads the result, and decides keep / revert / next step. The user
is the final judge on taste calls.

## If the Harness Cannot Call the Other Models (Fallback)

Check availability BEFORE starting the loop, not mid-climb: agy auth,
Codex auth / quota, agent pane reachable, deterministic gate command
exists and runs. Report exactly what is missing. Never invent a
provider, never fake a score, never silently substitute a same-family
model and call it a different judge.

| Mode | When | What changes |
|---|---|---|
| Full | agy + Codex + deterministic gate all reachable | As in The Loop below. Threshold = model judge >= 9 AND gate passed. |
| Degraded, 1 model | Only one of agy / Codex reachable | Implementer = available model. Critic = same model in a fresh context, different role prompt, read-only. Deterministic gate still hard. Human is final judge. Label every score "single-judge, low confidence". A 9/10 here is NOT consensus — if it hits 9, pause and ask the user whether to accept it as final. Cap at 4 rounds unless the user says more. |
| Degraded, 0 models | No other model reachable, only the orchestrator | No model scores at all. Deterministic gate only. Do not invent scores. Run as `bounded-agent-loop` instead, or stop and ask the user to score it / supply a judge. |
| No delegate tool | Harness cannot spawn subagents / agent pane unavailable | Run sequentially in one pane, one round at a time, with the review in a FRESH context (new session / fresh turn, never the same turn as the implementation). This is single-agent self-review, NOT a second judge: label every score "self-review, low confidence", human is final judge, cap at 4 rounds. If it hits 9, pause and ask the user whether to accept it as final. Threshold here does NOT count as consensus. See `requesting-code-review` fallback. |

Rules for any degraded mode:

- Tell the user the mode, which seats are missing, and what that costs
  in confidence — then get their "go" before continuing, unless they
  pre-approved degraded mode for this run.
- Never run at API prices without warning the user first.
- If a provider dies mid-climb: checkpoint the best version, stop the
  round, report what was lost, and ask whether to continue degraded,
  swap implementer / critic, or stop. Do not carry on as if nothing
  happened.

## If the Goal / Eval Is Unspecified (Walkthrough)

Do NOT start the loop with a blank goal or eval. Walk the user through
it first. Ask at most 5 questions, one at a time, in plain language.
Suggest a default with every question, so the user can just say "use
that", edit it, or say "I don't know".

1. What are we improving, in one sentence?
2. What does good look like — what would a 9/10 mean here?
3. How do we check it — tests, a checklist, screenshots, sources?
4. What must NOT change?
5. When do we stop — threshold, rounds, or time?

If the user is unsure, do the suggesting for them. Concrete defaults
per question — offer these verbatim, do not invent different ones:

| # | Question | Suggested default |
|---|---|---|
| 1 | What are we improving? | "Improve <the artefact, in the user's words> until the judges score it 9/10" |
| 2 | What does 9/10 mean? | The Model score column from the Define the Eval table for their task type (coding / research / UI / docs) |
| 3 | How do we check it? | The Deterministic gate column from the same table (tests + lint + build; sources checked; screenshots; checklist) |
| 4 | What must NOT change? | Tests, the eval itself, and every file in Immutable — by default, nothing outside Editable files |
| 5 | When do we stop? | Threshold 9/10 from the model judge, gate passed, max 8 rounds, plateau 2 rounds with no gain |

- Propose a draft goal and eval from the Define the Eval table for
  their task type (coding / research / UI / docs), with defaults:
  threshold 9/10, max 8 rounds, plateau 2.
- If they say "I don't know" to a question, offer 2-3 options,
  recommend one, and say why in one line. Let them pick.
- Fill in the authorization form below with your draft, show it back,
  and get an explicit "go" before starting. The user never has to fill
  a blank form.
- Score the baseline first and show it to them. Seeing a 5/10 and what
  the judges would fix often clarifies the goal faster than more
  questions.

If after the walkthrough there is still no scoreable eval, stop. Do
not guess one silently. Say what is missing, and offer `bounded-agent-loop`
or a one-pass draft instead.

## Authorizing a Run

Needs explicit authorization and hard limits before it starts. Fill every
field — an unfilled budget is not an unlimited budget, it is a reason to
stop and ask.

```text
Run a hill climb.

Goal:                <one sentence, what "top of the hill" looks like>
Eval:                <how to score 0-10, who scores, what counts>
Deterministic gate:  <exact command / checklist that must pass first>
Threshold:           <default 9/10 from the model judge, gate passed>
Max rounds:          <default 8>
Plateau:             <default 2 rounds with no gain = stop>
Baseline:            <score the starting version — must be scored before the loop starts>
Editable files:      <explicit paths the worker may change>
Immutable:           <tests, eval, and files it must not touch>
Worktree/branch:     <disposable branch or worktree to use>
Cost cap:            <limit, or "none enforceable">
```

## Define the Eval

| Task | Deterministic gate | Model score 0-10 |
|---|---|---|
| Coding | tests + lint + build pass, no regressions | Correctness, clarity, scope discipline, no over-engineering |
| Research idea | Sources checked, claims traceable, gaps listed | Accuracy, evidence, coverage, novelty, falsifiability |
| UI | Screenshots light + dark, desktop + phone, empty + full | Layout, hierarchy, consistency, distinctiveness |
| Docs / writing | Checklist: facts verified, no invented claims | Clarity, completeness, tone, structure |

Score the baseline first, before any change — in this order: run the
deterministic gate on the baseline, then score it. If the gate fails
on the baseline, the baseline score is reference-only and the loop
does NOT start until the gate passes; fix the baseline first. A
gate-failed baseline score never counts as a kept score.
Every 3rd round, re-score the baseline: if the re-score differs by
more than 1 from the original baseline, report the drift and re-anchor
like this: set baseline = new re-score, set best kept score = new
re-score, and mark all earlier scores as old-scale in the report —
pre-drift and post-drift scores are not comparable. If a
judge scores something that is not in the screenshots / code / sources
in front of it, discard that finding and say so — check every finding
against the artefact before acting on it.

## The Loop

Score rule — read this before step 5. There is ONE model judge and
one deterministic gate, and "the score went up" means all of this:

- Score = the model judge's 0-10 score for that round. The
  deterministic gate is pass/fail, it is never scored.
- Keep = judge score rose vs the best kept score so far, AND the gate
  passed. Compare only against the last kept round or the baseline —
  never against a reverted round.
- Threshold = model judge scores >= 9 AND the gate passes in the same
  round.
- Plateau = judge score did not rise above the best kept score for 2
  consecutive rounds. Flat is not a gain.

Checkpoint / revert mechanics. The loop runs ONLY on a disposable
branch / worktree. Before starting, verify the worktree is clean
(`git status --porcelain` empty, except files the loop is about to
edit). Stage ONLY the editable files from the authorization form —
never the whole tree: `git add -- <editable files>`. Checkpoint the
baseline first: commit those files with `git commit -m "hill-climb
baseline"`. Record that commit as the best checkpoint. On every kept
round, commit the editable files again:
`git commit -m "hill-climb round N: <score>/10"`, and update the best
checkpoint. On every revert, go back to the best checkpoint with
`git restore -- <editable files>` plus
`git clean -fd -- <editable files>` (or `git reset --hard
<best-checkpoint>` as a last resort, disposable branch only). These
commands destroy uncommitted state — never run them on a shared
branch, and never run `git add -A` or a bare `git clean -fd` here.
Never let dirty edits from a reverted round contaminate the next
attempt.

1. Record goal, eval, threshold, max rounds, plateau, baseline score,
   editable files, and immutable eval. Checkpoint the baseline
   (commit on the disposable branch, per above).
2. Implementer (agy first) makes ONE small change toward the judges'
   last notes. Small, or the score change tells you nothing.
3. Run the deterministic gate. Fail = revert (per above), record the
   failure, next attempt. Never weaken the gate, the tests, or the eval
   to get a pass.
4. The model judge scores the new version 0-10, read-only, with
   specific fixes listed. A fresh review after fixes is a new round.
   Every 3rd round, re-score the baseline (see Define the Eval); if
   drift is more than 1, report it and re-anchor.
5. Keep only if the judge score went up vs the best kept score (see
   Score rule above) AND the gate passed. On keep, commit and update
   the best checkpoint. On revert, reset to the best checkpoint.
   Revert if it went down or flat with no new information. Keep the
   best version seen so far, always.
6. Stop on: threshold reached by the model judge with the gate passed,
   plateau (default 2 rounds with no gain, per Score rule), max rounds,
   budget out, scope change, or missing tools / credentials. Plateau is
   a decision point, not a failure — report the best score and ask the
   user what the top is.
   Theo's line: "once you're climbing the hill, you decide what the top is."
7. Report rounds in a table, best score, what changed, what stalled,
   and the branch / checkpoint. Do not merge or deploy. That is a
   separate authorization.

## Escaping a Local Peak

Hill climbing gets stuck. When the score is flat for 2 rounds, the
loop STOPS (plateau). Do not autonomously branch, restructure, or
keep iterating. Present these options to the user and wait for their
pick — only proceed on their explicit pick:

- Change the approach, not the colour: restructure, split, remove, or
  restart from the best checkpoint with a different strategy.
- Or branch 2-3 different approaches in parallel worktrees, score each
  once, keep the best branch.
- Or stop. A flat score is usually waiting on a human decision, not
  more loops.

## Scope

Fight scope creep. The judges will find more things every round; fix
only what moves the eval score for this goal. Park the rest as
follow-ups. A climb that keeps widening never reaches the top.

## Agent Delegation

- Work through a visible agent pane, one step at a time, pasted so it
  is visible. Read the result, evaluate it, then paste the next step
  or a correction without asking. Report only when DONE, BLOCKED, or
  needing a decision.
- Never use headless exec (`codex exec`, `opencode run` with a piped
  prompt) for fleet-machine work — use a visible pane. On a standalone
  machine with no agent pane, one headless run is allowed for a
  review / audit step only: prompt from a file, log to the agent's log
  directory, no edits beyond the report. Never hijack another live agent.
- The orchestrator drives; the agent in the pane does the work.

## Debian / Linux (Standalone) — Addendum

The shared `skill-authoring` / `skill-create` texts are Windows /
OneDrive-first. Linux / Debian is first-class here too.

- Resolve the library clone from `~/.config/theprawnskills/library.json`
  (`library` key), never guess the path.
- Installed skills: `~/.agents/skills` (Linux, symlinks). Never edit
  an installed copy; edit the clone.
- Installer (Python 3.11+): run the repository installer from the library
  root — see `platforms/linux/README.md` for the exact
  `--dry-run` / `--apply` / `--check` commands. Auto mode is symlinks on
  Linux, copies on Windows.
- Shell: bash with `python3` on Linux, PowerShell on Windows.
  Do not copy Windows paths, OneDrive paths, or `dotagents sync`
  into a Linux run. Do not use the Windows machine registry
  for standalone propagation.
- This skill is ON-DEMAND, not in `default-profile.toml`, unless
  daily exposure is requested. Keep `default-profile.toml` as the
  shared daily selection; check all supported OSes before changing
  profile membership.

## Related Skills

- `bounded-agent-loop` — the closest existing skill; bounded repair
  loop with an acceptance command, max 3 attempts. Use it when the
  eval is pass/fail, not a score.
- `skill-judge` — multi-dimensional scoring; the scoring half of a
  council, for skills.
- `requesting-code-review` — review, fix, re-review loop.
- `skill-create`, `skill-authoring` — how this skill was made.
  Standalone variants live under `platforms/linux/skills/`.
- `skill-creator` — generic upstream skill-creation loop
  (draft, test, eval, rewrite, repeat). Method only; its Claude-only
  eval tooling and paths do not apply here.
- `skill-add` — import an existing skill from GitHub / a link / pasted
  text. Not used here: this skill is new, not imported, and Theo's
  `council` was adapted, not copied verbatim.

## Provenance

Adapted from Theo Browne's `council` skill (t3dotgg/tstack, MIT) and
the video "Agents Sucked At UI (Until Today)", 2026-11-03. Generalised
from UI-only to any scoreable goal, and from three providers to one
implementer provider, one model-judge provider, and one deterministic
gate.
