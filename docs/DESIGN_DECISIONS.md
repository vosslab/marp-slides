# Design decisions

<!-- VENDORED HEADER: START -->
Record each durable decision about how this code and repository are shaped, once it is settled, with
the reasoning a later reader needs. Guidance Neil Voss states belongs in
[HUMAN_GUIDANCE.md](HUMAN_GUIDANCE.md), dated history in `docs/CHANGELOG.md`, open discussion in
`docs/active_plans/decisions/`. [PROPAGATED HEADER - ENTRIES BELOW ARE YOURS]
<!-- VENDORED HEADER: END -->

## Native presentation design

### Marp is an authoring-language specification

**Decision.** Retain canonical Marp Markdown, adopt Marp Core v5 as the only upstream authoring
baseline, and independently implement its supported language subset in repository-owned Python.

**Why.** Marp Core v5 offers a mature authoring language and separates built-in behavior from
optional plugins. Its runtime and browser render paths do not meet the editable native-object
product requirement.

**Consequence.** `OTHER_REPOS/marp-core` and `OTHER_REPOS/marp-cli` are conformance evidence only.
The production dependency graph contains no Marp code, CLI, Node, browser, or render stage.
The author-facing contract distinguishes standard Marp Core v5 syntax from repository-specific
meanings. Marp Core v4 and earlier behavior is not supported. Optional v5 Shiki, Mermaid, KaTeX,
and MathJax features require explicit native capability decisions rather than implicit `/full`
compatibility. The current local evidence snapshot is Marp Core 5.0.1 at commit `06c5a54`.

**Owner.** `marp_lib/marp_parser.py`, [MARP_SYNTAX_GUIDE.md](MARP_SYNTAX_GUIDE.md),
[ROADMAP.md](ROADMAP.md), and [PIPELINE.md](PIPELINE.md).

### Native layout registry owns geometry

**Decision.** Implement all sixteen LibreOffice layout-grid patterns and `gallery` as distinct
native builders in `marp_lib/layouts.py`.

**Why.** Editable output needs predictable native text, list, image, and shape regions. The
LibreOffice grid provides a useful visual catalog, but applying it after conversion would not create
the required objects.

**Consequence.** Every canonical slide selects one class. Top-level blockquotes provide multi-cell
content in reading order. `native_export` imports the registry one way; CSS remains preview styling
and does not determine output geometry.

**Owner.** `marp_lib/layouts.py` and `docs/USAGE.md`.

### Bounded H1 display-size classes

**Decision.** Accept one optional Marp multi-class modifier from `font-size-64`, `font-size-80`,
`font-size-96`, `font-size-120`, `font-size-160`, and `font-size-200` beside exactly one layout
class.

**Why.** An authored display title needs predictable editable scale without a new repository-only
numeric directive or a browser-rendered exception.

**Consequence.** The parser retains a typed, source-located H1 request; native layout code applies
the CSS-pixel value only to the top-level H1 and rejects a title that cannot fit its title region.
Subtitles, body text, cells, links, notes, and pagination remain layout-defined.

**Owner.** `marp_lib/native_model.py`, `marp_lib/marp_parser.py`, `marp_lib/layouts.py`, and
`themes/genetics.css`.

### Explicit named cell markers replace blockquote cells

**Decision.** Migrate multi-cell slides to repository-owned `<!-- _cell: <slot> -->` markers, with
slot names defined by the selected layout class.

**Why.** Standard Markdown already assigns `>` to blockquotes. A named marker states placement
directly, keeps `-` unambiguously available for list items, and avoids depending on cell order for
geometry.

**Consequence.** The parser, native model, layout registry, importers, canonical decks, preview
behavior, tests, and documentation migrate together. Generic Marp ignores the comments and shows a
readable sequential fallback; the production parser owns native placement. The current
blockquote-as-cell syntax remains authoritative only until the coordinated pre-production migration
in [ROADMAP.md](ROADMAP.md) is complete.

**Owner.** [ROADMAP.md](ROADMAP.md), `marp_lib/marp_parser.py`, `marp_lib/native_model.py`,
`marp_lib/layouts.py`, and `themes/genetics.css`.

### ODP-derived PDF is the only PDF path

**Decision.** Generate PPTX first, convert it to editable ODP, then have LibreOffice create PDF from
that ODP.

**Why.** One ordered pathway avoids a second PDF implementation and makes the distributed PDF
represent the editable classroom artifact.

