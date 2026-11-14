---
name: interrogate
description: >-
  Use for "interrogate", "adversarial review", "multi-model review",
  "challenge this", "stress test this code", "find blind spots", or "tear this
  apart". Adversaries try to break a change or design, and only findings
  proven by a run survive.
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Interrogate

Adversaries try to break a change or a design. A finding survives only when a run proves it. Report the findings. Do not apply fixes.

## Frame

The scope is what the user names. Otherwise it is the branch diff from its merge base with the base branch, through the working tree. State the intent in your own words, from the user's message, the commits, and the PR description. Ask the user when the intent is unclear.

## Fan out

Run four adversaries in parallel, each in its own worktree. Copy the scope's uncommitted changes into each worktree. Delegate each adversary to a fresh agent context; if no delegation tool is available, run the four adversaries as separate phases in sequence, keeping each one's findings separate until verification. Give each adversary the scope, the intent, and this brief:

> Break this change. Prove each finding with a run against the real code, such as a failing test, a repro script, or command output that shows the wrong behavior. For a design or plan, run a prototype or probe the current tree. Keep repros in your own worktree. Report each finding with a title, the exact command, the output it printed, and the output the intent requires. Leave out anything you did not run. That covers style, naming, structure, and risks that need a future change to matter. No findings is a valid result.

## Verify

Verify each finding by rerunning its command. Keep a finding when the output shows the failure and the failure breaks the intent. Drop the rest. Merge findings that share a root cause.

Adversaries find different failures, so the verdict keeps every verified finding, not one adversary's list.

## Output

- **Intent**: the restatement.
- **Findings**: for each verified finding, the command, its output, how it breaks the intent, and the adversaries that found it. Say "no verified findings" when none survive.
- **Dropped**: for each adversary, the count of dropped findings and why.

## Provenance

Adapted from cursor/plugins `pstack/interrogate` (MIT).

Library adaptation: the arena fan-out and the in-your-own-words intent step are inlined (those skills were not imported); adversaries run as fresh agent contexts, or as separate phases when no delegation tool is available.
