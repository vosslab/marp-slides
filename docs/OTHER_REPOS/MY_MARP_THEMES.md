# My Marp themes review

- Local snapshot: `OTHER_REPOS/my-marp-themes`
- Upstream: [my-marp-themes](https://github.com/rnd195/my-marp-themes)
- Content type: Four small Marp CSS themes with samples
- License found: Mixed by theme
- Recommendation: Motif reference only

## What it contains

The repository contains Border, Gradient, Graph Paper, and Beam CSS themes, plus examples,
screenshots, and a short authoring guide. `LICENSE.md` records the file-specific terms. Border,
Gradient, and Graph Paper are MIT; Beam includes GPLv3 and Beamer-derived GPLv2 material.

## Reuse assessment

- Ideas: Graph-paper backgrounds could reinforce blackboard-style problems, while a restrained
  border can clarify section or question slides. CSS variables make palette variants manageable.
- Code and functions: There is no conversion logic.
- Themes: MIT files may be adapted with notice. Do not copy Beam into this MIT repository.
- Fonts and geometry: The themes use remote Google fonts and 16:9-oriented defaults. They do not
  satisfy offline rendering, OpenDyslexic, accessible contrast, or 1280x800 validation as written.

## Decision

If a deck demonstrates a need, independently add one small motif to `themes/genetics.css` and
measure it in context. The complete themes are unnecessary and should not be imported.

[Return to the inventory](../RELATED_PROJECTS.md).
