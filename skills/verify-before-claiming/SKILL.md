---
name: verify-before-claiming
description: >-
  Do not report work done until it has been read back live from its destination.
  Use before any done / complete / shipped claim to Bryan: state what was claimed,
  where it lives, how it was read back, and the verbatim evidence.
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Verify Before Claiming

A write is a claim. The read-back is the evidence.

## The rule

Before any "done" reaches Bryan, the reporter states, for each item:

1. What was claimed.
2. Where it lives (exact destination: machine, repo, branch, path, record id).
3. How it was read back.
4. The verbatim evidence (exit code, commit hash, row counts, contents, record id).

A script counting the calls it made is not evidence. A delegated agent saying
it sent / wrote / deployed something is not evidence.

## Forbidden proxies

These are never evidence, however confident the wording:

- Call counts, "N calls succeeded", "all steps ran".
- A subagent / Codex / agy / opencode handoff saying done, without your own
  destination check.
- A cached fetch, a stale page, a remembered pane state, a summary printed
  before a hang or non-zero exit.
- "It compiles", "no errors printed", a test summary with zero collected tests.

## Evidence by destination (minimum)

| Destination | Minimum read-back |
|---|---|
| Code / repo | commit hash + diff scope + test/build command, exit code, pass/fail counts |
| Database / dashboard | live read (getperson / getdashboard / equivalent) showing the actual rows, counts, contents |
| File / artifact | file exists on disk at the stated path, byte/row count, and (for artifacts) the live card / inspect result |
| Cron / tracker | last run log + stored state advanced (watermark / count changed), not just "ran" |
| Browser / live page | live page state as observed, not a cached fetch |
| Herdr pane | fresh screen-tail / `hc` status, not a remembered pane state |

Read-back against the wrong destination (stale cache, wrong machine, wrong
branch) is not read-back. Name the destination in the evidence.

## Evidence contract

Per check, use **PASS**, **FAIL**, **SKIPPED (reason)**,
**UNAVAILABLE (prerequisite)** or **NOT APPLICABLE (reason)** — the same
contract as `verification-loop`. A required check that is SKIPPED or
UNAVAILABLE leaves readiness unverified. Never turn it into PASS.

Verify against the real artifact, not a proxy, a self-report, or "it
compiles". Read the actual value, not a cached or derived representation;
check process liveness directly, not through derived state.

## Partial and unavailable

- Partial work is labelled partial, with the unmeasured / unverified scope
  named in the same message. Never present partial coverage as a gate or as
  whole-repo / whole-queue coverage (e.g. "3/51 measured, 48 unmeasured,
  not a whole-repo gate").
- Unavailable or skipped checks are labelled UNAVAILABLE / SKIPPED with the
  reason — never PASS.

## Exempt: trivial reversible claims

Trivial reversible claims are exempt from read-back (e.g. "renamed chat").
Everything that writes, sends, deploys, or reports a count is covered —
no exemption.

## Close-out format

Every finished run ends with one per-item list, verdict first, caveman style
(bullets, facts/numbers/paths verbatim, no prose chunks):

```text
<Run name> — DONE / PARTIAL / BLOCKED / NEEDS DECISION
- DONE — <item>: <verbatim evidence, one line>
- PARTIAL — <item>: <what is done, what is unmeasured / unverified>
- NOT DONE — <item>: <reason, what is missing>
- BLOCKED — <item>: <blocker, who/what unblocks it>
Still open: <list, or "nothing open">
```

Rules: every item appears exactly once. A DONE item without cited evidence
counts as NOT DONE. "Still open" is mandatory even when empty. A bare
"Done" is not a close-out. Silence is not a close-out — if the worker dies,
the dispatcher sends the close-out.

## Companions

- `verification-loop`: build/test/diff evidence for a code change. This skill
  is the reporting rule on top of it; it does not replace it.
- Spec 08 (gated verifier pane): a fresh agent independently checks the work.
  This skill is the reporter's own check; spec 08 is the independent checker.
  Cross-reference, do not merge.
- Spec 12 (read-back proof for writes): per-write proof mechanics (row
  counts, getperson/getdashboard diffs). This skill defines the claim →
  evidence rule; spec 12 defines the per-write steps. Cross-reference,
  do not merge.
