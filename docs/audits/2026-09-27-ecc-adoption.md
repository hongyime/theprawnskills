# ECC selective adoption and verification

Date: 2026-09-27. Source revision:
`e482e579415fde18357cafce70f177ae19fd7f03` from
[ECC](https://github.com/affaan-m/ECC/tree/e482e579415fde18357cafce70f177ae19fd7f03).
Scope approved by the owner: four on-demand skills and three improvement batches.
The [second-wave plan](../plans/2026-09-27-ecc-second-wave.md) is a proposal only.

## Delivered scope

| Change | Result |
|---|---|
| verification-loop | Project-defined completion checks, actual exit/count evidence, explicit unavailable/skipped results and scoped review |
| python-testing | Existing unittest/pytest conventions, independent oracles, boundaries, fixtures and async guidance; executable stdlib example |
| react-testing | Observable component/hook contracts, user-event, async content assertions, isolated providers/mocks and browser boundaries |
| homelab-pihole-dns | Diagnose existing Docker/Tailscale setup, distinguish container/UI/direct/system DNS evidence, use Pi-hole v6 settings |
| Browser testing in place | Existing project runner first, locator readiness, response wait ordering, artifact guidance, portable examples and server lifecycle fixes |
| Evaluation in place | Reuse creator baseline/trigger machinery, add supportive/neutral/competing/near-miss probes, real harness/model limits, external evaluation workspaces |
| Index/CI | Real YAML parser, nested metadata/profile validation, deterministic source index, Unicode text gate, Markdown secret-scan triggers, executable examples in three-OS CI |

The library now has **211 top-level skills**, **221 main-library definitions**,
and **7 portable definitions**, for **228 validated definitions**. The daily
profile remains **65**. New skills are on demand; router/build/review/debug
guidance makes the relevant boundaries explicit. No ECC hook, runtime, agent
registration, continuous-learning observer or global configuration was imported.

## Provenance and resource closure

[The manifest](../../scripts/ecc-adaptations.json) records each upstream path,
the pinned revision and local adaptation. MIT notices are retained beside the
adaptations; the browser skill's original Apache notice is preserved. The
catalog/text tooling is locally implemented Python inspired by upstream checks.
Pi-hole guidance was corrected against official v6 migration/configuration docs.

Static resource audit: **228 definitions, 1,660 Markdown files and 2,569
references; 0 missing, 16 exact contextual exceptions, 0 stale exceptions**.
These are static link/resource checks, not proof that every provider/tool works.
The text safety gate reports zero findings. The regenerated index matches parsed
metadata and does not claim installation counts observed on a different machine.

## Local evidence and independent review

- The initial full Windows unit run passed **55 tests**, with **20 explicit skips**:
  16 POSIX/symlink cases and 4 opt-in browser cases run separately. Three new
  server lifecycle cases were added afterward and passed locally as a focused run.
- The Python example runs 3 behavior tests. Its wrapper tests also demonstrate
  that two deliberate range/character-validation faults are detected.
- The React fixture passes **4 cases**: empty input, trimmed successful save,
  failed save, and delayed completion through an already-existing status element.
- Real Chromium probes cover a local polling page, delayed readiness, console
  flow, static file paths with spaces, and a missing-state failure. Initial T14
  runs passed three cases but hung during static-example browser shutdown.
  A debug run reached the correct file URL, visible state and screenshot, then
  stalled in Playwright browser cleanup. This is not counted as a passed run.
- Server helper tests cover 250 KB of startup logs, terminating the shell's child
  server, downstream exit-code propagation, occupied-port preservation, and
  startup failure. The helper now uses file-backed logs and process-tree/group
  cleanup, requires foreground commands and checks port closure. A busy-host
  review run exceeded the original 15-second Windows taskkill limit; the helper
  correctly failed, the known child was cleaned up, and the deadline was raised
  to 45 seconds. Three-OS CI exercises the final behavior.
- Independent catalog review passed **16 focused tests** and **25 additional
  adversarial assertions**. Fixes cover sanitized malformed YAML constructors,
  empty profiles, legitimate flag emoji, malformed tags and escaped filenames.
- Independent content review caught and corrected the React async assertion,
  server cleanup defect, creator workspace contradiction and Claude-model
  routing ambiguity. Seven applicable upstream MIT notices are retained.

Reasoning probes checked sixteen routing boundaries (four per new skill):

| Skill | Supportive / neutral | Competing / near miss |
|---|---|---|
| verification-loop | Completed patch; ready-for-review evidence | Hung tests stay incomplete; SPEC drift routes to check |
| python-testing | pytest boundaries; coursework requiring unittest | Reject copied production oracle; inference.sh routes to python-sdk |
| react-testing | Form contract; loading/error states | JSDOM cannot certify browser layout; integrated login routes to webapp-testing |
| homelab-pihole-dns | Pi-hole v6; direct query works but system query fails | UI green does not prove fleet health; Cloudflare MX is outside scope |

These are instruction/reasoning probes, **not measured automatic activation
rates**. File discovery and hashes are separate from runtime host activation.
The fixture is synthetic, not a production React application. No live DNS,
router settings, Tailscale settings or Pi-hole containers were changed.

## Publication and distribution

First publication: `e6ffd2e`. [CI run 36297779800](https://github.com/hongyime/theprawnskills/actions/runs/36297779800)
passed the complete Linux and Windows jobs, including browser and React cases.
macOS exposed a local-fixture startup timeout and zombie process-group cleanup
error. The fixtures now avoid reverse DNS on loopback, and POSIX cleanup reaps
the leader and checks for live group members before signaling. Permission errors
for live members remain failures. The startup symptom matches the maintainer-
confirmed [macOS runner issue](https://github.com/actions/runner-images/issues/14409).

Final executable revision: **b9bb28c**. [CI run 36298257310](https://github.com/hongyime/theprawnskills/actions/runs/36298257310)
completed successfully on all three operating systems:

| OS | Python cases passed | Chromium cases passed | React cases passed | Platform-specific skips |
|---|---:|---:|---:|---:|
| Linux | 74 | 4 | 4 | 0 |
| macOS | 74 | 4 | 4 | 0 |
| Windows | 58 | 4 | 4 | 16 POSIX/symlink cases |

The unit discovery command reports 78 cases and initially skips the four opt-in
browser cases; the separate Chromium step runs all four. The table counts each
executed case once. All final metadata, index, text and resource gates passed.
CodeQL, Semgrep, Bandit, TruffleHog and LFS Guard also passed for this revision.
Both Windows PowerShell 5 and PowerShell 7 index-wrapper checks passed locally.
The earlier T14 shutdown hang and first macOS failure remain recorded above;
the clean final Windows CI browser run is a separate result.

OneDrive delivery is verified against `b9bb28c`: all **2,236 tracked skill files**
match tested Git content after normalizing existing CRLF/LF differences (1,622
older files differ only in line endings). The four new on-demand definitions
are readable, the shared Claude/agents links resolve to this source, and the
profile remains 65. Six affected T14 daily copies were refreshed after checking
that their previous content was unmodified; all **41 delivered files** have
exact SHA-256 equality with their OneDrive source. No backup copies were created.
The existing untracked canonical `.agents/.gitignore` was preserved.

Automatic approval review blocked cleanup of three task-created temporary test
folders with the reason "blocked by policy"; they were left intact. This does
not affect source files, installed skills or test results.

The owner's latest instruction treats OneDrive as distribution
to the other machines. No new E14/L390 verification is claimed. Their separate
installed copies are not proven refreshed merely by updating the shared source.
The historical E14 cloud-read issue is not represented as repaired in this batch.

The GitHub `no-config-sync` topic remains present. No organisation config sync,
credential copying, profile expansion or unrelated X-drive checkout changes.
