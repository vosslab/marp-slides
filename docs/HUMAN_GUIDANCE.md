# Human guidance

<!-- VENDORED HEADER: START -->
Record the durable guidance Neil Voss states, or approves for preservation here, in his own words:
first person or close paraphrase, one to three lines per bullet. Material he supplies as a source
may inform [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) once it is settled, and an entry of uncertain
origin belongs there too. Rules: [REPO_STYLE.md](REPO_STYLE.md).
[PROPAGATED HEADER - ENTRIES BELOW ARE YOURS]
<!-- VENDORED HEADER: END -->

## Slide migration and presentation

- Legacy ODP is imported once; Marp Markdown and its local assets then become authoritative.
- Use Marp because it has a mature language specification. The production build uses neither Marp
  code nor Marp CLI.
- `OTHER_REPOS/marp-core` and `OTHER_REPOS/marp-cli` are interpretation and conformance evidence,
  not production dependencies, runtimes, or renderers.
- Build canonical Marp Markdown through repository-owned Python into native editable PPTX objects,
  then use LibreOffice to make editable ODP, then make PDF from that ODP.
- Run LibreOffice conversion with `--headless --norestore` through the established user profile.
  Keep LibreOffice closed during the batch build; use `--safe-mode` when repairing profile problems.
- Export ODP to PDF with the Impress PDF filter, 70 percent JPEG quality, a documented 150 DPI image
  limit, and PDF/A-3b output.
- Implement every individual LibreOffice layout-grid pattern as native editable Python objects, plus
  the repository `gallery` layout. The grid is a visual catalog, not a rendering dependency.
- Use layouts `blank`, `title-only`, `title-slide`, `title-content`, `centered-text`,
  `title-two-content`, `title-content-and-two-content`, and
  `title-two-content-and-content`.
- Use layouts `title-content-over-content`, `title-two-content-over-content`,
  `title-four-content`, `title-six-content`, `vertical-title-vertical-text`,
  `vertical-title-text-chart`, `title-vertical-text`, `title-two-vertical-text-clipart`, and `gallery`.
- Give every slide exactly one explicit layout class. Use ordinary blockquotes as multi-cell content
  in the layout's reading order.
- Use a bounded Marp `font-size-N` companion class when an H1 such as `THE END` should occupy the
  slide; keep the title editable and leave normal slide text at its layout size.
- Preserve text, lists, component images, links, layouts, and presenter notes as native objects.
- Treat every full-slide raster image or raster fallback in generated PPTX, ODP, or PDF production
  as a failed product result. A browser is not a normal build dependency.
- Use the heavily edited `md2pptx` clone for native-object implementation ideas while retaining
  Marp syntax as this repository's authoring contract.
- Use a `marp_lib` folder for common reusable functions that other presentation scripts import.
- Have `build_slides.sh` build every Marp deck in a selected folder; keep `marp_to_odp.py` and
  `marp_to_pptx.py` as obvious single-deck commands.
- Prefer simple teaching layouts instead of copying arbitrary legacy ODP geometry. Keep authored
  text and images within the 1280x800 16:10 frame, and fit component images with `contain`.
- Preserve the teaching sequence unless I explicitly approve a change.
- My ODP slides are hand-authored structured documents, not scans; normal conversion uses text and
  image objects rather than OCR.
- Use OpenDyslexic for ordinary slide text and PT Sans Narrow only when a long URL is displayed.
- Use OpenDyslexic for ordinary and inline-code runs. Apply PT Sans Narrow only to a displayed
  literal URL; keep ordinary linked labels in OpenDyslexic with their native hyperlink.
- Treat `slide_*_source` raster names as retired full-slide fallback evidence, not component images.
- For `title-vertical-text` and `vertical-title-vertical-text`, author one level-one title and one
  root body block: one paragraph, one list, or one component image.
- Use lots of images and aim for a visual image on every slide.
- Avoid raw HTML or XML in Markdown. Keep preview styling in the shared CSS theme.
- A normal instructor workflow must not require VS Code, npm, TypeScript, Node, or a Marp server.
- This pre-production repository uses direct replacements when terminology or architecture changes.

## Working style

- Have single-repository propagation add a `devel/changelog_lib.py`-compatible changelog entry only
  when it makes real changes; recurring `.gitignore` churn must not create one.
