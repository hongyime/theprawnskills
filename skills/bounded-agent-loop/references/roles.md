# Portable role prompts

These are prompts, not registered agents or executable commands. Give each role
the repository instructions, authorized scope, evidence paths and actual tools.
Keep model selection and permission settings in the host adapter.

| Role | Assignment | Output |
|---|---|---|
| Explorer | Read the task's entry points, callers, tests and constraints; cite paths/lines. Do not edit. | Evidence map, uncertainties, likely change boundary |
| Planner | Propose the smallest sequence satisfying acceptance, dependencies, file ownership and stop conditions. Do not invent repository facts. | Work units and verification commands |
| Implementer | Implement only its assigned files; preserve acceptance tests and report failures honestly. Stop when another writer owns a required file. | Patch, changed files, command exits, remaining risks |
| Reviewer | Read requirements before diff; challenge behavior and tests with concrete counterexamples. Do not edit or trust the implementer's success claim. | Severity, path/line, reproduction, required fix |

Use existing `cavecrew` investigator/builder/reviewer prompts when appropriate;
resolve that skill through the library rather than assuming a host agent name.
For independent tasks, use separate worktrees and one integrator. For dependent
tasks, wait for the producer's reviewed artifact before starting the consumer.

Optional review lenses, selected for the actual patch:

- Test quality: would a plausible faulty implementation still pass? Check an
  independent oracle, failure-path assertions, async waits and cleanup.
- Silent failures: swallowed exceptions, ignored process exits, retries without
  limits, misleading success states and missing observability.
- Type invariants: wire data versus static types, null/omission, large IDs,
  coercion and invalid states across API boundaries.
- Accessibility: keyboard flow, names/roles, focus, announcements and disabled
  states; inspect actual UI evidence rather than claiming compliance from code.
- Python: resource lifetimes, exception boundaries, mutation, concurrency and
  behavior under the project's supported Python versions; use `python-testing`.
- React/TypeScript: user-visible async behavior, effect ownership, stale state,
  runtime boundary checks and role-based assertions; use `react-testing`.

These lenses replace no specialist authorization and claim no security/compliance
certification. The full 68-role ECC mapping remains in the repository's approved
second-wave plan; registering that entire roster is intentionally outside scope.
