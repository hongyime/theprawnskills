# ECC second-wave implementation and pilot

Owner approved the [second-wave plan](../plans/2026-09-27-ecc-second-wave.md).
Implementation starts at `38b8bb50538657ab3c2afe0741e3b0497faa2f64`.
Source adaptation remains pinned to ECC
`e482e579415fde18357cafce70f177ae19fd7f03`; all four added skill directories
carry its MIT notice and appear in `scripts/ecc-adaptations.json`.

## Delivered scope

- `api-contracts`: authoritative contract workflow, compatibility reference and
  a runnable Draft 2020-12 provider/consumer teaching fixture.
- `codebase-onboarding`: evidence-based repository mapping, an orientation
  template and read-only behavior probes; no promised scanner/generator.
- `architecture-decision-records`: proposed/accepted/superseded lifecycle,
  existing-layout support, retrospective uncertainty and collision-safe authoring.
- `bounded-agent-loop`: opt-in workflow, portable role/lens prompts, a standard
  library foreground supervisor, example plan and adversarial behavior tests.
- Both routers, OpenAPI generation, design and durable-state links updated.
  CLI routing/Codex guidance now uses installed help and configured defaults;
  obsolete model/pricing assumptions and unsupported automatic flags removed.
- tmux/dmux adapter documents actual host boundaries, project-local permission
  settings and the external runtime requirements. No 68-agent registration,
  unattended schedule, automatic merge or global tmux configuration installed.

Library: 215 top-level skills, 225 main-library definitions plus seven portable
variants. The daily profile remains 65; all four additions are on demand.

## Verification and independent review

Five contract-example cases pass. Additional mutation probes replace a text
large ID with a number and rename a required provider field; both must fail the
same executable consumer tests, including from an unrelated working directory.

The supervisor suite covers successful repair, no progress with noisy logs,
attempt/wall budgets, missing/failed workers, dirty starts, test deletion and
weakening, unrelated edits, staging/intent-to-add, POSIX permission changes,
timeout with a confirmed live child, interruption, preserved checkpoints and
explicit cleanup failure. Platform-specific cases are skipped on the other OS.

Independent review reproduced and prompted repairs for permission-only changes,
intent-to-add index entries, timing noise defeating no-progress detection,
Windows cleanup timeout/error handling and a timeout test that could pass before
the worker started. Cleanup failure remains visible even with a scope breach.
This is scope-change detection and process supervision, not a security sandbox.
Ignored/external/transient effects and intentionally detached daemons are outside
the helper's contract. Git/cleanup have documented bounded grace periods.
Git submodules are rejected before launch rather than silently omitting their
nested changes. Private run directories are created with owner-only POSIX mode.

Independent instruction-following probes used Python, React monorepo, unborn
Git and a real depth-one clone. Existing AGENTS instructions were preserved;
five read-only before/after manifests matched, including ignored fixture files
and Git metadata. Six ADR lifecycle events passed in an existing custom layout:
proposed versus accepted, exclusive-create collision, supersession, unknown
retrospective rationale, existing index preservation and read-only rationale
lookup. All 11 fixture Markdown links resolve. These are direct reviewer probes,
not a model activation-rate measurement or a claim of exhaustive behavior.

Metadata/text/resource gates passed: 232 definitions, 1,671 Markdown files,
2,585 references, zero missing resources, 16 documented contextual exceptions
and zero stale exceptions. No text-safety findings.

Final full-suite, three-OS CI and installed-file evidence are recorded in the
delivery update below.

Initial CI run `36302444003` passed Linux/macOS (94 Python cases plus five
documented skips, four React cases and four Chromium cases on each). Windows
caught a scheduling race in a 1-millisecond wall-budget test: the verifier could
exit while tree cleanup started, yielding an explicit `cleanup-failed` result.
The exhausted-before-launch test now uses a controlled clock and asserts no
command starts. The separate confirmed-live-child timeout test passed and stays
in place; uncertain cleanup is still reported as a failure, not hidden.

## Live host pilot

