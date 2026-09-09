---
name: skill-authoring
description: >-
  Apply Linux conventions for creating, editing, validating, or auditing Prawn
  Skills in a Git clone. Use for SKILL.md changes and skill library maintenance.
license: MIT
metadata:
  platform: Linux
---

# Skill Authoring for Linux

Read the `library` path from `~/.config/theprawnskills/library.json`, then read
`<root>/platforms/linux/README.md` fully and follow its authoring conventions.
Read the active profile from `<root>/default-profile.toml`. The original
Windows management instructions are not the Linux installation procedure.

Create shared skills under `<root>/skills`; use `<root>/platforms/linux/skills`
for platform-specific variants. Validate frontmatter, references, and affected
behavior. Preserve attribution and supporting files. Update the index and
router when appropriate, and preview local installation before applying it.
Keep machine credentials and local installation state outside the repository.
