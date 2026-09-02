# Marp Core review

- Local snapshot: `OTHER_REPOS/marp-core`
- Upstream: [Marp Core](https://github.com/marp-team/marp-core)
- Local version: 5.0.1
- Content type: Official TypeScript Marp rendering engine and built-in themes
- License found: MIT
- Recommendation: Upstream compatibility reference only

## What it contains

Marp Core implements the Markdown-to-slide engine, theme parsing, slide sizing, auto-scaling,
heading slugs, math, emoji, and HTML handling. It contains the official Default, Gaia, and Uncover
SCSS themes. Version 5 also exposes optional Mermaid, syntax-highlighting, and math integrations.

## Reuse assessment

- Ideas: Theme metadata, size declarations, safe-HTML handling, and auto-scaling behavior define
  useful compatibility boundaries for local tests.
- Code and functions: The installed Marp CLI already supplies the engine. Copying its TypeScript
  internals would create an unsupported fork.
- Themes: Built-in themes are valuable examples, but the local theme has stricter fonts, contrast,
  and 16:10 geometry.
- Version risk: This snapshot is Core 5.0.1, while Marp CLI 4.5.0 uses the Core 4 generation.
  Version 5 documentation must not be assumed to describe the current runtime.

## Decision

Treat this repository as upstream documentation and migration evidence. Before a Marp major-version
upgrade, render representative decks and retest theme layout, notes, and all output formats.

[Return to the inventory](../RELATED_PROJECTS.md).
