# ECC second-wave review plan

Date: 2026-09-27. **Owner approved proceeding; implementation in progress.**
Reviewed ECC revision `e482e579415fde18357cafce70f177ae19fd7f03`, the current local skill library,
local Codex CLI help, and the primary dmux/tmux documentation. The approved
first wave is recorded in [the adoption audit](../audits/2026-09-27-ecc-adoption.md).

## Recommendation and order

| Order | Change to consider | Why it adds something here | Adoption shape |
|---|---|---|---|
| 1 | API contracts | Existing OpenAPI-to-TypeScript converts a schema; it does not coordinate provider/consumer compatibility or prove serialized responses match it | New on-demand `api-contracts`, with contract-first workflow and API-design references |
| 2 | Codebase onboarding | Existing design/spec skills choose changes; this maps an unfamiliar repo as it exists, with evidenced entry points and commands | New on-demand `codebase-onboarding` |
| 3 | Detailed ADRs | `codebase-design` and `cross-harness-state` record useful current decisions, but lack a dedicated accepted/superseded decision history | New on-demand `architecture-decision-records`, linked from design/state rather than duplicating them |
| 4 | Bounded autonomous loops | Useful for a specified repeated repair task with runnable acceptance criteria | One opt-in workflow combining loop design, progress checks and existing verification/handoff |
| 5 | tmux, then dmux | Persistent remote sessions first; multiple isolated agent worktrees only when that solves a real coordination need | WSL/Linux pilot; native Windows keeps its existing CLI workflow |
| 6 | Agent roles | Several specialist review lenses are useful; most of 68 roles overlap existing skills or unused stacks | Small prompt library with explicit host adapters, no blanket agent registration |

Keep the daily profile at 65 unless separately changed. First-wave approval is
not approval to install orchestration services or run unattended jobs.

## API contracts

Adapt [contract-first](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/skills/contract-first/SKILL.md), using
[api-design](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/skills/api-design/SKILL.md) as reference material. Start by
finding the repository's authoritative OpenAPI, GraphQL, protobuf or schema
artifact. Keep its version and generation tools; do not create a competing spec.
Describe owners, consumer use cases, errors, nullability, pagination, identifier
precision, compatibility and migration paths. Generate types/fixtures where the
project already supports it. Validate actual serialized provider responses,
consumer fixtures, mock/sandbox paths and at least one integration flow.

Deliver a skill, a compatibility checklist, and a small provider/consumer fixture.
Tests should reject renamed required fields, wrong nullability, undocumented
error shapes and lossy large IDs, while accepting a documented compatible change.
Update routing and the existing OpenAPI skill's handoff. Type generation alone
must not be described as runtime validation. Auth design stays with security
skills; domain boundaries stay with domain-modeling/codebase-design.

## Codebase onboarding

Adapt [onboarding](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/skills/codebase-onboarding/SKILL.md) to every supported
harness. Read AGENTS.md and existing project instructions first; inspect manifests,
actual entry points, tests and CI. Trace one real request or job with path/line
evidence, identify conventions and distinguish observed commands from commands
actually run. Report uncertainty and shallow/missing Git history.

Default output is a concise conversation map or an explicitly requested project
artifact. ECC writes a starter CLAUDE.md during its normal workflow; our version
should write or update agent instructions only when that is part of the task.
Do not duplicate README content, execute setup/migrations during reconnaissance,
or load private environment files. Use session-handoff for resuming actual work.

Acceptance fixtures: Python repo, React monorepo, empty/shallow repo, conflicting
README versus actual manifest, and a repo with existing agent instructions. Every
reported command and entry point must exist; read-only cases must leave no diff.

## Detailed ADRs

Adapt [architecture-decision-records](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/skills/architecture-decision-records/SKILL.md).
Use the project's existing ADR location/format if present. Record context,
constraints, the decision, alternatives actually considered, evidence, consequences,
tradeoffs, decision status, date and deciders. For retrospective records, distinguish
the historical decision date from the recording date and mark uncertain history.

A design proposal remains proposed until accepted in the task's existing authority.
Explicit instructions such as "record this decision" already authorize writing;
do not add repeated confirmations. When merely discussing a possible choice,
offer an ADR draft rather than silently treating it as accepted. Preserve accepted
records and link a new superseding record. State/JOURNAL point to the ADR; they
do not become a second copy of it. For parallel writers, allocate filenames at
write time and reject collisions instead of overwriting a record.

Test proposed/accepted/superseded records, existing custom layouts, filename
collisions, unknown rationale, and "why did we choose X?" read-only lookups.
No ADR for trivial formatting or routine variable names.

## Autonomous loops

