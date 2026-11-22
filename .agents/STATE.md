# Postplan rollout (hybrid, waves 1–3) — 2026-11-22 (Bryan: "yes full send wave 1 2 and 3 now do it for all fleet", "yes hybrid")

- 42 skills wired to `postplan-upload` (41 routing-line edits + standing rule in `postplan-upload`, mirrored in `skill-router`); 6 already wired; coverage 48/220 (~22%). `shell` inherits via alias, no edit. skill-creator checklist gains the routing-line rule for new skills.
- Standing rule (Bryan 2026-11-22): covered skills auto-publish their substantial .md deliverable as a hosted page by default (visual-explainer template + postplan-upload, URL next to local path). Gated 8 confirm first: internal-comms, cloudflare-one, why, session-handoff, project-transfer, repo-standardization, fleet-skill-audit, homelab-pihole-dns.
- Pinned `npx postplan@0.0.6 upload` in postplan-upload + version line "Matches postplan 0.0.6 (verified on E14, 2026-11-22)". npm registry latest is 0.0.6.
- Pre-flight (verified 2026-11-22, NOT assumed): postplan auth valid on L390/3410/T14/E14 (150 drafts, live uploads 1h ago); E14 has global postplan@0.0.6, others via npx. VM had neither — CLI installed to /home/hatch/.local/bin (npm through proxy works); VM LOGIN still needs Bryan (`postplan auth login` pastes an API key from the browser — credentials.json was NOT copied between machines). CSP: visual-explainer template degrades gracefully on Postplan (inline toggle script dead under script-src 'none', both diagram views render, controls stay hidden). URL stability: FORKED — same file re-uploaded from 3410 got a new draft ID (ccjj2avf3cah vs L390 k3uwz9yh3pjl); mapping is per-machine, rule says re-upload from the creating machine. Test drafts k3uwz9yh3pjl + ccjj2avf3cah are safe to delete (no CLI delete command; dashboard only).
- House validation green: quick_validate 44/44, text safety 0, resources Missing 0, platforms OK, INDEX --check agrees, full suite OK (skipped=9).
- Still to do after commit: fleet pull (5 primaries) + profiled-skill copies to T14/E14 .codex\skills; add postplan to setup-path docs (README + agent-machine-bootstrap) so future machine setups get it.

# NVIDIA SkillEvaluator — 2026-11-21 (steps 1–8 DONE; SkillSpector close-out in progress)

