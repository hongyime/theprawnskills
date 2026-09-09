# Shared visual standard

Version 1.0.0. Applies to explanatory HTML, plans, reviews, and reports. These
defaults come from an explicit standing preference, not from the current subject.

## Tokens

The template's CSS custom properties are the implementation of these tokens.
When editing a token, update this table and mermaid-config.json in the same change.

| Token | Value | Use |
|---|---|---|
| background | #101418 | Page |
| surface | #171D23 | Diagram panels and optional depth |
| raised | #202830 | Hover and nested surfaces |
| border | #36434F | Boundaries, separators, neutral diagram strokes |
| text | #E8EDF2 | Headings and essential labels |
| muted | #A8B5C2 | Secondary text; still readable |
| accent | #67D4E8 | Links, active state, selected path, section markers |
| accent-soft | #182D34 | Highlight backgrounds |

Use cyan as the only decorative accent. Communicate status with explicit words,
icons, line patterns, and weight; do not introduce a rainbow of status cards.
Explicitly requested charts that need categorical color must also have labels
and a legend; prefer neutral series with one emphasized cyan series by default.

## Typography and composition

- System sans-serif: Segoe UI on Windows, system-ui elsewhere. No network fonts.
- Monospace: ui-monospace, SFMono-Regular, Consolas, monospace.
- Body: 16-17px, line-height about 1.65. Secondary labels at least 13px.
- Title: responsive 30-52px. Section titles: 23-28px. Diagram labels about 16px
  at normal viewing size; split or allow scrolling before shrinking illegibly.
- Content width: about 1080px; prose measure around 70 characters. Use 24-48px
  section gaps and 8px spacing increments. Comfortable mobile margins: 20px.
- Prefer simple dividers and a few purposeful panels. Avoid nesting every
  sentence inside another card. No gradients, glows, giant hero banners,
  decorative charts, stock illustrations, or random color changes by topic.

## Required document spine

1. Header with subject, concrete conclusion, and short document context.
2. `#overview`: the main explanatory visual and a caption.
3. `#details`: supporting explanation, evidence, exceptions, and optional depth.
4. `#next-steps`: specific actions or a useful next check.

Keep these anchors consistent for navigation. The subject determines whether
the overview is a flow, architecture diagram, sequence, comparison, or chart.
For a short answer, keep all three sections compact and avoid redundant nav.

## Accessibility and resilience

- Semantic headings, meaningful link text, visible keyboard focus, and no hover-only
  information. Use native details/summary when possible. Label every control.
- Give each SVG a unique title/description, role=img, and aria-labelledby.
  Include a text caption explaining the takeaway. Prefix SVG IDs when embedding
  several generated diagrams so markers and styles do not collide.
- Diagrams need labeled relationships and boundaries, not color-only semantics.
- Preserve the normal document reading order. Avoid tiny sideways diagrams on mobile;
  use a clearly labeled scrolling region for dense visuals, or simplify the view.
- Support prefers-reduced-motion. Print styles use white backgrounds and dark text.
  Essential content must remain visible without JavaScript or network access.
- Inline SVG and local inline CSS/JS only. External links for citations are fine;
  they must not be required to render the document.
