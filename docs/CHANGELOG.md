## 2026-09-01

### Behavior or Interface Changes

- Replaced the browser-rendered, flattened presentation baseline with the native-output contract:
  repository-owned Python interprets authoritative Marp Markdown into editable PPTX objects, then
  LibreOffice writes editable ODP and PDF from that ODP.
- Added bounded Marp multi-class H1 display presets (`font-size-64` through `font-size-200`). The
  source-located typed request applies only to the editable top-level H1, rejects title-region
  overflow instead of shrinking, and makes `font-size-200` a 150-point native Office title.
- Split native ownership: `marp_lib/marp_parser.py` interprets the supported Marp language subset,
  `marp_lib/layouts.py` owns layout builders and geometry, and `marp_lib/native_export.py`
  orchestrates native PPTX, notes, pagination, and conversion. The destination-named commands retain
  single-deck ownership, while `build_slides.sh` retains folder-level ownership.
- Implemented every LibreOffice layout-grid pattern as a distinct native builder: `blank`,
  `title-only`, `title-slide`, `title-content`, `centered-text`, `title-two-content`,
  `title-content-and-two-content`, `title-two-content-and-content`, `title-content-over-content`,
  `title-two-content-over-content`, `title-four-content`, `title-six-content`,
  `vertical-title-vertical-text`, `vertical-title-text-chart`, `title-vertical-text`, and
  `title-two-vertical-text-clipart`, plus the repository `gallery` layout.
- Made one explicit native layout class mandatory per canonical slide and established top-level
  blockquotes as multi-cell content in layout reading order.
- Defined Marp as an authoring-language specification only. The newly added local `marp-core` and
  `marp-cli` clones provide conformance evidence outside the production dependency/runtime graph.
- Added destination-named `tools/marp_to_pptx.py` and `tools/marp_to_odp.py` commands backed by one
  validated `marp_lib/native_export.py` implementation.
- Calibrated native Office typography from CSS pixels and fitted native text to its assigned layout
  region; balanced nested-list columns by height and restored paragraph separation in native cells.
- Preserved Markdown links, slide title metadata, and component-image descriptions in native
  PPTX and ODP output.
- Added deterministic per-layout source validation that rejects blocks which a layout would omit
  or place in overlap, with a clear diagnostic for the source author.

### Design Decisions

- Recorded full-slide rasterization and raster fallbacks as failed presentation results. Normal
  presentation builds require no browser, Marp code, Marp CLI, Node, or rendering engine.
- Recorded the heavily edited local `md2pptx` clone as implementation prior art for native objects,
  image fitting, list construction, and notes while retaining Marp syntax rather than its dialect.

### Fixes and Maintenance

- Hardened the native typed boundary: CRLF Markdown preserves physical source lines, retired
  `slide_*_source` raster names fail at their image line, and layout, cell, and overflow errors
  identify the most precise authored block or cell.
- Applied OpenDyslexic to ordinary and inline-code native text while reserving PT Sans Narrow for a
  displayed literal URL; labeled hyperlinks retain their native hyperlink and ordinary typeface.
- Gave all seventeen registry entries distinct named native builders and aligned the vertical
  preview contracts with fixed native geometry and one-root-body authoring.

- Corrected the native authoring contract: formatted/link/inline-code runs, nested lists, component
  images, blockquote cells, directives, and presenter-note comments are supported; tables and fenced
  or indented code report a source location until native editable-object owners are implemented.
  Documented `gallery` as two through six component images and `title-content` as the one-image
  layout.

### Developer Tests and Notes

- Added the native semantic E2E gate. Run
  `source source_me.sh && python3 tests/e2e/e2e_native_odp_semantics.py` from a macOS GUI-capable
  host session outside the restricted execution sandbox. It inspects native PPTX and editable ODP
  text, lists, links, notes, component images, slide count, and full-slide-image absence.
- Hardened the ODP E2E gate with `defusedxml`, numeric page-relative full-slide-image detection,
  and verification that component-image descriptions survive editable ODP conversion.

## Historical renderer and migration records

The entries below retain evidence from the former Marp CLI/browser-rendered PPTX path and earlier
migration work. They are historical records, not the current presentation contract, except where
an entry explicitly identifies the current native package or native semantic E2E gate above.

### Additions

- Added `docs/PIPELINE.md` as the canonical component architecture for the import and build engine,
  including its interfaces, ownership boundaries, success properties, verification lanes, extension
  seams, and current architectural risks.
