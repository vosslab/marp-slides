# Usage

Use repository-owned `.md` Marp or `.djot` extended-Djot source to produce editable PPTX, ODP, and
ODP-derived PDF output. Legacy presentation import is a one-time source migration workflow.

## Build native decks

Write editable PPTX for one source deck:

```bash
source source_me.sh && python3 tools/marp_to_pptx.py genetics/lect01b-genetic_disorders.md
```

Write editable PPTX and ODP for one source deck:

```bash
source source_me.sh && python3 tools/marp_to_odp.py genetics/lect01b-genetic_disorders.md
```

Select one output format for a deck or a folder of direct-child source files:

```bash
source source_me.sh && python3 tools/marp_export.py genetics/djot --format pdf
source source_me.sh && python3 tools/marp_export.py genetics/lect01b-genetic_disorders.md --format pptx
```

Build every eligible Marp Markdown deck directly in a folder as PPTX, ODP, and PDF:

```bash
./build_slides.sh genetics
```

`tools/marp_export.py` accepts `--format all`, `odp`, `pdf`, or `pptx`; `all` is the default. It
recognizes `.md` and `.djot` source by suffix. Folder discovery considers only direct-child source
files and skips Markdown that lacks opening `marp: true` front matter. Outputs are written below
`output/pptx/`, `output/odp/`, and `output/pdf/`.

## Import legacy slides

Import a trusted ODP into a new extended-Djot deck and adjacent asset directory:

```bash
source source_me.sh && python3 tools/odp_to_djot.py genetics/lecture.odp --output genetics/lecture.djot
```

Import a trusted PPTX directly when it is the source evidence:

```bash
source source_me.sh && python3 tools/pptx_to_djot.py genetics/lecture.pptx --output genetics/lecture.djot
```

The importer refuses an existing `.djot` output or its asset directory. It keeps text, tables when
their native source metadata is available, ordinary images, and geometry-supported layouts
editable. Where a coupled visual component cannot be reconstructed faithfully, it writes a bounded
title-excluded source-region PNG in `assets/<deck>/`; it never requests a full-slide raster.

This is a one-time migration aid. Choose and maintain one canonical source after review; legacy ODP
or PPTX does not become a second authoring source. See [PIPELINE.md](PIPELINE.md) for ownership and
[genetics/djot/README.md](../genetics/djot/README.md) for the regenerable corpus boundary.

## Validate Djot source

Run the fast, source-only structural check while authoring:

```bash
source source_me.sh && python3 tools/djot_slide_lint.py genetics/djot
```

Before a Djot source-acceptance decision, run the separate strict native-parser gate followed by
the same semantic lint:

```bash
source source_me.sh && python3 tools/djot_slide_lint.py \
  --require-native --native-executable "$(command -v jotdown)" genetics/djot
```

Fast lint is a permanent, offline behavior check. Strict Jotdown validation, real native export,
and visual/Office review are one-time acceptance evidence, not replacements for each other. The
LibreOffice Impress animation implementation, structural tests, headless PPTX-to-ODP package
inspection, and PDF final-state export have passed. Attended click playback in Impress remains the
sole open visual gate; do not infer it from a successful export. See [ROADMAP.md](ROADMAP.md).

## Authoring boundaries

For classic Marp source, use the supported subset in [MARP_SYNTAX_GUIDE.md](MARP_SYNTAX_GUIDE.md).
For extended-Djot, begin each slide with `=== layout: <name>` and use `@<slot>` only where that
layout declares a slot. The layout registry is the authority for supported names and capacity;
source-located diagnostics identify unsupported or overflowing content instead of approximating it.

Keep source explanations, lists, links, and ordinary images as editable content. Use complete image
paragraphs for component images. Tables and source-region components have their own native or
bounded-image ownership; raw HTML and raw XML are not authoring inputs.

## Known gaps

- [ ] Record attended LibreOffice Impress click playback before claiming native animation playback
  support.
