# Behavioral and routing probes

Reuse `skill-creator` for baseline-versus-changed comparisons, assertions,
benchmark aggregation and description/trigger evaluations. This guide adds
scenario design; it does not install ECC's skill-comply runtime or a new model
provider. Resolve the existing evaluator through `skill-router`.

## Define cases before judging output

| Tier | Prompt design | Evidence to examine |
|---|---|---|
| Supportive | Explicitly requests the intended workflow | Correct skill read, required steps and truthful result |
| Neutral | Describes the real task without naming the skill | Appropriate selection from available library descriptions |
| Competing | Includes time pressure or a tempting conflicting shortcut | Required safeguards and evidence survive the distraction |
| Near miss | Shares vocabulary but belongs to another skill | Correct neighboring skill; no inappropriate workflow |

Competing cases remain synthetic fixture tasks; do not actually change a live
network or publish data to test whether an agent obeys a boundary.

For each case record the prompt, intended route, required observations,
forbidden actions and fixture setup. Include cases involving an on-demand skill
so an agent must find the full library rather than assume every skill is installed.
Keep expectations grounded in the user request and inspect the actual tool trace.

## Execute and grade

1. Pin the library revision, host/CLI version, configured model, available tools
   and exposure mode (daily copy, shared library or plugin). Use fresh isolated
   fixtures. Do not run evaluation workspaces inside the shared skill library.
2. Compare the changed version with the previous version or a no-skill baseline
   when measuring improvement. Use the same task and environment for both.
3. Grade deterministic effects first: files, outputs, exit codes, tool calls and
   forbidden side effects. Human/model assessment can supplement those checks,
   but a self-rating is not independent evidence.
4. For routing, record which SKILL.md was actually read. For workflow ordering,
   inspect timestamps/tool order (for example a failing regression before a fix).
   A final answer mentioning a skill does not prove it was invoked.
5. Report per-case results and uncertainty. Small samples are smoke tests, not
   activation-rate or reliability estimates. No baseline means no improvement
   claim. Missing credentials/tools mean UNAVAILABLE, not PASS.

Evaluate each intended harness separately: a Claude CLI evaluator is not proof
of Codex, Cursor or OpenCode behavior. Native review subagents can independently
critique instructions and solve fixture prompts, but that remains distinct from
measuring another product's installed skill router.

Use the supported/neutral/competing design from
[ECC skill-comply](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/skills/skill-comply/SKILL.md).
See its retained [MIT notice](../ECC-LICENSE.txt). Local adaptation adds near
misses and explicit limits on host portability, baselines and measurement claims.