- Added a related-projects guide that inventories every local prior-art clone, distinguishes
  themes, templates, importers, and output converters, and records what to adapt or reject.
- Added a bounded Python ODP importer that preserves structured slide text, content images, notes,
  visibility, and geometry without using full-slide screenshots as converted content.
- Added a central genetics Marp theme with accessible teaching colors and reusable lead, two-pane,
  and auto-fitting gallery layouts.
- Added `build_slides.sh` to generate PDF and PPTX with Marp 4.5.0 or newer and convert the PPTX
  into a classroom ODP with LibreOffice.
- Added installation, usage, design, human-guidance, and measured palette documentation plus a
  useful repository landing page.
- Added the first canonical migration candidate, `genetics/lect01b-genetic_disorders.md`, with its
  extracted content assets.
- Added `genetics/lect01a-course_intro.md` as the first recurring announcements/course-information
  deck with all 31 visible source slides represented as editable Marp layouts.
- Added deterministic importer tests for simple conversion, unsafe archive paths, and safe
  presenter-note comments, including drawing-page visibility and style-cascade behavior.

### Behavior Changes

- Made all six presentation command modules directly executable with canonical Python shebangs,
  `argparse` entry points, and aligned executable permissions; `odp_visibility.py` now reports each
  source slide's resolved visible or hidden state.
- Made the repository Python-only and moved Marp ownership from npm to the Homebrew `marp-cli`
  formula; Node remains only a transitive formula dependency.
- Established a one-way migration contract: legacy ODP is imported once, Marp Markdown becomes
  authoritative, and generated ODP is used for classroom presentation.
- Protected canonical Markdown by refusing to overwrite an existing deck or asset directory.
- Made hidden-slide detection preserve the source presentation sequence while excluding its nine
  hidden `lect01a` slides.
- Documented the importer and build trust boundaries: archive validation does not sandbox the
  LibreOffice ODP-to-PPTX normalization step, so legacy inputs must be instructor-owned and trusted.
- Made `build_slides.sh` reuse the same exporter as the destination-named commands so PPTX-only,
  ODP, and all-output workflows enforce one conversion contract.
- Made `build_slides.sh` batch-build every Marp deck directly inside a selected folder while
  keeping the destination-named Python converters single-deck commands.
- Recorded the instructor's stricter slide-layout contract: use the simple default layout
  vocabulary, keep all authored content inside the 1280x800 frame, use OpenDyslexic exclusively,
  and reserve PT Sans Narrow for long URLs.
- Established post-conversion polish as a separate phase from mechanical ODP import, with built-in
  Marp layouts preferred before adding custom per-slide geometry.
- Rejected full-slide PNGs as conversions: source renders are visual QA evidence only, never Marp
  slide content.
- Preserved the 31-slide `lect01a` teaching sequence while replacing all 11 source-rendered slides.

### Design Decisions

- Chose simple editable layouts over automatic reconstruction of arbitrary ODP drawing geometry.
- Chose successive build slides for classroom reveals because Marp browser fragments do not become
  native animations in the generated ODP.
- Centralized recurring visual layout in `themes/genetics.css` instead of raw per-slide HTML or XML.
- Simplified split-slide typography and recurring Discord and office-hours image placement so the
  weekly-edit deck remains readable without per-slide HTML.
- Standardized authored slide text on OpenDyslexic and displayed URL text on PT Sans Narrow in the
  central genetics theme.
- Limited PT Sans Narrow to slides that explicitly display long URLs; ordinary link labels continue
  to use OpenDyslexic with all other authored text.
- Made content images auto-fit their theme-owned panes and gallery cells instead of using per-image
  pixel dimensions.
- Made multi-image panes and galleries divide their available width from the number of images at
  render time rather than encoding two-image or three-image dimensions in the slide source.
- Reserved theme-owned gallery space for pagination so automatically fitted images do not sit
  beneath the slide number.
- Added a shared auto-fitting single-figure layout so screenshots remain below their Markdown title
  without per-slide dimensions or overlap.
- Chose structured slide-object extraction over OCR and measured temporary PPTX plus `python-pptx`
  as the geometry-normalization path for inconsistent legacy ODP layouts.
- Kept all `OTHER_REPOS/` clones as prior art only; future repository-owned work may adapt their
  ideas without adopting their code, dependencies, Markdown dialects, or VS Code workflows.
- Recorded an ordinary Marp-rendered PPTX followed by LibreOffice conversion as the temporary
  classroom baseline after a measured bakeoff; it was later retired for native output.

### Developer Tests

