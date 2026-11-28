---
name: skill-router
description: >-
  When to read: a task may need a non-installed skill, or the user asks which skill to use. Use
  for: routing user requests to on-demand skills in the Git clone library. Does: searches the
  clone by name and description, picks the smallest relevant set, and reads each selected
  SKILL.md fully; covers media, documents, presentations, writing, cloud platforms, agent setup,
  skill creation, and unfamiliar tooling.
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Skill Router

Use this skill to find and load on-demand skills without installing the
whole library into every agent session.

Debian/Linux variant (curated shortlist, not a mirror): `../../platforms/linux/skills/skill-router/SKILL.md`.

## Source of Truth

Canonical skill library: the Git clone. On this VM: `~/workspace/theprawnskills`
(repo `hongyime/theprawnskills`). On any machine, read
`~/.config/theprawnskills/library.json` and use its `library` path as the
repository root. If absent and this skill is a symlink, resolve it to locate
the clone. For a copied installation, inspect the intended clone and repair
the pointer through the installer; the installed copy is not the library.
The repo root contains `default-profile.toml` and `skills/`.

Skill file convention:

```text
<clone>/skills/<kebab-name>/SKILL.md
```

Legacy Windows-only mirror (not canonical): some Windows machines keep a
OneDrive library at `<user-home>\OneDrive\01 SKILLS\.agents\skills`. It is a
mirror for those machines only. The Git clone is the source of truth on every
platform; if the mirror and the clone disagree, the clone wins.

Linux portable variant (curated shortlist, not a mirror):
`platforms/linux/skills/skill-router/SKILL.md` — the 7 standalone management
skills only. Prefer a standalone variant when present.

## Fleet Roles — Flat Index (One Level)

One routing level, no hierarchy, no sub-routers. Role → flat index → `SKILL.md`.
The flat index is `INDEX.md` at the repo root (all 258 top-level skills, purpose
+ DAILY/ON-DEMAND status). Each role below lists only its core skills; everything
else stays on-demand via the flat index — search it, do not guess, do not
build a second router per role.

| Role | Machine / agent | Core skills (load these first) | Everything else |
|---|---|---|---|
| Muse orchestrator | VM, Muse | `skill-router`, `cross-harness-state`, `session-handoff`, `verification-loop`, `to-spec`, `to-tickets`, `check`, `skill-judge`, `project-transfer`, `competitive-upgrade`, `fleet-skill-audit`, `caveman` | Flat index (`INDEX.md`) |
| Codex implementer | Fleet, Codex | `build`, `check`, `bug-diagnosis`, `systematic-debugging`, `to-spec`, `to-tickets`, `verification-loop`, `requesting-code-review`, `refactor`, `tdd`, `python-testing`, `react-testing`, `webapp-testing`, `skill-cleanup` | Flat index (`INDEX.md`) |
| agy challenger | Fleet, agy | `requesting-code-review`, `interrogate`, `blast-radius`, `skill-judge`, `hill-climb`, `show-me-your-work`, `figure-it-out`, `skill-reviewer` | Flat index (`INDEX.md`) |
| opencode (DeepSeek-only) | Fleet, opencode | `opencode-cli`, `build`, `check`, `verification-loop`, `bug-diagnosis`, `skill-router` | Flat index (`INDEX.md`) |
| Herdr pane driver | Fleet, any agent in a pane | `cli-agent-router`, `bounded-agent-loop`, `cross-harness-state`, `session-handoff`, `skill-router`, `fleet-skill-audit` | Flat index (`INDEX.md`) |

Roles come from `agents.toml` (claude, cursor, codex, vscode, opencode) plus
the fleet roles in `AGENTS.md` (Muse orchestrator, agy challenger, Herdr pane
driver). `machines.toml` in this repo is an example only — real devices live
in ignored `machines.local.toml`; no role is missing from it, so neither file
is edited by this spec.

## Routing Workflow

When the user's request may match an on-demand skill:

1. Search canonical skill names and frontmatter descriptions.
2. Pick the smallest set of relevant skills.
3. Open and read each selected `SKILL.md` fully before using it.
4. If the selected skill links to task-specific references, read only the
   relevant referenced files.
5. If no skill clearly fits, continue normally and mention that no exact skill
   matched.

Search the clone with `rg` (Linux/macOS) or `rg` / PowerShell `Select-String`
(Windows). Never search the OneDrive mirror as the source of truth.

