---
name: related-skill
description: >-
  When to read: the user asks to install an inference.sh skill that is not in this library yet.
  Use for: installing complementary inference.sh skills from the external registry. Does: finds
  and installs the external skill. For skills already in this library use skill-router; to add
  an external skill to the library permanently, propose it via skill-creator instead.
allowed-tools: Bash(npx skills *)
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---


# Related Skills Discovery

Find and install complementary inference.sh skills to expand your AI agent's capabilities.

Skills already in this library are installed via `../../scripts/install_skills.py` — do NOT install them with `npx skills add`. Use the commands below only for inference.sh skills that are not in this library yet.

![Related Skills Discovery](https://cloud.inference.sh/app/files/u/4mg21r6ta37mpaz6ktzwtt8krr/01kgvftjwhby36trvaj66bwzcf.jpeg)

## Quick Start

```bash
# Search for skills
npx skills search "inference-sh image generation"

# List available skills
npx skills list inference-sh/skills

# Install a skill
npx skills add inference-sh/skills@ai-image-generation
```

## Available Skill Categories

| Category | Skill | Description |
|----------|-------|-------------|
| **AI Models** | `llm-models` | Access all LLM models |
| **Images** | `ai-image-generation` | Generate images with AI |
| **Images** | `flux-image` | FLUX image models |
| **Images** | `image-upscaling` | Upscale and enhance images |
| **Images** | `background-removal` | Remove backgrounds from images |
| **Video** | `ai-avatar-video` | Create avatar videos |
| **Video** | `google-veo` | Google Veo video generation |
| **Audio** | `text-to-speech` | Convert text to speech |
| **Audio** | `speech-to-text` | Transcribe audio to text |
| **Audio** | `ai-music-generation` | Generate music with AI |
| **Search** | `web-search` | Search the web with AI |
| **Social** | `twitter-automation` | Automate Twitter/X actions |
| **Full** | `inference-sh` | All apps in one skill |

## Install by Category

### Media Generation
```bash
npx skills add inference-sh/skills@ai-image-generation
npx skills add inference-sh/skills@google-veo
npx skills add inference-sh/skills@seedance
npx skills add inference-sh/skills@ai-music-generation
```

### Image Processing
```bash
npx skills add inference-sh/skills@image-upscaling
npx skills add inference-sh/skills@background-removal
npx skills add inference-sh/skills@flux-image
```

### Audio Processing
```bash
npx skills add inference-sh/skills@text-to-speech
npx skills add inference-sh/skills@speech-to-text
```

### Research & Automation
```bash
npx skills add inference-sh/skills@web-search
npx skills add inference-sh/skills@twitter-automation
```

### Everything at Once
```bash
# Install the full platform skill with all apps
npx skills add inference-sh/skills@infsh-cli
```

## Skill Combinations

### Research Agent
```bash
npx skills add inference-sh/skills@web-search
npx skills add inference-sh/skills@llm-models
```

### Content Creator
```bash
npx skills add inference-sh/skills@ai-image-generation
npx skills add inference-sh/skills@google-veo
npx skills add inference-sh/skills@seedance
npx skills add inference-sh/skills@text-to-speech
```

### Media Processor
```bash
npx skills add inference-sh/skills@image-upscaling
npx skills add inference-sh/skills@background-removal
npx skills add inference-sh/skills@speech-to-text
```

## Managing Skills

```bash
# List installed skills
npx skills list

# Update all skills
npx skills update

# Remove a skill
npx skills remove inference-sh/skills@ai-image-generation
```

## Documentation

- [Agent Skills Overview](https://inference.sh/blog/skills/skills-overview) - The open standard for AI capabilities
- [Getting Started](https://inference.sh/docs/getting-started/introduction) - Introduction to inference.sh
- [Apps Overview](https://inference.sh/docs/apps/overview) - Understanding the app ecosystem
- [CLI Setup](https://inference.sh/docs/extend/cli-setup) - Installing the CLI
- [What is inference.sh?](https://inference.sh/docs/getting-started/what-is-inference) - Platform overview

Explore: [inference.sh/explore](https://inference.sh/explore)

