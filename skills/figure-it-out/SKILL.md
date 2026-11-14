---
name: figure-it-out
description: >-
  Design an auditable playbook when no narrower one fits: a large migration,
  an ambitious multi-part change, or work a human reviews after stepping away.
  Scales rigor to the task, runs a hypothesis loop, and logs decisions. Use
  for /figure-it-out or 'figure it out'.
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Figure it out

When the task matches no playbook, design one. The deliverable before any code is the workflow itself: a sequence of phases that scales rigor to the task, runs the scientific method, and leaves a decision trail a human can audit after stepping away.

## Start

Open a todolist whose first item is to state the working principles for this run: the definition of done must be a falsifiable predicate (checkable by running something, not by reading a writeup); reversible work proceeds without waiting on the user; rigor is gates and artifacts, not "try harder". Then add the phases below as todos.

## Phase A: Frame

Ground first, then commit. Don't start the run until you can state:

- The definition of done as a falsifiable predicate: checkable by running something against the real artifact, not by reading a writeup.
- Scope, quantified: rough units and effort, plus the blockers grounding surfaced.
- The rigor level, biased high. One-way doors and high blast radius get more. Reversible low-stakes steps get less. Rigor is gates and artifacts, not "try harder".

Present the framing and tradeoffs before committing to a long run. Reversible work proceeds without waiting on the user, but a multi-hour run earns one checkpoint.

## Phase B: Design the workflow

Decompose into atomic, independently-landable units. Sequence riskiest-unknown-first. Scaffold and verification come before features.

- Build the verification harness before the work, with the baseline captured from the pre-change state, so the check reads as "old value vs new value".
- For one-way-door design decisions, get a second perspective on the design before committing (see `interrogate` for an adversarial pass). Skip it for mechanical work whose shape is already concrete. A second review pass over a settled design is over-engineering: subtract before adding.
- Decide what fans out. Parallelize only across seams, and give each worker its own worktree or branch so shared state is never written concurrently. Don't over-fan. Use the strongest reasoning model available for each worker; if only one provider is available, say so.
- Write the designed phase list down. That list is what the human reviews.

Then execute the design. Add its steps to the todolist as concrete items between the Phase C and Phase D entries. Run each under the Phase C loop discipline, and weave the Phase D log through them, a row as each step lands, rather than saving the whole trail for the end.

## Phase C: Run the loop

Each unit is an experiment. State the hypothesis, make the smallest change, measure against the predicate on the real artifact, keep it if it advanced, revert it if it didn't. Verify each unit before starting the next instead of batching checks at the end.

- Verify by inspecting the artifact, never a self-report. When something passes too easily, suspect the observation method before the system.
- Pair delegated work with a judge. If a worker games the gate, reset and harden the contract. If the gate itself is wrong, fix the gate in its own change rather than routing around it.
- A verdict is VERIFIED, NOT VERIFIED, or INCONCLUSIVE. Inconclusive is not a pass. Don't hide a negative.

## Phase D: Keep the audit trail

Log the run via the **show-me-your-work** skill. figure-it-out's work is usually ambitious enough to commit the trail so the reviewer can read it in the PR. The trail plus the diff is what lets the human come back and trust the work.

## Phase E: Verify and hand back

Check the whole against the Phase A predicate on the real product, not just the harness. Encode any recurring correction in structure — a gate, a lint rule, a check, or a script — so the next agent can't repeat it.

**Reply:** the playbook you designed, the rigor level and why, the decision-trail path, what's verified against the predicate, and what's still open.

## Provenance

Adapted from cursor/plugins `pstack/figure-it-out` (MIT).

Library adaptation: poteto-mode principles and the architect/arena references are inlined as plain guidance; `show-me-your-work` is imported.
