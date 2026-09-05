# Classic Marp syntax guide

This guide covers classic Marp Markdown that is compatible with Marp CLI. It is the upstream
language reference for hand-authored decks, not a specification for this repository's native
exporter or a proposal for a future extension language.

The local native-exporter transition is intentionally kept out of this guide. A future, explicitly
chosen language extension will receive its own separately named guide. See
[LAYOUT_LANGUAGE_SURVEY.md](LAYOUT_LANGUAGE_SURVEY.md) for comparison evidence and
[ROADMAP.md](ROADMAP.md) for the temporary implementation transition.

## Core deck shape

Start a deck with Marp front matter. A line containing `---` after that front matter begins the
next slide.

```markdown
---
marp: true
theme: default
paginate: false
title: "Lecture title"
---

# Lecture title

Course name

---

## First topic

- First point
- Second point
```

`marp: true` enables Marp processing. `theme`, `size`, `paginate`, `header`, and `footer` are
ordinary Marp configuration, not a layout language. Consult the [official directive guide] for the
complete set of supported directives and their scope.

## Standard Markdown

Use ordinary CommonMark-style Markdown for headings, paragraphs, blockquotes, emphasis, links,
images, and lists. Nested lists remain ordinary Markdown; indent a child item beneath its parent.

```markdown
## DNA repair pathways

- Direct repair
  - Photoreactivation
  - Alkyltransferase repair
- Excision repair
  - Base excision repair
  - Nucleotide excision repair
```

In classic Marp, `>` always retains its standard blockquote meaning. Do not use it as a column,
cell, or layout marker.

## Directives and classes

Marp directives are HTML comments. A leading underscore scopes a directive to the current slide.

```markdown
<!-- _class: lead -->
<!-- _paginate: false -->

# A section heading
```

`_class` attaches a CSS class. The class name has no universal presentation meaning: `lead`,
`title-slide`, `two-column`, and similar names work only when the selected CSS theme defines them.
Marp itself does not standardize a title/subtitle layout, a two-panel layout, named cells, or a
grid vocabulary.

Use a theme's documented classes when you intentionally rely on that theme. Keep such theme
choices separate from claims about Marp language compatibility.

## Images and backgrounds

Use normal image Markdown for content images.

```markdown
![Chromosome rearrangement](assets/chromosome.png)
```

Marp also has documented image directives and background-image syntax, such as `![bg]`. Those are
classic Marp features and remain compatible only to the degree described by the selected Marp CLI
version and theme. Read the [official image guide] before using sizing, positioning, background,
or filter modifiers.

## Layout boundary

Classic Marp delegates layout to CSS. It can select slide classes and render standard Markdown, but
it does not provide a portable source syntax for "left cell," "right cell," or arbitrary regions.
Raw HTML and theme-specific CSS can create those layouts, but they make a deck dependent on that
rendering environment.

That boundary is deliberate in this guide. It prevents a local or theme-specific convention from
being mistaken for official Marp. The [LAYOUT_LANGUAGE_SURVEY.md](LAYOUT_LANGUAGE_SURVEY.md) compares
FOSS projects that make different tradeoffs between terse hand-authoring and explicit structure.

## Primary references

- [Marp Core v5 Markdown guide]
- [Marp Core v5 migration guide]
- [Official directive guide]
- [Official image guide]
- [Marp CLI repository]

[Marp Core v5 Markdown guide]: https://github.com/marp-team/marp-core/blob/v5.0.1/docs/markdown.md
[Marp Core v5 migration guide]: https://github.com/marp-team/marp-core/blob/v5.0.1/docs/migration-v5.md
[official directive guide]: https://marpit.marp.app/directives
[official image guide]: https://marpit.marp.app/image-syntax
[Marp CLI repository]: https://github.com/marp-team/marp-cli