Observed Ubuntu 24.04 WSL: tmux 3.4, Git 2.43.0, Node 20.20.2. dmux 5.11.1 was
installed into a private user-owned pilot prefix with lifecycle scripts disabled.
Its project-local settings disable permission bypass, autopilot, goal mode and
notifications. Native Windows CLI shims are visible inside WSL; version output
alone does not establish working directory or tool readiness.

tmux: a detached private-socket session retained its repository and output across
separate clients. A real pseudo-terminal client attached and detached, and dmux
rendered its control UI and registered a shell pane. This was a local WSL test,
not an SSH/Tailscale disconnect/reconnect test from another laptop.
Controlled Python workers through Git/tmux passed two independent worktrees,
intentional conflict detection, a failing acceptance exit and cancellation.
The integration branch stayed unmerged. These lifecycle probes did not use
authenticated dmux agents. The private tmux server was stopped after the pilot;
dmux remained version 5.11.1 and its local runtime updater was disabled.

Codex 0.157.0: the disposable repair task failed at the host command adapter.
Its exec process repeatedly stalled and ended with runner-handshake cancellation.
It changed no files. The supervisor independently reran acceptance and stopped
`no-progress` after one attempt (437.109 seconds); it did not accept the worker's
zero exit as success. No hard monetary cap was available for this Codex run.

Claude 2.1.222: a read-only second-CLI handoff failed because its OAuth session
was expired and could not refresh. The CLI reported zero API usage/cost. A
preexisting session-end hook also reported a malformed cavemem path. No global
authentication or hook configuration was changed as part of this skill work.

These host failures prevent claiming a successful live autonomous repair or a
complete two-agent dmux workflow. The skills and deterministic supervisor tests
are independently deliverable; live agent integration remains a bounded pilot.
No unattended operation is enabled. Reauthenticate Claude and repair/retest the
Codex local command runner before repeating the live acceptance task.

dmux's `--help` is not a read-only help path in this release: an early probe
entered startup and created local runtime files. The adapter now explicitly
requires starting only in the disposable project. No credentials were written
to the skills repository, and private CLI transcripts are not committed.
Automatic approval review blocked removal of that probe's empty home-directory
`.dmux/` runtime and `.gitignore` containing only its ignore entry, with the
reason "blocked by policy". They were left in place; no deletion workaround was
attempted. This is separate from the three earlier first-wave cleanup blocks.

## Delivery update

Published executable revision: `e0479fc723c87e35a2fa06f3897a8917b8c01a7a`.
[Final three-OS CI](https://github.com/hongyime/theprawnskills/actions/runs/36302727616)
passed: Linux/macOS each ran 99 Python cases (94 passed, five documented skips),
Windows ran 99 (77 passed, 22 skips). Each OS separately passed all four React
and all four real Chromium cases. Index, resource and text gates passed, as did
CodeQL, Semgrep, Bandit, TruffleHog and LFS jobs for this revision. The local
Windows full run passed 76 of 98 cases with 22 skips; the added gitlink and final
deadline regressions also passed locally before their final 99-case CI run.

The intervening privacy commit `2fa914f` was integrated without losing its
changes. OneDrive was fast-forwarded, with the prior machine inventory preserved
in ignored `machines.local.toml` before any fleet command could use disabled
public examples. No fleet operation ran.

Another completed local task had added four Orca skills while this work ran.
Their 12 files, router row and uncommitted STATE/JOURNAL/index changes were
preserved through the update; the temporary merge stash was removed after
verification. They were not added to this ECC Git publication. Consequently the
published catalog has 232 definitions, while that local combined catalog has
236. The daily profile remains 65.

All 2,257 tracked skill files (including portable variants) were checked against
tested Git content: 636 exact byte matches, 1,620 with only existing CRLF/LF
differences, and one router matching after removal of its preserved local Orca
row. Twelve affected T14 daily skill directories were refreshed: 12 files match
source SHA-256 exactly, and the router's intentional local row was merged and
verified separately. All 65 selected daily entries resolve; the four new ECC
skills are readable through the shared on-demand library. No backup copies were
created. Existing shared-library links and unrelated local skills remain intact.

Other-machine delivery follows the owner's instruction to rely on OneDrive;
no new E14/L390 verification is claimed. Remaining live-pilot prerequisites are
the Codex command-runner repair and Claude reauthentication described above.
