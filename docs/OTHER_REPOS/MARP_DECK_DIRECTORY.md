# Marp deck directory review

- Local snapshot: `OTHER_REPOS/marp-deck-directory`
- Upstream: [marp-deck-directory](https://github.com/nicolas-goudry/marp-deck-directory)
- Content type: Nix-based reproducible builder for directories of Marp decks
- License found: MIT
- Recommendation: Adapt output and asset ownership ideas

## What it contains

The project discovers decks recursively and builds HTML, PDF, and cover images in a reproducible
Nix environment. `pkgs/slides.nix` maps nested deck paths into outputs, rewrites asset references,
and supports shared and per-deck assets. It also includes Catppuccin styling and local font files.

## Reuse assessment

- Ideas: Collision-safe output names, explicit per-deck asset ownership, and a reproducible tool
  version directly address risks that appear as the course gains more lecture directories.
- Code and functions: Its implementation is Nix, so copying it would introduce an unwanted package
  system and a second build architecture.
- Themes and fonts: The styling does not match the local visual contract. Bundled fonts must retain
  their own licenses and are not needed.
- Workflow: Site publishing and Marp server behavior are outside the normal local classroom build.

## Decision

Use this as high-value architecture prior art. If duplicate deck basenames become possible, add a
small Python-owned output mapper that preserves relative course paths and deterministic asset
ownership. Do not adopt Nix or the included theme.

[Return to the inventory](../RELATED_PROJECTS.md).