- Bryan (2026-11-21): "i want you to use this https://github.com/NVIDIA/SkillEvaluator and evaluate all our theprawnskills repo" + "can you help to full send the 8 tasks in plan and babysit until all complete now?" Muse does the work directly (this chat's no-delegation rule).
- Tool: skillevaluator 1.0.1 in ~/workspace/skillevaluator-venv (uv 0.13.9, bandit 1.9.4, gitleaks 8.30.0). SkillSpector 2.13.6 pip-installed 2026-11-21 (uv path times out on pypi.org via egress proxy — 44.4s total; pip works). VM-local security runs need `SKILLEVALUATOR_SKILLSPECTOR_PATH=/home/hatch/workspace/skillevaluator-venv/bin/skillspector` (tool pins 2.13.4, override bypasses the uv fallback).
- Step 1 SkillSpector close-out IN PROGRESS 2026-11-21 evening (Bryan picked "fix the real hygiene first, then baseline"): full catalog WITH security ran 2026-11-21 ~17:15 (67 min): 125/220 failed, ALL only on Security Scan; 117 incomplete scans; 1619 findings (critical 1, high ~306, medium ~1275, low ~15). Triage: ~/workspace/skillevaluator-reports/tier1-full-security-TRIAGE.md. Hygiene DONE: .pyc/__pycache__ deleted (SC8 verified gone), __MACOSX stripped from deploy-to-vercel/Archive.zip, web-perf chrome-devtools-mcp pinned to 1.13.0 (only true unpinned MCP server; the ~700 other `npx` hits are user-run CLIs). The 1 critical (javascript-sdk tool-builder.md:159) is a FALSE POSITIVE — doc sample demonstrating the stored-secret pattern. Baseline `skillevaluator-skillspector-baseline.yaml` (164 rules, v2) validated: hill-climb 3/3, javascript-sdk 13/13, cloudflare 512/512, claude-api 105/105, skill-update 6/6, turnstile-spin 37/37, caveman-compress 9/9, webapp-testing 10/10, impeccable 70/70 suppressed, 0 left. KEY LESSON: baseline `message` globs match SkillSpector's RAW MATCHED TEXT, not SkillEvaluator's summary prefix (first version suppressed 0). Full catalog re-run with security + baseline DONE 2026-11-21 ~20:28 (66 min, output tier1-full-security2/): **120/220 fail, all security-only; baseline suppressed 1,250 findings; 94 fail with ZERO active findings — pure incompleteness.** Incomplete ledger (as SHOWN in SEV reports): reference_missing 142, static_parse_limit 95, obfuscated_instruction_text 20, reference_unresolved 6, output_limit 2, runtime_limit 1, opaque_content 1, referenced_uninspected 1. Triage: ~/workspace/skillevaluator-reports/tier1-full-security2-TRIAGE.md. **Verdict: the security gate CANNOT pass for this library as-is — findings are at zero, incompleteness blocks it.** Bryan DECIDED 2026-11-21 22:16: fix the 95. FINDING 2026-11-21 ~23:15: the 95 are NOT long commands — no line in any file tops 1,765 chars. Triggers are parser limits on correct code, proven by minimal repros: (a) shell word `command` + redirect (`command > /tmp/x.txt` trips command_word_boundary; `ls >` / bare `command` / `command foo bar` pass; rename to `your-command` clears it); (b) JS/TS template literals with `${}` containing calls/multiple/dotted interpolations (`` `${await getToken()}` ``, `` `${Date.now()}` ``, `` `${env.A}/${env.B}` ``, `` `%${filters.name}%` `` trip printf_invocation; simple `` `${name}` `` passes). Full classification (direct scans, 302 rows, 28 skills): command_string_runtime 132, printf_invocation 65, expansion_boundary 57, command_word_boundary 39, command_argument_boundary 7, runtime_command_identity 1, brace_characters 1 — 254/302 are template literals in live skill scripts + reference docs. CRITICAL SCOPE CORRECTION: SkillEvaluator truncates the completeness ledger to the FIRST 20 rows per skill (`skillspector_diagnostics.py: _MAX_ROWS = 20`); the SEV reports show 268 rows with 253 omitted — true total 521 ledger rows. The SEV-visible "95" static_parse_limit files are only the first 20 rows per skill; direct scans show the true scope is **302 files**. Fixing the visible 95 will surface the next batch in the next run (whack-a-mole via truncation). Awaiting Bryan's strategy call (options sent 2026-11-21 ~23:00): fix only the genuine shell cases + report upstream, mass-rewrite template literals anyway, or leave security out of CI. Do NOT add `security` as a blocking gate until decided. Do NOT rewrite correct TS/JS to dodge the scanner (house stance). **Bryan DECIDED 2026-11-21 23:19: "Fix only the genuine shell cases, report the rest upstream."** Fix outcome 2026-11-22: genuine scope was exactly 1 file — bug-diagnosis SKILL.md `command` placeholder → `your-command` (2 lines), re-scan verified clean with AND without baseline (complete, 0 SPL rows). The other 2 candidates proven NOT fixable by isolation repros: cloudflare c3/gotchas.md:34-92 trips only as the full 58-line mix (halves pass, single continuation passes, YAML+tables pass — cross-block accumulation, no clean edit); turnstile-spin auth-probe.sh first 60 lines pass alone, real trigger is Python f-strings (`{verdict}`, `{created_sitekey}`) inside the bash heredoc — correct code, parser misreads embedded Python (brace_characters 1450 observed / 256 limit). Both join the upstream report. **Upstream filed 2026-11-22:** SkillSpector#1165 (parser limits: template literals, `command` builtin, XML fixtures, embedded f-strings, cross-block accumulation; all repros re-verified on 2.13.6) + SkillEvaluator#861 (ledger truncation _MAX_ROWS=20; 268 shown / 253 omitted / 521 true). Issue texts: ~/workspace/skillevaluator-reports/upstream-skillspector-issue.md, upstream-skillevaluator-issue.md.
- Step 2 pilot (10 skills): 9/10 pass, claude-api failed. Step 3 full run: 197 pass, 32 fail of 229. Quality 75.0–93.2, median 89.5, none below 70. Triage: ~/workspace/skillevaluator-reports/tier1-full-TRIAGE.md.
- Step 4 fix pass COMMITTED 2b7f6c1 (49 files) + CI pin 31b4452 (ubuntu-latest → 24.04; Playwright 1.59.1 has no 26.04 chromium — pre-existing infra break, not the fix). CI on 31b4452: Skill library run 44872743797 completed success (all 3 OSes). Fleet: all 5 primaries at 31b4452; 14 edited profiled skills hash-verified in T14/E14 .codex\skills; T14 OneDrive mirror verified via hook.
- Step 5 Muse-as-judge DONE 2026-11-21: all 41 judged (pilot 10 + flagged 32), ALL PASS ≥70, zero security issues. Top: hill-climb 93, claude-api 92, virtualbox/pptx 91. Lowest: caveman-stats 70 (stub by design), postgres-mcp-onboarding + web-design-guidelines 72. Patterns: error_handling weakest in 24/41; example_quality second; trigger over-claim in cloudflare/react-dev/press-release-writing. Stale content found (not fixed yet): fleet-skill-audit "69/69" (profile is 68), claude-code-cli Gemini comparison + hermes- temp path, security-best-practices empty Examples + stale metadata block. Report: ~/workspace/skillevaluator-reports/step5-rubric-pilot10.md.
- Step 6 Tier 2 dedup DONE 2026-11-21: Ollama on L390 (nomic-embed-text) via SSH tunnel; 196 pairs above threshold — 1 critical (nano-banana ↔ nano-banana-2, 0.951 exact dupe), 6 high, 189 medium. Triage: ~/workspace/skillevaluator-reports/tier2-TRIAGE.md. Merges are Bryan's call — options widget sent 2026-11-21 ~13:53, awaiting his pick. Tunnel died in the ~14:16 runtime restart; nothing pending needs it.
- Step 7 Tier 3 hand pilot DONE 2026-11-21 (4 helps, 1 neutral, 0 hurts;
  n=1 per skill, judge is Muse): caveman -77% words; docx helps weakly
  (2 latent gotchas avoided, both validate); xlsx helps (None cached
  total -> 40300 after recalc); press-release-writing helps (8
  superlatives + 2 exclamations + I-quote + missing dateline/contact ->
  all clean); skill-router neutral (same 5 picks with/without — Muse
  knows the library). Side findings: docx "preinstalled" claim false on
  the VM (installed to /tmp for the pilot); validate.py needs defusedxml
  + lxml, undocumented in the skill's Dependencies. Report:
  ~/workspace/skillevaluator-reports/step7-tier3-pilot.md.
- Step 8 CI workflow DONE 2026-11-21: .github/workflows/skill-checks.yml
  (own pip-based workflow — upstream reusable runs default OSS policy
  only). PR = changed skills; push/policy-waiver change/dispatch = full
  catalog. Two real bugs caught by CI itself and fixed: (1) full-catalog
  gate globbed `reports/full/*.json` but the tool writes per-skill dirs
  (run 44875525912 failed on IndexError while validation passed 222/222
  — fixed 182b962, dispatch 44876017275 green); (2) changed-skills
  `for f in ${{ outputs.changed }}` broke on multiline substitution —
  bash for-lists cannot span lines (reproduced locally, exit 2) — fixed
  to while-read from changed.txt + skip deleted dirs (e1feace); loop
  verified locally (3 skills pass, 2 deleted skipped, FAILED=0).
  Full dispatch 44876466141 green (completed success 2026-11-21
  ~14:48 SGT); Skill library on merge commit 7708383 green all 3 OSes
  (run 44876267732). Step 8 CLOSED.
- Tier 2 merges DONE 2026-11-21 (Bryan: "merge all that needs to be
  merged", green-lit 14:31 SGT): verified all 7 critical/high + 10
  medium pairs by reading the skills. MERGED 2 (commit 7708383):
  nano-banana-2 -> nano-banana (3-model table, Output table, Python SDK
  folded in; quality 87.0 B) and ai-voice-cloning -> text-to-speech
  (Kokoro library, voice examples, multi-voice, chunking, pacing, best
  practices folded in; quality 89.5 B). Library 229 -> 227. KEPT with
  reasons: commit-work/git-commit (designed split-vs-single pair),
  avatar trio (catalog vs production vs single-tool), music + TTS/STT
  pairs (chooser vs single-tool pattern), spec/to-spec (format vs
  process), skill-cleanup/remove (audit vs execute), skill-create/creator
  (thin workflow vs 530-line guide + Linux twin), dialogue-audio/
  elevenlabs-dialogue (craft vs tool), skill-judge/reviewer, bug-diagnosis/
  systematic-debugging, ponytail-audit/review, aliases (shell/molt),
  siblings (p-image/p-video, docx/xlsx, elevenlabs family). Fleet: all 5
  primaries at e1feace; skill-router copied to T14/E14 .codex\skills (fc
  clean both); T14 OneDrive deleted dirs removed + router mirror verified
  via hook; E14 OneDrive via sync (async).

# web-to-markdown deleted — 2026-11-18 (committed 483e82a, fleet rolled out, CI green run 44265136638)

- Bryan (2026-11-18): "delete web2md lol". The skill depended on his local softaworks web2md project, which is not on any fleet machine (checked VM, L390, 3410, T14, E14) — deleted instead of chasing the project.
- Deleted skills/web-to-markdown; router row fixed; default-profile.toml 69 → 68; tests/test_install_skills.py:251 69 → 68 (tripwire by design). Library 230 → 229 definitions. Suite 129 tests OK (skipped=9).
- Belt: already installed on the VM (belt v1.29.5, /home/hatch/.local/bin/belt; .bashrc PATH line present) — Bryan's "sure install belt" needed no action, verified live. Web-perf: kept, version line chrome-devtools-mcp 1.13.0 already in place.
- Fleet: all 5 primaries at 483e82a. Windows: skill-router xcopy'd to .codex\skills (hash-verified); web-to-markdown removed from both .codex\skills roots + T14 OneDrive .agents.

# Full Azure removal — 2026-11-18 (committed e1d85b9, fleet rolled out, CI green run 44262752694)

- Bryan (2026-11-18): "yes remove azure". Full-send covers the edits.
- Deleted 25 top-level dirs (814 files): all 19 azure-* skills, entra-agent-id, entra-app-registration, airunway-aks-setup, deploy-model tree, microsoft-foundry tree, preset, appinsights-instrumentation (Azure Application Insights — its whole purpose). Library 262 → 230 definitions.
- Hand-offs fixed in surviving skills: skill-router (6 azure/Entra/deploy-model rows + 2 "Azure, " list mentions + line 122 azure-prepare), Linux router row 41, docker-expert (AKS + azure-prepare rows), skill-cleanup:104, wizard:111. "preset" word hits in 9 surviving skills are all generic (LoRA presets, shadcn --preset, babel preset-env, wrangler --preset) — left alone. Cloudflare ai-gateway's "Azure OpenAI" provider row is a factual capability table of a third-party product, not a library hand-off — left alone. skill-creator:115 `azure.md` is an example file tree — left alone. skill-router:68 `rg ... azure|...` is a search-pattern example — left alone.
- scripts/skill-resource-exceptions.json: 23 → 14 (9 dying-source entries removed; audit rejects stale entries).
- tests/test_restored_helpers.py: preset tests deleted (bash + powershell); only the dependency-updater test remains. Suite 129 tests OK (skipped=9).
- Belt installed on the VM (Bryan: "if u need to install pls install"): `curl -fsSL cli.inference.sh | sh` with INSTALL_DIR=/home/hatch/.local/bin (installer defaults to /usr/local/bin as root — ephemeral on the VM). belt v1.29.5. Version line added to all 69 `Bash(belt *)` skills via script (63 after H1, 6 after an existing app Matches line). web-perf line: chrome-devtools-mcp 1.13.0 (npx --version verified live on the VM; skill runs it via `npx -y chrome-devtools-mcp@latest`).
- Fleet: all 5 primaries at e1d85b9. Windows: 6 profiled edited skills xcopy'd to .codex\skills (hash-verified, `\*` copy — no nesting this time); 25 dirs deleted from T14 OneDrive .agents (hook never deletes; E14 via OneDrive sync). No STALE-CODEX entries.
- web2md: NOT found on any of the 5 machines (VM, L390, 3410, T14, E14 — checked workspace/softaworks, Projects/softaworks, and softaworks paths). It is Bryan's own custom softaworks project (local CLI, not a published package). Version line stays open until he says where the project lives.

# Skill consolidations — 2026-11-18 (committed e01ff06, fleet rolled out, CI green run 44256442840)

- Bryan (2026-11-18): "yes agree.. merge thos / i dont need azure or qwen image lol / idk waht to do about the preset" + tapped yes to add the 3 version lines. Full-send covers the edits.
- Preset: kept `skills/preset` as canonical, deleted the 2 nested copies (`skills/deploy-model/preset`, `skills/microsoft-foundry/models/deploy-model/preset` — content identical, only relative link depth differed). Fixed path links in deploy-model + foundry deploy-model SKILL.md and both capacity files (foundry capacity needs 4 ups: `../../../../preset/SKILL.md`). Test `test_preset_variants_have_identical_self_contained_helpers` deleted (it asserted the 3 variants' helper scripts identical — only 1 variant left); VARIANTS reduced to `("skills/preset",)`.
- agent-tools deleted (infsh-cli kept — the newer copy: extra `belt app list` row, Seedance 2.0 vs 1.5). Foundry `agent-tools.md` / `azd ai toolbox agent-tools` mentions are a different thing (Foundry tool file / toolbox name), left alone.
- azure-kubernetes-automatic-readiness deleted BOTH copies (Bryan doesn't need Azure); azure-messaging deleted. Fixed hand-offs in azure-kubernetes/SKILL.md, app-deploy description + body, safeguards.md (source-of-truth pointer to the deleted constraint-spec removed), azure-storage description. azure-diagnostics/azure-upgrade `azure-messaging-*` hits are SDK package names, left alone.
- ai-product-photography / ai-marketing-videos / ai-social-media-content deleted (belt-app wrappers; covered by product-photography, ai-image-generation, google-veo/seedance). Fixed npx lines in ai-automation-workflows + content-repurposing, router rows.
- qwen-image-2 + qwen-image-2-pro deleted (Bryan doesn't need Qwen image).
- Version lines added: shadcn 4.23.0, @remotion/cli 4.0.544 (both npm latest, VM, 2026-11-18), VirtualBox 7.2.16 (T14, 2026-11-18). Remaining unverifiable: belt (install route unclear), az/azd, web-perf, web2md (project not found on VM/L390/3410/T14 — ask Bryan where it lives).
- Library 273 → 262 definitions (11 SKILL.md files removed). INDEX regenerated + agrees; quick_validate 14/14 edited skills; resources Missing 0; platforms OK (262, 13 exceptions); text safety 0; full suite OK (skipped=10).
- Fleet: all 5 primaries at e01ff06. Windows: skill-router + shadcn xcopy'd to .codex\skills (hash-verified); 11 dirs deleted from T14 OneDrive .agents (hook never deletes — manual step; E14 via OneDrive sync). Gotcha: PowerShell Copy-Item of a dir into an existing dir NESTS it (`skills\skill-router\skill-router`) — copy with `\*` instead.
- NOT done: full Azure removal (deploy-model tree, microsoft-foundry tree, azure-prepare hand-offs) — bigger job, only if Bryan asks.

# Full skills vet (agy + codex, all 273) — 2026-11-18 (committed a4ae37a, fleet rolled out, CI green run 44247478429)

- Bryan (2026-11-17): "Double check sanity check. Ask agy and codex to vet alll our skills in prawnskills. Then make edits where necessary. Then push to whole fleet." Full-send confirmed 2026-11-18 13:04 — no per-item approval.
- Design: 6 alphabetical batches (46/46/46/46/46/43), both agents vet every batch independently, read-only; Muse verifies each finding against its file before editing. VM agy auth EXPIRED 2026-11-17 (interactive TUI needs a real TTY + browser OAuth, not doable from the VM shell) — agy half ran on L390 via Herdr (cargo herdr CLI, agents skills-vet-agy-l390[-b2..b6]); codex half ran on the VM (all 6 batches, one retry on b2 Bad Request).
- Totals: codex Must 45, Should 19, Nice 1 (reviewed 272, clean 217); agy Must 24, Should 44, Nice 19 (reviewed 273, clean 113). All verdicts NEEDS CHANGES.
- Fixes (190 files, +580/−572): claude-api catalog rebuilt from live-verified data (Fable/Mythos 5.1, Opus/Sonnet/Haiku 5.5; Sonnet 4.5 retires 2026-11-30) — agy b2's "opus-5/sonnet-5 don't exist" claim was half wrong; 83 npx belt banners + 31 dead ai-video-generation refs removed repo-wide; token-printing commands fixed (systematic-debugging, vercel-cli-with-tokens); dead hand-offs, missing H1s (sharpen, impeccable, entra, workers-best-practices, +4 ponytail/internal-comms), description WHAT+WHEN gaps, trigger collisions (twitter automation vs thread writing, technical-blog vs technical-writing, nano-banana vs nano-banana-2, dialogue-audio vs ElevenLabs); web-to-markdown softaworks path + hard trigger gate removed; web-design-guidelines re-scoped (fetch via any web tool, offline fallback to design-taste-frontend + better-accessibility); 26 version-matched lines added.
- Validation caught in the pass: 5 quick_validate failures from my own edits (leaving-pr-comments angle brackets; 4 plain-scalar `WHEN: "..."` + systematic-debugging `protocol: ...` — colon-space breaks YAML plain scalars; all rewritten as prose); 2 resource-audit misses (`scripts/install_skills.py` → `../../scripts/install_skills.py` in find-skills + related-skill). Final: quick_validate 168 edited skills 0 failures; text safety 0; resources Missing 0; platforms OK (273, 13 exceptions); INDEX regenerated + agrees; full suite 132 tests OK (skipped=10).
- Unverifiable version lines (no live install anywhere in the fleet — do not invent): belt (~35 files), microsoft-foundry az/azd, shadcn, remotion-render, vercel-react-best-practices + vercel-react-native-skills (no version stated in-file), virtualbox-guest-access, web-perf, web-to-markdown.
- Structural consolidations NOT done — Bryan's call: preset triplicate, agent-tools ≈ infsh-cli, azure-kubernetes nested dup, ai-* prompt wrappers, azure-messaging, qwen-image-2 vs qwen-image-2-pro.
- Judgment calls recorded: fleet-skill-audit `--unmask` kept (explicit operator opt-in, default masked); skill-creator Claude.ai section + `claude -p` eval lines kept (scripts genuinely call claude -p); vercel-cli-with-tokens printenv PROJECT_ID/ORG_ID kept (IDs, not secrets); related-skill re-scoped, not retired.
- Fleet: all 5 primaries at a4ae37a (L390/3410 git pull; T14/E14 git pull + xcopy 35 edited profiled skills to .codex\skills, fc/hash 35/35 identical; T14 OneDrive mirror verified via hook). E14 fc loop was mis-structured (ran the check mid-copy, false FC-DIFFs) — re-verified clean with PowerShell Get-FileHash, 35/35, 0 mismatches.
- Debunked (do not re-raise): codex b3 docx pdftoppm zero-pad claim (pdftoppm DOES zero-pad); agy b2 claude model non-existence claims (partially wrong); agy b5 related-skill "6 of 14 table skills non-existent" (partly wrong — 4 exist locally).

# Import better-accessibility + break from jakubkrehel/skills — 2026-11-17 (committed + fleet rolled out — see JOURNAL for hash)

- Bryan (2026-11-17): drop build-design, import the other 2. build-design is Figma-first as shipped (Figma link = exact values via Figma MCP; no Figma tool = hard stop asking the user to connect one) — Bryan: don't be dependent on Figma. build-design NOT imported; no Figma-dependent skill in the library.
- Imported (on-demand, MIT, interfaces 1.20.0, verified 2026-11-17): better-accessibility (WCAG 2.2 review + fix, criterion-cited, Block/Approve verdict; 6 reference files) and break (stress-test one component under worst-case scenarios on a throwaway harness page; scenarios.md). Whole dirs copied, including agents/openai.yaml display metadata (break's also carries allow_implicit_invocation: false, matching the dropped disable-model-invocation).
- Adaptation: frontmatter per house rules (license MIT; metadata author "Local setup", version "1.0.0", upstream-version "1.20.0", platform contract line); dropped break's `disable-model-invocation` (Claude-only key, fails quick_validate); hand-off lines rewritten from non-imported jakub skills to local owners (design-taste-frontend for typography/layout/color/UI/copy; verification-loop for code review) or dropped where no equivalent exists; contrast measurement kept inline via the skill's own table; provenance line after each H1. Router rows added by the frontend rows (main router only — Linux router is a curated shortlist and doesn't carry the frontend design rows either).
- Validations: quick_validate both valid; text safety 0; resource audit Missing 0; platform audit OK (273 files, 13 exceptions); INDEX regenerated + agrees (271 → 273 definitions); full suite 132 tests OK (skipped=10). Profile stays 69 (on-demand, no installer run, no test-count change).
- Fleet wrinkle (2026-11-17): T14 OneDrive clone corrupted AGAIN — pack unreadable, fsck 6,600+ failed entries, same OneDrive-eats-.git hazard as 2026-11-14. Repaired by killing OneDrive, deleting the corrupt pack + stale commit-graph, xcopy /R of the primary clone's .git/objects, fsck 0 failed, pull to 8797b67; OneDrive sync had also dropped the CI-green line from JOURNAL.md in the worktree — restored from HEAD. OneDrive relaunched and running. OneDrive sync of .git internals is a recurring corruption vector on T14.
- OneDrive de-git, durable fix (2026-11-17, Bryan: yes, both machines): .git removed from the OneDrive live root on T14 + E14 — third corruption (also found .git.broken-20260927 on T14). Primaries keep .git; nothing lost. NEW FLEET RULE: never git-pull in C:\Users\bryan\.agents — it is not a repo anymore. Pull the primary clone only (C:\Users\bryan\Projects\theprawnskills). T14 primary has a post-merge hook (C:\Users\bryan\.githooks\post-merge — T14 core.hooksPath points there, .git/hooks is ignored; local file, NOT committed; repo-guarded since the hooks dir is global) that mirrors the primary into the OneDrive folder after every pull (robocopy /E /XD .git — add/update only, never deletes; the folder also holds non-repo files machines.toml, agents.toml, node_modules, packages, pnpm-*). Log: C:\Users\bryan\sync-skills.log. E14 receives the mirror through OneDrive sync. .codex\skills xcopy stays manual per pull round. Hook gotcha (proven live): Git Bash mangles /E into E:/ — the hook sets MSYS_NO_PATHCONV=1 on the robocopy call. First manual run: 4510 files copied, exit 3, 0 failed; 7 extras left alone (all non-repo files). Proved via `git hook run post-merge`: 2 files mirrored, exit 3, 0 failed.
- Skill-craft fold-in (2026-11-17, Bryan: yes): jakubkrehel AGENTS.md patterns folded into skill-creator — domain vs verb split, calibration lines, point-carrying sentence-case headings, Before-you-finish tables, Reporting with severity ladder, rule ownership (one skill per rule, point by bold heading never number), reference-file discipline, counts that cannot go stale, four edit checks (30-word ceiling, description matches INDEX.md row, one statement per rule, pruning pass). Deliberate differences recorded in the skill: descriptions keep trigger phrases (house contract); user-invoked switch lives in agent metadata, never frontmatter. DialKit declined (Bryan: no need) — not added to polish-repo Phase 5.
- Annotation packet (2026-11-17, Bryan: yes): Agentation annotation-packet format folded into polish-repo — one annotation round at the end of Phase 5 (present render, user annotates in plain words, agent builds one packet per note into docs/annotations.md, fixes in severity order, re-renders once; second round only on the user's word); Phase 6 gate — every packet resolved or user-dismissed before verification passes; agent never dismisses a packet. Format only, no dependency — the Agentation tool itself is not adopted.

# Version-matched skills + Tier D pointers + 9 quick_validate fixes — 2026-11-16 (committed + fleet rolled out — see JOURNAL for hash)

- Bryan (2026-11-16): approved all three open items — version-matched rule, Tier D links, fix the 9 quick_validate failures now.
- Version-matched rule recorded in AGENTS.md Skill System: a skill describing a versioned tool states the tool version it matches, in the body after the title, with machine + date verified; updating the tool without updating the line is a bug. Matched lines added: codex 0.167.2 (VM), claude-code-cli 2.1.296 (3410), opencode-cli 1.18.34 (VM). Note: codex is 0.169.0 on 3410 — versions differ per machine, the line records where verified. Frontmatter cannot carry the version (quick_validate allows only name/description/license/allowed-tools/metadata/compatibility).
- Tier D pointers: all 7 skill-management files now point at their Linux twin (`../../platforms/linux/skills/<name>/SKILL.md`); skill-router notes its twin is a curated shortlist, not a mirror. Platform lines untouched (documented exceptions).
- 9 quick_validate failures fixed: ai-content-pipeline (`->` → `→`), vercel-react-view-transitions (angle brackets out), airunway-aks-setup (dropped `argument-hint`), claude-api (description 1068 → 1020 chars, cut the "looks like a one-liner" aside), cloudflare + turnstile-spin (dropped `references` key; files stay on disk), docker-expert (dropped category/risk/source/date_added), react-dev (dropped top-level `version`), shadcn (dropped `user-invocable`).
- Validations: quick_validate sweep 0 failures (was 9); text safety 0; resource audit Missing 0; platform audit OK; INDEX regenerated + agrees; installer --check 69/0; full suite 132 tests OK (skipped=10).

# agy review fixes — 2026-11-16 (committed + fleet rolled out — see JOURNAL for hash)

- Bryan (2026-11-15): fix all 9 agy findings on the hill-climb wiring. Verdict was NEEDS CHANGES; Muse verified all 9 against the files first, all held. Report: ~/workspace/polish-repo-hillclimb-agy-review-20261115.md.
- Fixes: (1) baseline checkpoint now stages explicit path groups (editable files + Phase 3 tests + docs/user-stories.md) and bans `git reset --hard` in the loop — NOT agy's proposed `git add -A`, which hill-climb:227 forbids; reverts use only scoped restore/clean. (2) "Phase 8 turns gaps into tasks" removed from description + early-stage (pre-existing loose wording carried through the renumbering) — gaps are logged in docs/user-stories.md; Phase 3 turns them into a fix queue. (3) Degraded 1-model harness check added (cap 4 rounds, single-judge labels, 9/10 not consensus). (4) Editable files now "the files for <area>" (default Phase 3–5 files). (5) Baseline gate failure: propose fix + get approval, or abort to Phase 8. (6) Cost cap field added (none enforceable). (7) Yes-to-loop authorizes autonomous per-round edits, not just commits. (8) Skip Phase 7 when no test/build/lint gate exists. (9) Next feature continues on the same branch.
- Validations: quick_validate; text safety 0; resource audit Missing 0; platform audit OK; INDEX regenerated + agrees (no INDEX diff — description change falls past truncation); full suite 132 tests OK (skipped=10).

# hill-climb wired into polish-repo — 2026-11-15 (committed + fleet rolled out — see JOURNAL for hash)

- Bryan (2026-11-15): yes, add hill-climb to polish-repo. New optional Phase 7 "Iterate" sits between Verify (6) and Ship (renumbered 8). Ask at the end of Phase 6: run the loop on the weakest area, or ship as-is. The weakest area comes from the Phase 6 wrap-up ("still open") + mismatch log; user may pick a different area.
- The authorization form is filled from polish context, no fresh walkthrough: goal = improve the area to 9/10; eval = Phase 2 acceptance criteria + hill-climb's coding row; gate = the Phase 1 baseline test/build/lint; threshold 9/10, max 8 rounds, plateau 2; baseline scored post-Phase-6 first; editable = files changed in Phases 3–5 only; same disposable branch. Saying yes authorizes local checkpoint commits on that branch; push still needs a separate yes in Phase 8. Plateau is a decision point (escape options, wait for the pick). Skipped for early-stage repos.
- Description + intro chain + early-stage note updated (Phase 7 → Phase 8 for the gaps-into-tasks line); INDEX.md regenerated (polish-repo row only).
- Validations: quick_validate polish-repo; text safety 0; resource audit Missing 0; platform audit OK; INDEX --check agrees; full suite 132 tests OK (skipped=10).

# Pacing is provider-neutral — 2026-11-15 (committed + fleet rolled out — CI green run 43723283168)

- Bryan (2026-11-15): the 5h window doesn't only apply to agy — pacing must apply to whatever agent is running. The cook-lessons wording said "the provider's limit window" but used "5h window" as the example everywhere, which reads as agy-only. Fixed in hill-climb (authorization form), polish-repo (ground rules), and MEMORY.md: the window belongs to whichever agent is running (Codex, agy, OpenCode, Muse) — agy's is 5h; use the active provider's own window. Rule unchanged otherwise (~20% per hour, never 100%, check at boundaries).
- Also answered 2026-11-15: polish-repo does NOT include hill-climb (grep: zero mentions). Its chain ends at verification-loop → file-pr. Hill-climb is a separate on-demand skill. Offered to wire it in; awaiting Bryan's word.

# PostPlan consistency fix — 2026-11-15 (committed + fleet rolled out — see JOURNAL for hash)

- Bryan (2026-11-15): postplan gives different style/format on different machines and projects — fix it. Diagnosis (verified live, all 5 machines): the 5 postplan/visual-explainer files are hash-identical everywhere and installed copies are complete — NOT machine drift. Cause: agents free-wrote HTML instead of copying the template, and check_html.py checked structure only, never tokens.
- Fix: check_html.py gains a design-token check (8 hex values from design-system.md, checked in <style> blocks only — an inline style cannot fake it) + a section-order check (overview, then details, then next-steps); new tests/test_check_html.py (7 tests, all pass). visual-explainer + postplan-upload gain a copy-the-template hard rule ("copy the template, replace content only; do not write HTML from scratch"). Both gain the Enso at-a-glance finish gate (the page alone must state the answer; fresh-agent cold read for substantial plans, max 3 rounds) and the branding exception (explicitly requested branding waives the token check — note the override, do not force the tokens back). design-system.md token-edit line now also names check_html.py (EXPECTED_TOKENS).
- Also vetted 2026-11-15: Enso Method (25 skills, MIT) — whole-method import NOT done (80% overlaps the library, client-handoff oriented, auto-commits); stole its renderer-with-invariants + cold-read ideas, which shaped this fix. Enso app CLI vetted earlier — don't install (macOS-only, zero macOS machines in the fleet).
- Validations: template passes the new checker; 7 new tests OK; full suite 132 tests OK (skipped=10); quick_validate both skills; text safety 0; resource audit Missing 0; platform audit OK; INDEX --check agrees. NOTE: the first full-suite run failed 1 test while postplan-upload carried a bad relative path (`templates/explainer.html` — the resource audit resolves it against the skill dir); fixed to `../visual-explainer/templates/explainer.html` and the suite went green. Windows quirk: the dotted test path (`python -m unittest tests.test_check_html`) fails to import on Windows — no `tests/__init__.py` — run tests via `discover -s tests` there, same as CI.

# Cook lessons applied — 2026-11-15 (committed + fleet rolled out — see JOURNAL for hash)

- Bryan: "I love the pointers u made for 'cook' lets go those." Cook-sourced edits only (no cook skill import): hill-climb gains a calibration offset (user's score vs model score, applied to later scores), zero-context critics in Full Mode, and a usage-pacing line in the authorization form; polish-repo gains a too-fast check (zero mismatches on a non-trivial repo = bar read too low), a decide+log rule (only product decisions and approval gates stop the run), and a pacing line; design-taste-frontend gains cook's visual slop ban list in section 6 Never. MEMORY.md gains the pacing standing rule (~20% of the 5h window per hour, never 100%).
- Branch stance (Bryan 2026-11-15): NO branch-per-agent default — direct on main where needed, branch only when the workflow needs one (e.g. opening a PR). The omnigraph-inspired branch-per-agent fleet default was rejected; polish-repo keeps its implied branch only at the file-pr step. Version-matched-skills rule (omnigraph) NOT applied — Bryan approved cook pointers only.
- Closed 2026-11-15 (Bryan: "dont need these"): people-graph convergence rules and Fudan write-side idempotency — dropped, not pursued. Cook skill import also declined the same day; cook lessons already applied (5671293).

# molt + shell moved to the default profile — 2026-11-15 (committed + fleet rolled out — see JOURNAL for hash)

- Bryan (2026-11-15): agents must know to use molt/shell without being told — they belong in the default skills. Added both to default-profile.toml (Core coding workflow, after cross-harness-state), 67 → 69 selected skills. INDEX regenerated (molt/shell ON-DEMAND → DAILY). Test count updated 67 → 69 (tests/test_install_skills.py:251 — same tripwire as the 66→67 fix).
- Load chain verified on the VM: profile lists both → INDEX marks both DAILY → skill-router rows list both → installer --apply installed both as symlinks into ~/.agents/skills (69 selected, 0 changes after). No live agent invocation test — agents pick them up through the installed profile root.
- agy correction (Bryan 2026-11-15): agy WORKS — no credits, but a 5-hour limit window. The "agy credits GONE, Codex only" note was stale; corrected in MEMORY.md.

# Debian edits for Windows-only skills — 2026-11-15 (edits applied; committed + fleet rolled out — see JOURNAL for hash)

- Audit (2026-11-12, resumed 2026-11-15 on Bryan's word): 32 files mention Windows with no Linux/Debian/macOS; 5 false positives left alone (azure-kusto, deploy-model/customize, microsoft-foundry duplicate, image-to-video, storyboard-creation); 28 real candidates in 4 tiers — A 13 metadata-only, B 5 notes/fences, C 2 genuinely Windows-implemented (claude-code-cli, opencode-cli), D 7 skill-management (NOT edited: shared files stay Windows/OneDrive by design, Linux twins under platforms/linux/skills/ cover Debian).
- Reconciliation vs the 2026-11-14 platform pass: the pass already gave all 13 Tier A files the contract platform line, so 8 of them needed nothing (only Windows mention was the platform line itself). 5 Tier A files needed body fixes only.
- Edits applied (12 files, 85 insertions, 19 deletions): Tier A — codebase-design (powershell fence → bash, Measure-Object → wc -l), merge-conflict-resolution (2 powershell fences → bash), repo-standardization (2 powershell fences → bash), prototype ($env:TEMP → $TMPDIR on macOS/Linux (Debian)), cross-harness-state (OneDrive bullet + git counterpart for Debian/Linux). Tier B — bounded-agent-loop (OneDrive library → any synced folder; cleanup parenthetical + POSIX SIGKILL/15s; npm shim note; POSIX line → proper bash fence with dirname), bug-diagnosis (bash evidence capture after the PowerShell one), cli-agent-router (WSL sentence scoped + native-shim note; Start-Process + nohup/setsid equivalent), codex (npm shim note), dependency-updater (Bash-native on Debian/Linux). Tier C — claude-code-cli + opencode-cli got a "Debian/Linux adaptation" section (detached subshell + /tmp temp file + marker poll loop + tail -f; opencode config paths also given as ~/.config / ~/.local/share). Platform lines of claude-code-cli/opencode-cli left as the honest "on Windows (PowerShell)" (audit-fix decision, exceptions JSON untouched).
- Tier D NOT edited per the Nov 12 audit decision (house rule: preserve OneDrive workflows in shared text). Open question for Bryan: add a pointer section in the 7 D files to their Linux twins, or leave them as-is.
- Validations: all 4 new bash blocks pass bash -n; detached-subshell + marker + poll pattern smoke-tested live; quick_validate passes on all 12 edited files; INDEX --check agrees; text safety 0; resource audit Missing 0; platform audit OK (271 files, 13 exceptions); installer --check 67 selected, 0 changes.
- De-fleet: all new wording is generic "Debian/Linux" — no machine names or personal paths. default-profile.toml untouched.

# Platform-line pass + molt/shell aliases + platform CI check — 2026-11-14 (alias pair + pass + CI + audit fixes committed; 7 + 8 left alone)

- Platform-line pass (2026-11-14, Bryan's word "YES DO ALL"): 269 files
  scanned; 222 changed (193 added the contract line, 29 replaced a
  narrower line), 14 kept as documented exceptions (4 agent-specific:
  codex, claude-code-cli, opencode-cli, claude-api; 2 platform-specific:
  homelab-pihole-dns, virtualbox-guest-access; 7 Windows variant copies
  with Linux twins; opencode-bedrock-config). Re-audit: 254 exact
  contract string + 1 contract+extras (cross-harness-state); the 14 kept
  files are the only ones without it, all by design.
- PASS-SCRIPT BUG, caught by spot-check + quick_validate: the first run
  glued the closing `---` onto the platform line in all 142 added-block
  files ("Invalid frontmatter format"). Repaired by inserting the
  missing newline; all 142 now validate. LESSON: YAML-parsing the
  frontmatter fragment is not enough — verify the reconstructed file
  with quick_validate on samples.
- molt + shell alias skills (new, ON-DEMAND, not in default-profile):
  molt routes to cross-harness-state + session-handoff; shell routes to
  repo-standardization. Router rows extended (continuity row, repo
  standardization row). INDEX 269 → 271 definitions. De-fleet grep
  clean. Validations pass. Provenance fix 2026-11-14 (Bryan's word):
  sourcerepo deleted STANDARD.md in b01008a, so the shell skill's
  "canonical home is hongyime/sourcerepo/STANDARD.md" line was a dead
  path — now names repo-standardization as the standard's home (its
  checklist is the standard); _shell/ folder holds a local copy of the
  retired doc. sourcerepo docs/skills-manifest.md now points at
  theprawnskills as the single skills home and names repo-standardization
  as the SHELL home.
- Platform-line CI check: scripts/audit_skill_platforms.py +
  scripts/skill-platform-exceptions.json (14 entries) + a step in
  .github/workflows/skills.yml after the resource audit. Token-set check
  (Codex, Antigravity (agy), OpenCode, Muse, Windows, macOS,
  Linux (Debian) all must appear); rejects stale exceptions. Local run:
  271 files OK. Negative tests pass (old Windows-only line flagged,
  missing line flagged, contract + extras pass).
- Full validations: quick_validate loop over 271 dirs — 9 failures, ALL
  pre-existing at HEAD (description angle brackets / too long,
  unexpected top-level keys; none platform-related). INDEX --check
  agrees, text safety 0, resource audit Missing 0, installer --check
  verified (67 selected, 0 changes).
- Alias pair (molt + shell + INDEX + router) committed 2026-11-14 on
  Bryan's word ("fix both of these now first and commit and push to
  main") — the SHELL-home fix ships with it. Platform pass (222 files)
  + CI check + audit fixes committed 2026-11-14 on Bryan's word. agy
  audit fixes, round 1 (2026-11-14, Bryan's word "do all 10" — scoped):
  findings 1, 2, 3, 4, 5, 6, 9 APPLIED. 1: to_posix() normalizes rel paths; 2: Linux
  router gained molt/shell rows; 3: claude-api out of exceptions +
  contract line (SDK reference, not a runner); 4: codex / claude-code-cli
  / opencode-cli gained honest agent-specific platform lines, exceptions
  kept with true reasons; 5: stale check now flags unscanned existing
  paths; 6: new tests/test_audit_skill_platforms.py (16 tests, all pass);
  9: trailing newline in exceptions JSON (13 entries now). Validations:
  platform audit OK (271 files, 13 exceptions), text safety 0, resource
  audit Missing 0, INDEX --check agrees, installer --check 67/0. Full
  suite 125 tests, 1 failure — the pre-existing test_install_skills
  66-vs-67 (polish-repo). claude-api quick_validate still fails on the
  pre-existing description-length issue (1068 > 1024), untouched.
  Findings 7 + 8 LEFT ALONE per Bryan 2026-11-14 23:47 ("leave 7 and 8
  alone") — aliases stay (names are the interface), stamped lines stay
  (fleet stable, re-stamp is one script run). Finding 10 DEBUNKED
  (sibling audit scripts also non-executable; CI calls via python) — no
  action.

# polish-repo entry-point skill — 2026-11-14 (uncommitted)

- New ON-DEMAND skill `polish-repo` (INDEX 257 → 258 rows, definitions
  268 → 269): one command ("polish this repo") chaining user-stories
  (map) → interrogate (challenge) → correct + tdd (fix) →
  design-taste-frontend / impeccable (looks, async no-live default) →
  verification-loop (prove it). Ground rules inherited from user-stories:
  no code changes until the user approves a specific fix, no unrelated
  refactors, no commit/push unless asked, running record in
  docs/user-stories.md, one feature at a time with stop points.
- Built because invoking 29 skills one by one from memory is too much
  friction. Checked kunchenguid/headless + kun first: neither fits
  (headless = machine provisioning over SSH; kun = one generalist
  "think like a principal engineer" skill, not a runner for other skills).
- Built because invoking 29 skills one by one from memory is too much
  friction. Checked kunchenguid/headless + kun first: neither fits
  (headless = machine provisioning over SSH; kun = one generalist
  "think like a principal engineer" skill, not a runner for other skills).
- Router row added. Validations pass: quick_validate (polish-repo,
  skill-router), INDEX --check agrees, text safety 0, resource audit
  Missing 0, installer dry-run + check verified.
- DEFAULT since 2026-11-14 (user's word): added to default-profile.toml
  (Core coding workflow, after requesting-code-review); INDEX regenerated
  (polish-repo now DAILY, 67 selected). Installed on the VM via installer
  --apply (opencode): ~/.agents/skills/polish-repo symlinked to the clone,
  --check verified.
- ADDITIONS folded in 2026-11-14 (user's word, all six): security-best-
  practices (new Phase 4 Tighten with modernize + unslop/sharpen), blast-
  radius before each fix, why/figure-it-out for stubborn bugs (Phase 2),
  file-pr as Phase 7 Ship (asks first, then opens the PR). Final chain:
  user-stories → interrogate → correct + tdd → modernize, unslop,
  sharpen → security-best-practices → design-taste-frontend / impeccable
  → verification-loop → file-pr. 7 phases. Validations re-passed.
- COMMITTED + PUSHED 2026-11-14 as fb7a72e ("feat: add polish-repo
  entry-point skill (default)"). Fleet install verified same day: all 7
  clones at fb7a72e, clean trees, polish-repo present in opencode +
  codex roots on every machine (byte-identical to the clone where
  checked).
- FLEET INSTALL NOTES: installer default (no --agents) fails on L390/3410
  with "Legacy Codex skills would be duplicated" — ~/.codex/skills holds
  66 legacy entries, but they are symlinks into the same clone, not
  copies, so the guard is over-cautious there. Used --agents opencode
  for the installer + a manual polish-repo symlink into ~/.codex/skills.
  On T14/E14 the installer refuses with "Parent is a symlink or
  junction" (C:\Users\bryan\.agents is the known OneDrive symlink) —
  skill already present in the OneDrive tree via pull, and codex root
  got a manual xcopy + fc byte-compare. Do NOT "fix" these guards
  blindly; the workarounds above are the verified path.
- T14 OneDrive clone was CORRUPT (OneDrive.exe running, 20 *-Prawn-*
  conflict files under .git, broken local/remote refs, invalid reflog
  entries, stale commit-graph). Repaired in place: deleted conflict
  files + stale commit-graph/multi-pack-index + logs, deleted 6 broken
  refs via update-ref -d, fetch + pull to fb7a72e. E14 OneDrive clone
  arrived at fb7a72e via OneDrive sync with a desynced index (staged D
  + ?? on polish-repo, stale INDEX.md/default-profile.toml content) —
  fixed with git reset + checkout of the 2 stale files, now clean.
  LESSON: OneDrive syncs .git internals between T14 and E14 (same shared
  folder) — that is both how E14 got the update and a standing corruption
  vector for git repos under OneDrive. T14 codex root still carries stale
  Orca copies (computer-use, orchestration) — not cleaned, out of scope.
- E14's OneDrive clone arriving via sync (not git) is why "Already up to
  date" appeared there with no fetch.
- agy fixes applied 2026-11-14 (user's word): dropped
  modernize/unslop/sharpen/correct (wrong skills — verified against their
  SKILL.md descriptions); Phase 3 now uses blast-radius + inline
  fix-the-fault guidance + tdd only when the test target is obvious/cheap;
  Phase 4 Tighten is now refactor + ponytail-review with an approval gate;
  security moved to Phase 2; batch story review (one summary table);
  baseline test/build check in Phase 1; loop/exit after Phase 7 (next
  feature or wrap up); "What this skill does not do" deleted; frontmatter
  description compressed; verification verbiage trimmed. File 6,731 →
  6,140 bytes. Validations re-passed, INDEX regenerated. COMMITTED +
  PUSHED as e745fc5. Fleet install verified same day: VM, L390, 3410,
  T14 primary, E14 primary + OneDrive all at e745fc5; T14 OneDrive clone
  git is BROKEN again (see below) but its working-tree files were synced
  from the primary clone and SHA256-match e745fc5 content.
- T14 OneDrive clone REPAIRED 2026-11-14 (Bryan approved pause):
  root cause was the .pack/.idx files were GONE from
  .git/objects/pack (only .rev/.mtimes left) — OneDrive had eaten them,
  so every fetch failed on the missing fb7a72e base object. Repair with
  OneDrive killed: deleted 6 *-Prawn-* conflict files, commit-graph,
  logs, 3 broken remote refs; xcopy /R (NOT plain xcopy — git pack files
  are read-only, plain xcopy fails "Access denied" on them) of the
  primary clone's .git/objects (46 files incl. the 37MB pack); fsck
  clean (3 dangling commits only), pull already up to date, git reset
  fixed stale index (status MM → clean). HEAD ea4100c, status clean.
  LESSON: never run git on a OneDrive-synced clone while OneDrive.exe
  is running — it re-corrupts the object DB in real time; proper repair
  needs OneDrive paused first. T14 OneDrive path is C:\Program Files\
  Microsoft OneDrive\OneDrive.exe (per-machine install, NOT
  %LOCALAPPDATA%); relaunch from SSH lands in Session 0 (no tray icon,
  sync still works, normal again after next login/reboot).
- Early-stage note + cross-harness-state platform fix (2026-11-14,
  Bryan's word, COMMITTED + PUSHED as 5f1620d): polish-repo gained an
  "Early-stage repos" section + description line + Phase 1 no-code line
  (second-opinion-only stops after Phase 2; Phases 3–5 skip until code
  exists; no invented baseline). cross-harness-state platform line fixed
  from "Codex, Claude, Cursor, OpenCode on Windows" to the contract string
  + Claude Code/Cursor; Harness Notes updated to match. Validations
  re-passed; INDEX.md unchanged (descriptions are truncated in the table,
  the new sentence falls past the cut). Fleet install verified same day:
  VM, L390, 3410, T14 primary + OneDrive, E14 primary + OneDrive all at
  5f1620d; both skills byte-identical in opencode + codex roots.
- _molt / _shell (2026-11-14, found on T14 + E14, identical on both): NOT
  skills — standalone folders under C:\Users\bryan\Projects\. _molt is the
  MOLT continuity system itself (2026-08-08 rev 2): README + a
  harness-agnostic agent prompt (paste into whichever CLI has tokens
  today) + AGENTS stanza + STATE.md templates for a repo's _molt/
  folder. cross-harness-state + session-handoff in theprawnskills are the
  skill versions of the same idea. _shell is the SHELL repo standard
  (2026-08-08 rev 2, target hongyime/sourcerepo/STANDARD.md): desired
  state for every hongyime/bryanseah234 repo (Apache-2.0 everywhere) +
  CLI/repo inventory, tiers, scan_identity.py. Not a terminal-shell skill.

# Skill sourcing build: 29 new skills, impeccable 4.9.0, 3 principle folds — 2026-11-14 (committed + pushed 48310f4, fleet synced)

- 29 new ON-DEMAND skills (INDEX 228 → 257 rows, definitions 239 → 268):
  user-stories (fresh, from the user's prompt + pstack mechanics); pstack 14
  (interrogate, why, how, figure-it-out, correct, tdd, unslop, sharpen,
  blast-radius, teach, show-me-your-work, reflect, statechart,
  technical-writing); design-taste-frontend (taste-skill, adapted for CLI
  agents); ponytail 6; tstack 7 (full-stop, full-send, file-pr, takeover,
  babysit-pr, modernize, leaving-pr-comments). None installed pstack as a
  plugin; all adapted in-library with Provenance sections.
- impeccable 4.1.1 → 4.9.0: 37 reference files ported with launcher calls
  translated to node scripts (`node .agent/skills/impeccable/scripts/*.mjs`)
  and commands to `/impeccable <command>`; live scripts stay at 4.1.1
  (upstream live-browser.js is launcher-coupled). Async no-live mode is now
  the default; live is opt-in. 13 upstream verbs have no library equivalent
  (comp-spec, comp-diff, build-phase, component-review, live-generate,
  font-match, audit-storage, signals, ignores, world, update, install,
  design) — reference files present as guidance, verbs left bare.
- Principle folds: prove-it-works + test-behavior-not-implementation into
  verification-loop and skill-judge; fix-root-causes into bug-diagnosis and
  systematic-debugging.
- Validations pass: quick_validate 35/35, INDEX --check agrees, text safety
  0, resource audit Missing 0 (7 new exceptions for example/placeholder
  paths), installer dry-run + check 66 selected / 0 changes.
- Router: 10 new rows for the new skills. No default-profile.toml change.
- Committed + pushed 2026-11-14 on the user's word as 48310f4. Fleet sync
  verified same day: VM, L390, 3410, T14, E14 primary clones all at
  48310f4, INDEX 257 rows, clean trees. SSH from the VM runs as root, so
  the ssh-config Host stanzas do not apply — use explicit
  `-o ProxyCommand` + `-i` flags (direct 3410 SSH resets; jump via L390).
  OPEN: E14's second clone FOUND 2026-11-14 — it is the live OneDrive
  clone at `C:\Users\bryan\.agents` (symlink → OneDrive\01 SKILLS\.agents);
  T14 has the same setup and its OneDrive clone synced cleanly to 2993050.
  RESOLVED 2026-11-14: Bryan rebooted E14; the OneDrive clone pulled
  clean to 2993050 (status 0), then to b1f3d38 with the rest of the fleet.
  The locked index file was cleared by the reboot. Docs for this saga
  committed as b1f3d38; all 7 clones (VM, L390, 3410, T14 Projects +
  OneDrive, E14 Projects + OneDrive) at b1f3d38, clean. (This STATE
  update itself uncommitted — rides with the next commit.)
- 3410 direct SSH CORRECTED 2026-11-14: direct works with explicit flags
  (verified login twice, incl. a pull over direct SSH); the old "refuses
  connection" note was stale — the failures were root ignoring ssh-config
  (no ProxyCommand). L390 jump is fallback only.
- VM SSH lesson (2026-11-14): exec runs as root, so ssh-config Host
  stanzas do NOT apply and /root/.ssh/known_hosts is ephemeral (wiped on
  VM restart — E14 host-key check failed mid-session after a restart).
  Always use explicit flags: -o ProxyCommand, -i key,
  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null. Direct
  3410 SSH resets; jump via L390.

# Hill-climb skill created (on demand, uncommitted) — 2026-11-11

- New skill `hill-climb` in `skills/hill-climb/SKILL.md`, based on Theo's
  `council` (t3dotgg/tstack), generalised from UI-only to any scoreable
  goal. Judges: agy (implementer first) + Codex (critic), 3rd judge
  deterministic. Defaults: threshold 9/10, max 8 rounds, plateau 2.
- Debian/Linux addendum in the skill: library clone paths resolve from library.json; `~/.agents/skills`, Python installer.
  Windows/OneDrive text preserved. Not added to `default-profile.toml`.
- INDEX.md regenerated (227 top-level, 244 definitions), router route
  added, validations pass: quick_validate, index check, text safety 0,
  resource audit Missing 0, installer dry-run 66 selected / 0 changes.
- v1.1.0 (2026-11-12): fallback ladder + walkthrough mode added per
  the user's concern — see skill. No scores invented, no silent substitution.
- v1.2.0 (2026-11-12): Codex audit verdict NEEDS FIXES 7.5/10, 4 blockers
  fixed (score aggregation, no-delegate self-review, fleet paths,
  walkthrough defaults). Report: ~/workspace/hill-climb-audit-codex-20261112.md.
- v1.3.0 (2026-11-12): de-fleeted per the user — no machine names, personal
  paths, provider balances, or "Bryan"/"fleet" in the skill. Grep clean.
- v1.4.0 (2026-11-12): agy audit NEEDS FIXES 8.0/10, all findings fixed
  (ONE model judge, not two; plateau = stop, escape is a user menu; git
  checkpoint/revert; baseline must be scored; drift every 3rd round;
  headless ban scoped to fleet work). Reports in ~/workspace.
- v1.5.0 (2026-11-12): Codex third check NEEDS FIXES 8.2/10, all fixed
  (baseline gate-first, drift re-anchor, degraded exception, scoped git
  commands, stale wording). Report: ~/workspace/hill-climb-audit-codex-v140-20261112.md.
- STATE.md / JOURNAL.md scrubbed 2026-11-12 (machine names → generic
  roles, personal paths removed, grep clean).
- Pulled 2026-11-12 15:42 SGT: HEAD 04477d5 (Bryan's hardening commit).
- Verified READY by Muse 2026-11-12 against the Codex third-check
  findings (all 5 fixed, full consistency sweep clean). Committed to
  main and pushed to origin/main on the user's word.

# Full fleet agent replication and dedicated root rollout — 2026-11-02

- Replicated all 66 profile skills to dedicated agent roots across the entire fleet:
  - Linux: symlinked 66 profile skills into `~/.claude/skills`, `~/.codex/skills`,
    and `~/.config/opencode/skills`, while preserving existing custom skills (`arkcli-*`)
    and internal system directories (`.system`).
  - Windows: copied 66 profile skills into `.cursor\skills` and `.config\opencode\skills`
    across all nodes, matching existing `.claude` and `.codex` roots.
- Updated `audit_fleet_skills.py` to audit dedicated OpenCode roots on Windows.
- Verified fleet-wide audit: all 4 online nodes show 100% OK (66/66) across all
  agents (Shared, Codex CLI, Claude Code, Cursor, OpenCode, Kiro).
- 0 broken skills, 0 missing profile skills across all nodes.

# Fleet skill verification and Windows Kiro junction repair — 2026-11-02

- Repaired Kiro skill discovery on Windows fleet nodes: replaced individual per-skill
  junctions with a single direct junction to the canonical OneDrive skills library
  (`OneDrive\01 SKILLS\.agents\skills`), matching OpenCode's architecture.
- Resolved NTFS "untrusted mount point" errors and corrupted reparse point issues.
- Filtered internal agent dot-directories (e.g. `.system`) in `audit_fleet_skills.py`
  and removed orphan empty directory under `.codex/skills`.
- Verified all online fleet nodes: 0 broken skills, 66/66 daily profile skills
  present and valid across OpenCode, Codex CLI, Claude Code, and Kiro.
- All repositories fast-forwarded to main (`aa5a527`).

# Fleet skill audit and generic verification — 2026-11-02

Delivered `fleet-skill-audit` skill and portable `scripts/audit_fleet_skills.py`.
Provides generic, fault-tolerant verification of agent discovery roots (OpenCode,
Codex, Claude Code, Kiro, Cursor, DeepSeek) without requiring agent logins.
Supports dynamic network discovery and anonymizes node names and IPs by default.
Registered in `skills/skill-router/SKILL.md` and updated `INDEX.md`.

# Add project-transfer skill — 2026-11-02

Delivered new canonical skill `project-transfer` under `skills/project-transfer/SKILL.md`.
Added to `default-profile.toml` (under core coding workflow) so machines running
`scripts/install_skills.py` deploy it automatically to configured agent roots.
Added discovery route in `skills/skill-router/SKILL.md` and regenerated `INDEX.md`.
Verified with `quick_validate.py`, `update_skill_index.py --check`, `audit_text_safety.py`
and `audit_skill_resources.py` (242 definitions, 1,682 Markdown files checked, 0 errors).
Fleet rollout complete: pushed to origin/main (`363ac71`), deployed and verified across
active Linux and Windows fleet nodes.

# ECC second wave — 2026-09-27

Skills delivered; live-agent pilot limitations remain recorded. Owner approved
proceeding with the reviewed second-wave plan:
API contracts, codebase onboarding, detailed ADRs, then a bounded orchestration
pilot and selective agent review lenses. Keep 65 daily skills; publish tested
source through main and OneDrive, with local copy verification on the Windows daily laptop. Other-machine
delivery continues under the owner's OneDrive assumption.

Implementation starts from 38b8bb5 and preserves the intervening privacy fix.
Four on-demand additions and CLI/routing integrations are delivered at e0479fc.
Three-OS CI 36302727616 passed: 99 Python cases with platform/browser skips,
plus four React and four Chromium cases per OS. Security jobs passed.
OneDrive: 2,256 tracked skill files match tested Git content after line-ending
normalization; its router matches plus the separately added local Orca row.
Windows daily laptop: 12 affected daily skills refreshed (12 files exact, one router merge
verified); all 65 profile entries resolve. Preserved 12 local Orca files and
their uncommitted state/index changes. Private machine inventory moved to its
ignored override. No new backup copies; temporary merge stash removed.
tmux/dmux launched in isolated Ubuntu WSL. Live Codex repair stopped no-progress
after a host command-runner failure; Claude handoff is blocked by expired OAuth.
No unattended schedules or blanket agent registration. See
docs/audits/2026-09-27-ecc-second-wave.md for pilot boundaries and delivery status.

# Orca skill installation — 2026-09-27

Owner requested four official Orca skills and preservation of the existing
library conventions. Added computer-use, orchestration, orca-per-workspace-env,
and orca-cli from stablyai/orca revision
90bae01db930f11951f75cb28f2da54c2b8b4b9b, with original discovery stubs,
MIT licenses and source hashes. All four version-matched guides respond in the
installed Orca runtime. Keep the 65-skill daily profile and existing links;
this is a targeted local addition, not a fleet refresh. Local Codex copies and
the existing shared-library links verify against the staged source hashes.
The 2,228 pre-existing skill files other than the router are unchanged; the
router adds one Orca route. All three registry files are byte-identical.
Metadata/index validation passes; text safety finds zero issues; the resource
audit checks 232 definitions, 1,664 Markdown files and 2,569 references with
zero missing references and zero stale exceptions. Other-machine delivery is
not verified. Preserve all prior handoff records below.

# ECC selective adoption — 2026-09-27

Completed and delivered. Owner approved four on-demand additions (verification-loop,
python-testing, react-testing, homelab-pihole-dns), browser-testing improvements,
skill evaluation/discovery improvements, and index/CI fixes. Keep the daily
profile at 65. Adapt from ECC revision e482e579415fde18357cafce70f177ae19fd7f03;
preserve attribution and validate all bundled dependencies.

Publish tested changes to main and the local OneDrive library. The owner's
latest instruction delegates other-machine delivery to OneDrive: do not retry
remote installs or claim a new remote verification. API contracts, onboarding,
ADRs, autonomous loops, tmux/dmux and the agent roster were research/plan only
in the first wave; the later second-wave authorization above supersedes that.

Four skills and three improvement batches are implemented; daily profile is 65.
Executable revision b9bb28c passed three-OS CI run 36298257310: 74 Python cases
on Linux/macOS, 58 on Windows with 16 POSIX skips, plus four React and four real
Chromium cases on each OS. Metadata/index/text/resource and security jobs pass.
Independent review repairs include malformed YAML handling, async assertions,
server cleanup and macOS loopback fixture startup.
See docs/audits/2026-09-27-ecc-adoption.md for exact failures and test boundaries.
See docs/plans/2026-09-27-ecc-second-wave.md for the three next skill proposals,
bounded loop/tmux/dmux pilot and all 68 upstream agent role mappings.

OneDrive source: 2,236 tracked skill files match tested content after existing
CRLF/LF normalization. Six affected daily copies on the Windows daily laptop: 41 files match source
SHA-256 exactly. Four new skills are readable on demand through the shared
library; no new backup copies were created. Automatic approval review blocked
cleanup of three temporary test folders. Earlier Chromium shutdown delays on the Windows daily laptop
remain recorded separately from the clean final Windows CI result.

First-wave next step was owner review; the owner has now approved proceeding.

# Installed skill refresh — 2026-09-27

The owner requested installed skills on the Windows work laptop, the Debian dev machine, and the Windows daily laptop be refreshed from
main. The 65-skill profile is unchanged. All seven registered agent roots pass
file verification against skill content from `74355d2`; 216 separate skill
copies were refreshed. After another successful installed-file verification,
the owner requested cleanup and all 213 old backup copies were removed.

- Windows work laptop: Codex, Claude, and Cursor pass. Debian dev machine: Codex and Claude pass. Windows daily laptop: Codex
  passes; Claude's existing shared-library link is preserved and verified.
- Full Git snapshots outside OneDrive pass all 2,219 skill-file hashes and the
  resource audit on each machine. All four handoff commands start successfully.
- the Windows daily laptop's missing Git object was recovered by a fresh fetch, and its OneDrive
  checkout was fast-forwarded without discarding local files. the Debian dev machine's eight
  shared handoff files match the updated source. the Windows work laptop's shared OneDrive copy
  returns cloud-read errors for the new files; do not mark that source synced.
- Installed-copy refreshes used the verified Git snapshot when OneDrive was
  delayed. No remote canonical folders or existing shared-library links were
  replaced. For the Windows work laptop handoffs, use the verified snapshot until OneDrive is fixed.
- Local evidence and snapshot on each machine:
  `~/Backups/2026-09-27/skills-main-refresh/`. The initiating machine retains
  the combined report and per-machine cleanup records. Working Git snapshots
  remain available; the obsolete copies under the separate `skills/` backup
  directory were deleted at the owner's request.

# Skill resource repair — 2026-09-26

Current task: complete. Repairs are published to main (`b2d1a70`, `8fde37a`).

- Audited 224 skill definitions and 1,631 baseline bundled Markdown files (plus
  the platform overview in independent review). Addressed 60
  findings; current scan checks 1,650 files and 2,551 references with zero unresolved
  missing references, 16 documented contextual exceptions, and zero stale entries.
- Implemented four handoff commands, supporting code and guides, six preset helper
  copies, and three portable Cavecrew prompts. Restored 12 MIT-licensed upstream
  resources and authored four local review guides. External Caveman/OpenCode setup
  remains a documented prerequisite rather than an implied installed capability.
- Verification: 53 local tests, 37 passed and 16 platform-specific skips, zero
  failures. Native PowerShell and Git Bash wrappers use fake CLIs; handoff tests
  use real disposable Git projects. Independent reviewers cleared the repairs;
  the handoff reviewer passed 14 extra assertions and eight alias-fix checks.
  CI found a temporary-directory alias bug on macOS/Windows, now fixed.
  Final CI passed all 53 tests on Linux/macOS and 37 with 16 POSIX skips on Windows:
  https://github.com/hongyime/theprawnskills/actions/runs/36224710255
- Report: `docs/audits/2026-09-26-skill-resources.md`; all baseline findings have
  dispositions in the adjacent JSON register. Resource audit and three-OS CI pass.
  Existing X-drive and OneDrive checkouts and machine installations are preserved.

# Portfolio review — 2026-09-10

Installer/profile source review and both core Python syntax checks passed. The current Windows suite ran 22 tests: nine passed and thirteen Unix symlink cases were skipped. Verification used temporary homes, including install/update/repeat checks for the actual 65-skill profile; installed agent directories were not changed. The repository still has the `no-config-sync` topic. Keep its library and current opt-out intact.

The older remote-machine rollout notes below remain unresolved; this portfolio check did not retry remote installation or validate every referenced provider tool. Current source is a local skill library/installer, not a Supabase or Vercel application.

# Daily visual explanations

- Published `visual-explainer` in commit `254f727`: restrained dark/cyan style,
  proactive visuals even for short explanations, and visual overview -> details
  -> next steps. Shared assets own the style; Postplan and both routers use it.
- Library now contains 207 top-level skills, 217 skill definitions, and 65 daily
  selections. All 2,165 original skill files remain; no skills were deleted.
- The OneDrive source checkout received the new skill through Git. The current
  Windows machine's Codex, Claude, and Cursor copies match the four selected
  sources; each installed daily profile contains 65 skills. Previous copies
  were archived in dated backups outside OneDrive.
- Remote rollout is incomplete: one registered machine has not received the new
  OneDrive source; the other times out over SSH. Neither remote installation
  was changed. Retry the documented selected-skill sync after source delivery
  and connectivity recover. Do not overwrite remote canonical folders.
- Fixed Windows SSH helper transport using SCP plus SHA256 verification instead
  of waiting for stdin EOF. Remote execution reports missing source cleanly;
  local preview, repeat application, and backup preservation were verified.
- Native Windows and fresh-checkout Windows/macOS/Linux installation tests pass:
  https://github.com/hongyime/theprawnskills/actions/runs/34305986010
  Windows runs 9 tests and skips 13 POSIX cases; macOS/Linux run all 22.
- HTML structure, desktop/mobile rendering, switcher, no-JavaScript fallback,
  and absence of external runtime resources were checked. Axe reported no
  violations with SVG contrast requiring manual review. Three Mermaid examples
  rendered; a separate class-example browser check encountered local launch issues.
- Standalone machines use Git pull plus the Python installer. OneDrive carries
  shared source files and the Windows helper refreshes separate agent copies.
  No scheduled background updater was installed. README contains setup, update,
  and Codex handoff instructions for Windows, macOS, and Linux.

## Repository protection and earlier work

- Recovery `62cbd1f` restored the original library after organisation cleanup.
  Preserve the GitHub topic `no-config-sync`; never run that cleanup here.
- Standalone installation on all three operating systems was added in `6d6b0d9`.
  Original management variants remain in platforms/linux for link compatibility.
- Both local checkout remotes point to hongyime/theprawnskills. Repository
  visibility is unchanged; changing it requires a matching sourcerepo override.
- Earlier Postplan audit found seven direct skill references and a reverse
  reference to repo-standardization. This task adds visual-explainer integration.
- JOURNAL.md and Git history retain the earlier migration and audit decisions.

---
## 2026-09-16 - baseline review batch-a
- Health: main HEAD 08f16d5 after fast-forward. git status clean.
- Open PRs: #5 (Dependabot: trufflehog action bump). Open issues: 0.
- pnpm audit: 26 vulns (1 critical vitest <3.2.6, 15 high, 9 moderate, 1 low) - ALL in dev-only paths (vitest tree, esbuild). Runtime deps (graphology*) clean. Critical vitest advisory GHSA-5xrq-8626-4rwp requires UI server exposed to attacker; not applicable in CI/local test runs.
- Semver ranges (^3.1.0) already permit patched vitest >=3.2.6; lockfile is stale. Deferred: lockfile is sourcerepo-managed (last touched by post-recovery snapshot 5c8ef90). Update should flow through sourcerepo, not this target.
- Free-tier surface: none. Skill library, no Vercel/Supabase.
- Next safe steps: file issue in sourcerepo to refresh pnpm-lock.yaml (bumps vitest, postcss/nanoid, esbuild transitives).

## Privacy-safe machine examples - 2026-09-27

Keep machine-specific inventory in an ignored private override, with disabled public examples and packaging exclusions. Preserve the current skill catalog, profile and newer provider-auth instructions. No fleet installation or registry-based synchronization ran.

## Current task — 2026-11-18

Extended `project-transfer` with git-history mining, no-ownership mode, and a
fluid store/target split (`644481b`). New private repo `hongyime/theprawnlearnings`
(one folder per source repo, markdown PACKs + consolidated lessons.md).
Trial Phase 1 harvest on `bchuminx/healthkaki-pov`: remote is unreachable from
GitHub (repository not found via `gh` + `ls-remote`, VM and L390) — the L390
clone (1341 commits, 56 branches) is the only copy; harvest ran clone-only,
no PRs/issues. PACK at `~/workspace/healthkaki-pov-lessons.md` (11 lessons,
3 dropped), awaiting Bryan's review before filing to theprawnlearnings.
Fleet all at `644481b`; project-transfer copied to T14/E14 codex roots
(hash match both).

<!-- MOLT_AUTO_START -->
## Auto State

- Updated: 2026-11-12 15:13:23 +08:00
- Machine: Windows daily laptop
- Harness: codex
- Event: session-start
- Branch: main
- HEAD: 6e61c4a
- Dirty files: 0
- Resume hint: Read .agents/STATE.md, then the latest file in .agents/handoffs/ if present.
<!-- MOLT_AUTO_END -->
