# Marp CLI review

- Local snapshot: `OTHER_REPOS/marp-cli`
- Upstream: [Marp CLI](https://github.com/marp-team/marp-cli)
- Local version: 4.5.0
- Content type: Official TypeScript command-line renderer
- License found: MIT
- Recommendation: Exclude it from future extension rendering

## What it contains

Marp CLI is the official command-line interface for converting Marp Markdown to HTML, PDF, PPTX,
images, and presenter-note output. It owns browser integration, theme loading, configuration, and
server behavior. The installed 4.5.0 release is already the renderer used by this repository.

## Reuse assessment

- Ideas: Theme-set loading, output options, notes, and documented security boundaries should guide
  the local wrapper contract.
- Code and functions: Copying the TypeScript implementation would duplicate the renderer and break
  the local Python-only ownership boundary.
- Themes: Official themes are useful compatibility references, but `themes/genetics.css` remains
  the local visual authority.
- Risks: `--allow-local-files` broadens file access and should remain limited to trusted local
  decks. Editable PPTX is documented as lower fidelity and locally failed the notes/layout bakeoff.

## Decision

Do not route new language or renderer work through Marp CLI. Retain this snapshot only as reference
evidence for existing Marp behavior while the project selects and tests a direct rendering path.

[Return to the inventory](../RELATED_PROJECTS.md).
