# Marp community themes review

- Local snapshot: `OTHER_REPOS/marp-community-themes`
- Upstream: [marp-community-themes](https://github.com/rnd195/marp-community-themes)
- Content type: Marp CSS theme gallery with samples and license records
- License found: Mixed by theme
- Recommendation: Visual and licensing reference

## What it contains

This repository collects Academic, Border, Gradient, Graph Paper, Neobeam, Rose Pine, and Beam
theme families. It pairs CSS sources with preview decks and keeps theme-specific license material
under `themes/licenses/`.

Most listed themes are MIT. Beam includes GPLv3 material and Beamer-derived GPLv2 material. The
repository-level MIT license does not replace those per-theme terms.

## Reuse assessment

- Ideas: The preview gallery and explicit per-theme provenance are excellent maintenance patterns.
  Graph-paper and restrained academic motifs could suit problem-solving slides.
- Code and functions: There is no pipeline code to adopt.
- Themes: A small MIT-licensed rule may be adapted with its notice, but each source file must be
  checked first. Do not copy Beam CSS into this MIT project.
- Fonts and assets: Several themes fetch Google fonts. Remote fonts conflict with deterministic,
  offline classroom rendering and with the OpenDyslexic contract.

## Decision

Use the gallery for visual comparison and as a model for recording provenance. Any motif added to
the central theme should be rebuilt for 1280x800, tested for contrast, and free of remote assets.

[Return to the inventory](../RELATED_PROJECTS.md).
