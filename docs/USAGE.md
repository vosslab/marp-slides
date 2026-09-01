# Usage

## One-time import

Import an instructor-owned legacy ODP once:

```bash
source source_me.sh && python3 tools/odp_to_marp.py genetics/lecture.odp
```

The importer uses LibreOffice only to make a temporary structured PPTX for extraction. It preserves
text, images, notes, visibility, and sequence for human cleanup. Edit the resulting Markdown and
assets; generated ODP is never a second source of course content.

Import an already trusted PPTX when that is the source evidence:

```bash
source source_me.sh && python3 tools/pptx_to_marp.py genetics/lecture.pptx
```

## Author a native slide

Each slide has exactly one explicit Marp class directive. The directive selects a native builder,
not a CSS renderer. The class must be one of the layout names in [PIPELINE.md](PIPELINE.md).

```markdown
---

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

The H1 is the slide title. Top-level blockquotes are cells in the layout's reading order. Each cell
can begin with an H2, then contain paragraphs, formatted/link/inline-code runs, nested lists, or
ordinary component images. Image alt text becomes the native image description. Keep image text as
image content, but author slide explanations and lists as Markdown.

Use opening YAML front matter, slide separators, `_class` and `_paginate` directives, and standalone
presenter-note comments from the supported Marp subset. Tables plus fenced or indented code are
rejected with their source location until a native editable-object owner is added.

Use `gallery` for two through six related component images. Use `title-content` for one image:

```markdown
---

<!-- _class: gallery -->

# Cryo-electron microscope

![Column](column.png) ![Console](console.png) ![Researchers](researchers.png)
```

Use the remaining named layouts when their cell count and reading order fit the teaching beat. The
registry validates all source content before creating output. Keep every object inside the 1280x800
frame; shared layout code owns geometry and `contain` image fitting.

The shared CSS theme is an authoring preview and visual reference. It does not provide production
geometry. Avoid raw HTML, raw XML, pixel dimensions, layout background-image directives, and retired
class names in canonical source.

## Build a deck

Write only native editable PPTX:

```bash
source source_me.sh && python3 tools/marp_to_pptx.py genetics/lecture.md
```

Write native PPTX and editable ODP:

```bash
source source_me.sh && python3 tools/marp_to_odp.py genetics/lecture.md
```

Build PPTX, editable ODP, and PDF for every Marp deck directly in a folder:

```bash
./build_slides.sh genetics
```

The folder build emits `output/pptx/lecture.pptx`, `output/odp/lecture.odp`, and
`output/pdf/lecture.pdf`. It always makes PDF by converting the produced ODP, never by creating a
parallel PDF branch from PPTX.

## Validate output

Run the native semantic E2E gate from a macOS GUI-capable host session:

```bash
source source_me.sh && python3 tests/e2e/e2e_native_odp_semantics.py
```

The exporter invokes LibreOffice with `--headless`, but macOS initialization requires a host GUI
session outside the restricted execution sandbox. The gate verifies native semantic objects and the
PPTX-to-ODP-to-PDF order. Rendered PDF pages are visual QA evidence only.

## Classroom reveals

Use consecutive slides for click-to-reveal teaching sequences:

```markdown
<!-- _class: title-content -->

# Which mutation changes one nucleotide?

- A. Deletion
- B. Point mutation

---

<!-- _class: title-content -->

# Which mutation changes one nucleotide?

- A. Deletion
- **B. Point mutation**
```

## Import limits and trust

Import only trusted instructor-owned presentations. Both importers enforce archive and decoded-image
limits, but validation does not sandbox LibreOffice. See [INSTALL.md](INSTALL.md) for the full
trust boundary.

The local `OTHER_REPOS/marp-core` and `OTHER_REPOS/marp-cli` clones help interpret the Marp
language and design conformance fixtures. The production build does not import, execute, or depend
on either clone. See [RELATED_PROJECTS.md](RELATED_PROJECTS.md).
