# Human guidance

<!-- VENDORED HEADER: START -->
Record the durable guidance Neil Voss states, or approves for preservation here, in his own words:
first person or close paraphrase, one to three lines per bullet. Material he supplies as a source
may inform [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) once it is settled, and an entry of uncertain
origin belongs there too. Rules: [REPO_STYLE.md](REPO_STYLE.md).
[PROPAGATED HEADER - ENTRIES BELOW ARE YOURS]
<!-- VENDORED HEADER: END -->

## Decision priority

## Review expectations

## Working style

- Have single-repository propagation add a `devel/changelog_lib.py`-compatible changelog entry only
  when it makes real changes; recurring `.gitignore` churn must not create one.

## Slide migration and presentation

- This is a Python and Marp repository; that choice is settled.
- legacy ODP &rarr; one-time import &rarr; Marp Markdown becomes authoritative &rarr; generated
  ODP for class
- Marp Markdown &rarr; Marp-rendered PPTX &rarr; LibreOffice conversion &rarr; classroom ODP
- The destination and requirements are understood, but the best implementation for generated
  classroom output is not locked down yet.
- Use the cloned slide repositories as idea sources and build our own repository-owned tool; do
  not adopt their code or workflows directly.
- A normal instructor workflow must not require VS Code.
- Retire the legacy ODP authoring format in favor of Marp Markdown as the future source of truth.
- Treat ODP import as a one-time migration; after Markdown becomes canonical, do not round-trip
  edits from generated ODP files back into Markdown.
- Generate ODP files for presenting course content in class with LibreOffice Impress.
- Have `build_slides.sh` build every Marp deck in a selected folder; keep `marp_to_odp.py` and
  `marp_to_pptx.py` as obvious single-deck commands.
- Prefer simple teaching layouts instead of preserving every detail of the old ODP formatting.
- Treat layout simplification as post-conversion polish; keep the one-time ODP importer mechanical.
- Use more simple default slide layout templates: title and body, title and two columns, title
  slide, section header, and title only.
- Every 16:10 slide must keep authored text and images inside its 1280x800 frame.
- Let images auto-fit their layout with `contain`; avoid hard-coded per-image pixel dimensions.
- My ODP slides are hand-authored structured documents, not scans; normal conversion must use their
  text and image objects rather than OCR.
- A `slide_*_source.png` containing the slide's text is a failed conversion and cannot be used as a
  Marp slide.
- A full-slide source render may be used to check placement during review, but never as converted
  slide content.
- Preserve the source slide count unless I explicitly approve changing the teaching sequence.
- Use Marp's small layout vocabulary to enforce consistency even when legacy slides do not follow
  their ODP templates consistently.
- Use OpenDyslexic exclusively for all text, except long URLs, which use PT Sans Narrow.
- Prioritize the announcements/course-introduction deck for Marp migration because it needs small
  edits each week.
- Use lots of images and try to include a visual image on every slide.
- Avoid lots of HTML or XML tags in Markdown; keep styling in one central CSS file.
- Require Marp 4.5.0 or newer; older releases carry too many known vulnerabilities.
- Keep this repository Python-only. Quarto has too much overhead, and npm or TypeScript is not
  needed for the slide pipeline.
- Do not run a Marp server as part of the normal workflow.
- Treat the Marp-rendered PPTX followed by LibreOffice conversion as the current tested baseline,
  rather than a permanently selected implementation detail.
