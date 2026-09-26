# Resume checklist

1. Read the project's `.agents/STATE.md` and its active handoff. Follow a
   continuation link when needed; stop if the chain cycles or a document is absent.
2. Confirm the repository and branch. Fetch/pull only within the user's authorized
   scope, preserving local edits. A handoff does not transport uncommitted code.
3. Run the validator and staleness checker using this skill's absolute script
   paths and an explicit `--project` target. A nonzero result requires review.
4. Check the actual code, referenced files, pending changes, and test results.
   Fresh metadata is not proof that the task is complete or the environment works.
5. Review blockers, tool availability, and machine-specific prerequisites.
   Authenticate using the receiving machine's own credentials.
6. Resolve conflicting state from concurrent agents before editing shared files.
   Do not discard another agent's work based only on a newer timestamp.
7. Begin with the first valid Immediate Next Steps item. Update project state
   after verified progress; create a new linked handoff for another transfer.

For a Git transfer, the sender reviews and commits the handoff alongside relevant
project changes, then pushes the intended branch. The receiver pulls that branch.
For a shared-folder transfer, ensure all code and handoff files have finished
syncing. The helper scripts perform neither transfer nor automatic Git writes.
