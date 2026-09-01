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

### Homebrew owns the Marp installation

**Decision.** Install Marp CLI 4.5.0 or newer through Homebrew and keep this repository Python-only,
without `package.json`, `package-lock.json`, local `node_modules`, TypeScript, or Quarto.

**Why.** Marp is an external renderer rather than application code. Homebrew gives it one upgrade
path and avoids the npm forced-audit solver alternating between old and new vulnerable Marp trees.

**Consequence.** `brew bundle` installs the rendering tools, Node remains only a transitive Marp
formula dependency, and repository commands invoke `marp` from `PATH`.

**Owner.** `Brewfile`, `tools/marp_export.py`, and `build_slides.sh`.

## Generated artifacts

### Marp Markdown is the only editable slide source

**Decision.** Import each legacy ODP once, then make its Marp Markdown and local assets the
authoritative editable source. PDF, PPTX, and ODP files are generated presentation artifacts.

**Why.** A closed one-way model prevents classroom-side ODP edits from creating a second source of
truth while still preserving LibreOffice Impress as the in-class presenter.

**Consequence.** The importer refuses to overwrite existing Markdown or asset directories. Content
changes after migration belong in Markdown; generated ODP files may be rebuilt at any time.

**Owner.** `tools/odp_to_marp.py` and `docs/USAGE.md`.

### Complex source slides use explicit migration fallbacks

**Decision.** Convert simple title, bullet, and figure slides into editable Markdown. Render dense
or geometrically complex ODP pages as full-slide PNG fallbacks and retain their extracted text in
presenter-note comments.

**Why.** Automatic reconstruction of arbitrary ODP drawing geometry would produce fragile layouts
and lose visual information. A visible fallback keeps the lecture teachable while making cleanup
work explicit.

**Consequence.** A converted deck can be presented immediately, but source-rendered fallback slides
remain migration debt until an instructor replaces them with simple Markdown layouts.

**Owner.** `tools/odp_to_marp.py` and `themes/genetics.css`.

### Legacy ODP import has a local trust boundary

**Decision.** Accept only instructor-owned, trusted legacy ODP files for one-time import, and
render only trusted repository-owned Marp Markdown and assets.

**Why.** The importer validates archive members, XML, and extracted images before processing them,
but complex source slides can require LibreOffice fallback rendering. Input validation does not
sandbox LibreOffice.

**Consequence.** Archive limits reduce accidental or malformed-input risk but do not authorize
opening ODP files from unknown sources. The build wrapper's local-file access remains limited to
the repository's teaching assets.

**Owner.** `tools/odp_to_marp.py`, `tools/marp_export.py`, `build_slides.sh`, and
`docs/INSTALL.md`.

### Classroom reveals use successive build slides

**Decision.** Represent click-to-reveal bullets, images, and answers as consecutive Markdown slides
that progressively add content.

**Why.** Marp browser fragments do not become native animations in the static PPTX-to-ODP export,
while successive slides work consistently in LibreOffice Impress, PDF, and PowerPoint.

**Consequence.** Generated ODP decks preserve the teaching sequence without requiring browser
presentation mode or post-generation ODP editing.

**Owner.** `docs/USAGE.md`.

### Flattened PPTX conversion is the current classroom baseline

**Decision.** Build normal classroom output through Marp 4.5's ordinary rendered PPTX, then
convert that PPTX to ODP with LibreOffice. This is a current verified baseline, not a permanent
choice of output implementation.

**Why.** The 23-slide genetics bakeoff preserved every page, the 16:10 layout, and all 23 ODP note
parts containing about 6,460 note characters. Marp's official `--pptx-editable` mode instead lost
all notes and visibly broke the two-pane layout, despite producing native PowerPoint objects.

**Consequence.** The normal build output remains visually faithful and flattened. Editable PPTX
may be run manually as a measured experiment for simple slides, but it is not normal build output
and must not promise page geometry or presenter-note preservation.

**Owner.** `tools/marp_export.py`, `tools/marp_to_odp.py`, `build_slides.sh`, `docs/USAGE.md`, and
the output bakeoff evidence.

### Destination-named converters expose the pipeline

**Decision.** Provide `tools/marp_to_pptx.py` for PPTX-only export and `tools/marp_to_odp.py` for
the rendered-PPTX-to-ODP classroom path. Keep `build_slides.sh` as the PDF, PPTX, and ODP bundle.

**Why.** A command named for its destination is easier to discover than a generic build command and
makes the generated side effects explicit.

**Consequence.** Every public export command reuses `tools/marp_export.py`; format-specific commands
do not duplicate renderer discovery, version enforcement, path validation, or conversion logic.

**Owner.** `tools/marp_export.py`, `tools/marp_to_pptx.py`, `tools/marp_to_odp.py`, and
`build_slides.sh`.

### A central theme owns the visual vocabulary

**Decision.** Keep slide source close to ordinary Markdown and centralize typography, color,
spacing, and reusable layout behavior in one Marp CSS theme. Favor image-led title, split, and
full-visual slides.

**Why.** The lectures use a visual on most slides, while repeated HTML, XML, and inline styling
would make the authoritative Markdown harder to read and maintain.

**Consequence.** Add a small named layout to the central theme when a repeated teaching pattern is
needed. Do not solve recurring layout needs with copied raw HTML or per-slide style blocks.

**Owner.** `themes/genetics.css` and `docs/USAGE.md`.

### Post-conversion polish owns layout and typography

**Decision.** Keep the ODP importer conservative, then simplify the canonical Marp deck in a
separate post-conversion polish pass. Prefer Marp's built-in advanced-background geometry over
per-slide layout classes. Use OpenDyslexic for authored slide text and PT Sans Narrow for displayed
URLs.

**Why.** A mechanical importer preserves evidence from the legacy deck, while human-readable
Markdown is the right place to choose a simpler teaching layout. Marp already reserves the content
pane beside a `bg right` image; adding custom right padding constrains that pane twice and causes
unnecessary wrapping or clipping.

**Consequence.** `lect01a-course_intro.md` uses ordinary headings, lists, and Marp background-image
directives for its split slides. Typography and spacing remain central theme decisions. Text baked
into a source-fallback PNG keeps the legacy appearance until that fallback slide is reauthored as
Markdown.

**Owner.** `genetics/lect01a-course_intro.md`, `themes/genetics.css`, and `docs/USAGE.md`.

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
