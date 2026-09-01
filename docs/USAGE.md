# Usage

The pipeline is deliberately one-way:

```text
legacy ODP -> one-time Python import -> Marp Markdown -> PDF/PPTX -> classroom ODP
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
- `genetics/assets/lecture/` for extracted images and source-rendered fallbacks.

To create a review draft elsewhere, use an explicit new output path:

```bash
source source_me.sh && python3 tools/odp_to_marp.py \
  genetics/lecture.odp --output output/import_preview/lecture.md
```

The importer will not overwrite an existing Markdown file or asset directory. This protects a deck
after Markdown has become canonical.

### Trust the legacy input

Import only instructor-owned, trusted ODP files. Archive, XML, and image validation bounds the
Python extraction work, but a complex slide can require LibreOffice fallback rendering. That
validation does not sandbox LibreOffice. Keep the same trust boundary when building: Marp Markdown
and assets must be local, repository-owned teaching material.

## What the importer preserves

Simple title, question, bullet, and figure slides become editable Markdown. The importer also:

- preserves list nesting and ordinary Unicode text;
- extracts embedded PNG and JPEG images under internally generated filenames;
- carries ODP speaker notes into Marp presenter-note comments;
- skips ODP slides explicitly marked hidden, including inherited drawing-page styles; and
- validates archive paths, member counts, compressed size, expanded size, XML, and image signatures.

Dense slides, unsupported image formats, and slides with positioned drawing geometry become
full-slide PNG fallbacks. Their source text and the fallback reason remain in a presenter-note
comment. The deck is immediately presentable, and each fallback identifies a slide that still needs
manual simplification.

## Clean up the Markdown

Edit the `.md` file and its local assets. Favor the layouts already supported by the genetics theme:

- a title or question;
- a title with a short bullet list;
- a title and one figure;
- a simple two-column text-and-figure slide; or
- a full-slide image when the original figure itself is the teaching content.

Replace source-rendered fallback slides gradually with concise Markdown. Do not edit the generated
ODP as a way to change course content.

Treat this cleanup as a post-conversion polish pass, not as more importer logic. Start with ordinary
Marp headings, lists, and advanced background images. For a text-and-image split, let a directive
such as `![bg right:42% contain](figure.png)` own the pane geometry; do not add a second class that
also reserves space on the right.

The central genetics theme uses OpenDyslexic for all authored slide text and PT Sans Narrow for URL
text. Text contained inside screenshots, figures, or full-slide source-fallback PNGs is raster
content and cannot inherit either theme font. Reauthor a fallback as Markdown when its legacy text
needs to adopt the current typography.

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
