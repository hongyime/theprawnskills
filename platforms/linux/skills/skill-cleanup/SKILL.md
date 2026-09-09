---
name: skill-cleanup
description: >-
  Audit and explain duplicate, broken, default, and on-demand skills in a Linux
  Prawn Skills installation. Use for messy skills or requests to clean up the library.
license: MIT
metadata:
  platform: Linux
---

# Skill Cleanup for Linux

Locate the clone from `~/.config/theprawnskills/library.json` (`library` key).
Read `<root>/platforms/linux/README.md`, including cleanup and removal rules.

Inventory the canonical library, Linux variants, daily profile, and relevant
local agent roots. Check symlink targets, duplicate exposure, frontmatter,
referenced files, and platform prerequisites. Produce a table of path, label,
evidence, and recommended action. Use DEFAULT, ON-DEMAND, DUPLICATE, BROKEN,
KEEP, or ARCHIVE-CANDIDATE as appropriate.

Preserve all skills during migration. An audit does not authorize archiving.
On-demand skills remain useful even when not installed. For a separately
authorized removal, follow the Linux `skill-remove` workflow. Do not run
Windows propagation or `dotagents sync`.
