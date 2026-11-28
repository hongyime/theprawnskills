# Verification Packet — <task name>

- Date:
- Plan file:
- Implementer pane: (name, address, machine, agent)
- Verifier pane: (name, address, machine, agent — different agent, different pane, fresh session)
- Repo / branch / commit (or working-tree scope):
- Evidence file (implementer's pointers only, no verdict):

## FACT

Verifiable statements, each with a source (file path + line / commit hash /
command + verbatim exit code + output excerpt). No source = not a FACT.

- ...

## INFERENCE

Conclusions drawn from the FACTs above, labelled as inference.

- ...

## ASSUMPTION

Anything taken on trust, labelled. Includes any implementer verdict/summary
stripped from the evidence file before the verifier read it.

- ...

## UNKNOWN

Anything that could not be checked, labelled. UNKNOWN is never presented as
PASS.

- ...

## Checks table

Per-check verdict: PASS / FAIL / SKIPPED (reason) / UNAVAILABLE (prerequisite)
/ NOT APPLICABLE (reason). A required check that is SKIPPED or UNAVAILABLE
leaves readiness unverified; it is never turned into PASS.

| Check | Verdict | Evidence (command, working directory, exit code, counts) |
|---|---|---|
| Build / types / lint | | |
| Tests | | |
| Behavior | | |
| Security | | |
| Diff | | |

## Position (verifier's own assessment vs the plan)

## Challenge (strongest case the work is wrong / incomplete / unverified)

## Verdict

One of: PASS / FAIL / BLOCKED.

Verdict: ...

Deciding facts (cite the FACTs above by number or quote):

- ...
