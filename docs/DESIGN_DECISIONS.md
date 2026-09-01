# Design decisions

<!-- VENDORED HEADER: START -->
Record each durable decision about how this code and repository are shaped, once it is settled, with
the reasoning a later reader needs. Guidance Neil Voss states belongs in
[HUMAN_GUIDANCE.md](HUMAN_GUIDANCE.md), dated history in `docs/CHANGELOG.md`, open discussion in
`docs/active_plans/decisions/`. [PROPAGATED HEADER - ENTRIES BELOW ARE YOURS]
<!-- VENDORED HEADER: END -->

Write each decision as a level-three heading with these four fields. `Owner` names the
authoritative code or contract document, rather than a person.

```markdown
### <decision title>

**Decision.** <the durable direction>

**Why.** <the reason it was chosen>

**Consequence.** <the constraint a future change preserves>

**Owner.** <the authoritative code or contract doc>
```

## Software design

### Propagation records consumer maintenance

**Decision.** A successful, non-dry-run single-repository propagation that changes files adds one
canonical maintenance entry to the consumer's active changelog through `devel/changelog_lib.py`.

**Why.** Propagated maintenance belongs in the repository history, while no-op runs and failed runs
must not manufacture history. Using the shared parser and serializer keeps the entry compatible with
the changelog query, rotation, and commit tools.

**Consequence.** Propagation change accounting and `.gitignore` normalization remain idempotent, and
future changelog writes use the shared changelog library rather than assembling Markdown separately.

**Owner.** `devel/changelog_lib.py` and the single-repository propagation contract.

## Dependencies

### Repository-owned Python writes presentation objects

**Decision.** Use repository-owned Python tooling to read the supported Marp Markdown vocabulary and
write native, editable PPTX objects directly. LibreOffice converts that native PPTX into editable ODP.

**Why.** The classroom product requires editable text, lists, component images, layout, and presenter
notes. Browser-rendered presentation pages cannot meet that product meaning.

**Consequence.** The presentation build has no browser requirement. The supported vocabulary maps to
native title slide, section header, title-only, title/body, two-content, gallery, and multi-content
templates instead of a general CSS rendering engine.

**Owner.** `marp_lib/native_export.py` and `docs/PIPELINE.md`.

## Generated artifacts

### Marp Markdown is the only editable slide source

**Decision.** Import each legacy ODP once, then make its Marp Markdown and local assets the
authoritative editable source. PDF, PPTX, and ODP files are generated presentation artifacts.

**Why.** A closed one-way model prevents classroom-side ODP edits from creating a second source of
truth while still preserving LibreOffice Impress as the in-class presenter.

**Consequence.** The importer refuses to overwrite existing Markdown or asset directories. Content
changes after migration belong in Markdown; generated ODP files may be rebuilt at any time.

**Owner.** `tools/odp_to_marp.py` and `docs/USAGE.md`.

### Full-slide source images are conversion failures

**Decision.** Never use a rendered source slide as Marp content. A `slide_*_source.png` containing
the source slide's text is evidence that semantic conversion failed, not a presentation fallback.

**Why.** A screenshot may preserve appearance, but its text is no longer editable, searchable, or
controlled by the central theme. That defeats the reason for making Marp Markdown authoritative.

**Consequence.** Import must extract text and content images as separate objects. A source render may
be generated temporarily as a visual review oracle, but canonical Markdown and buildable decks must
not reference it.

**Owner.** `tools/odp_to_marp.py`, `genetics/*.md`, and `docs/USAGE.md`.

### Structured slide data replaces OCR

**Decision.** Treat legacy ODP decks as structured documents, not scanned pages. Read text, lists,
notes, and content images from document objects; do not use OCR in the normal import path.

**Why.** Authored slide text already exists in ODP XML and survives LibreOffice's PPTX translation
as text shapes. OCR is less accurate and discards structure that the source already provides.

