# MarpX review

- Local snapshot: `OTHER_REPOS/MarpX`
- Upstream: [MarpX](https://github.com/cunhapaulo/MarpX)
- Content type: Marp theme suite with examples and image assets
- License found: MIT
- Recommendation: Adapt selected ideas, not the theme package

## What it contains

MarpX is a large CSS-centered theme system. It has a shared constants layer, a template layer,
many named themes, example decks, and substantial image content. Its semantic slide vocabulary
includes title, chapter, table-of-contents, reference, quote, question, warning, note, success,
column, and grid treatments.

Useful files to study include `themes/marpx.css`, `themes/_constants.css`,
`themes/_template.css`, and the named theme files under `themes/`.

## Reuse assessment

- Ideas: The layered base-theme and token-override structure is useful. Question, reference,
  warning, and chapter classes could improve teaching decks if kept deliberately small.
- Code and functions: There is no conversion logic that the local Python pipeline needs.
- Themes: MIT permits reuse with its notice, but wholesale copying would bring excessive CSS,
  raw-HTML assumptions, remote fonts, and dimensions that do not match the local 16:10 contract.
- Assets: Do not copy example images without verifying each asset's origin and license.

## Decision

Independently implement only proven semantic classes in `themes/genetics.css`, then measure color
contrast and inspect rendered 1280x800 slides. Preserve OpenDyslexic and simple Markdown. MarpX is
high-value visual prior art, not a theme dependency.

[Return to the inventory](../RELATED_PROJECTS.md).
