# Marp syntax guide

Use this guide as the authoring contract for canonical presentation Markdown in this repository.
The source stays recognizable as Marp Markdown while the production build interprets a deliberate,
validated subset into native editable PPTX and ODP objects.

## Compatibility baseline

This repository adopts the author-facing Markdown contract of **Marp Core v5 only**. The primary
references are the version-pinned [Marp Core v5 Markdown guide][core-v5-markdown] and
[v5 migration guide][core-v5-migration]. Basic slide syntax comes from the inherited
[Marpit directives][marpit-directives] and [Marpit image syntax][marpit-images].

Marp Core is conformance evidence, not a production dependency. The repository-owned parser
accepts the subset documented here. Marp Core v4 and earlier behavior is not a compatibility target.

Marp Core v5 separates built-in behavior from optional Shiki, Mermaid, KaTeX, and MathJax plugins.
Adopting v5 does not automatically adopt the `/full` entry point or every plugin feature. A feature
becomes accepted only when this guide documents its native editable-object behavior.

Use the versioned official sources and this guide as the authorities. The upstream and secondary
references used to prepare this contract are collected under External links.

[core-v5-markdown]: https://github.com/marp-team/marp-core/blob/v5.0.1/docs/markdown.md
[core-v5-migration]: https://github.com/marp-team/marp-core/blob/v5.0.1/docs/migration-v5.md
[marpit-directives]: https://marpit.marp.app/directives
[marpit-images]: https://marpit.marp.app/image-syntax
[marp-directives]: https://github.com/marp-team/marp/blob/main/website/docs/guide/directives.md
[deepwiki-syntax]: https://deepwiki.com/marp-team/marp/3.1-directives-and-syntax
[marp-cheatsheet]: https://miriam-mueller.com/MarpCheatsheet.pdf

## Minimal deck

Start every deck with YAML front matter. Use `paginate: false` so the presentation has no slide
numbers.

```markdown
---
marp: true
theme: genetics
size: 16:10
paginate: false
title: "Lecture title"
---

<!-- _class: title-slide -->

# Lecture title

## Course name
## Presenter name

---

<!-- _class: title-content -->

# First topic

- First point
- Second point
```

The opening pair of `---` lines encloses the front matter. Every later `---` line starts a new
slide.

## Standard and local syntax

The source combines standard Marp syntax with a small repository-specific authoring contract.

| Source feature | Meaning in this repository |
| --- | --- |
| YAML front matter | Standard Marp syntax, restricted to the supported keys below |
| `---` after front matter | Standard Marp slide separator |
| Headings, paragraphs, lists, images, and links | Standard Markdown with the limits below |
| `<!-- _class: ... -->` | Standard scoped Marp class syntax with required local layout names |
| `<!-- _paginate: ... -->` | Standard scoped Marp syntax for one slide |
| `theme: genetics` | Repository theme used for authoring previews |
| Top-level blockquotes in cell layouts | Repository interpretation: ordered layout cells |
| `font-size-N` classes | Repository title-size modifiers |
| Native PPTX and ODP output | Repository-owned Python behavior, not Marp CLI rendering |

The CSS theme provides an authoring preview and visual reference. Python owns production geometry,
pagination, validation, and native object creation.

## Front matter

The production parser accepts exactly these keys:

| Key | Requirement |
| --- | --- |
| `marp` | Required; use `true` |
| `theme` | Required; use `genetics` |
| `size` | Required; use `16:10` |
| `paginate` | Use `false` for the repository's no-page-number convention |
| `title` | Optional string used as presentation metadata |

Write `paginate: false` explicitly. The CSS theme cannot set pagination, and the parser currently
treats an omitted value as `true`.

## Slide directives

Every non-skipped slide declares exactly one supported layout class on its own line:

```markdown
<!-- _class: title-content -->
```

The leading underscore makes `_class` a scoped Marp directive for the current slide. The production
parser requires the scoped form and rejects unsupported directives.

Add at most one title-size modifier beside the layout class:

```markdown
<!-- _class: centered-text font-size-120 -->
```

Supported modifiers are `font-size-64`, `font-size-80`, `font-size-96`, `font-size-120`,
`font-size-160`, and `font-size-200`. The modifier applies only to the slide's direct H1 and must
fit within that layout's title region.

## Pagination

Keep page numbers off for the complete deck in front matter:

```yaml
paginate: false
```

Use `_paginate` only for a one-slide exception:

```markdown
<!-- _paginate: true -->
```

The underscore means the setting applies only to the current slide. A slide-level
`<!-- _paginate: false -->` is redundant when front matter already contains `paginate: false`.
Pagination is output behavior, so hiding a CSS pseudo-element is not a substitute for the directive.

## Layout vocabulary

Cells appear in Markdown reading order. Grid descriptions below use that same order.

| Layout class | Required source shape |
| --- | --- |
| `blank` | No authored content |
| `title-only` | One H1 |
| `title-slide` | One H1 followed by optional H2 subtitle lines |
| `centered-text` | One H1 followed by optional H2 subtitle lines |
| `title-content` | One H1 and text body, list body, or one component image |
| `title-two-content` | One H1 and two cells arranged left, right |
| `title-content-and-two-content` | One H1 and left, upper-right, lower-right cells |
| `title-two-content-and-content` | One H1 and upper-left, lower-left, right cells |
| `title-content-over-content` | One H1 and upper, lower cells |
| `title-two-content-over-content` | One H1 and upper-left, upper-right, lower cells |
| `title-four-content` | One H1 and four cells in a two-by-two grid |
| `title-six-content` | One H1 and six cells in a three-column, two-row grid |
| `vertical-title-vertical-text` | One vertical H1 and one vertical root body block |
| `vertical-title-text-chart` | One vertical H1 and two cells arranged left, right |
| `title-vertical-text` | One H1 and one vertical root body block |
| `title-two-vertical-text-clipart` | One H1, two stacked left cells, and one tall right cell |
| `gallery` | Optional H1 and two through six standalone component images |

