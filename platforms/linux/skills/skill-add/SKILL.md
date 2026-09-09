---
name: skill-add
description: >-
  Add a skill to the Prawn Skills Git clone on Linux from GitHub, a URL, pasted
  instructions, or a described workflow. Use when asked to add or install a skill.
license: MIT
metadata:
  platform: Linux
---

# Skill Add for Linux

Locate the clone from `~/.config/theprawnskills/library.json` (`library` key).
Read `<root>/platforms/linux/README.md` and the Linux `skill-authoring` variant.

Inspect the requested source and identify the intended name and purpose. Check
for an existing skill before adding a directory. Preserve licenses, attribution,
and necessary scripts/assets/references; do not include credentials or session
data. Write shared content under `skills/<name>/SKILL.md`, or a Linux variant
under `platforms/linux/skills/<name>/SKILL.md` when the difference is platform-specific.

Validate it and update the index and router as needed. Change the daily profile
only when requested; preview/apply/check local installation. Report the source,
installed path, validation, and any manual tool setup. Do not run `dotagents sync`.
