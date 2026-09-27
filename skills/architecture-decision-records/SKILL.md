---
name: architecture-decision-records
description: >-
  Record or explain significant architectural decisions with context,
  alternatives, consequences and proposed/accepted/superseded status. Use for
  ADRs, record this decision, why did we choose this, or durable design rationale.
license: MIT; see LICENSE.txt
---

# Architecture Decision Records

Preserve why a significant architectural choice was made and what supersedes it.

## When to use

Use for material decisions about boundaries, contracts, storage, security,
frameworks, infrastructure or engineering policy. Routine formatting and variable
names rarely need an ADR. Use `codebase-design` to develop a structural proposal;
use `cross-harness-state` for current progress and `session-handoff` for recovery.

## Read before recording

1. Read project instructions and find its existing decision records, index,
   naming convention and template. Search actual content; do not assume every
   project uses the same folder or numbering system.
2. For "why X?", cite the relevant record and its current status. Distinguish an
   accepted rationale from a proposal, historical inference or missing evidence.
   A read-only question does not require creating an ADR.
3. For a new record, identify the decision, constraints, deciders and alternatives
   actually discussed. Do not invent rejected options or their motivations.
   Record unknown rationale explicitly; retrospective records distinguish the
   original decision date from today's recording date.

## Write and maintain

Explicit requests such as "record this decision" already authorize the artifact.
Respect that authorization without a second confirmation. A discussion of a
possible choice alone warrants a draft/proposal, not an accepted decision.
Reuse the existing location and format. If the task authorizes a new ADR practice,
choose a minimal project-local location and explain it; do not create extra
instruction files or another memory database.

Use the [template](templates/decision.md) when the project lacks one. Include
context, decision, alternatives, consequences, evidence, status and dates. Keep
the main rationale readable; link detailed benchmarks/designs rather than copying
them. Only label a decision accepted when project authority supports that status.

Before writing, rescan the target directory and allocate a fresh filename. Use
exclusive creation for a new record; on collision, rescan/reassign rather than
overwrite another writer. Update the existing index under one writer's ownership.
If concurrent updates occur, reconcile both records and recheck links.

Do not silently rewrite an accepted historical decision into a different one.
Create a new record and connect both through explicit superseding/superseded-by
links; correct factual typos transparently. Keep index status consistent. Read
[lifecycle examples](references/lifecycle.md) for the expected relationships.

## Completion

Report the record, its status, evidence and index updates. Link it from STATE or
JOURNAL when useful instead of maintaining a second rationale. Check real paths,
status transitions, dates, counterpart links and filename collisions. These are
instruction/template resources; no ADR-generation script is claimed.

Adapted from [ECC architecture-decision-records](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/skills/architecture-decision-records/SKILL.md).
The [MIT notice](LICENSE.txt) is retained.