```bash
# <clone> = repo root from library.json, e.g. ~/workspace/theprawnskills
rg -n "deck|presentation|pptx|slides|pdf|image|video|azure|supabase|vercel" "<clone>/skills" -g "SKILL.md"
rg -n --no-heading "description:" "<clone>/skills" -g "SKILL.md" | rg -i "<keyword>"
```

On Windows, the same `rg` command works from PowerShell or cmd; if `rg` is
absent, use `Select-String -Path "<clone>\skills\*\SKILL.md" -Pattern "<keyword>"`.

Do not read secret files while routing. Skill folders should normally contain
instructions, references, scripts, assets, templates, and examples, not secrets.

## Common Routes

Use these as starting points, then verify by reading the actual `SKILL.md`.

| User intent | Candidate skills |
|---|---|
| API compatibility, serialized responses, provider/consumer contracts | `api-contracts`; `openapi-to-typescript` for generated types |
| Understand an unfamiliar repository and trace its existing behavior | `codebase-onboarding`; `codebase-design` for choosing changes |
| Record or find an architectural decision and its rationale | `architecture-decision-records`; `cross-harness-state` for current task state |
| Bounded repeated repair, agent roles, terminal/worktree coordination | `bounded-agent-loop`, `cli-agent-router` |
| Hill climb a scoreable goal, iterate until threshold or plateau | `hill-climb`, `bounded-agent-loop`, `skill-judge` |
| Create a brand-new local skill | `skill-create`, `skill-authoring`, `skill-creator` |
| Add a skill from GitHub, link, pasted text, or tool docs | `skill-add`, `skill-create` |
| Update one skill or improve skills from coding practice | `skill-update`, `skill-authoring` |
| Clean up, prune, dedupe, or reduce skill context | `skill-cleanup`, `skill-remove` |
| Remove or retire a skill | `skill-remove`, `skill-cleanup` |
| Score, review or audit skill quality | `skill-judge`, `skill-reviewer`, `skill-authoring` |
| Audit fleet machine skill discovery, health, and agent roots | `fleet-skill-audit`, `skill-judge` |
| Find a skill or decide what applies | `skill-router`, `find-skills`, `skill-authoring`, `related-skill` |
| Coding, refactor, review, testing | `refactor`, `requesting-code-review`, `systematic-debugging`, `webapp-testing` |
| Verify a completed change, ready for review, completion evidence | `verification-loop`; `check` specifically for SPEC drift |
| Review a finished project with the user through user stories: map what users can actually do, find edge cases, reconcile the mental model with the code | `user-stories` |
| Polish a somewhat-done repo end to end: map, challenge, fix, improve the frontend, verify | `polish-repo`; `user-stories` for the mapping step alone, `interrogate` for the challenge step alone |
| Adversarial review: stress-test a change, prove it by running it, find blind spots | `interrogate`, `blast-radius`, `figure-it-out`, `show-me-your-work` |
| Understand why and how: rationale for a design, how something works, teach it | `why`, `how`, `teach` |
| Stop repeating the same mistake: diagnose a recurring error pattern and fix the cause | `correct` |
| Write tests by behavior first, regression test before the fix | `tdd` |
| Sharpen writing, strip slop, structure state machines and technical docs | `unslop`, `sharpen`, `technical-writing`, `statechart` |
| Reflect on a session, write down what worked, harvest a reusable lesson | `reflect` |
| Check connector health, which connectors need re-login | `connector-health` |
| Find the cheapest flight for a route and date | `flight-search` |
| Record a correction or mistake the same day, keep the diary/learnings loop | `diary-learnings` |
| Python fixtures, mocks, boundary cases, unittest or pytest | `python-testing`; `python-sdk` specifically for inference.sh |
| React component, hook or form tests | `react-testing`; `webapp-testing` for real browser flows |
| React or TypeScript engineering patterns | `react-dev`, `react-useeffect`, `typescript-advanced-types`, `vercel-composition-patterns`, `vercel-react-view-transitions`; `vercel-react-native-skills` for React Native |
| Agent-facing UI components: chat, tools, widgets | `agent-ui`, `chat-ui`, `tools-ui`, `widgets-ui`; `web-artifacts-builder` for multi-component HTML artifacts |
| Database schema, indexes, migrations | `database-schema-designer`; `supabase-postgres-best-practices` for Postgres specifics; `project-db-autodetect` to detect local settings |
| Application and API security practices | `security-best-practices`; `mcp-security-hygiene` for MCP configuration |
| Dependency updates and vulnerability triage | `dependency-updater` |
| Pi-hole DNS, Docker resolver health, Tailscale DNS routing | `homelab-pihole-dns`, `docker-expert` |
| VirtualBox guest VM access, guestcontrol, host-only networking, guest shell traps | `virtualbox-guest-access` |
| New machine setup, fresh install, replicate or move an agent environment | `agent-machine-bootstrap`; `virtualbox-guest-access` for VM access, `opencode-bedrock-config` for provider auth |
| Two accounts of the same agent CLI on one machine, wrong-account drift, WSL versus host identity | `agent-account-isolation` |
| Bug investigation and root cause | `bug-diagnosis`, `systematic-debugging`, `backprop` |
| Merge conflicts and git surgery | `merge-conflict-resolution`, `commit-work`, `git-commit` |
| Take a PR to merged: autonomous full send, merge-ready full stop, file a PR, take over someone else's PR, babysit CI and reviews, modernize a stale PR, leave review comments | `full-send`, `full-stop`, `file-pr`, `takeover`, `babysit-pr`, `modernize`, `leaving-pr-comments` |
| Spec writing (one clear feature) | `to-spec`, `spec`, `build`, `check` |
| Ticket breakdown / work planning | `to-tickets`, `to-spec`, `postplan-upload` |
| Explain visually, diagrams, flows, UML/C4, comparisons, HTML reports | `visual-explainer`; `postplan-upload` for hosted delivery |
| Prototypes / feasibility spikes | `prototype`, `wayfinder` |
| Large ambiguous initiatives | `wayfinder`, `domain-modeling`, `codebase-design` |
| Guided step-by-step setup | `wizard`, `wrangler` |
| Session continuity across agents | `cross-harness-state`, `session-handoff`, `molt` |
| Transfer lessons, harvest rules or reuse workflows from another project | `project-transfer`; `cross-harness-state` for active sessions |
| Repo standardization and compliance | `repo-standardization`, `shell` |
| Compare repo with competitors / market upgrades | `competitive-upgrade`, `competitor-teardown` |
| Reduce token usage, compress output or memory files | `caveman`, `caveman-compress`, `caveman-help`; `caveman-commit` for commits, `caveman-review` for PR feedback, `caveman-stats` for usage, `cavecrew` for compressed subagents |
| Build or repair an MCP server or MCP config | `mcp-builder`; `mcp-health-repair` for failures, `mcp-security-hygiene` for secrets, `postgres-mcp-onboarding` for Postgres MCP |
| Web or frontend design | `frontend-design`, `web-design-guidelines`, `shadcn`, `impeccable`; `landing-page-design` for conversion pages, `email-design` for email |
| Anti-slop company/landing frontend: plain copy, one system, taste gate | `design-taste-frontend`; `impeccable` for app UI and design systems |
| Accessibility: keyboard, focus, ARIA, forms, motion, zoom vs WCAG 2.2 | `better-accessibility` |
| Stress-test one component under worst-case content on a throwaway page | `break` |
| Lazy senior-dev review: repo audit, change review, tech-debt ledger | `ponytail`, `ponytail-review`, `ponytail-audit`, `ponytail-debt`; `ponytail-gain` for benchmark scores, `ponytail-help` for the reference card |
| Brand, theme, palette or visual identity | `brand-guidelines`, `theme-factory`, `logo-design-guide`, `canvas-design` |
| Static visual assets: covers, icons, screenshots, social images | `book-cover-design`, `app-store-screenshots`, `og-image-design`, `character-design-sheet`, `slack-gif-creator`, `algorithmic-art` |
| Charts, dashboards and data storytelling | `data-visualization`; `pitch-deck-visuals` for investor decks |
| Web performance and Core Web Vitals | `web-perf` |
| Cloudflare and Workers | `cloudflare`, `wrangler`, `workers-best-practices`, `durable-objects`, `agents-sdk`, `turnstile-spin`; `cloudflare-email-service` for email, `sandbox-sdk` for sandboxed execution |
| Cloudflare Zero Trust / SASE | `cloudflare-one`; `cloudflare-one-migrations` for migrating off another vendor |
| Supabase or Postgres | `supabase`, `supabase-postgres-best-practices`, `postgres-mcp-onboarding` |
| Vercel | `deploy-to-vercel`, `vercel-react-best-practices`, `vercel-cli-with-tokens` |
| Documents, PDFs, spreadsheets, decks | `docx`, `pdf`, `xlsx`, `pptx`; `pitch-deck-visuals` for investor decks |
| Writing and communication | `technical-blog-writing`, `press-release-writing`, `case-study-writing`, `newsletter-curation`; `internal-comms` for internal updates, `doc-coauthoring` for structured docs, `product-changelog` for release notes |
| Marketing and launch content | `seo-content-brief`, `product-hunt-launch`, `linkedin-content`, `content-repurposing`; `customer-persona` for audience research |
| Prompt engineering and model prompting technique | `prompt-engineering`; `video-prompting-guide` for video models |
| Image generation or editing | `ai-image-generation`, `gpt-image`, `flux-image`, `background-removal`, `image-upscaling`, `product-photography`; model-specific: `nano-banana`, `p-image` |
| Video generation | `image-to-video`, `google-veo`, `seedance`, `happyhorse`, `p-video`, `remotion-render`; `video-prompting-guide` for prompting, `video-ad-specs` for platform specs, `storyboard-creation` and `explainer-video-guide` for planning |
| Talking-head and avatar video | `ai-avatar-video`, `talking-head-production`, `p-video-avatar` |
| Speech, voice and music | `text-to-speech`, `speech-to-text`, `ai-music-generation`, `dialogue-audio`, `ai-podcast-creation`; ElevenLabs-specific: `elevenlabs-tts`, `elevenlabs-stt`, `elevenlabs-dialogue`, `elevenlabs-dubbing`, `elevenlabs-music`, `elevenlabs-sound-effects`, `elevenlabs-voice-changer`, `elevenlabs-voice-isolator` |
| Multi-step AI content or automation pipelines | `ai-content-pipeline`, `ai-automation-workflows`, `ai-rag-pipeline` |
| inference.sh platform: run apps, build apps, SDKs | `infsh-cli`, `building-inferencesh-apps`, `python-sdk`, `javascript-sdk`, `python-executor`, `llm-models` |
| Social content | `social-media-carousel`, `twitter-thread-creation`, `youtube-thumbnail-design`; `twitter-automation` for posting via API |
| Web search, scraping and page extraction | `web-search`, `agent-browser` |
| Claude API, model ids, pricing, tool use | `claude-api` |
| Agent tooling and delegation | `cli-agent-router`, `claude-code-cli`, `opencode-cli`, `codex`, `agent-browser` |
| OpenCode Bedrock provider auth, region pinning, per-agent model override | `opencode-bedrock-config` |