**Consequence.** OCR is reserved for a genuine content image whose text must be recovered. It is not
used to interpret whole slides or to compensate for arbitrary layout.

**Owner.** `tools/odp_to_marp.py` and `docs/USAGE.md`.

### Temporary PPTX normalizes legacy geometry

**Decision.** Convert trusted ODP input to a temporary PPTX with LibreOffice, then use `python-pptx`
to extract separate text, image, note, visibility, and geometry objects for Marp layout selection.
The original ODP remains the source evidence for the one-time import.

**Why.** A measured `lect01a` bakeoff preserved all 40 source slides, identified the same 9 hidden
slides, retained the original note slide, and exposed separate text and picture geometry for every
slide that the direct importer had rasterized.

**Consequence.** PPTX geometry selects from a small Marp layout vocabulary; it does not reproduce
arbitrary source coordinates. The temporary PPTX is discarded after extraction, and Marp Markdown
becomes authoritative after polish.

**Owner.** `tools/odp_to_marp.py`, `tools/pptx_to_marp.py`, and `docs/USAGE.md`.

### Legacy ODP import has a local trust boundary

**Decision.** Accept only instructor-owned, trusted legacy ODP files for one-time import, and
render only trusted repository-owned Marp Markdown and assets.

**Why.** The importer validates archive members before processing them, but its geometry-normalizing
ODP-to-PPTX step invokes LibreOffice. Input validation does not sandbox LibreOffice.

**Consequence.** Archive limits reduce accidental or malformed-input risk but do not authorize
opening ODP files from unknown sources. The build wrapper's local-file access remains limited to
the repository's teaching assets.

**Owner.** `tools/odp_to_marp.py`, `marp_lib/native_export.py`, and `docs/INSTALL.md`.

### Classroom reveals use successive build slides

**Decision.** Represent click-to-reveal bullets, images, and answers as consecutive Markdown slides
that progressively add content.

**Why.** Successive slides work consistently in LibreOffice Impress and native PowerPoint output.

**Consequence.** Generated ODP decks preserve the teaching sequence without post-generation ODP
editing.

**Owner.** `docs/USAGE.md`.

### Native editable output replaces rendered presentation pages

**Decision.** Generate native editable PPTX and ODP as the only normal classroom-output path.

**Why.** Full-slide rasterization defeats editable slide objects and is incompatible with the
instructor's product requirement.

**Consequence.** Generated decks contain separately addressable text, list, shape, and component-image
objects. The exporter rejects unsupported source features explicitly and has no raster fallback.

**Owner.** `marp_lib/native_export.py` and its validation contracts.

### Destination-named converters expose native output

**Decision.** Provide `tools/marp_to_pptx.py` for native PPTX export and `tools/marp_to_odp.py` for
native-PPTX-to-ODP classroom export. Each Python command accepts one Markdown deck. Keep
`build_slides.sh` as a directory-level batch command that builds PDF, PPTX, and ODP for every
Marp deck directly in the selected folder.

**Why.** A command named for its destination is easier to discover than a generic build command and
makes the generated side effects explicit. The plural shell command provides one obvious way to
rebuild a collection without weakening the single-deck Python interface.

**Consequence.** `marp_lib/native_export.py` owns the parser, native writer, templates, and output
selection. `marp_lib/__init__.py` establishes the package boundary. The destination-named commands
select one output destination; the batch command scans one directory non-recursively and ignores
Markdown without `marp: true` in its YAML front matter.

**Owner.** `marp_lib/native_export.py`, `tools/marp_export.py`, `tools/marp_to_pptx.py`,
`tools/marp_to_odp.py`, and
`build_slides.sh`.

### CSS defines authoring vocabulary and native templates own output geometry

**Decision.** Keep slide source close to ordinary Marp Markdown. Treat `themes/genetics.css` as the
canonical authoring vocabulary and visual reference; let `marp_lib/native_export.py` own the native
output geometry and typography until an explicit shared theme-data contract exists. Favor image-led
title, split, gallery, and multi-content slides.

