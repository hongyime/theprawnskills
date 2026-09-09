---
name: skill-remove
description: >-
  Plan and carry out an explicitly requested standalone skill retirement with
  recoverable backups. Use for uninstalling or archiving an exact named skill.
license: MIT
metadata:
  platform: Windows, macOS, Linux
---

# Skill Remove for Standalone Installs

Locate the clone from `~/.config/theprawnskills/library.json` (`library` key).
Read `<root>/platforms/linux/README.md`, especially cleanup and removal rules.

Establish the exact skill and scope: installation only, source archive, or both.
Inspect affected links/copies, profile entries, router/index references, and variants.
Report the effect before canonical archiving unless the user already authorized
that exact scope. During migration, preserve all skills.

For an authorized retirement, preserve recoverable copies outside the checkout
in a dated backup directory. Verify resolved move targets stay within the intended
home before moving directories on Windows. Preserve local edits in installed
copies. Operate on installed links themselves, never delete
their source targets by following symlinks. Keep original upstream files and
licenses recoverable. Update relevant profile/index/router references and report
backup paths and verification. Do not touch plugin/system skills or propagate
through the Windows registry. The installer has no automatic removal mode.
