# Pipeline architecture

This repository owns a native-object presentation pipeline. Marp Markdown is the canonical
authoring language; the local implementation interprets its supported subset and never calls Marp
code, Marp CLI, a browser, or a rendered-slide converter.

## Component map

```text
ONE-TIME IMPORT

trusted legacy ODP -> LibreOffice temporary PPTX -> semantic importer -> Marp Markdown + assets

REPEATABLE BUILD

canonical Marp Markdown
  -> marp_lib.terminal_output
  -> marp_lib.marp_parser
  -> typed native slide-object model
  -> marp_lib.layouts
  -> python-pptx editable PPTX
  -> LibreOffice editable ODP
  -> LibreOffice PDF from that ODP
```

The PDF path is intentionally downstream of editable ODP. Rendering a final ODP-derived PDF for
visual QA is separate from the production object-conversion chain and never supplies slide content.

## Ownership boundaries

| Owner | Responsibility | Artifact |
| --- | --- | --- |
| `tools/odp_to_marp.py` | Trusted legacy ODP import | Canonical Markdown and assets |
| `tools/pptx_to_marp.py` | Structured PPTX extraction | Import records and Markdown |
| `marp_lib/marp_parser.py` | Marp-subset framing, directives, and block parsing | Typed slide model |
| `marp_lib/layouts.py` | Registry and native geometry for every supported layout | Editable PPTX objects |
| `marp_lib/libreoffice.py` | Process preflight, conversion, and PDF filter | PPTX, ODP, and PDF conversions |
| `marp_lib/native_export.py` | Deck discovery, export stages, notes, pagination, and paths | Ordered deck and artifact paths |
| `marp_lib/terminal_output.py` | Transient progress, summaries, and expected failures | One concise Rich interface |
| `tools/marp_export.py` | One-deck or direct-child folder command | Selected PPTX, ODP, and PDF outputs |
| `tools/marp_to_pptx.py` | One-deck editable PPTX command | PPTX |
| `tools/marp_to_odp.py` | One-deck editable ODP command | PPTX and ODP |
| `build_slides.sh` | Environment bootstrap for the folder command | One Python batch process |

`terminal_output` invokes `native_export`, which imports the layout and LibreOffice owners. None of
those lower-level owners imports the terminal interface. This one-way boundary keeps presentation,
parsing, geometry, conversion, and artifact orchestration separate.

## Native layout contract

`marp_lib.layouts` has one distinct builder for each LibreOffice layout-grid entry:

- `blank`
- `title-only`
- `title-slide`
- `title-content`
- `centered-text`
- `title-two-content`
- `title-content-and-two-content`
- `title-two-content-and-content`
- `title-content-over-content`
- `title-two-content-over-content`
- `title-four-content`
- `title-six-content`
- `vertical-title-vertical-text`
- `vertical-title-text-chart`
- `title-vertical-text`
- `title-two-vertical-text-clipart`
- `gallery`

The first sixteen names are the LibreOffice grid catalog. `gallery` is a repository layout for a
contained image row. LibreOffice is not asked to apply the grid: Python creates the text boxes,
lists, images, shapes, and vertical text direction directly through `python-pptx`.

Each slide declares exactly one `_class`. For layouts with content cells, top-level blockquotes
supply cells in reading order. A cell may have an optional H2 heading and native Markdown body/list
content or contained component images. `gallery` accepts a slide title and two through six
component images; use `title-content` for one image. Layout validation reports unsupported or
overflowing source rather than emitting a raster fallback.

An `_class` directive may also contain one bounded title-size modifier: `font-size-64`,
`font-size-80`, `font-size-96`, `font-size-120`, `font-size-160`, or `font-size-200`. The parser
stores it as a source-located typed request and the layout writer applies it only to the top-level
editable H1. It never changes subtitles, bodies, cells, links, or pagination. An explicit request
that cannot fit its assigned native title region fails at the H1 source line instead of shrinking.

## Marp-language boundary

The repository adopts Marp Core v5 only for its mature authoring-language specification.
Repository-owned Python handles the selected vocabulary: opening YAML front matter, slide
separators, `_class` and `_paginate` directives, headings, paragraphs,
formatted/link/inline-code runs, nested lists, standalone component images, blockquote cells, and
presenter-note comments. Tables plus fenced or indented code are source-located rejections until a
native editable-object owner is added. Other unsupported constructs also fail with a source path
and line number.

`OTHER_REPOS/marp-core` and `OTHER_REPOS/marp-cli` are local reference and conformance evidence.
The Marp Core snapshot is v5.0.1; v4 and earlier behavior is not a compatibility target. Both
clones are outside the runtime graph. Their HTML/browser and raster export paths are neither
invoked nor bundled.

## Verification lanes

| Lane | Establishes |
| --- | --- |
| Fast Python tests | Parser, layout validation, native object construction, and source diagnostics |
| Native semantic E2E | PPTX/ODP text, lists, links, notes, component images, counts, and no full-slide image |
| ODP-derived PDF review | Final-page containment and visual teaching clarity |

No one lane proves the complete product. Fast tests cannot prove LibreOffice conversion, and a
rendered page cannot prove editability. The E2E build verifies the ordered PPTX-to-ODP-to-PDF path.

## Durable source boundary

After one-time import, only canonical Markdown and its local assets are edited. PPTX, ODP, and PDF
are reproducible products. This prevents competing authoring sources while retaining editable
LibreOffice files for teaching.

See [HUMAN_GUIDANCE.md](HUMAN_GUIDANCE.md), [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md), and
[USAGE.md](USAGE.md) for the corresponding requirement, rationale, and authoring contract.