Use `title-content` for an ordinary list or a single image. Use `gallery` for a row of related
images. Use a cell layout only when the slide needs distinct content regions.

## Content cells

Standard Markdown uses `>` for a blockquote. In this repository, each top-level blockquote in a
multi-cell layout becomes one layout cell. This is a repository-specific interpretation.

This is the current accepted syntax. The planned Marp+ contract replaces it with explicit named
`_cell` markers so `>` can return to ordinary blockquote meaning. Do not author `_cell` yet; track
the coordinated migration in [ROADMAP.md](ROADMAP.md) and [TODO.md](TODO.md).

```markdown
<!-- _class: title-two-content -->

# Types of gene disorders

> ## Main categories
>
> - Point mutation
> - Deletion
> - Translocation

> ## Visual example
>
> ![Chromosome rearrangement](assets/lecture/chromosome.png)
```

Follow these cell rules:

- Supply exactly the number of cells required by the layout.
- Put cells in visual reading order.
- Start a cell with at most one optional H2.
- Use paragraphs and lists together as editable text content when needed.
- Use one or more standalone component images as image content when needed.
- Keep text and component images in separate cells.
- Keep cells top-level and do not nest blockquotes.

Because `>` identifies a layout cell in these layouts, use quoted wording as ordinary text rather
than a top-level Markdown blockquote.

## Text and lists

Supported editable text includes:

- Paragraphs.
- Bulleted lists using `-`.
- Numbered lists using `1.` or another integer start.
- Nested bulleted and numbered lists.
- Bold text using `**bold**`.
- Emphasis using `*emphasis*`.
- Inline code using backticks.
- Explicit and soft line breaks.

Use an H1 for the slide title. Use H2 only for subtitle lines in title layouts or for an optional
cell heading.

## Links

Use ordinary Markdown links with an absolute `http`, `https`, or `mailto` destination:

```markdown
[Course resource](https://example.edu/resource)
```

A displayed literal URL uses PT Sans Narrow in native output. A descriptive linked label retains
OpenDyslexic.

## Images

Write component images as standalone Markdown images with meaningful alt text:

```markdown
![Chromosome rearrangement](assets/lecture/chromosome.png)
```

Image sources must be repository-relative files inside the repository. Keep explanations as
editable Markdown instead of baking them into a full-slide image. Retired `slide_*_source` images,
remote images, data URLs, background-image modifiers, and full-slide raster fallbacks are rejected.

Do not mix an image with inline text in the same paragraph. Put multiple gallery images on one line
or separate lines:

```markdown
![Column](column.png) ![Console](console.png) ![Researchers](researchers.png)
```

## Presenter notes

Write presenter notes as a standalone HTML comment. The comment must occupy its own source lines.

```markdown
<!-- notes: Explain why the deletion changes the reading frame. -->
```

Use a multiline comment for longer notes:

```markdown
<!--
Compare this image with the previous chromosome.
Pause before revealing the clinical consequence.
-->
```

Notes become editable presenter notes in PPTX and ODP. They do not appear on the projected slide.

## Unsupported syntax

The native pipeline reports a source path and line number for unsupported constructs. Do not use:

- Front-matter keys outside the five documented above.
- Unscoped or unsupported slide directives.
- Raw HTML or XML slide content.
- Markdown tables.
- Fenced or indented code blocks.
- Strikethrough, fragmented-list markers, emoji conversion, or `<!-- fit -->` headings.
- Marp Core v5 plugin syntax for Shiki highlighting, Mermaid diagrams, or math typesetting.
- Background-image syntax or per-image pixel geometry.
- Inline text mixed with an image.
- Remote or data-URL component images.
- Nested layout cells.
- More than one layout class or title-size modifier on a slide.
- Marp Core v4 or earlier compatibility behavior and highlight.js theme contracts.

These restrictions keep every accepted source feature mapped to a validated native editable object.
They are current behavior, not a promise to implement every upstream feature. See
[ROADMAP.md](ROADMAP.md) for planned capability boundaries and [TODO.md](TODO.md) for immediate
next actions.

## External links

Use these primary upstream references:

- [Marp Core v5 Markdown guide][core-v5-markdown]
- [Marp Core v5 migration guide][core-v5-migration]
- [Marpit directives][marpit-directives]
- [Marpit image syntax][marpit-images]
- [Official Marp directives][marp-directives]

Use these secondary quick references:

- [DeepWiki directives and syntax overview][deepwiki-syntax]
- [Miriam Mueller's Marp cheat sheet][marp-cheatsheet]

The primary sources explain upstream Marp behavior. This guide remains the authority for the
narrower syntax accepted by the native pipeline.

## Build validation

Build one deck to validate its syntax and native layout:

```bash
source source_me.sh && python3 tools/marp_export.py genetics/lecture.md --format pptx
```

Parser and layout diagnostics identify the authored source line that needs correction. See
[USAGE.md](USAGE.md) for import, folder-build, ODP, PDF, and validation workflows, and
[PIPELINE.md](PIPELINE.md) for implementation ownership.
