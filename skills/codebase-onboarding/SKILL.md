---
name: codebase-onboarding
description: >-
  Explain an unfamiliar repository using evidenced architecture, entry points,
  request or job flow, test commands and conventions. Use for onboard me,
  understand this repo, where do I start, or preparing a codebase orientation.
license: MIT; see LICENSE.txt
---

# Codebase Onboarding

Map how the existing repository works before proposing or making changes.

## When to use

Use for first-time orientation or an unfamiliar subsystem. Use `codebase-design`
to design a change, `systematic-debugging` for a specific failure, and
`session-handoff` to resume unfinished work. An onboarding request normally
authorizes reading and explaining, not running setup or rewriting instructions.

## Evidence-first workflow

1. Read AGENTS.md, existing project instructions and README. Note the repository
   root, branch and scope. Preserve applicable instructions when documentation
   disagrees with observed code; report the discrepancy for resolution.
2. Inspect source paths with `rg --files`, excluding dependency/build/generated
   trees. Read relevant manifests, lockfile/tool-version metadata, test config,
   CI and entry points. Avoid credentials and real environment files; consult
   sanitized examples only when needed. Do not recursively read the whole repo.
3. Identify languages and framework evidence, workspace boundaries and data
   stores. Distinguish a dependency's presence from actual use. In a monorepo,
   state the working directory for each command and component.
4. Trace one real request or job from entry through validation, business logic,
   persistence/external boundary and result. Cite existing paths and line
   numbers. If that trace is incomplete, mark the missing link; do not invent it.
5. Derive conventions from a few representative files and test/CI configuration.
   Inspect recent history only if available. For shallow/unborn repositories,
   state that historical conventions cannot be established.
6. Produce a concise map using the [output template](templates/orientation.md).
   Mark commands as observed, executed, unavailable or unknown. Reading a
   package script proves its definition, not that it succeeds. Flag stale README
   commands rather than silently repeating them.
7. Finish with the best starting locations for the user's task and concrete
   unknowns. Suggest next checks whose side effects fit the requested scope.

## Outputs and boundaries

Default to a conversation answer. Write a guide, AGENTS.md or CLAUDE.md only
when writing/updating that artifact is part of the user's task. Read existing
instructions first, merge relevant evidence and avoid conflicting duplicates.
Explicit authorization already given in the task does not need to be requested
again. Put any approved output in the target project, not this shared skill.

This is an instruction workflow; no scanner or generator script is advertised.
The [probe guide](references/probes.md) describes how to evaluate it on isolated
repositories, including checks that read-only work leaves no diff.

Adapted from [ECC codebase-onboarding](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/skills/codebase-onboarding/SKILL.md).
The [MIT notice](LICENSE.txt) is retained.
