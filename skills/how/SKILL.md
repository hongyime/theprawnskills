---
name: how
description: >-
  Use for "how does X work", code walkthroughs before changing something, and
  placement / ownership / layering questions ("where should this live", "which
  package owns this", "is this the right layer"). Explains subsystem
  architecture, runtime flow, onboarding mental models. Use why for
  motivation.
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# How

Explore the codebase to answer "how does X work?" questions. Produce architectural explanations at the level of a senior engineer onboarding onto a subsystem, enough to build a working mental model, not so much that it reads like annotated source code.

Explorers and the explainer each run as a separate delegated agent context, with the strongest reasoning model available to you. If only one provider is available, use it for every role and say so; do not invent a second provider. If no delegation tool is available, run the phases in sequence in one session, keeping each explorer's findings separate until synthesis. Explorers read only; they must not write anything.

## 1. Assess complexity

If the scope is ambiguous, state your interpretation and explore. The user can redirect.

- **Simple** (a single module, a small utility, a narrow question such as "how does function X work"): no explorers. Spawn one explainer that explores and explains in one pass, built from `references/explainer-prompt.md` without the explorer-findings section. Go to step 4.
- **Complex** (a subsystem spanning multiple files or services, a cross-cutting feature, a full architectural overview): go to step 2.

When in doubt, take the simple path.

## 2. Explore (complex only)

Decompose the question into 2 to 4 angles, each a distinct slice of the subsystem. Spawn all explorers in a single message, each with `references/explorer-prompt.md` and its angle filled in.

## 3. Synthesize (complex only)

Once all explorers have returned, spawn one explainer with `references/explainer-prompt.md` and every explorer's findings filled in.

## 4. Present

Present the explainer's output. Light edits for clarity or context from the conversation are fine. Do not substantially rewrite it.

## Output format

The explanation uses the sections defined in `references/explainer-prompt.md`, dropping any that do not apply: Overview, Key Concepts, How It Works, Where Things Live, Gotchas.

## Provenance

Adapted from cursor/plugins `pstack/how` (MIT).

Library adaptation: Cursor model routing (`pstack-models.mdc`, model slugs) replaced with strongest-available-model guidance.
