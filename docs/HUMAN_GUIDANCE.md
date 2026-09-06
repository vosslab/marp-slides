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
- Use Marp Core v5 only as the upstream authoring and conformance baseline. Do not support Marp
  Core v4 or earlier behavior.
- Keep classic Marp Markdown as the current migration baseline rather than replacing it with a YAML
  or `md2pptx` dialect. Before committing to a successor language, assess whether a FOSS Markdown
  presentation language should be adopted or a small extension should be defined. Clearly separate
  standard Marp syntax from any later repository-owned language.
- Do not show slide numbers; they encourage the audience to track remaining time and watch the
  clock instead of the presenter.
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
- Give every slide exactly one explicit layout class. Keep `-` as ordinary list syntax and `>` as
  a standard Markdown blockquote; do not use comment-based cell markers for normal layout structure.
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
- Keep presentation-build output concise: show the current deck and stage transiently, then leave
  one compact summary with relative paths, file sizes, and one elapsed total. Hide successful
  third-party conversion chatter.
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

- Keep a separate Markdown review for every repository in `OTHER_REPOS/` that identifies its
  content and whether its ideas, code, functions, themes, or assets fit this project.
- Evaluate these repositories for useful ideas rather than license analysis when source copying is
  out of scope. Prioritize correctness, maintainability, validation, and delivery risks over
  trivial details.
- Review each repository for whether it improves an active task, offers a stronger pipeline model,
  or shows a useful possibility for Marp and its themes.
- Marp is not feature-complete for the planned teaching layouts. Explore a coherent, independently
  named language instead of adopting CDL or a rushed custom language wholesale.
- Do not route an extension language through Marp CLI. The repository-owned native exporter is the
  rendering boundary.
- Survey every `OTHER_REPOS/` project for how it handles Marp's missing layout vocabulary. Separate
  semantic language extensions, CSS visual catalogs, output transformations, and unrelated tools.
- Classic Marp is known not to support the required slide layouts. The remaining decision is whether
  to define a small new language or adopt another Markdown presentation language; do not imply that
  standard Marp is sufficient.
- Produce decision-support documentation before creating a future language guide or changing the
  parser. Compare literal source for recurring teaching layouts, and investigate existing Marp
  extensions as attempts to bridge linear Markdown content to spatial slide structure.
- Judge the choice by hand-authoring quality, ordinary nested Markdown, structural punctuation and
  comment burden, semantic layout names, and a clean mapping to typed editable native slide
  objects. Treat the repository Python parser and exporter as the rendering boundary.
- The future slide-language wishlist is:
  - Multiple named teaching layouts, including title slide, title plus content, two equal columns,
    asymmetric columns, stacked regions, 2x2, 3x2, and related LibreOffice-style patterns.
  - Ordinary nested bulleted and numbered lists inside every content region.
  - Simple Markdown image insertion with predictable placement inside a named region.
  - Equation support, using LaTeX-compatible syntax or a similarly capable hand-writable equation
    syntax, for both inline and display math without turning the language into a
    scientific-publishing framework.
  - Simple teaching animation: on an advance, make an authored item appear or reveal an outline one
    bullet at a time. Complex motion paths, timing tracks, and animation choreography are not needed.
  - Hand-writable source with very little structural punctuation or comment scaffolding.
  - Native editable output: text, lists, practical equations, and images remain real PPTX and ODP
    objects, never slide screenshots.
- These are requirements for the language choice, not approval for a particular grammar.
- Regardless of the chosen source language, the repository will own the parser, native editable
  PPTX/ODP builders, LibreOffice bridge, and validation. "Adopt a language" means adopt or adapt
  its source grammar and semantics, never its runtime or presentation pipeline.
- After reviewing the language survey, I see no viable presentation format to adopt directly. Keep
  the source-language choice open: assess GFM, Djot, and a Marp-derived surface before selecting
  the foundation and spatial syntax of a separately named language.
- I am leaning toward extending Djot as the source foundation. I value its removal of indented code
  blocks and its simpler list-item indentation rule; ordinary nested lists and explicit slide-layout
  semantics still need to be specified.
- Hands-on Djot specimens reinforce that preference: its visible, line-by-line parsing behavior
  makes the authored source easy to read and reason about.
- I want a Djot-based slide language to retain its design goals: linear and local parsing, simple
  list and inline behavior, hard-wrap-friendly source, uniform composition, preserved attributes and
  containers, and the simplest syntax consistent with those constraints.
- I particularly value source that remains readable when hard-wrapped. Keep every slide directive
  short and single-line so wrapping ordinary teaching prose never creates or changes structure.
- Avoid braces and other paired punctuation in normal slide authoring. Retain one-line Djot
  attributes for exceptional content or renderer overrides, never as the default layout, slot,
  gallery, reveal, size, or color vocabulary; never use multiline brace structures.
- A future slide-boundary line should be visually unique enough to divide a source file into slides.
  `=>layout: <layout>` with short `@left` and `@right` lines is an available thought experiment, not
  selected grammar. `@` and `=>` remain speculative.
- `===== layout: <layout>` is a tempting visually distinctive slide boundary. Keep it as an
  unassigned Djot-compatible thought experiment until the grammar fixtures select or reject it.
- I like the visual presence of Marp Extended's `%%` markers, but not their XML-like closing pairs.
  Keep one-sided `%% name` available for future fixture tests; do not assume its scope or role yet.
- Kova's `|||` split delimiter is notable prior art, but triple repeated characters are not ideal for
  ordinary authoring.
- There is no official successor-language layout catalog yet. Do not make the current implementation
  layout names the language's future vocabulary before the teaching fixtures establish it.
- Make ordinary `![alt](path)` the official component-image form and reserve it from all extension
  structure. Make `$inline$` and `$$display$$` the official mathematics forms and reserve them as
  well. The repository-owned math adapter may configure MathJax or a similar plugin to accept that
  surface; this does not adopt Marp image modifiers.
- Do not add a successor-language presenter-note syntax. Djot footnotes are audience-facing
  citations or clarifications, not hidden speaker notes; the existing importer still preserves
  notes from historical decks.
- A declared layout, rather than image count, should ultimately own slot capacity and geometry. Do
  not silently change a slide's selected layout because of image count.
- Keep teaching reveals within a small predefined action set rather than a general animation
  language. The spelling and geometry for a floating answer box remain unassigned.
- Use Djot's emphasis on an explicit, unambiguous grammar as a design lesson, not as the current
  base language. Do not require raw HTML tags or `<!-- ... -->` comments for normal slide structure.
- Do not call the successor language Marp+ by default. It may diverge substantially from Marp and
  should receive its own name after its grammar is selected.
- Keep one canonical authored source. Do not characterize the language discussion as a proposal for
  a separate GFM review copy and a presentation copy.

## Working style

- Have single-repository propagation add a `devel/changelog_lib.py`-compatible changelog entry only
  when it makes real changes; recurring `.gitignore` churn must not create one.
- Classify one-time implementation checks separately from permanent tests. Apply the permanent
  pytest checklist, keep temporary proof out of the suite, and remove a test when in doubt.
