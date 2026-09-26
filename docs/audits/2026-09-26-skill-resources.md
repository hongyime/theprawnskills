# Skill resource audit — 26 September 2026

The audit covered every skill in this repository: 217 main-library definitions
and seven portable variants, for **224 definitions**. The baseline `bbfe3cf`
contained 1,631 Markdown files within the automated checker's scope. Independent
review also read the portable-platform overview, for 1,632 files, and identified **60
actionable resource and path findings**; each has a disposition in the
[finding register](2026-09-26-skill-resource-findings.json).

## Repairs

| Baseline category | Findings | Disposition |
|---|---:|---|
| Missing bundled files | 28 | Restored or recreated handoff, commit, dependency, React, review, and preset resources |
| Missing agent prompts | 3 | Added portable Cavecrew prompts and dispatch instructions |
| Missing upstream test/sample references | 5 | Replaced unavailable dependencies with the existing complete inline guidance |
| Obsolete specification contract | 1 | Aligned build with spec and permitted status-only updates |
| Links to unavailable related skills/documents | 5 | Corrected equivalent Cloudflare destinations or documented absent optional skills |
| Incorrect relative paths | 15 | Corrected Azure aliases and Vercel aggregate links |
| External runtime prerequisites presented as installed | 3 | Documented Caveman hooks and optional OpenCode setup; added truthful unavailable behavior |

The last category remains an external runtime prerequisite: this repair does not
install hooks, authenticate OpenCode, or claim those integrations are active.

Additional contextual review clarified loaded-skill versus project working
directories, canonical-library discovery from installed copies, and the newest-
first journal convention. Existing skills were retained; the daily profile is
unchanged at 65 selections.

## Handoff behavior

The four CLI helpers use Python 3.11+ and an explicit project directory. They
create a draft, validate it, list documents, and compare recorded context with
the Git working tree. Supporting code and two guides ship in the skill folder.

- Generated documents use portable project-relative paths and UTC timestamps.
- Creation never overwrites an existing document; path traversal is rejected.
- Validation fails on unfinished sections, missing files, malformed metadata,
  and heuristic secret detections. Diagnostics withhold detected secret values.
- Freshness considers branch, ancestry, age, working bytes, staged entries,
  rename sources, and file type. Incomplete snapshots report UNKNOWN.
- Git operations are read-only. The agent separately reviews, commits, and pushes
  project changes; the receiving machine pulls the same branch and checks reality.

## Automated guard

Run from any working directory:

```text
python <library>/scripts/audit_skill_resources.py
python -m unittest discover -s <library>/tests -v
```

The final static scan covers **1,650 bundled Markdown files** and **2,551 explicit
references** across all 224 definitions. It reports **zero unresolved missing
references**, **16 exact contextual exceptions**, and **zero stale exceptions**.
The exceptions are documented examples, generated project outputs, and one
explicit external SDK example. They do not allow missing bundled helpers.

The guard checks ordinary and reference-style local Markdown links and explicit
resource paths, including parent-relative and Windows paths. It rejects invalid
audit roots and stale exceptions. CI runs it before the Python test suite on
Windows, Linux, and macOS. Dedicated tests exercise the parser's failure cases.

## Provenance

Twelve resources were restored from
[softaworks/agent-toolkit at 3027f20](https://github.com/softaworks/agent-toolkit/tree/3027f20f3181758385a1bb8c022d4041dfb4de84):
the commit template, two dependency wrappers, seven React development guides,
and two Effect guides. Each affected skill includes the upstream MIT licence.
[The provenance manifest](../../scripts/restored-resource-sources.json) records
immutable source URLs and content hashes before local adaptations. One wrapper
now quotes the tool executable; both wrappers were tested with fake commands.

Handoff helpers, preset helpers, Cavecrew prompts, and the four reviewer guides
were written locally. Upstream reviewer content was not retained because the
retrieved repository licence did not substantiate its advertised MIT metadata.
The locally authored reviewer references carry their own MIT notice.

The Azure name helpers use the documented read-only
[deployment list command](https://learn.microsoft.com/en-us/cli/azure/cognitiveservices/account/deployment?view=azure-cli-latest#az-cognitiveservices-account-deployment-list).
They were exercised against fake Azure CLI output and failure responses, not a
live subscription. Selecting a name does not reserve or create a deployment.

## Verification boundaries

This is a resource-integrity audit plus targeted runtime testing of repaired
helpers. It is not certification of every skill's domain guidance, provider API,
model routing, dependency compatibility, or external integration. Dynamic paths,
arbitrary prose filenames, remote URLs, and Markdown anchor semantics are outside
the automated check; independent contextual review supplements it.

The Windows run includes native PowerShell and Git Bash wrapper tests and real
temporary Git repositories for handoffs. POSIX symlink cases are left to the
Linux/macOS CI matrix. Tests do not update real agent homes, cloud resources, or
dependencies. A published repository update does not itself refresh installed
copies or establish that OneDrive has synchronized on every machine.

Final local run: **52 tests, 37 passed, 15 platform-specific skips, zero failures**.
Independent handoff review passed 14 additional disposable-fixture assertions,
including the previously reported freshness and redaction defects. Independent
resource review passed all ten checker tests and four fake-CLI helper tests and
found no remaining blockers in scope. Publication-time CI results are recorded
separately from these local results.
