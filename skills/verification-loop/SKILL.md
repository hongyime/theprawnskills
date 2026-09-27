---
name: verification-loop
description: >-
  Verify a completed change with the project's actual build, type, lint, test and
  diff checks before reporting readiness. Use for verify this change, ready for
  review, prove this works, or completion checks across any supported harness.
license: MIT
metadata:
  author: Local setup, adapted from ECC
  version: "1.0.0"
  platform: Windows, macOS, Linux
---

# Verify a Change

Turn a completion claim into evidence tied to the actual change.

## When to use

Use after implementation or before a review/merge decision. For SPEC.md drift,
use `check`. For a live browser flow, use `webapp-testing` or an available host's
flow-verification skill; consume its evidence without repeating the same run.
Do not run a full build for a wording-only edit or introduce a test framework
solely to satisfy this checklist.

## Workflow

1. Read the request, repository instructions and acceptance criteria. Identify
   the real scope: working tree, staged changes, commit range or PR base/head.
   Include untracked files when the task includes them. Do not assume HEAD~1
   is the review base; it misses uncommitted work and multi-commit changes.
2. Discover commands from manifests, CI and project docs. Preserve the project's
   package manager, versions, framework, coverage policy and test boundaries.
   Missing commands are unavailable checks, not a reason to invent npm scripts.
3. Select the smallest checks that cover the changed behavior: build/types/lint
   as applicable, focused regression tests, then broader checks required by the
   repo or justified by integration risk. A zero exit code with zero collected
   tests is not test coverage. Inspect skips and unexpected empty discovery.
4. Run each command with its working directory and capture its real exit code.
   Keep full output locally when needed; summarize without masking failures
   through head/tail pipelines. In PowerShell, capture `$LASTEXITCODE`
   immediately after a native command, before another native command runs.
5. Use the repo's configured secret/security checks for relevant changes. Never
   label a grep for key-shaped strings a security audit or print matched secrets.
   State scan scope and missing prerequisites. Inspect Markdown/config changes
   too when they can carry credentials or executable agent instructions.
6. Review the actual diff for unintended changes, boundary cases, generated
   files and changes made after testing. Fix within the authorized scope, then
   rerun checks affected by the fix. Do not endlessly repeat successful checks.
7. Report evidence and remaining limitations. Readiness is not authorization to
   commit, push, merge or deploy. Use existing authorization for those actions.

## Evidence contract

| Check | Required evidence |
|---|---|
| Build / types / lint | Command, working directory, exit code, relevant findings |
| Tests | Command, collected/passed/failed/skipped counts and coverage if measured |
| Behavior | Requirement exercised and observed result; mocks versus real integration |
| Security | Scanner and scope, redacted finding count, unavailable dependencies |
| Diff | Base/head or working-tree scope, changed files, untested later changes |

Use **PASS**, **FAIL**, **SKIPPED (reason)**, **UNAVAILABLE (prerequisite)** or
**NOT APPLICABLE (reason)** per check. Required unavailable/skipped checks leave
readiness unverified. Never turn them into PASS. A test summary printed before
a hang or nonzero process exit is incomplete evidence.

## Prerequisites and companions

This is instructions-only: it supplies no `/verify` command, hooks or scanner.
Use the loaded project's tools. Route through `skill-router` to find
`python-testing`, `react-testing`, `webapp-testing`, `requesting-code-review`,
`security-best-practices` or `session-handoff` when relevant.

## Provenance

Adapted from [ECC verification-loop at the reviewed revision](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/skills/verification-loop/SKILL.md).
See [MIT notice](LICENSE.txt). Local changes replace fixed commands/thresholds,
timed repetition and superficial security checks with project-scoped evidence.
