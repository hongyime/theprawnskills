---
name: visual-explainer
description: >-
  When to read: most answers where a visual improves understanding — explain how it works, show
  the flow, compare options, diagram, UML, Mermaid, C4, or an HTML report. Use for: explaining
  ideas, plans, architecture, code changes, comparisons, audits, and workflows with consistent
  standalone HTML and useful diagrams. Does: uses a restrained dark theme with one cyan accent
  and a visual overview, details, next steps structure; works with postplan-upload for hosted
  delivery.
license: MIT
metadata:
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Visual Explainer

Make explanations easier to understand with one consistent HTML design system.
This is a daily-use presentation skill, not a replacement for domain expertise.

## Standing preferences

- Prefer HTML whenever a diagram, spatial layout, comparison, or small interaction
  makes the answer clearer. A short explanation can merit a small HTML document.
- Use a restrained dark interface with one cyan accent. Keep the same palette,
  type scale, spacing, and diagram treatment across documents and agents.
- Use this order: **Visual overview -> Details -> Next steps**. A short document
  can have one diagram, a paragraph of detail, and one next step. Do not pad it.
- Use visuals to explain relationships, behavior, decisions, and changes. A page
  of styled prose and tables alone is insufficient when a diagram would help.
- Respect a user's explicit requested format, project brand, or theme. Skip HTML
  for a single fact, a simple command, casual chat, or a task needing no visual.
- These preferences persist; do not ask the user to choose a new theme each time.

## Load the shared assets

Resolve this SKILL.md's containing directory, following its symlink if needed.
All assets below are relative to that directory and work in installed copies too.

1. Read [design-system.md](references/design-system.md).
2. Copy [explainer.html](templates/explainer.html) to the output path first.
   It is the document, not an example to imitate: replace only its subject
   matter, diagrams, links, and next steps; retain its stylesheet, design
   tokens, accessibility, and three section anchors in order. Do not write the
   HTML from scratch and do not rewrite the stylesheet — a page that drifts
   from the template drifts from every other page.
3. Read [diagrams.md](references/diagrams.md) when a diagram is useful. Use
   [mermaid-config.json](assets/mermaid-config.json) for Mermaid rendering.

The assets here own the style. Do not invent a new palette or ask theme-factory
to pick one for each document. Change the shared assets when the user changes
their standing preference; do not patch only a generated report.

## Choose the explanation before choosing the layout

Ground all claims in the user's context, actual files, or cited sources. Name
unknowns explicitly; do not invent components, metrics, transitions, or APIs to
make a diagram look complete. Separate observed and proposed behavior.

| What the reader needs to understand | Useful visual |
|---|---|
| Steps, branching, or a user's journey | Flowchart or user-flow diagram; include failure/retry paths when relevant |
| Who talks to whom, and in what order | UML-style sequence diagram, including waits and error responses |
| System scope and external dependencies | C4 context view: people, system boundary, external systems, labeled relationships |
| Applications and data stores inside a system | C4 container view; label technologies and responsibilities |
| Components within one application | C4 component view; do not mix abstraction levels |
| Types, ownership, or inheritance | UML class diagram; ER diagram for tables and cardinality |
| Lifecycle or allowed transitions | State diagram |
| Old versus proposed behavior | Paired diagrams or a labeled before/after comparison |
| Options and tradeoffs | Comparison matrix plus a visual showing the decision or consequences |
| Time or dependencies | Timeline, dependency graph, or Gantt when dates are supported |
| Numeric evidence | An appropriately scaled chart with units, sources, and uncertainty |

Use the smallest number of visuals that answers the question. Prefer one
readable overview over a huge graph. Split dense diagrams into a context view
and focused detail views. Label edges with verbs; color alone never conveys meaning.

## Build the document

1. Lead with a concrete title and one sentence answering the user's question.
2. **Visual overview:** put the main diagram or explanatory visual near the top,
   with a plain-language caption. Keep the overview readable without interaction.
3. **Details:** explain the diagram, evidence, tradeoffs, and exceptions. Use
   native details/summary for optional depth. Tables are for genuine comparisons.
4. **Next steps:** list a small number of specific actions, owners or prerequisites
   when known. For a pure explanation, offer one useful check or experiment.
5. Add source links next to claims and a date when the subject changes over time.
   Label assumptions and proposals visibly. Never fabricate citations.
6. Save to a task-appropriate output directory, normally `artifacts/<slug>.html`
   inside an authorized project. Without a project, use a local output directory
   under the current user's home. Do not put task reports or private content in
   the skill library. Preserve existing outputs by choosing a new filename.

Useful interaction includes expandable detail, diagram zoom, meaningful filters,
or a before/after toggle. Every control must work and remain keyboard accessible.
Keep navigation and essential content usable if scripting is disabled or stripped
by a host. Do not add dashboard controls or decorative animations without a purpose.

## Diagrams must arrive rendered

Mermaid source is an authoring format, not the final visual. Render it to SVG
locally and inline the SVG, or write a small accessible inline SVG directly.
Retain the editable Mermaid source beside the HTML or escaped inside a details
element. Never deliver a blank Mermaid container or source text as the only diagram.

Use the pinned CLI recipe and sample sources in [diagrams.md](references/diagrams.md).
If the renderer is unavailable, draw the needed SVG directly and keep any Mermaid
source for future editing. Do not block a simple explanation on installing a stack.
Do not use CDN scripts, remote fonts, runtime fetches, iframes, or external CSS.

## Verify and deliver

- Run `python scripts/check_html.py <output.html>` from this skill's directory
  (Windows: `py -3`; macOS/Linux: `python3`). It must pass before delivery: it
  checks structure, the design tokens, and the section order — not a visual
  review or a full security audit. A token failure means the stylesheet was
  rewritten instead of reused; restore the template's stylesheet rather than
  patching the check.
- Glance test: read only the finished page — no chat, no source documents —
  and state the answer in one sentence. If the page needs the chat to be
  understood, redraw the overview before delivering. For a substantial plan or
  report, have a fresh agent with no context on the work read only the page
  and answer as a stranger: what is being decided, and could they act on it?
  Rework anything it cannot explain; at most three rounds.
- If the user explicitly requested different project branding, the token check
  is expected to fail — note the override in your reply instead of forcing the
  shared tokens back.
- Inspect a screenshot or browser view when making a new layout or diagram.
  Check wide and narrow screens, readable labels, no clipped content, and controls.
  Prefer a local headless browser; if unavailable, disclose that visual inspection
  was not performed. Reusing the unchanged template does not require a new theme review.
- Ensure no sample-specific content remains, source claims are supported, and
  all diagrams show real or clearly labeled proposed relationships.
- Return the local clickable HTML path with the answer. When a hosted link is
  requested or authorized by the user's established workflow, use `postplan-upload`
  with this finished HTML. That upload produces a public URL; local HTML generation
  alone does not authorize publishing private project material.
- If hosting fails, preserve and link the local HTML. Never claim an upload or
  rendering succeeded without checking its result.

## Integration and maintenance

`postplan-upload` owns the hosting command and delivery result. This skill owns
the visual design and diagram choices. Planning/review/domain skills own their
subject matter and can use this presentation without repeating the style rules.

Keep this skill in `default-profile.toml` alongside `postplan-upload`. Both the
OneDrive library and standalone Git installations carry its complete asset tree.
After changing it, update the repository and propagate installed copies using
the repository's documented sync procedure; do not copy a machine's credentials.
