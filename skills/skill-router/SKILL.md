---
name: skill-router
description: >-
  Route user requests to on-demand skills in the OneDrive canonical skill
  library. Use when a task sounds like it may need a non-installed skill, when
  the user asks which skill to use, or when work involves media, documents,
  presentations, writing, cloud platforms, agent setup, skill creation, or
  unfamiliar specialized tooling.
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Claude, Cursor, OpenCode on Windows"
---

# Skill Router

Use this skill to find and load on-demand skills without installing the
whole library into every agent session.

## Source of Truth

Canonical skill library:

```text
<user-home>\OneDrive\01 SKILLS\.agents\skills
```

Skill file convention:

```text
<user-home>\OneDrive\01 SKILLS\.agents\skills\<kebab-name>\SKILL.md
```

Installed agent roots are only exposure targets. The canonical OneDrive
`skills/` folder is the durable library.

## Routing Workflow

When the user's request may match an on-demand skill:

1. Search canonical skill names and frontmatter descriptions.
2. Pick the smallest set of relevant skills.
3. Open and read each selected `SKILL.md` fully before using it.
4. If the selected skill links to task-specific references, read only the
   relevant referenced files.
5. If no skill clearly fits, continue normally and mention that no exact skill
   matched.

Use PowerShell-compatible search from this machine:

```powershell
$root = "<user-home>\OneDrive\01 SKILLS\.agents\skills"
Get-ChildItem -LiteralPath $root -Directory |
  ForEach-Object {
    $skill = Join-Path $_.FullName "SKILL.md"
    if (Test-Path -LiteralPath $skill) {
      Select-String -LiteralPath $skill -Pattern "description:|name:|# " -Context 0,2
    }
  }
```

Prefer `rg` for targeted text search:

