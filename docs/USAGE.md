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

Use [MARP_SYNTAX_GUIDE.md](MARP_SYNTAX_GUIDE.md) as the concise authoring contract for front matter,
directives, layouts, content cells, pagination, supported Markdown, and native-pipeline limits.

Each slide has exactly one explicit Marp class directive. The directive selects a native builder,
not a CSS renderer. The class must be one of the layout names in [PIPELINE.md](PIPELINE.md).

For an enlarged display title, add one bounded font-size class beside the layout class. The order is
ordinary Marp multi-class syntax, so either order is valid. The size applies only to the direct H1
and remains editable in PPTX; `font-size-200` is 200 CSS px (150 Office pt).

```markdown
<!-- _class: centered-text font-size-200 -->
# THE END
```

Use exactly one layout class and zero or one of `font-size-64`, `font-size-80`, `font-size-96`,
`font-size-120`, `font-size-160`, or `font-size-200`. A requested H1 size must fit its native title
region; choose a smaller preset, shorter title, or different layout when the source-located export
diagnostic reports that it does not fit.

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

Use the general command when selecting one format from either one deck or one folder:

```bash
source source_me.sh && python3 tools/marp_export.py genetics --format pdf
source source_me.sh && python3 tools/marp_export.py genetics/lecture.md --format pptx
```

Folder discovery examines only direct-child `*.md` files, sorts them by path, and skips Markdown
without `marp: true` in its opening front matter. A terminal build shows one transient line for the
current deck's parsing, PPTX, ODP, or PDF stage. Successful output leaves one borderless table with
relative deck names and artifact sizes, followed by the output directories and one elapsed total.
Redirected output is static and contains no ANSI styling. Expected input, parsing, and conversion
failures use one concise stderr panel and a nonzero status; unexpected defects retain a traceback.

Close the LibreOffice desktop application before any command that invokes it, including one-time
ODP import and ODP/PDF builds. The shared conversion code uses `--headless --norestore` through the
established user profile. Use LibreOffice's `--safe-mode` only when diagnosing or repairing a
profile problem.

The ODP-to-PDF step uses LibreOffice's `impress_pdf_Export` filter with 70 percent JPEG quality,
150 DPI image reduction, and PDF/A-3b output. LibreOffice documents 75, 150, 300, 600, and 1200 as
the supported image-resolution limits; 150 is the supported ceiling used in place of 100 DPI.

The folder build emits `output/pptx/lecture.pptx`, `output/odp/lecture.odp`, and
`output/pdf/lecture.pdf`. It runs all selected decks in one Python process and always makes PDF by
converting the produced ODP, never by creating a parallel PDF branch from PPTX. LibreOffice stdout
and stderr remain hidden after success and appear as concise diagnostics only after failure.

## Validate output

Run the native semantic E2E gate from an ordinary macOS user session:

```bash
source source_me.sh && python3 tests/e2e/e2e_native_odp_semantics.py
```

The exporter invokes LibreOffice with `--headless --norestore` from the current macOS user session.
The gate verifies native semantic objects and the PPTX-to-ODP-to-PDF order. Rendered PDF pages are
visual QA evidence only.

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

The local `OTHER_REPOS/marp-core` and `OTHER_REPOS/marp-cli` clones help interpret the adopted Marp
Core v5 language and design conformance fixtures. The production build does not import, execute, or
depend on either clone. See [RELATED_PROJECTS.md](RELATED_PROJECTS.md).
