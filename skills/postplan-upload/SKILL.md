---
name: postplan-upload
description: >-
  Use this when generating a substantial execution plan, architecture spec,
  refactoring blueprint, implementation plan, visual draft report, PR review
  summary, or when the user asks to upload, publish, share, or make a clickable
  plan. Use visual-explainer's shared dark/cyan style and diagrams to render
  standalone HTML, then upload it with `npx postplan upload`.
license: MIT
metadata:
  author: Bryan local setup
  version: "1.1.0"
  platform: "Codex, Claude, Cursor, OpenCode on Windows, macOS, Linux"
---

# PostPlan Upload

Use PostPlan to turn substantial plans, architecture notes, review summaries,
and implementation blueprints into a shareable draft URL that can be opened from
any terminal or machine.

PostPlan is the publishing workflow. `visual-explainer` owns the shared design,
diagram choices, and reusable template; this skill publishes the finished HTML.

## When To Use

Use this skill when the user asks for, or would clearly benefit from sharing, a
non-trivial:

- an execution plan
- an implementation plan
- a refactoring blueprint
- an architecture spec
- a visual draft report
- a PR review summary
- a technical proposal
- a planning document that should be easy to open in a browser

Also use it when the user says phrases like:

- "upload this plan"
- "share this plan"
- "make a postplan"
- "publish the plan"
- "send me a draft URL"
- "make it easy to view"
- "clickable plan"
- "html plan"

Bias toward using this for multi-step coding plans, cleanup plans, architecture
decisions, refactor proposals, audit reports, and review summaries. Do not use
it for tiny inline plans where a normal chat response is enough, unless the user
asks to upload/share it. Short visual explanations from `visual-explainer` are
also valid upload inputs when hosted delivery is requested or already authorized.

## Workflow

1. Read `visual-explainer` fully and use its design system, diagram guidance,
   and template. Its SKILL.md is normally at `../visual-explainer/SKILL.md`
   relative to this skill's resolved directory. Existing HTML already following
   that standard can be uploaded without recreating it. If the sibling is
   missing, locate it in the shared library; report a missing dependency rather
   than silently reverting to a different theme. Respect explicitly requested
   project branding. Create a local standalone HTML file, usually:

   ```text
   .\plan.html
   ```

2. Make the HTML self-contained:

   - Use the shared dark/cyan tokens and system typography.
   - Keep visual overview -> details -> next steps.
   - Include useful rendered diagrams, not only tables and prose.
   - Pre-render Mermaid to inline SVG; do not depend on a CDN or runtime renderer.
   - Inline JavaScript is allowed for small interactions such as collapsible sections, tabs, filters, or copy buttons.

3. Do not include external runtime dependencies:

   - No external scripts such as `<script src="...">`.
   - No external stylesheets.
   - No forms.
   - No iframes.

4. Upload with PostPlan:

   ```powershell
   npx postplan upload ./plan.html --description "<short useful description>"
   ```

5. Present the resulting public draft URL directly to the user.

## HTML Guidance

Prefer a document that is useful for review, not a decorative landing page.

Use `visual-explainer` for the outer structure and visual choices. Place these
subject-specific details inside that structure as useful:

- title and short summary
- goals and non-goals
- assumptions
- proposed approach
- phases or milestones
- risks and tradeoffs
- open questions
- next actions

For PR review summaries, prefer:

- severity-grouped findings
- affected files or components
- suggested fixes
- test gaps
- decision log

For architecture specs, prefer:

- system context
- components
- data flow
- operational concerns
- security and failure modes
- rollout plan

## Constraints

Follow `visual-explainer`'s structural and visual checks. A local headless browser
is appropriate for checking a new layout or diagram. Do not launch a visible
browser window unless requested. Preserve a usable local artifact if tools or
hosting are unavailable.

Do not use external scripts, forms, or iframes.

Do not upload secrets, private credentials, environment files, tokens, or raw logs containing sensitive values. If the source material may contain secrets, summarize safely and omit the sensitive values.

If `npx postplan upload` fails because PostPlan is unavailable, report the failure and leave the generated `plan.html` in place.

## Output

After upload, respond with:

- the public PostPlan draft URL
- the local HTML path
- any caveat if upload failed or content was intentionally redacted

## Handoff Sources

PostPlan is the rendering target for larger planning artifacts. When another
skill produces a substantial document, offer to render it here:

| Source skill | Typical artifact |
|---|---|
| `visual-explainer` | visual explanation -> consistently styled HTML |
| `to-spec` | approved spec -> spec plan HTML |
| `to-tickets` | ticket board -> work-breakdown HTML |
| `wayfinder` | wayfinding map -> initiative map HTML |
| `competitive-upgrade` | upgrade report -> strategy HTML |
| `repo-standardization` | compliance report -> audit HTML |