## Maintenance Rules

When adding, deleting, renaming, pruning, or auditing skills, also use
`skill-authoring`.

After skill library changes:

1. Ensure each new skill lives at `skills/<kebab-name>/SKILL.md`.
2. Update `default-profile.toml` if default-installed membership changed.
3. Update `INDEX.md` so installed/on-demand status stays accurate.
4. Update this router only when a new skill changes the common routing table or
   a renamed/deleted skill appears in the table.
5. Install this router into the default agent roots so future agents can find
   on-demand skills.

Do not run:

```powershell
dotagents sync
```

Use `dotagents install` only when `agents.toml` is known to be safe and the user
explicitly wants the manifest-installed defaults refreshed.

## Default Install Strategy

Keep default-installed skills lean:

- Always install this `skill-router`.
- Always install `skill-create`, `skill-add`, `skill-update`, `skill-cleanup`,
  and `skill-remove`.
- Always install `visual-explainer` and `postplan-upload`: use consistent
  dark/cyan HTML whenever a visual helps, even for short explanations. Use
  visual overview -> details -> next steps; publish when hosting is authorized.
- Keep essential coding, review, debugging, Cloudflare, and local setup skills
  installed when the user wants automatic discovery.
- Leave media, writing, document, presentation, Supabase, and Vercel
  skills on demand unless the user asks to make one default again.

**The Postplan rule (standing, Bryan 2026-11-22):** whenever a covered skill finishes a substantial Markdown plan, spec, report, review, or design document, also publish it as a hosted page — render with `visual-explainer`'s template, upload with `postplan-upload`, and return the Postplan URL next to the local path. Auto-publish by default; gated skills ask first (gated list lives in `postplan-upload`). Re-upload updates from the same machine that created the draft — another machine forks a new URL.

Use `default-profile.toml` as the source of truth for default profile
membership. When a new CLI agent is installed, add its skill root to
`machines.toml` and apply the default profile.

Do not delete on-demand skills just because they are not installed.

Machine-specific values in this document use privacy placeholders.
