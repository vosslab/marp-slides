## 2026-09-01

### Additions

- Added a related-projects guide that inventories every local prior-art clone, distinguishes
  themes, templates, importers, and output converters, and records what to adapt or reject.
- Added a bounded Python ODP importer that extracts simple slide content into Marp Markdown,
  preserves supported images and notes, and renders explicit full-slide fallbacks for complex
  source geometry.
- Added a central genetics Marp theme with accessible teaching colors and reusable lead, split,
  source-fallback, and Markdown-only two-pane layouts.
- Added `build_slides.sh` to generate PDF and PPTX with Marp 4.5.0 or newer and convert the PPTX
  into a classroom ODP with LibreOffice.
- Added destination-named `tools/marp_to_pptx.py` and `tools/marp_to_odp.py` commands backed by one
  validated `tools/marp_export.py` implementation.
- Added installation, usage, design, human-guidance, and measured palette documentation plus a
  useful repository landing page.
- Added the first canonical migration candidate, `genetics/lect01b-genetic_disorders.md`, with its
  extracted and fallback assets.
- Added `genetics/lect01a-course_intro.md` as the first recurring announcements/course-information
  deck: 31 visible slides, 20 editable layouts, and 11 explicit source-rendered fallbacks.
- Added deterministic importer tests for simple conversion, unsafe archive paths, and safe
  presenter-note comments, including drawing-page visibility and style-cascade behavior.

### Behavior Changes

- Made the repository Python-only and moved Marp ownership from npm to the Homebrew `marp-cli`
  formula; Node remains only a transitive formula dependency.
- Established a one-way migration contract: legacy ODP is imported once, Marp Markdown becomes
  authoritative, and generated ODP is used for classroom presentation.
- Protected canonical Markdown by refusing to overwrite an existing deck or asset directory.
- Made hidden-slide detection honor page visibility through the ODP drawing-page style cascade,
  then map fallback render pages by original source-page position.
- Documented the importer and build trust boundaries: archive and XML validation do not sandbox
  LibreOffice fallback rendering, so legacy ODP inputs must be instructor-owned and trusted.
- Made `build_slides.sh` reuse the same exporter as the destination-named commands so PPTX-only,
  ODP, and all-output workflows enforce one conversion contract.
- Established post-conversion polish as a separate phase from mechanical ODP import, with built-in
  Marp layouts preferred before adding custom per-slide geometry.

### Design Decisions

- Chose simple editable layouts over automatic reconstruction of arbitrary ODP drawing geometry.
- Chose successive build slides for classroom reveals because Marp browser fragments do not become
  native animations in the generated ODP.
- Centralized recurring visual layout in `themes/genetics.css` instead of raw per-slide HTML or XML.
- Simplified split-slide typography and recurring Discord and office-hours image placement so the
  weekly-edit deck remains readable without per-slide HTML.
- Standardized authored slide text on OpenDyslexic and displayed URL text on PT Sans Narrow in the
  central genetics theme.
- Kept all `OTHER_REPOS/` clones as prior art only; future repository-owned work may adapt their
  ideas without adopting their code, dependencies, Markdown dialects, or VS Code workflows.
- Chose ordinary Marp-rendered PPTX followed by LibreOffice conversion as the current classroom
  baseline after a measured bakeoff; it is not a permanent output-mechanism commitment.

### Developer Tests

- Verified the canonical genetics sample imports as 23 visible slides: 17 editable, 6 explicit
  source-rendered fallbacks, 6 extracted images, and no hidden slides.
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
- Rendered all 31 `lect01a` slides after post-conversion polish and inspected both a full contact
  sheet and the dense split layouts at full size; no authored text or images cross a slide edge.

### Fixes and Maintenance

- Removed the redundant `split` and `compact` classes from `lect01a`: Marp's `bg right` directive
  already reserves the text pane, so the old theme padding was constraining it a second time.
- Synchronized shared style guides, tests, and repository support files from the starter template.