```powershell
rg -n "deck|presentation|pptx|slides|pdf|image|video|azure|supabase|vercel" "<user-home>\OneDrive\01 SKILLS\.agents\skills" -g "SKILL.md"
```

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
| Create a brand-new local skill | `skill-create`, `skill-authoring`, `skill-creator` |
| Add a skill from GitHub, link, pasted text, or tool docs | `skill-add`, `skill-create` |
| Update one skill or improve skills from coding practice | `skill-update`, `skill-authoring` |
| Clean up, prune, dedupe, or reduce skill context | `skill-cleanup`, `skill-remove` |
| Remove or retire a skill | `skill-remove`, `skill-cleanup` |
| Score, review or audit skill quality | `skill-judge`, `skill-reviewer`, `skill-authoring` |
| Find a skill or decide what applies | `skill-router`, `find-skills`, `skill-authoring`, `related-skill` |
| Coding, refactor, review, testing | `refactor`, `requesting-code-review`, `systematic-debugging`, `webapp-testing` |
| Verify a completed change, ready for review, completion evidence | `verification-loop`; `check` specifically for SPEC drift |
| Python fixtures, mocks, boundary cases, unittest or pytest | `python-testing`; `python-sdk` specifically for inference.sh |
| React component, hook or form tests | `react-testing`; `webapp-testing` for real browser flows |
| React or TypeScript engineering patterns | `react-dev`, `react-useeffect`, `typescript-advanced-types`, `vercel-composition-patterns`, `vercel-react-view-transitions`; `vercel-react-native-skills` for React Native |
| Agent-facing UI components: chat, tools, widgets | `agent-ui`, `chat-ui`, `tools-ui`, `widgets-ui`; `web-artifacts-builder` for multi-component HTML artifacts |
| Database schema, indexes, migrations | `database-schema-designer`; `supabase-postgres-best-practices` for Postgres specifics; `project-db-autodetect` to detect local settings |
| Application and API security practices | `security-best-practices`; `mcp-security-hygiene` for MCP configuration |
| Dependency updates and vulnerability triage | `dependency-updater` |
| Pi-hole DNS, Docker resolver health, Tailscale DNS routing | `homelab-pihole-dns`, `docker-expert` |
| VirtualBox guest VM access, guestcontrol, host-only networking, guest shell traps | `virtualbox-guest-access` |
| Android device or emulator control over adb | `orca-emulator-android` |
| New machine setup, fresh install, replicate or move an agent environment | `agent-machine-bootstrap`; `virtualbox-guest-access` for VM access, `opencode-bedrock-config` for provider auth |
| Bug investigation and root cause | `bug-diagnosis`, `systematic-debugging`, `backprop` |
| Merge conflicts and git surgery | `merge-conflict-resolution`, `commit-work`, `git-commit` |
| Spec writing (one clear feature) | `to-spec`, `spec`, `build`, `check` |
| Ticket breakdown / work planning | `to-tickets`, `to-spec`, `postplan-upload` |
| Explain visually, diagrams, flows, UML/C4, comparisons, HTML reports | `visual-explainer`; `postplan-upload` for hosted delivery |
| Prototypes / feasibility spikes | `prototype`, `wayfinder` |
| Large ambiguous initiatives | `wayfinder`, `domain-modeling`, `codebase-design` |
| Guided step-by-step setup | `wizard`, `azure-prepare`, `wrangler` |
| Session continuity across agents | `cross-harness-state`, `session-handoff` |
| Repo standardization and compliance | `repo-standardization` |
| Compare repo with competitors / market upgrades | `competitive-upgrade`, `competitor-teardown` |
| Reduce token usage, compress output or memory files | `caveman`, `caveman-compress`, `caveman-help`; `caveman-commit` for commits, `caveman-review` for PR feedback, `caveman-stats` for usage, `cavecrew` for compressed subagents |
| Build or repair an MCP server or MCP config | `mcp-builder`; `mcp-health-repair` for failures, `mcp-security-hygiene` for secrets, `postgres-mcp-onboarding` for Postgres MCP |
| Web or frontend design | `frontend-design`, `web-design-guidelines`, `shadcn`, `impeccable`; `landing-page-design` for conversion pages, `email-design` for email |
| Brand, theme, palette or visual identity | `brand-guidelines`, `theme-factory`, `logo-design-guide`, `canvas-design` |
| Static visual assets: covers, icons, screenshots, social images | `book-cover-design`, `app-store-screenshots`, `og-image-design`, `character-design-sheet`, `slack-gif-creator`, `algorithmic-art` |
| Charts, dashboards and data storytelling | `data-visualization`; `pitch-deck-visuals` for investor decks |
| Web performance and Core Web Vitals | `web-perf` |
| Cloudflare and Workers | `cloudflare`, `wrangler`, `workers-best-practices`, `durable-objects`, `agents-sdk`, `turnstile-spin`; `cloudflare-email-service` for email, `sandbox-sdk` for sandboxed execution |
| Cloudflare Zero Trust / SASE | `cloudflare-one`; `cloudflare-one-migrations` for migrating off another vendor |
| Azure: apps, deploy, diagnose, cost | `azure-prepare`, `azure-deploy`, `azure-validate`, `azure-diagnostics`, `azure-cost`, `azure-ai`, `microsoft-foundry` |
| Azure: infrastructure, compute, storage, quotas, inventory | `azure-enterprise-infra-planner`, `azure-compute`, `azure-storage`, `azure-quotas`, `azure-resource-lookup`, `azure-resource-visualizer`, `azure-upgrade`, `azure-cloud-migrate`, `azure-compliance` |
| Azure: Kubernetes and AI gateway | `azure-kubernetes`, `azure-kubernetes-automatic-readiness`, `airunway-aks-setup`, `azure-aigateway` |
| Azure: data, messaging, telemetry | `azure-kusto`, `azure-messaging`, `appinsights-instrumentation` |
| Microsoft Entra identity and app registration | `entra-app-registration`; `entra-agent-id` for agent identities |
| Azure OpenAI model deployment and capacity | `deploy-model`, `preset` |
| Supabase or Postgres | `supabase`, `supabase-postgres-best-practices`, `postgres-mcp-onboarding` |
| Vercel | `deploy-to-vercel`, `vercel-react-best-practices`, `vercel-cli-with-tokens` |
| Documents, PDFs, spreadsheets, decks | `docx`, `pdf`, `xlsx`, `pptx`; `pitch-deck-visuals` for investor decks |
| Writing and communication | `technical-blog-writing`, `press-release-writing`, `case-study-writing`, `newsletter-curation`; `internal-comms` for internal updates, `doc-coauthoring` for structured docs, `product-changelog` for release notes |
| Marketing and launch content | `seo-content-brief`, `product-hunt-launch`, `linkedin-content`, `content-repurposing`; `customer-persona` for audience research |
| Prompt engineering and model prompting technique | `prompt-engineering`; `video-prompting-guide` for video models |
| Image generation or editing | `ai-image-generation`, `gpt-image`, `flux-image`, `background-removal`, `image-upscaling`, `product-photography`, `ai-product-photography`; model-specific: `nano-banana`, `nano-banana-2`, `qwen-image-2`, `qwen-image-2-pro`, `p-image` |
| Video generation | `image-to-video`, `google-veo`, `seedance`, `happyhorse`, `p-video`, `remotion-render`; `video-prompting-guide` for prompting, `video-ad-specs` for platform specs, `storyboard-creation` and `explainer-video-guide` for planning |
| Talking-head and avatar video | `ai-avatar-video`, `talking-head-production`, `p-video-avatar` |
| Speech, voice and music | `text-to-speech`, `speech-to-text`, `ai-voice-cloning`, `ai-music-generation`, `dialogue-audio`, `ai-podcast-creation`; ElevenLabs-specific: `elevenlabs-tts`, `elevenlabs-stt`, `elevenlabs-dialogue`, `elevenlabs-dubbing`, `elevenlabs-music`, `elevenlabs-sound-effects`, `elevenlabs-voice-changer`, `elevenlabs-voice-isolator` |
| Multi-step AI content or automation pipelines | `ai-content-pipeline`, `ai-automation-workflows`, `ai-rag-pipeline`, `ai-marketing-videos` |
| inference.sh platform: run apps, build apps, SDKs | `infsh-cli`, `agent-tools`, `building-inferencesh-apps`, `python-sdk`, `javascript-sdk`, `python-executor`, `llm-models` |
| Social content | `ai-social-media-content`, `social-media-carousel`, `twitter-thread-creation`, `youtube-thumbnail-design`; `twitter-automation` for posting via API |
| Web search, scraping and page extraction | `web-search`, `web-to-markdown`, `agent-browser` |
| Claude API, model ids, pricing, tool use | `claude-api` |
| Agent tooling and delegation | `cli-agent-router`, `claude-code-cli`, `opencode-cli`, `codex`, `agent-browser` |
| OpenCode Bedrock provider auth, region pinning, per-agent model override | `opencode-bedrock-config` |
| Orca ADE worktrees, terminals, handoffs, or embedded browser | `orca-cli`; `orchestration` for supervised workers; `orca-per-workspace-env` for environment recipes; `computer-use` only for visible desktop GUI tasks |

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
- Leave media, writing, document, presentation, Azure, Supabase, and Vercel
  skills on demand unless the user asks to make one default again.

Use `default-profile.toml` as the source of truth for default profile
membership. When a new CLI agent is installed, add its skill root to
`machines.toml` and apply the default profile.

Do not delete on-demand skills just because they are not installed.

Machine-specific values in this document use privacy placeholders.
