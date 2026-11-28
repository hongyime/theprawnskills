---
name: llm-models
description: >-
  When to read: access to Claude, Gemini, Kimi, GLM, or 100+ LLMs is needed. Use for: accessing
  LLMs via the inference.sh CLI using OpenRouter. Does: one API for all models with automatic
  fallback and cost optimization — Claude Opus/Sonnet/Haiku 4.5, Gemini 3 Pro, Kimi K2, GLM-4.6,
  Intellect 3.
allowed-tools: Bash(belt *)
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---


# LLM Models via OpenRouter
Matches belt 1.29.5 (verified on the VM, 2026-11-18)

Access 100+ language models via [inference.sh](https://inference.sh) CLI.

![LLM Models via OpenRouter](https://cloud.inference.sh/app/files/u/4mg21r6ta37mpaz6ktzwtt8krr/01kgvftjwhby36trvaj66bwzcf.jpeg)

## Quick Start

> Requires inference.sh CLI (`belt`). [Install instructions](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# Call Claude Sonnet
belt app run openrouter/claude-sonnet-45 --input '{"prompt": "Explain quantum computing"}'
```


## Available Models

| Model | App ID | Best For |
|-------|--------|----------|
| Claude Opus 4.5 | `openrouter/claude-opus-45` | Complex reasoning, coding |
| Claude Sonnet 4.5 | `openrouter/claude-sonnet-45` | Balanced performance |
| Claude Haiku 4.5 | `openrouter/claude-haiku-45` | Fast, economical |
| Gemini 3 Pro | `openrouter/gemini-3-pro-preview` | Google's latest |
| Kimi K2 Thinking | `openrouter/kimi-k2-thinking` | Multi-step reasoning |
| GLM-4.6 | `openrouter/glm-46` | Open-source, coding |
| Intellect 3 | `openrouter/intellect-3` | General purpose |
| Any Model | `openrouter/any-model` | Auto-selects best option |

## Search LLM Apps

```bash
belt app search "openrouter"
belt app search "claude"
```

## Examples

### Claude Opus (Best Quality)

```bash
belt app run openrouter/claude-opus-45 --input '{
  "prompt": "Write a Python function to detect palindromes with comprehensive tests"
}'
```

### Claude Sonnet (Balanced)

```bash
belt app run openrouter/claude-sonnet-45 --input '{
  "prompt": "Summarize the key concepts of machine learning"
}'
```

### Claude Haiku (Fast & Cheap)

```bash
belt app run openrouter/claude-haiku-45 --input '{
  "prompt": "Translate this to French: Hello, how are you?"
}'
```

### Kimi K2 (Thinking Agent)

```bash
belt app run openrouter/kimi-k2-thinking --input '{
  "prompt": "Plan a step-by-step approach to build a web scraper"
}'
```

### Any Model (Auto-Select)

```bash
# Automatically picks the most cost-effective model
belt app run openrouter/any-model --input '{
  "prompt": "What is the capital of France?"
}'
```

### With System Prompt

```bash
belt app sample openrouter/claude-sonnet-45 --save input.json

# Edit input.json:
# {
#   "system": "You are a helpful coding assistant",
#   "prompt": "How do I read a file in Python?"
# }

belt app run openrouter/claude-sonnet-45 --input input.json
```

## Use Cases

- **Coding**: Generate, review, debug code
- **Writing**: Content, summaries, translations
- **Analysis**: Data interpretation, research
- **Agents**: Build AI-powered workflows
- **Chat**: Conversational interfaces

## Related Skills

```bash
# Full platform skill (all apps)
npx skills add inference-sh/skills@infsh-cli

# Web search (combine with LLMs for RAG)
npx skills add inference-sh/skills@web-search

# Image generation
npx skills add inference-sh/skills@ai-image-generation

# Video generation
npx skills add inference-sh/skills@google-veo
npx skills add inference-sh/skills@seedance
```

Browse all apps: `belt app list`

## Documentation

- [Agents Overview](https://inference.sh/docs/concepts/agents) - Building AI agents
- [Agent SDK](https://inference.sh/docs/api/agent/overview) - Programmatic agent control
- [Building a Research Agent](https://inference.sh/blog/guides/research-agent) - LLM + search integration guide