ECC's [continuous-agent-loop](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/skills/continuous-agent-loop/SKILL.md) is its
canonical entry; [autonomous-loops](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/skills/autonomous-loops/SKILL.md) is
retained for compatibility. The canonical page is a short pattern guide, not a
self-contained runner: its combined stack references other commands, skills and
runtime components. [Loop-design-check](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/skills/loop-design-check/SKILL.md)
adds useful failure analysis. Adapt that reasoning, not its blanket assumption
that every loop needs the same permission ritual or weekly frequency.

Proposed first pilot: one disposable branch/worktree, one bounded bug-fix task,
explicit acceptance tests, maximum three attempts, a wall-clock budget, and a cost
limit only if the selected CLI actually exposes enforceable accounting. Record
actual limits rather than pretending an instruction is a hard runtime cap. A
failure fingerprint repeated without progress stops the loop; missing credentials,
ambiguous scope or an unavailable dependency produces a resumable handoff.

Reuse `.agents/STATE.md`, JOURNAL and session-handoff. Do not add another memory
database. Preserve acceptance tests and constraints; changes to them must be
visible and reviewed. Each iteration records changed files, command exits,
failures, remaining work and the next action. Independent final review and CI
verify the resulting branch. The pilot produces a reviewable patch/PR; any later
merge/deployment behavior must fit the authorization for that particular job.

Failure tests: child hang, timeout, cancellation, repeated same failure, test
deletion, weakened checks, unrelated edits, dirty initial tree, interrupted resume,
missing tool and exhausted budget. No unattended schedule before this manual pilot.
The [RFC pipeline](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/skills/ralphinho-rfc-pipeline/SKILL.md) and
[team orchestration](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/skills/team-agent-orchestration/SKILL.md) can contribute
work-unit ownership/dependencies later. Defer DevFleet, NanoClaw, GAN harnesses,
automatic PR merging and infinite generation: each expands runtime/state scope.

## tmux and dmux

A tmux session keeps terminal processes on the host where tmux runs. Reconnecting
from another laptop attaches to that host; OneDrive does not move the running
process. Git transfers committed work, and handoff/state files transfer context.
Use the existing Tailscale/SSH path; keep active worktrees on the execution host's
local disk outside the OneDrive canonical skills tree.

Pilot tmux first on a chosen WSL/Linux host with user-owned tools. Verify detached
reattach, SSH disconnect/reconnect, correct repository/branch, child stop behavior
and a handoff to a second CLI. Native PowerShell is a separate operating surface;
tmux's [installation guidance](https://github.com/tmux/tmux/wiki/Installing)
documents Unix-family targets and Windows environment options. T14 has wsl.exe,
but tmux/dmux were not found on its native PATH; WSL distro readiness was not audited.

