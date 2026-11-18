---
name: web-to-markdown
description: "Converts webpage URLs to clean Markdown by calling the local web2md CLI (Puppeteer + Readability), suitable for JS-rendered pages. Use when converting a webpage or URL to Markdown, or when the user asks for a page as Markdown."
metadata:
  version: 0.1.0
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# web-to-markdown

Convert web pages to clean Markdown by driving a locally installed browser (via `web2md`).

## What this skill does

- Handles JS-rendered pages (Puppeteer → user Chrome).
- Works best with Chromium-family browsers (Chrome/Chromium/Brave/Edge) via `puppeteer-core`.
- Extracts main content (Readability).
- Converts to Markdown (Turndown) with cleaned links and optional YAML frontmatter.

## Non-goals

- Do not use Playwright or other browser automation stacks; the mechanism is `web2md`.

## Inputs you should collect (ask only if missing)

- `url` (or a list of URLs)
- Output preference:
  - Print to stdout (`--print`), OR
  - Save to a file (`--out ./file.md`), OR
  - Save to a directory (`--out ./some-dir/` to auto-name by page title)
- Optional rendering controls for tricky pages:
  - `--chrome-path <path>` (if Chrome auto-detection fails)
  - `--interactive` (show Chrome and pause so the user can complete human checks/login, then press Enter)
  - `--wait-until load|domcontentloaded|networkidle0|networkidle2`
  - `--wait-for '<css selector>'`
  - `--wait-ms <milliseconds>`
  - `--headful` (debug)
  - `--no-sandbox` (sometimes required in containers/CI)
  - `--user-data-dir <dir>` (login/session; use a dedicated profile directory)

## Workflow

1) Validate URL(s) start with `http://` or `https://`.
2) Ensure `web2md` is installed:
   - Run: `command -v web2md`
   - If missing, ask the user for the web2md project location — it is a local project, not a published package — then, with their approval:
     - `cd <project-dir> && npm install && npm run build && npm link`
     - Or: `cd <project-dir> && npm install && npm run build && npm install -g .`
3) Convert:
   - Single URL → file:
     - `web2md '<url>' --out ./page.md`
   - Single URL → auto-named file in directory:
     - `mkdir -p ./out && web2md '<url>' --out ./out/`
   - Human verification / login walls (interactive):
     - `mkdir -p ./out && web2md '<url>' --interactive --user-data-dir ./tmp/web2md-profile --out ./out/`
     - Then: complete the check in the browser window and press Enter in the terminal to continue.
   - Print to stdout:
     - `web2md '<url>' --print`
   - Multiple URLs (batch):
     - Create output dir (e.g. `./out/`) then run one `web2md` command per URL using `--out ./out/`
4) Validate output:
   - If writing files, verify they exist and are non-empty (e.g. `ls -la <path>` and `wc -c <path>`).
5) Return:
   - The saved file path(s), or the Markdown (stdout mode).

## Defaults (recommended)

- For most pages: `--wait-until networkidle2`
- For heavy apps: start with `--wait-until domcontentloaded --wait-ms 2000`, then add `--wait-for 'main'` (or another stable selector) if needed.