**Consequence.** `build_slides.sh` retains the PPTX, ODP, and ODP-derived PDF artifacts. PDF review
rendering remains evidence only and never becomes slide content.

**Owner.** `marp_lib/native_export.py`, `build_slides.sh`, and
`tests/e2e/e2e_native_odp_semantics.py`.

### LibreOffice conversion uses its established profile

**Decision.** Run batch conversions with `--headless --norestore` and LibreOffice's established
user profile after confirming that the main desktop application is closed.

**Why.** A brand-new `-env:UserInstallation` directory forces first-profile initialization for
each conversion and produces a macOS task-policy diagnostic. LibreOffice already owns normal and
safe-mode profile behavior.

**Consequence.** Temporary directories contain converted artifacts only. `--safe-mode` is available
for explicit profile repair rather than routine isolation, and `--headless` already supplies the
non-visual batch mode. ODP-to-PDF conversion uses `impress_pdf_Export`, 70 percent JPEG quality,
150 DPI image reduction, and `SelectPdfVersion=3` for PDF/A-3b. The 150 DPI limit replaces the
unsupported 100 DPI value with the next documented resolution.

**Owner.** `marp_lib/libreoffice.py` and all LibreOffice conversion callers.

### One terminal owner presents every build

**Decision.** Route folder builds and destination-named single-deck commands through one Rich
terminal interface. Keep `build_slides.sh` as a bootstrap wrapper and keep artifact generation free
of permanent per-stage logging.

**Why.** One presentation owner can show transient current work while leaving a concise,
consistent, redirect-safe result for every command.

**Consequence.** `marp_export.py` accepts a file or folder in one Python process. Folder discovery
selects sorted direct-child Marp Markdown, successful LibreOffice output stays captured, and
expected failures receive a concise stderr panel. Unexpected defects retain their traceback.

**Owner.** `marp_lib/terminal_output.py`, `marp_lib/native_export.py`, and `build_slides.sh`.

### Native objects replace slide rasterization

**Decision.** Native text, lists, shapes, component images, links, and notes are the only normal
output objects.

**Why.** A full-slide image loses editability, searchability, accessibility, and durable layout
ownership.

**Consequence.** Source features without an explicit native mapping fail with an actionable source
diagnostic. Temporary visual renders may support QA but never enter canonical Markdown or output.

**Owner.** `marp_lib/layouts.py`, `marp_lib/native_export.py`, and their tests.

### Vertical root-body layouts use one author-visible block

**Decision.** `title-vertical-text` and `vertical-title-vertical-text` accept exactly one root body
block after the level-one title: a paragraph, list, or component image.

**Why.** The one authored block maps directly to one native vertical text frame or contained image
region without inventing a repository-specific Markdown wrapper language.

**Consequence.** Preview and native geometry share the fixed 94px title, 24px spacer, and 1042px
body tracks. `vertical-title-text-chart` uses 94px, 24px, 500px, 42px, and 500px tracks with
explicit child placement.

**Owner.** `marp_lib/layouts.py`, `themes/genetics.css`, and their contract tests.

## Canonical source design

### Markdown is the editable source

**Decision.** Import legacy ODP once, then make the generated Markdown and local assets the sole
editable source.

**Why.** One canonical state prevents Markdown, PPTX, and ODP from silently diverging.

**Consequence.** Generated artifacts are reproducible. Legacy ODP and temporary normalization PPTX
remain migration evidence, not future editing surfaces.

**Owner.** `tools/odp_to_marp.py`, `tools/pptx_to_marp.py`, and `docs/USAGE.md`.

### Structured import replaces OCR

**Decision.** Extract legacy ODP/PPTX text, lists, notes, and component images as document objects.

**Why.** The source decks are authored structured documents; OCR is lower fidelity and discards
available semantics.

**Consequence.** Whole-slide source images are conversion failures. OCR is reserved only for text
that genuinely exists within a component image.

**Owner.** `tools/odp_to_marp.py` and `tools/pptx_to_marp.py`.

### Local reference projects remain outside runtime

**Decision.** Keep every `OTHER_REPOS/` clone outside the production runtime and dependency graph.

**Why.** Prior art can inform bounded implementation choices without importing incompatible syntax,
workflows, licenses, or renderer assumptions.

**Consequence.** The repository adapts verified ideas into local Python. The inventory records the
specific evidence and limitations for each clone.

**Owner.** `docs/RELATED_PROJECTS.md` and `docs/USAGE.md`.
