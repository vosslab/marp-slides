# Marp slides template review

- Local snapshot: `OTHER_REPOS/marp-slides-template`
- Upstream: [marp-slides-template](https://github.com/codebytes/marp-slides-template)
- Content type: Marp starter, themes, publishing workflow, and overflow script
- License found: MIT
- Recommendation: Adapt the overflow-checking idea

## What it contains

The template combines sample decks, CSS themes, GitHub Pages automation, DevContainer and VS Code
configuration, Copilot instructions, and `check-overflow.mjs`. The overflow script renders Marp
HTML, opens it in Playwright, and compares each slide's scroll dimensions with its visible frame.

## Reuse assessment

- Ideas: Browser-measured horizontal and vertical overflow is the clearest near-term improvement
  found in the collection. It can turn a visual layout obligation into repeatable evidence.
- Code and functions: The MIT script can be studied, but it invokes changing npm packages and is
  coupled to Node. A local implementation should use the installed Marp 4.5.0 and existing browser
  test infrastructure from a Python-owned command.
- Themes: The simple variables and column layouts offer little beyond the current central theme.
- Workflow: GitHub Pages, DevContainers, VS Code, and remote Font Awesome are not local needs.

## Decision

Prototype a deterministic repository-owned overflow check against representative 1280x800 decks.
Do not adopt the template or its editor and publishing workflow.

[Return to the inventory](../RELATED_PROJECTS.md).
