# Marp slides review

- Local snapshot: `OTHER_REPOS/marp-slides`
- Upstream: [marp-slides](https://github.com/robonuggets/marp-slides)
- Content type: Agent instructions and 22 example Marp decks
- License found: None; the README's MIT statement is not a license file
- Recommendation: Visual inspiration only

## What it contains

This collection demonstrates dashboards, cards, comparisons, timelines, flowcharts, charts, hero
slides, inline SVG, and image-rich layouts. The examples rely heavily on per-deck CSS, raw HTML,
remote fonts, remote assets, and agent prompting.

## Reuse assessment

- Ideas: One visual idea per slide, varied explanation forms, and clear compare or sequence layouts
  are good teaching-design prompts. Biology-specific versions could be created locally.
- Code and functions: There is no converter or tested library worth adopting.
- Themes and assets: No license file grants permission to copy the decks, CSS, SVG, or images.
- Fit: The examples assume 16:9 output, VS Code-centered authoring, network resources, and much
  more inline HTML than the local Markdown convention permits.

## Decision

Use screenshots and examples only to spark original layouts. Rebuild any selected pattern in
`themes/genetics.css` with local assets, accessible contrast, OpenDyslexic, and 16:10 validation.
Do not copy source material from this snapshot.

[Return to the inventory](../RELATED_PROJECTS.md).
