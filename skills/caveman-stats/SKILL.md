---
name: caveman-stats
description: >
  Show real token usage and estimated savings for the current session.
  Requires the external Caveman Claude Code plugin and its registered hooks.
  Triggers on /caveman-stats. Report unavailable when the runtime integration
  is absent; never estimate token counts or claim hooks ran without evidence.
---

This library contains the instruction only. The external Caveman plugin supplies
`caveman-stats.js` and `caveman-mode-tracker.js` and registers them with Claude
Code. Installing this skill alone does not install or activate those hooks.

When the registered hook provides measured output, relay it without inventing
additional numbers. Otherwise report: "Caveman statistics are unavailable in
this session because the required plugin hooks are not active." Other agents
must not assume they can read or reproduce Claude Code's session accounting.

Do not silently install a plugin, edit hook configuration, or fabricate estimated
savings. Plugin setup is a separate task using the host's supported installer.
