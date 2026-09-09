---
name: skill-router
description: >-
  Find and load on-demand skills from a Prawn Skills Git clone on any supported OS.
  Use for unfamiliar tooling, specialized tasks, skill discovery, or requests
  involving documents, media, cloud platforms, writing, or skill maintenance.
license: MIT
metadata:
  platform: Windows, macOS, Linux
---

# Skill Router for Standalone Installs

Read `~/.config/theprawnskills/library.json` and use its `library` path as the
repository root. If absent and this skill is a symlink, resolve it to locate
the clone. For a copied installation, inspect the intended clone and repair
the pointer through the installer; the installed copy is not the library.
The repo root contains `default-profile.toml` and `skills/`.

Read `<root>/platforms/linux/README.md` for platform conventions. Search names
and descriptions with `rg` in `<root>/skills` and `<root>/platforms/linux/skills`.
Choose the smallest relevant set, prefer a standalone variant when present, and
read each selected `SKILL.md` fully before acting. Resolve symlinks before
following relative references. Never install the full library just to search it.

| Request | Starting points |
|---|---|
| Create, add, update, audit, remove skills | Standalone variants of skill-create, skill-add, skill-update, skill-cleanup, skill-remove, skill-authoring |
| Coding, review, debugging | build, check, refactor, requesting-code-review, systematic-debugging |
| Visual explanations, diagrams, UML/C4, flows, comparisons, HTML reports | visual-explainer; postplan-upload for hosted delivery |
| Documents, spreadsheets, presentations | pdf, docx, xlsx, pptx |
| Frontend design | frontend-design, web-design-guidelines, shadcn |
| Cloudflare | cloudflare, wrangler, workers-best-practices |
| Azure / Supabase / Vercel | azure-prepare, supabase, deploy-to-vercel |
| Images, video, audio | ai-image-generation, image-to-video, text-to-speech |
| Writing and marketing | technical-blog-writing, case-study-writing, content-repurposing |

Verify candidate availability and tool prerequisites from the actual files.
Keep source skills and installed links/copies separate. Use the Python installer
for local exposure, and do not run OneDrive propagation or `dotagents sync`.

Keep `visual-explainer` in the daily profile with `postplan-upload`. Use its
shared dark/cyan template whenever a visual helps, including short answers.
The document order is visual overview, details, next steps. Hosting is a
separate delivery step governed by the user's authorization.
