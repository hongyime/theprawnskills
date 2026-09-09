---
name: skill-create
description: >-
  Create a new reusable skill in a standalone Prawn Skills Git clone. Use when
  asked to create a skill, teach an agent a workflow, or make future agents know it.
license: MIT
metadata:
  platform: Windows, macOS, Linux
---

# Skill Create for Standalone Installs

Locate the clone from `~/.config/theprawnskills/library.json` (`library` key).
Read `<root>/platforms/linux/README.md` and the standalone `skill-authoring` variant.

1. Choose a focused lowercase kebab-case name and check for an existing match.
2. Create `skills/<name>/SKILL.md`, including accurate trigger language and
   only the supporting files needed for its workflow.
3. Validate frontmatter, references, and any scripts. Update `INDEX.md` and
   the router if discovery changes.
4. Keep it on demand unless daily exposure is requested. For daily exposure,
   update the profile and preview/apply/check the local Python installer.
5. Report the source path, validation, exposure, and any missing prerequisites.

Do not propagate through the Windows machine registry or overwrite an existing
skill as part of creating a new one.
