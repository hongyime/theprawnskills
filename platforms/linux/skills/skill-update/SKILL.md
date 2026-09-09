---
name: skill-update
description: >-
  Update or improve existing Prawn Skills in a standalone Git clone using observed
  workflow evidence. Use when asked to refresh a skill or change its behavior.
license: MIT
metadata:
  platform: Windows, macOS, Linux
---

# Skill Update for Standalone Installs

Locate the clone from `~/.config/theprawnskills/library.json` (`library` key).
Read `<root>/platforms/linux/README.md` and the standalone `skill-authoring` variant.

Identify the requested skill or related set, then read each existing definition
fully. Gather evidence only from task-authorized paths. Make focused edits to
shared content or a standalone variant as appropriate; preserve OneDrive behavior,
attribution, and references. Do not turn a single observation into a universal rule.

Validate changed instructions/scripts, update index and routing when needed,
and preview/apply/check the Python installer after content or profile changes.
Existing symlinks follow source edits. Managed copies require `--apply` to
refresh; unchanged copies are backed up first, and local edits cause a conflict.
Review the Git diff and report the actual
changes and tests. Do not automatically propagate through `machines.toml`.
