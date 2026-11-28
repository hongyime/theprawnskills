---
name: skill-reviewer
description: >-
  When to read: 'review skill', 'review skill PR', or 'check skill quality'. Use for: reviewing
  skill PRs with structured severity-rated feedback. Does: covers token budgets, routing
  conflicts, required sections, and repo conventions, with severity-classified findings and a
  summary table.
license: MIT
metadata:
  author: Local setup (adapted from the imported Microsoft skill)
  version: "1.1.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Skill PR Reviewer

Performs thorough, structured code reviews of skill PRs — severity-classified findings with actionable fixes, positive acknowledgment, and a summary table.

The four reference guides are locally authored for this library. Apply its
AGENTS.md, skill-authoring conventions, INDEX.md, and default-profile.toml.
Review bundled paths with the repository's resource audit and exercise changed
helpers in isolated fixtures. Do not assume provider-specific test registries,
hook systems, or routing algorithms exist in every agent.

## When to Use

- Reviewing a PR that adds or modifies a skill under `plugin/skills/` or `.github/skills/`
- Checking skill compliance before submitting a PR
- Auditing an existing skill for quality issues

Apply the conventions of the repository under review; a different library may
have its own profile, tests, licences, and discovery system.

## Review Workflow

1. **Collect** — Identify all changed skill files (SKILL.md, references, tests, scripts)
2. **Check** — Run each category from the [review checklist](references/review-checklist.md)
3. **Classify** — Assign severity per the [severity guide](references/severity-classification.md)
4. **Analyze Routing** — Check triggers for conflicts per [routing analysis](references/routing-analysis.md)
5. **Draft** — Write the review per the [output format](references/output-format.md)
6. **Validate** — Verify suggested fixes are actionable with accurate file/line references
7. **Probe behavior** — For changed workflows, use the existing `skill-creator`
   baseline/trigger evaluation facilities and the [behavior probe guide](references/behavior-probes.md).
   Run supportive, neutral and competing prompts as distinct cases. Static
   resource validation and a reviewer reading prompts are not measured activation.

Also publish this skill PR review as a hosted page: hand the finished file to `postplan-upload` and return the Postplan URL next to the local path.

## Error Handling

| Error | Remediation |
|-------|-------------|
| Cannot determine changed files | Ask user for the file list or PR number |
| Token counting unavailable | Estimate at ~4 chars per token |

## References

- [Review Checklist](references/review-checklist.md)
- [Severity Classification](references/severity-classification.md)
- [Routing Analysis](references/routing-analysis.md)
- [Output Format](references/output-format.md)
- [Behavior Probes](references/behavior-probes.md)
