# Orientation probes

Evaluate the agent's evidence and side effects, not whether its answer mentions
the skill name. Use an isolated repository for each case and compare the complete
file set/content before and after a read-only request, including ignored files.

| Case | Expected behavior |
|---|---|
| Python package | Finds real CLI/application entry and defined test runner |
| React monorepo | Identifies package ownership and command working directories |
| Unborn/shallow Git repo | Does not invent commit/branch conventions |
| README conflicts with manifest | Reports discrepancy and cites both sources |
| Existing AGENTS.md/CLAUDE.md | Reads and preserves instructions; does not auto-rewrite |
| Missing tests or incomplete route | Marks unknown/unavailable instead of fabricating a path |
| Request to design a new feature | Routes structural decisions to codebase-design |

Static template checks cannot establish orientation accuracy. For runtime probes,
retain the agent's actual file-read trace and a baseline file manifest. Report the
host/model and fixture scope; a few examples are not a general activation rate.