- Verified the `lect01a` ODP-to-PPTX bakeoff as 40 source slides, the same 9 hidden slides, one
  preserved source note slide, and separate text/image geometry on every former rasterized slide.
- Verified Marp and LibreOffice generate matching 23-slide PDF, PPTX, and ODP outputs and that
  LibreOffice can reopen the generated ODP and export all 23 pages at 16:10, with all 23 note
  parts and about 6,460 note characters preserved.
- Ran the official Marp `--pptx-editable` bakeoff: it yielded native objects but lost all notes and
  visibly broke two-pane geometry, so it is reserved for manual experiments on simple slides.
- Verified the Markdown-only two-pane layout through Marp, PPTX, LibreOffice ODP, and a rendered
  visual inspection.
- Measured every theme foreground at the 5.5:1 target: 16.27:1, 7.41:1, and 6.31:1 against white.
- Ran `bash -n build_slides.sh`, `git diff --check`, and the non-index-dependent pytest suite:
  661 passed and 1 skipped. The focused importer and import-requirements checks add 49 passes.
- Reconciled the human guidance, implementation decisions, usage guide, and README with the open
  output-design direction; documented the related-project inventory without linking ignored output
  artifacts.
- Confirmed `brew bundle check` reports every Brewfile dependency installed and Marp CLI reports
  version 4.5.0.
- Verified both destination-named commands against `lect01a-course_intro.md`; PPTX-only export and
  PPTX-to-ODP conversion completed successfully, and 302 focused hygiene tests passed.
- Verified the folder-level batch command discovered and regenerated both genetics decks as PDF,
  PPTX, and ODP; `bash -n build_slides.sh` passed, and the project-owned suite reported 683 passed
  and 1 skipped.
- Rendered all 31 `lect01a` slides after post-conversion polish and inspected both a full contact
  sheet and the dense split layouts at full size; no authored text or images cross a slide edge.
- Compared structured and OCR extraction across the 31-slide source PDF: structured extraction
  retained 99.6% of estimated words versus 95.8% for OCR, confirming OCR is unnecessary here.
- Ran the complete repository suite: 683 passed and 1 skipped.
- Rebuilt both canonical decks with Homebrew Marp 4.5.0 and regenerated their rendered PPTX and
  classroom ODP outputs.
- Reopened both final ODP files with LibreOffice 26.2.5.2 and exported them as 16:10 PDFs: `lect01a`
  retained 31 pages and `lect01b` retained 23 pages.
- Inspected full ODP-readback contact sheets plus the dense lists, three-image microscope gallery,
  and tall carrier-report panes; no authored text or teaching image crosses a slide edge.
- Ran six independent audit passes covering plan conformance, tests, style, documentation, dead
  code, and comments; after the low-risk repairs, the project-owned suite reported 717 passed and
  1 skipped, and 221 focused command/documentation hygiene checks passed.
- Validated the component-focused pipeline architecture with ASCII, line-width, Markdown-link, and
  full project checks; the suite reported 722 passed and 1 skipped.

### Fixes and Maintenance

- Fixed the importable `odp_visibility.main()` entry point, aligned the standalone PPTX importer's
  shebang and executable permission, removed a dead duplicate presenter-note encoder, and documented
  both diagnostic import commands and their bounded trust contract.
- Removed the redundant `split` and `compact` classes from `lect01a`: Marp's `bg right` directive
  already reserves the text pane, so the old theme padding was constraining it a second time.
- Replaced all `slide_*_source.png` references in `lect01a` with editable text and extracted content
  images while keeping the source slide count unchanged.
- Replaced the six remaining `lect01b` full-slide fallbacks and two fixed-width galleries with
  structured Markdown and shared auto-fitting layouts while preserving all 23 source slides.
- Mapped the two tall-image carrier-report pairs to the shared figure layout plus Marp's native
  auto-fitting right pane after rendered review exposed intrinsic-height distortion in a generic
  one-row gallery and in paired replaced elements.
- Kept the second carrier-report slide as a visually untitled continuation after Marp repeatedly
  painted its tall screenshot over the redundant repeated heading; the title remains in source as
  a continuation comment and the 23-slide sequence is unchanged.
- Made the Marp exporter reject retired source-fallback classes and `slide_*_source` image
  references before rendering.
- Added required shebangs to the initial executable Marp commands and normalized four legacy
  line-separator characters in `lect01b`; `odp_visibility.py` was later promoted from a library
  helper to a documented command.
- Synchronized shared style guides, tests, and repository support files from the starter template.
