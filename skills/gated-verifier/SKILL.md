---
name: gated-verifier
description: >-
  When to read: a delegated task finished executing and needs its verifier gate before merge,
  close-out, or DONE. Use for: running the fresh-context verifier pane, writing the evidence
  packet, and issuing PASS / FAIL / BLOCKED. Does: enforces the gate — different agent, different
  pane, plan + evidence pointers only, three-seat loop, packet-first verdict, no self-certification.
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Linux (Debian), Windows"
---

# Gated Verifier Pane

No non-trivial delegated work is reported DONE until a fresh-context verifier
pane — a different agent, in a different Herdr pane, with no proposer summary —
has independently verified it and issued a verdict, recorded as a file.

## When to use

Use after execute, before merge / test / close-out, for every non-exempt
delegated task. The gate sits in the standing workflow:

plan → approve → execute → **verify** → diff review + rectify → merge → test →
delete worktrees; never skip a gate.

## Exemption rule (testable, no judgement)

Work is exempt ONLY if ALL of these hold:

- Reversible in under a minute.
- No send (message, email, post, ping).
- No deploy.
- No write to a shared place (repo push, shared doc, dashboard, artifact,
  cron, live state).

If any one fails, gate it. If unsure whether exempt, gate it. Exempt work is
labelled `EXEMPT — cheap/reversible` in the close-out, never "verified" and
never PASS.

## The gate

1. **Plan file.** Task plan written to a file before execution. Packet lives
   alongside the plan file as `verification-packet.md`.
2. **Execute.** Implementer agent (default Codex) works in its own Herdr pane,
   fresh session, named pane, correct default workspace.
3. **Implementer hands off evidence, not a verdict.** Implementer writes an
   evidence file (separate file from the plan — never appends a summary to the
   plan file): what changed (files, commits), the exact commands run with
   working directory and verbatim exit codes / outputs, test
   collected/passed/failed/skipped counts, and pointers to the live artefacts
   (repo, branch, commit hash, test output). It does NOT write "done" or any
   summary judgement. A zero exit code with zero collected tests is not
   coverage.
4. **Verifier pane (fresh context).** Muse starts a DIFFERENT agent in a
   DIFFERENT Herdr pane, fresh session, on the implementer's machine.
   Verifier agent default: agy (challenger). If the implementer was agy, the
   verifier is Codex — never the same agent as the implementer. Never route
   verifier work to opencode-DeepSeek: no DeepSeek token exists (Bryan
   2026-11-27).
5. **Verifier inputs only.** The verifier is given ONLY: the plan file, the
   implementer's evidence-pointers file, and the repo / branch / commit. It is
   NOT given the implementer's summary or its "done" claim. If the evidence
   file contains a verdict or summary judgement, Muse strips it before handing
   the file to the verifier, and notes the strip in the packet's ASSUMPTION
   section.
6. **Three-seat loop.** The verifier runs: 1 position (its own assessment of
   the work against the plan), 1 challenge (the strongest case the work is
   wrong / incomplete / unverified), 1 verdict (PASS / FAIL / BLOCKED).
7. **Evidence packet.** The verifier writes one packet file per task,
   `verification-packet.md` alongside the plan file — see
   `verification-packet-template.md` in this skill directory. Sections:
   FACT (sourced), INFERENCE, ASSUMPTION, UNKNOWN, checks table, verdict.
8. **Gate decision.** Muse reads the packet — not the implementer's claim —
   and only then reports DONE / FAIL / BLOCKED to Bryan, in caveman close-out
   form (per-item done-or-not). FAIL → the implementer pane gets the packet's
   findings as a follow-up, no new Bryan question unless blocked. BLOCKED →
   report to Bryan as needing his decision.
9. **No "done" without fresh test output read in full.** The verifier re-runs
   (or re-reads in full, from the live artefact) the tests / build output the
   claim depends on. A test summary printed before a hang or non-zero exit is
   incomplete evidence. Check process liveness / the real record directly, not
   through a derived state.

## Verifier rules

- The verifier never shares a session with the implementer, and never reads
  the implementer's session history.
- Every FACT in a packet carries a source (file path + line / commit hash /
  command + verbatim exit code + output excerpt). Anything without a source is
  labelled INFERENCE, ASSUMPTION, or UNKNOWN — never FACT.
- A required check that is SKIPPED (reason) or UNAVAILABLE (prerequisite)
  leaves readiness unverified; it is never turned into PASS.
- If the work looks correct but the evidence is too thin to check, the verdict
  is BLOCKED (cannot verify), never PASS on trust.
- If the verifier is wrong and the implementer is right: the implementer pushes
  back with reasoning and evidence (per `requesting-code-review`); Muse
  adjudicates from the packet; Bryan is the final arbiter, not the verifier.

## Evidence contract

Per `verification-loop`: use PASS, FAIL, SKIPPED (reason), UNAVAILABLE
(prerequisite), NOT APPLICABLE (reason) per check.

| Check | Required evidence |
|---|---|
| Build / types / lint | Command, working directory, exit code, relevant findings |
| Tests | Command, collected/passed/failed/skipped counts |
| Behavior | Requirement exercised and observed result |
| Security | Scanner and scope, redacted finding count, unavailable dependencies |
| Diff | Base/head or working-tree scope, changed files, untested later changes |

## Dispatch and proof

- Start the verifier pane through Herdr Core (`hc`) only, named pane, correct
  workspace — never an unlabeled pane, never the cargo `herdr` server.
- Proof follows the `herdr_auto_driver` dispatch-proof rule: fresh `hc ls` +
  `hc get` + short screen-tail read, recorded in the dispatch log. Visibility
  is claimed only after the proof check; `unknown` status is never proof.
- Never remove the last pane in a workspace. Count panes fresh before closing
  any pane.

## Cost

The gate applies per task, not per sub-step. A second fresh agent roughly
doubles agent spend on gated tasks; that is what the exemption is for. Pacing:
about 20% of the active provider's limit window per hour, never 100% — check
remaining budget at step boundaries.

## Invariants

- V1: A non-exempt task is never reported DONE to Bryan without a verifier
  packet file whose verdict is PASS.
- V2: The verifier pane is a different agent in a different Herdr pane with a
  fresh session; it never shares a session with the implementer.
- V3: The verifier receives the plan + evidence pointers only; it never
  receives the implementer's summary or "done" claim before its verdict.
- V4: Every FACT in a packet carries a source; anything without a source is
  labelled INFERENCE, ASSUMPTION, or UNKNOWN, never FACT.
- V5: A required check that is SKIPPED or UNAVAILABLE leaves readiness
  unverified; it is never reported as PASS.
- V6: The verifier re-reads or re-runs the test/build output the claim depends
  on in full; a summary or a pre-hang printout is not evidence.
- V7: A FAIL verdict routes findings back to the implementer without a new
  Bryan question, unless the packet is BLOCKED.

## Companions

Wires together, does not replace: `verification-loop` (evidence contract),
`requesting-code-review` (fresh-session reviewer, pushback rule),
`verify-before-claiming` (read-back proof, per-item close-out),
`herdr_auto_driver` (dispatch proof, close guard). Reporting to Bryan is
caveman voice, per-item done-or-not.
