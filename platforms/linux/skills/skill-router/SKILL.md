---
name: skill-router
description: >-
  Find and load on-demand skills from the local Prawn Skills Git clone on Linux.
  Use for unfamiliar tooling, specialized tasks, skill discovery, or requests
  involving documents, media, cloud platforms, writing, or skill maintenance.
license: MIT
metadata:
  platform: Linux
---

# Skill Router for Linux

Read `~/.config/theprawnskills/library.json` and use its `library` path as the
repository root. If absent, locate the user's clone by resolving this skill's
symlink; the repo root contains `default-profile.toml` and `skills/`.

Read `<root>/platforms/linux/README.md` for platform conventions. Search names
and descriptions with `rg` in `<root>/skills` and `<root>/platforms/linux/skills`.
Choose the smallest relevant set, prefer a Linux variant when present, and
read each selected `SKILL.md` fully before acting. Resolve symlinks before
following relative references. Never install the full library just to search it.

| Request | Starting points |
|---|---|
| Create, add, update, audit, remove skills | Linux variants of skill-create, skill-add, skill-update, skill-cleanup, skill-remove, skill-authoring |
| Coding, review, debugging | build, check, refactor, requesting-code-review, systematic-debugging |
| Documents, spreadsheets, presentations | pdf, docx, xlsx, pptx |
| Frontend design | frontend-design, web-design-guidelines, shadcn |
| Cloudflare | cloudflare, wrangler, workers-best-practices |
| Azure / Supabase / Vercel | azure-prepare, supabase, deploy-to-vercel |
| Images, video, audio | ai-image-generation, image-to-video, text-to-speech |
| Writing and marketing | technical-blog-writing, case-study-writing, content-repurposing |

Verify candidate availability and tool prerequisites from the actual files.
Keep source skills and installed links separate. Use the Linux installer for
local exposure, and do not run Windows propagation or `dotagents sync`.
