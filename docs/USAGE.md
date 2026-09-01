# Usage

The pipeline is deliberately one-way:

```text
legacy ODP -> temporary PPTX -> Python object extraction -> Marp Markdown -> classroom ODP
```

Marp Markdown and its assets become the editable source of truth. The generated ODP is the file to
open in LibreOffice Impress for class, not a source to edit and import again.

## Import one legacy ODP

Activate Python 3.12 and run the importer:

```bash
source source_me.sh && python3 tools/odp_to_marp.py genetics/lecture.odp
```

By default this writes:

- `genetics/lecture.md`; and
- `genetics/assets/lecture/` for extracted content images.

To create a review draft elsewhere, use an explicit new output path:

```bash
source source_me.sh && python3 tools/odp_to_marp.py \
  genetics/lecture.odp --output output/import_preview/lecture.md
```

The importer will not overwrite an existing Markdown file or asset directory. This protects a deck
after Markdown has become canonical.

### Trust the legacy input

Import only instructor-owned, trusted ODP files. Archive validation bounds the Python extraction
work, but the importer invokes LibreOffice to create a temporary geometry-normalized PPTX. That
validation does not sandbox LibreOffice. Keep the same trust boundary when building: Marp Markdown
and assets must be local, repository-owned teaching material.

## What the importer preserves

The importer converts the ODP to a temporary PPTX, then uses `python-pptx` to map every visible
source slide into editable Marp Markdown. It also:

- preserves list nesting and ordinary Unicode text;
- extracts embedded PNG and JPEG images under internally generated filenames;
- carries ODP speaker notes into Marp presenter-note comments;
- skips slides marked hidden by the normalized presentation; and
- uses source geometry to select a simple Marp layout rather than copying arbitrary coordinates.

The importer never uses a full-slide source render as converted content. A source render may be used
temporarily for visual comparison, but `slide_*_source.png` references are conversion failures and
must not appear in canonical or buildable Marp decks. OCR is not part of the normal workflow because
the legacy slides are structured authored documents, not scans.

## Clean up the Markdown

Edit the `.md` file and its local assets. Favor the layouts already supported by the genetics theme:

- a title or question;
- a title with a short bullet list;
- a title and one figure;
- a simple two-column text-and-figure slide; or
- a full-slide image when the original figure itself is the teaching content.

Preserve the source slide count and order while simplifying each slide. Do not edit the generated
ODP as a way to change course content.

Treat this cleanup as a post-conversion polish pass, not as more importer logic. Start with ordinary
Marp headings, lists, and advanced background images. For a text-and-image split, let a directive
such as `![bg right:42% contain](figure.png)` own the pane geometry; do not add a second class that
also reserves space on the right.

Use `contain` and let the layout provide the available image area. Do not add per-image pixel widths
or heights to make one render fit; fix the shared layout when its images do not auto-fit correctly.

The central genetics theme uses OpenDyslexic for all authored slide text and PT Sans Narrow for URL
text. Text that is naturally part of a screenshot or figure remains image content, but the slide's
headings, explanations, and lists must be Markdown so they inherit the theme.

### Header with one auto-fitting figure

Use the shared `figure` layout for a heading above one content image:

```markdown
<!-- _class: figure -->

# Blackboard website

![Blackboard course page](blackboard.png)
```

The figure consumes the remaining space below the heading and fits with `contain`; do not add a
per-image height or width.

### Header with left and right panes

Use the central `two-pane` theme layout when both sides need ordinary Markdown content. Each quoted
block becomes one pane, so the source needs no raw HTML or XML:

```markdown
<!-- _class: two-pane -->

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

The first heading spans the slide. The first and second quoted blocks become the left and right
panes. Put the image in either pane to reverse the visual emphasis. Repeated geometry belongs in
`themes/genetics.css`, not copied style blocks.

### Header with a three-image gallery

Use the shared `gallery` layout when one source slide contains three related visuals:

```markdown
<!-- _class: gallery -->

# Cryo-Electron Microscope

![Column](column.png) ![Console](console.png) ![Researchers](researchers.png)
```

The gallery preserves one teaching beat and one slide while keeping placement and automatic image
fitting in the central theme.

## Convert Marp to ODP

Run the destination-named converter when the classroom ODP is the goal:

```bash
source source_me.sh && python3 tools/marp_to_odp.py genetics/lecture.md
```

It generates:

- `output/pptx/lecture.pptx` as the required Marp interchange file; and
- `output/odp/lecture.odp` for presenting in LibreOffice Impress.

The converter intentionally does not create a PDF. To generate only the Marp-rendered PPTX, run:

```bash
source source_me.sh && python3 tools/marp_to_pptx.py genetics/lecture.md
```

## Build all classroom files

Run the bundle command when you want PDF, PPTX, and ODP together:

```bash
./build_slides.sh genetics/lecture.md
```

The bundle generates:

- `output/pdf/lecture.pdf` for review and distribution;
- `output/pptx/lecture.pptx` as the Marp interchange output; and
- `output/odp/lecture.odp` for presenting in LibreOffice Impress.

Both ODP commands use Marp's rendered PPTX pages, then LibreOffice conversion. This current baseline
is visually faithful but flattened, so its ODP is not intended for content editing. Make corrections
in Markdown and rebuild. It is a tested baseline, not a permanent decision that rules out a future
repository-owned output implementation.

### Editable PPTX is a manual experiment

Marp 4.5 also offers `--pptx-editable`, which tries to create native PowerPoint objects instead of
the ordinary rendered PPTX pages. It is not used by `build_slides.sh`: in the 23-slide bakeoff it
lost all presenter notes and visibly broke the Markdown-only two-pane geometry. You may try it
manually for a simple slide deck, but do not use it as the normal classroom path or expect it to
preserve notes and layout. Neither normal workflow requires VS Code.

## Click-to-reveal teaching sequences

Marp's browser-only fragmented lists do not become native ODP animations. Use consecutive build
slides instead. For example, reveal a multiple-choice answer on the next click:

```markdown
# Which mutation changes one nucleotide?

- A. Deletion
- B. Point mutation
- C. Translocation

---

# Which mutation changes one nucleotide?

- A. Deletion
- **B. Point mutation**
- C. Translocation
```

Use the same pattern for an image: duplicate the explanatory slide, then add the image to the second
copy. LibreOffice treats the next build as an ordinary slide advance, so the sequence remains
reliable in ODP, PPTX, and PDF.

## Import limits

The importer accepts one ZIP-based `.odp` at a time and enforces these defensive limits:

- 256 MiB compressed input;
- 512 MiB total expanded members;
- 128 MiB per archive member; and
- 2,000 archive members.

See [INSTALL.md](INSTALL.md) for system setup and the Marp security boundary.

## Future output experiments

The cloned projects are useful prior art, not part of this pipeline. They are not renderers,
dependencies, or second Markdown dialects for these lectures. If a classroom need appears later,
their ideas about reference-PPTX geometry, image fitting, notes, ODP writing, or native objects may
inform a narrow, repository-owned Python tool. There is no current adoption and no click-object
animation solution. See [RELATED_PROJECTS.md](RELATED_PROJECTS.md) for the full inventory and the
specific ideas and limitations of each clone.