**Why.** The lectures use a visual on most slides, while repeated HTML, XML, and inline styling
would make the authoritative Markdown harder to read and maintain.

**Consequence.** Add a small named layout to the native exporter when a repeated teaching pattern is
needed. Images use `contain` inside their assigned native layout region. Marp class directives and
the CSS theme remain authoring cues; the exporter does not parse CSS into native geometry or
typography unless shared theme data is deliberately implemented.

**Owner.** `marp_lib/native_export.py` and `docs/USAGE.md`.

### Native exporter has a shared package boundary

**Decision.** Keep reusable Marp parsing, native PPTX writing, template geometry, and output
selection in `marp_lib/native_export.py`, with `marp_lib/__init__.py` as the package boundary.

**Why.** The exporter serves several executable commands and future presentation scripts. A
repository-owned module gives them one direct implementation to import.

**Consequence.** `tools/marp_export.py`, `tools/marp_to_pptx.py`, and `tools/marp_to_odp.py` stay
small executable CLIs. `marp_lib` organizes shared code; the product pipeline remains Marp Markdown
to native editable PPTX to editable ODP.

**Owner.** `marp_lib/native_export.py`, `marp_lib/__init__.py`, and `docs/PIPELINE.md`.

### Post-conversion polish owns layout and typography

**Decision.** Keep the ODP importer conservative, then simplify the canonical Marp deck in a
separate post-conversion polish pass. Prefer Marp's built-in advanced-background geometry over
per-slide layout classes. Use OpenDyslexic for authored slide text and PT Sans Narrow for displayed
URLs.

**Why.** A mechanical importer preserves evidence from the legacy deck, while human-readable
Markdown is the right place to choose a simpler teaching layout. Marp already reserves the content
pane beside a `bg right` image; adding custom right padding constrains that pane twice and causes
unnecessary wrapping or clipping.

**Consequence.** `lect01a-course_intro.md` uses ordinary headings, lists, Marp background images,
and shared figure, two-pane, and auto-sizing gallery layouts. Typography, spacing, and image fitting
remain central theme decisions, and no full-slide source render is acceptable in the deck.
OpenDyslexic remains the default for link labels; only slides that visibly print long URLs opt into
the theme's PT Sans Narrow `url-list` treatment.

**Owner.** `genetics/lect01a-course_intro.md`, `themes/genetics.css`, and `docs/USAGE.md`.

### Import preserves the teaching sequence

**Decision.** Preserve the visible source slide count and order during import and polish unless the
instructor explicitly approves a sequence change.

**Why.** Slide boundaries encode pacing and click order even when the legacy layout is inconsistent.
Consistency should come from Marp layouts, not from silently combining or splitting teaching beats.

**Consequence.** A multi-image source slide uses an auto-fitting shared gallery, and dense paired
content uses a shared pane layout when necessary to retain one source slide as one Marp slide.

**Owner.** `tools/odp_to_marp.py`, `genetics/*.md`, and `themes/genetics.css`.

### Cloned projects are idea sources, not implementation dependencies

**Decision.** Keep every project in `OTHER_REPOS/` outside the renderer and dependency graph.
Adapt useful ideas into this repository's own tools only after a measured classroom need identifies
the required behavior.

**Why.** The clones span themes, templates, direct renderers, importers, and editable-PPTX
experiments. Direct adoption would import incompatible Markdown dialects, Node workflows, or
editor assumptions, while the source-of-truth contract needs one locally maintained workflow.

**Consequence.** Marp Markdown remains the only slide source. A future repository-owned Python
postprocessor or converter may borrow ideas such as template geometry, image fitting, notes, or
native-object boundaries, but does not adopt external code, dependencies, or VS Code as a normal
requirement. The candidate inventory and its limits live in `docs/RELATED_PROJECTS.md`.

**Owner.** `docs/RELATED_PROJECTS.md`, `docs/USAGE.md`, and a future approved implementation
contract.
