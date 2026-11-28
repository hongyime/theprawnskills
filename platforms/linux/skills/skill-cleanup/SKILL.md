---
name: skill-cleanup
description: >-
  When to read: the skill library is messy or a cleanup is requested. Use for: auditing
  duplicate, broken, default, and on-demand skills in a standalone install. Does: explains what
  is duplicated, broken, or unused and what to prune.
license: MIT
metadata:
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Skill Cleanup for Standalone Installs

Locate the clone from `~/.config/theprawnskills/library.json` (`library` key).
Read `<root>/platforms/linux/README.md`, including cleanup and removal rules.

Inventory the canonical library, standalone variants, daily profile, and relevant
local agent roots. Check symlink targets, managed copies, duplicate exposure, frontmatter,
referenced files, and platform prerequisites. Produce a table of path, label,
evidence, and recommended action. Use DEFAULT, ON-DEMAND, DUPLICATE, BROKEN,
KEEP, or ARCHIVE-CANDIDATE as appropriate.

Preserve all skills during migration. An audit does not authorize archiving.
On-demand skills remain useful even when not installed. For a separately
authorized removal, follow the standalone `skill-remove` workflow. Do not run
OneDrive propagation or `dotagents sync`.