[dmux](https://github.com/standardagents/dmux) adds agent panes with separate Git
worktrees and branch/merge operations. Its current README requires tmux 3.0+,
Node 18+, Git 2.20+ and a supported agent CLI. AI naming/analysis has additional
optional provider configuration. The current `m` key opens a menu; merging can
commit and clean up work, so "merge output" is not merely copying a transcript.

After the tmux pilot, test a pinned dmux release with two independent tiny tasks,
then an intentional conflict, failed tests, a cancelled worker and interrupted
resume. Inspect lifecycle hooks and preserve local edits. Do not install with
sudo npm, transfer credentials through the skills repo, or auto-merge the pilot.
Prefer native host subagents for bounded review work when they already suffice.

ECC's [dmux guide](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/skills/dmux-workflows/SKILL.md) also references
`scripts/orchestrate-worktrees.js`, library modules and a shell worker. Copying
just its SKILL.md would omit these dependencies. Its sample Codex launcher uses
`--cwd` and `--task-file`; T14's installed `codex exec --help` exposes `--cd`
and a prompt/stdin interface instead. Any adapter must be verified against the
actual CLI before use. tmux/dmux were researched, not installed or exercised.

## Agent roster: selective roles, not 68 new skills

The pinned upstream tree contains **68 top-level agent definitions**. Their
frontmatter names, descriptions, tool lists and model fields were inventoried.
This is a role/dependency comparison, not a runtime certification of all prompts.
Claude tool names, MCP servers and model aliases do not become available merely
because a Markdown file was copied. Existing cavecrew already bundles portable
investigator/builder/reviewer prompts and falls back honestly when dispatch is
unavailable. Existing cli-agent-router already selects a CLI.

For a first agent pilot, reuse explorer, planner, implementer and reviewer roles;
add only useful review lenses (test quality, silent failures, type invariants,
accessibility, Python/React/TypeScript specifics). Put prompt resources under the
skill that owns the workflow, and keep harness registration optional and explicit.
Do not inherit "MUST use for every change" mandates or fixed model selection.
Probe permissions, artifact format, missing tools, cancellation and independent
review before expanding. A complete inventory follows; rows are recommendations,
not actions performed.

| ECC agent | Proposed treatment | Existing home or reason |
|---|---|---|
| [a11y-architect](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/a11y-architect.md) | Candidate review lens | Frontend/browser workflow; audit real accessibility behavior |
| [agent-evaluator](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/agent-evaluator.md) | Improve existing evaluation only | skill-creator and skill-reviewer; no second scoring runtime |
| [architect](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/architect.md) | Reuse existing | codebase-design, domain-modeling, to-spec, to-tickets |
| [build-error-resolver](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/build-error-resolver.md) | Improve checklist if needed | systematic-debugging, bug-diagnosis, React guidance |
| [chief-of-staff](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/chief-of-staff.md) | Defer communications workflow | Accounts, message permissions and post-send hooks are separate |
| [code-architect](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/code-architect.md) | Reuse existing | codebase-design, domain-modeling, to-spec, to-tickets |
| [code-explorer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/code-explorer.md) | Reuse; onboarding reference | cavecrew investigator; proposed onboarding |
| [code-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/code-reviewer.md) | Reuse existing | requesting-code-review and cavecrew reviewer |
| [code-simplifier](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/code-simplifier.md) | Reuse existing | refactor; retain behavior checks and scoped removals |
| [comment-analyzer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/comment-analyzer.md) | Improve existing documentation workflow | Onboarding/ADR proposals plus doc-coauthoring; no automatic instruction rewrites |
| [conversation-analyzer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/conversation-analyzer.md) | Skip automatic hook workflow | Hookify command/hook machinery not adopted |
| [cpp-build-resolver](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/cpp-build-resolver.md) | Project-specific later | Language/framework specialization; add when an active project needs it |
| [cpp-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/cpp-reviewer.md) | Project-specific later | Language/framework specialization; add when an active project needs it |
| [csharp-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/csharp-reviewer.md) | Project-specific later | Language/framework specialization; add when an active project needs it |
| [dart-build-resolver](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/dart-build-resolver.md) | Project-specific later | Language/framework specialization; add when an active project needs it |
| [database-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/database-reviewer.md) | Reuse existing | database-schema-designer, Supabase/Postgres skills |
| [django-build-resolver](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/django-build-resolver.md) | Project-specific later | Language/framework specialization; add when an active project needs it |
| [django-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/django-reviewer.md) | Project-specific later | Language/framework specialization; add when an active project needs it |
| [doc-updater](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/doc-updater.md) | Improve existing documentation workflow | Onboarding/ADR proposals plus doc-coauthoring; no automatic instruction rewrites |
| [docs-lookup](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/docs-lookup.md) | Reuse available documentation tools | Context7 only where configured; official-doc fallback |
| [e2e-runner](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/e2e-runner.md) | Reuse existing | webapp-testing, agent-browser; preserve failure evidence |
| [fastapi-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/fastapi-reviewer.md) | Project-specific later | Language/framework specialization; add when an active project needs it |
| [flutter-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/flutter-reviewer.md) | Project-specific later | Language/framework specialization; add when an active project needs it |
| [fsharp-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/fsharp-reviewer.md) | Project-specific later | Language/framework specialization; add when an active project needs it |
| [gan-evaluator](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/gan-evaluator.md) | Defer runtime bundle | Needs coordinated evaluator/generator state and tools |
| [gan-generator](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/gan-generator.md) | Defer runtime bundle | Needs coordinated evaluator/generator state and tools |
| [gan-planner](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/gan-planner.md) | Defer runtime bundle | Needs coordinated evaluator/generator state and tools |
| [go-build-resolver](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/go-build-resolver.md) | Project-specific later | Language/framework specialization; add when an active project needs it |
| [go-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/go-reviewer.md) | Project-specific later | Language/framework specialization; add when an active project needs it |
| [harmonyos-app-resolver](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/harmonyos-app-resolver.md) | Project-specific later | Language/framework specialization; add when an active project needs it |
| [harness-optimizer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/harness-optimizer.md) | Improve existing evaluation only | skill-creator and skill-reviewer; no second scoring runtime |
| [healthcare-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/healthcare-reviewer.md) | Skip for current setup | No established healthcare application scope |
| [homelab-architect](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/homelab-architect.md) | Add focused references later | homelab-pihole-dns, docker-expert; topology-specific evidence |
| [java-build-resolver](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/java-build-resolver.md) | Project-specific later | Language/framework specialization; add when an active project needs it |
| [java-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/java-reviewer.md) | Project-specific later | Language/framework specialization; add when an active project needs it |
| [kotlin-build-resolver](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/kotlin-build-resolver.md) | Project-specific later | Language/framework specialization; add when an active project needs it |
| [kotlin-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/kotlin-reviewer.md) | Project-specific later | Language/framework specialization; add when an active project needs it |
| [loop-operator](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/loop-operator.md) | Defer to bounded loop pilot | Requires real runner, stop controls and progress evidence |
| [marketing-agent](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/marketing-agent.md) | Reuse existing | Existing marketing, launch, copy and SEO skills |
| [mle-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/mle-reviewer.md) | Project-specific later | Only when active ML/RAG/PyTorch work justifies specialized checks |
| [network-architect](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/network-architect.md) | Defer enterprise networking | Current scope is a Docker/Pi-hole/Tailscale homelab |
| [network-config-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/network-config-reviewer.md) | Defer enterprise networking | Current scope is a Docker/Pi-hole/Tailscale homelab |
| [network-troubleshooter](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/network-troubleshooter.md) | Add focused references later | homelab-pihole-dns, docker-expert; topology-specific evidence |
| [opensource-forker](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/opensource-forker.md) | Defer release-specific workflow | Secret/history handling and packaging need an explicit release task |
| [opensource-packager](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/opensource-packager.md) | Defer release-specific workflow | Secret/history handling and packaging need an explicit release task |
| [opensource-sanitizer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/opensource-sanitizer.md) | Defer release-specific workflow | Secret/history handling and packaging need an explicit release task |
| [performance-optimizer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/performance-optimizer.md) | Candidate reference later | Profile a real bottleneck; existing React performance guidance |
| [php-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/php-reviewer.md) | Project-specific later | Language/framework specialization; add when an active project needs it |
| [planner](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/planner.md) | Reuse existing | codebase-design, domain-modeling, to-spec, to-tickets |
| [pr-test-analyzer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/pr-test-analyzer.md) | Candidate review lenses | requesting-code-review references; concrete behavior/invariant checks |
| [python-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/python-reviewer.md) | Candidate stack review lenses | Existing Python/React/TypeScript and review skills |
| [pytorch-build-resolver](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/pytorch-build-resolver.md) | Project-specific later | Only when active ML/RAG/PyTorch work justifies specialized checks |
| [rag-pipeline-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/rag-pipeline-reviewer.md) | Project-specific later | Only when active ML/RAG/PyTorch work justifies specialized checks |
| [react-build-resolver](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/react-build-resolver.md) | Improve checklist if needed | systematic-debugging, bug-diagnosis, React guidance |
| [react-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/react-reviewer.md) | Candidate stack review lenses | Existing Python/React/TypeScript and review skills |
| [refactor-cleaner](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/refactor-cleaner.md) | Reuse existing | refactor; retain behavior checks and scoped removals |
| [rust-build-resolver](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/rust-build-resolver.md) | Project-specific later | Language/framework specialization; add when an active project needs it |
| [rust-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/rust-reviewer.md) | Project-specific later | Language/framework specialization; add when an active project needs it |
| [security-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/security-reviewer.md) | Reuse existing | security-best-practices and MCP security skills |
| [seo-specialist](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/seo-specialist.md) | Reuse existing | Existing marketing, launch, copy and SEO skills |
| [silent-failure-hunter](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/silent-failure-hunter.md) | Candidate review lenses | requesting-code-review references; concrete behavior/invariant checks |
| [spec-miner](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/spec-miner.md) | Revisit only for a brownfield spec task | Existing to-spec/check; upstream assumes OpenSpec output conventions |
| [swift-build-resolver](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/swift-build-resolver.md) | Project-specific later | Language/framework specialization; add when an active project needs it |
| [swift-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/swift-reviewer.md) | Project-specific later | Language/framework specialization; add when an active project needs it |
| [tdd-guide](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/tdd-guide.md) | Reuse existing | python-testing, react-testing, verification-loop; no blanket 80% mandate |
| [type-design-analyzer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/type-design-analyzer.md) | Candidate review lenses | requesting-code-review references; concrete behavior/invariant checks |
| [typescript-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/typescript-reviewer.md) | Candidate stack review lenses | Existing Python/React/TypeScript and review skills |
| [vue-reviewer](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/agents/vue-reviewer.md) | Project-specific later | Language/framework specialization; add when an active project needs it |

## Next review decision

Review the three document/contract skills as the next small batch. Keep loop
execution and tmux/dmux as a separate pilot with explicit host, task and limits.
Use the roster as a menu of review lenses; do not increase the daily profile or
register all upstream agents. Every future import must include provenance,
applicable notices, closed resource references, and tests of the advertised path.
