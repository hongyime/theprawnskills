# Diagrams that explain

Keep one abstraction level per diagram and name the question it answers.
For C4, context means people/systems, containers mean applications/data stores,
and components live inside one container. A container is not necessarily Docker.
UML sequence diagrams explain ordered messages; class diagrams explain structure.

## Render Mermaid before delivery

Use the checked examples in `examples/diagrams/`. From the skill directory,
with Node/npm and a compatible Chromium installation available:

```text
npx --yes --package @mermaid-js/mermaid-cli@11.17.0 mmdc -i examples/diagrams/user-flow.mmd -o user-flow.svg -c assets/mermaid-config.json -b transparent
```

The same command works in PowerShell and bash/zsh. Replace the input and output
paths for the other examples: sequence, c4-context, and class-model. The CLI is
an authoring dependency only; it is not loaded by the delivered HTML. Do not
install the repository's unrelated legacy npm dependencies to render diagrams.
Use `mmdc --help` or the pinned CLI's help when a browser configuration is needed.

Read the SVG output, omit any XML declaration/doctype, and inline the SVG markup
inside a figure. Preserve its viewBox; add unique accessible title/description
IDs. Prefix generated IDs and their references for multiple diagrams. Ensure
styles are scoped to that diagram. Do not turn SVG labels into unreadable pixels.

If rendering tools are unavailable, create a small inline SVG with the same
colors, labeled arrows, proper bounds, and a caption. Report that fallback.
Do not upload an HTML document that needs a Mermaid CDN to show its overview.

## C4 compatibility

The bundled C4 context example uses ordinary Mermaid flowchart syntax with
explicit person/system labels and a system boundary. This preserves the C4
meaning while using the shared theme. Mermaid's dedicated C4 syntax is
experimental; use it only after checking the rendered result and styling.

## Quality checks

- Read the relationships as sentences: actor -> verb -> target.
- Label the happy path and material alternate paths. Mark hypothetical flows
  as proposed. For sequences, show responses and failures where they matter.
- About 3-8 entities per overview is a useful starting point, not a quota.
- Avoid crossing arrows, clipped labels, gratuitous icons, and invented depth.
- Leave numeric charts to an appropriate plotting tool when accuracy/export
  matters; preserve units, scales, and sources.

References: [Mermaid CLI](https://github.com/mermaid-js/mermaid-cli),
[theme configuration](https://mermaid.js.org/config/theming.html),
[C4 syntax and its experimental status](https://mermaid.js.org/syntax/c4.html).
