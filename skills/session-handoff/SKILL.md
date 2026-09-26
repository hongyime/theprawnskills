---
name: session-handoff
description: >-
  Save and resume project work across agents or machines using verified Markdown
  handoffs. Use for create handoff, save state, pause this task, load handoff,
  resume from, or continue where we left off. Includes portable draft, validation,
  listing, and staleness helpers; Git transfer remains a separate action.
license: MIT
metadata:
  author: Local setup
  version: "1.1.0"
---

# Handoff

Preserve the context another agent needs to continue work, then verify it against
the actual project. Handoffs belong to the target project, not this skill library.

## Script location and prerequisites

Use Python 3.11+ and Git for freshness checks. Set `SKILL_DIR` (Bash) or
`$skillDir` (PowerShell) to the absolute folder containing this loaded SKILL.md.
Set `PROJECT` / `$project` to the target project. Never change into the skill
folder and accidentally create a handoff for the library itself.

PowerShell example after resolving those two paths:

```powershell
python "$skillDir/scripts/create_handoff.py" task-slug --project "$project"
python "$skillDir/scripts/validate_handoff.py" .agents/handoffs/<file>.md --project "$project"
```

All four commands accept `--project` and `--json`. File arguments and document
links are project-relative, allowing a different checkout path on the next machine.
The scripts never stage, commit, push, pull, contact another machine, or update
STATE.md/JOURNAL.md automatically. They capture filenames and Git identifiers,
not code contents, commit messages, authentication files, or chat history.

## Mode Selection

Determine which mode applies:

**Creating a handoff?** User wants to save current state, pause work, or context is getting full.
- Follow: CREATE Workflow below

**Resuming from a handoff?** User wants to continue previous work, load context, or mentions an existing handoff.
- Follow: RESUME Workflow below

**Proactive suggestion?** After substantial work (5+ file edits, complex debugging, major decisions), suggest:
> "We've made significant progress. Consider creating a handoff document to preserve this context for future sessions. Say 'create handoff' when ready."

## CREATE Workflow

### Step 1: Generate Scaffold

Run the smart scaffold script to create a pre-filled handoff document:

```bash
python "$SKILL_DIR/scripts/create_handoff.py" task-slug --project "$PROJECT"
```

Use a lowercase slug such as `implementing-user-auth`.

**For continuation handoffs** (linking to previous work):
```bash
python "$SKILL_DIR/scripts/create_handoff.py" auth-part-2 --project "$PROJECT" --continues-from previous-file.md
```

The script will:
- Create `.agents/handoffs/` directory if needed
- Generate timestamped filename
- Pre-fill: UTC timestamp, project name, Git branch, recent commit hashes, modified-file fingerprints
- Add handoff chain links if continuing from previous
- Output file path for editing

### Step 2: Complete the Handoff Document

Open the generated file and fill in all `[TODO: ...]` sections. Prioritize these sections:

1. **Current State Summary** - What's happening right now
2. **Important Context** - Critical info the next agent MUST know
3. **Immediate Next Steps** - Clear, actionable first steps
4. **Decisions Made** - Choices with rationale (not just outcomes)

Use the template structure in [references/handoff-template.md](references/handoff-template.md) for guidance.

### Step 3: Validate the Handoff

Run the validation script to check completeness and security:

```bash
python "$SKILL_DIR/scripts/validate_handoff.py" .agents/handoffs/<file>.md --project "$PROJECT"
```

The validator checks:
- [ ] No `[TODO: ...]` placeholders remaining
- [ ] Required sections present and populated
- [ ] No potential secrets detected (API keys, passwords, tokens)
- [ ] Referenced files exist
- [ ] Quality score (0-100)

**Do not finalize unless validation exits 0.** Every required section must be
populated, placeholders removed, and explicit references valid. A score of 70+
does not override an error. The score starts at 100 and deducts points for missing
metadata, sections, placeholders, and files; it is a completeness heuristic, not
a guarantee of factual accuracy. Secret matching is also heuristic: manually
review the entire document and staged diff before sharing.

### Step 4: Confirm Handoff

Report to user:
- Handoff file location
- Validation score and any warnings
- Summary of captured context
- First action item for next session

## RESUME Workflow

### Step 1: Find Available Handoffs

List handoffs in the current project:

```bash
python "$SKILL_DIR/scripts/list_handoffs.py" --project "$PROJECT"
```

This shows all handoffs with dates, titles, and completion status.

### Step 2: Check Staleness

Before loading, check how current the handoff is:

```bash
python "$SKILL_DIR/scripts/check_staleness.py" .agents/handoffs/<file>.md --project "$PROJECT"
```

Staleness levels:
- **FRESH**: Safe to resume - minimal changes since handoff
- **SLIGHTLY_STALE**: Review changes, then resume
- **STALE**: Verify context carefully before resuming
- **VERY_STALE**: Consider creating a fresh handoff
- **UNKNOWN**: Git or complete file fingerprints are unavailable; inspect manually

Only FRESH exits 0; other assessments exit 1, invalid inputs exit 2. Age over
seven days is STALE, over 30 days VERY_STALE. New commits are at least
SLIGHTLY_STALE; branch, index, or working-file changes are STALE. Missing or
divergent Git history is VERY_STALE. Sensitive files and dirty submodules are
not fingerprinted and force UNKNOWN. Freshness does not imply task completion.

The script checks:
- Time since handoff was created
- Git commits since handoff
- Files changed since handoff
- Branch divergence
- Missing referenced files

### Step 3: Load the Handoff

Read the relevant handoff document completely before taking any action.

If handoff is part of a chain (has "Continues from" link), also read the linked previous handoff for full context.

### Step 4: Verify Context

Follow the checklist in [references/resume-checklist.md](references/resume-checklist.md):

1. Verify project directory and git branch match
2. Check if blockers have been resolved
3. Validate assumptions still hold
4. Review modified files for conflicts
5. Check environment state

### Step 5: Begin Work

Start with "Immediate Next Steps" item #1 from the handoff document.

Reference these sections as you work:
- "Critical Files" for important locations
- "Key Patterns Discovered" for conventions to follow
- "Potential Gotchas" to avoid known issues

### Step 6: Update or Chain Handoffs

As you work:
- Mark completed items in "Pending Work"
- Add new discoveries to relevant sections
- For long sessions: create a new handoff with `--continues-from` to chain them

## Integration With Cross-Harness State (MOLT)

Handoffs are one layer of the repo's persistent state system. After creating a
handoff, wire it into the MOLT files so any harness finds it:

1. Add ONE bullet to `.agents/STATE.md`: "Paused <task>, see
   `.agents/handoffs/<file>` for full recovery context."
2. Append one line to `.agents/JOURNAL.md`: "- YYYY-MM-DD: paused <task>,
   handoff at <file>."
3. On resume, read STATE.md first; only open this handoff when the task is the
   active one.

For transfer through Git, review and commit these project files together with
the relevant code, then push the intended branch when authorized. The receiving
machine pulls that same branch and verifies the working tree before resuming.
Saving a Markdown file alone does not transfer uncommitted code. For a shared
folder, verify synchronization has completed before the next agent writes.

See `cross-harness-state` for the full file contracts.

## Handoff Chaining

For long-running projects, chain handoffs together to maintain context lineage:

```
handoff-1.md (initial work)
    ↓
handoff-2.md --continues-from handoff-1.md
    ↓
handoff-3.md --continues-from handoff-2.md
```

Each handoff in the chain:
- Links to its predecessor
- Can mark older handoffs as superseded
- Provides context breadcrumbs for new agents

When resuming from a chain, read the most recent handoff first, then reference predecessors as needed.

## Storage Location

Handoffs are stored in: `.agents/handoffs/`

Naming convention: `YYYY-MM-DD-HHMMSS-[slug].md`

Example: `2024-01-15-143022-implementing-auth.md`

## Resources

### scripts/

| Script | Purpose |
|--------|---------|
| `create_handoff.py [slug] [--continues-from <file>]` | Generate new handoff with smart scaffolding |
| `list_handoffs.py [path]` | List available handoffs in a project |
| `validate_handoff.py <file>` | Check completeness, quality, and security |
| `check_staleness.py <file>` | Assess if handoff context is still current |

### references/

- [handoff-template.md](references/handoff-template.md) - Complete template structure with guidance
- [resume-checklist.md](references/resume-checklist.md) - Verification checklist for resuming agents

### Related Skills

- `cross-harness-state` - MOLT state layer that indexes handoffs via STATE.md and JOURNAL.md
