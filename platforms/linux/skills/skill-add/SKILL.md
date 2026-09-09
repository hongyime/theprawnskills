---
name: skill-add
description: >-
  Add a skill to a standalone Prawn Skills Git clone from GitHub, a URL, pasted
  instructions, or a described workflow. Use when asked to add or install a skill.
license: MIT
metadata:
  platform: Windows, macOS, Linux
---

# Skill Add for Standalone Installs

Locate the clone from `~/.config/theprawnskills/library.json` (`library` key).
Read `<root>/platforms/linux/README.md` and the standalone `skill-authoring` variant.

Inspect the requested source and identify the intended name and purpose. Check
for an existing skill before adding a directory. Preserve licenses, attribution,
and necessary scripts/assets/references; do not include credentials or session
data. Write shared content under `skills/<name>/SKILL.md`, or a standalone variant
under `platforms/linux/skills/<name>/SKILL.md` for workflows that differ from OneDrive.

Validate it and update the index and router as needed. Change the daily profile
only when requested; preview/apply/check local installation. Report the source,
installed path, validation, and any manual tool setup. Do not run `dotagents sync`.
