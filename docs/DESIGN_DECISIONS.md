# Design decisions

<!-- VENDORED HEADER: START -->
Record each durable decision about how this code and repository are shaped, once it is settled, with
the reasoning a later reader needs. Guidance Neil Voss states belongs in
[HUMAN_GUIDANCE.md](HUMAN_GUIDANCE.md), dated history in `docs/CHANGELOG.md`, open discussion in
`docs/active_plans/decisions/`. [PROPAGATED HEADER - ENTRIES BELOW ARE YOURS]
<!-- VENDORED HEADER: END -->

## Native presentation design

### Strict Djot compatibility governs the successor language

**Decision.** The successor language is an extended Djot language. It inherits every construct
supported by the pinned Djot syntax revision. Every source it accepts must be valid strict Djot and
pass every applicable Djot parser, formatter, editor rule, and linter in the project's pinned
compatibility suite before the repository's extension linter evaluates its slide semantics.

**Why.** Djot's linear, local, hard-wrap-friendly grammar is the selected authoring foundation. A
compatibility gate prevents convenience slide syntax from silently turning the language into a Djot
fork with an incompatible parser.

**Consequence.** Pin the exact Djot syntax revision and all compatibility tools before
implementation. The extension linter adds source-located layout, slot, and animation diagnostics;
it never excuses a Djot failure. Djot has no advertised official standalone linter, so a concrete
parser/formatter/editor-rule/linter inventory is required before any claim that source "passes all
Djot linters." Extended-Djot presentation source uses the upstream `.djot` suffix, so standard
Djot tooling continues to recognize it. This decision adds no language-accepting parser or renderer:
the experimental source-only linter cannot accept a source until its pinned native Djot gate passes.

**Initial suite member.** Jotdown 0.10.0, installed with its CLI, is the pinned native parser. It
runs before the source-only extension linter and accepts every imported genetics source. It is a
parser, not a formatter, editor rule, or standalone linter, so its clean result does not close the
remaining compatibility-suite selection.

**Owner.** [djot_slide_extension_exploration.md](active_plans/decisions/djot_slide_extension_exploration.md)
and a future approved language guide.

### Marp is an authoring-language specification

**Decision.** Retain canonical Marp Markdown as the current migration baseline, adopt Marp Core v5
as the only upstream compatibility baseline, and independently implement its supported language
subset in repository-owned Python while the extended-Djot successor grammar remains unimplemented.

**Why.** Marp Core v5 offers a mature authoring language and separates built-in behavior from
optional plugins. Its runtime and browser render paths do not meet the editable native-object
product requirement.

**Consequence.** `OTHER_REPOS/marp-core` and `OTHER_REPOS/marp-cli` are conformance evidence only.
The production dependency graph contains no Marp code, CLI, Node, browser, or render stage.
`MARP_SYNTAX_GUIDE.md` describes only standard Marp Core v5 / Marp CLI-compatible syntax. Classic
Marp is known not to express the required spatial layouts; it remains a migration baseline while
the extended-Djot grammar is specified. The repository-owned parser and native editable-output
pipeline do not adopt an external runtime or renderer. Marp Core v4 and earlier behavior is not
supported. Optional v5 Shiki, Mermaid, KaTeX, and MathJax features require explicit native
capability decisions rather than implicit `/full` compatibility. The current local evidence snapshot
is Marp Core 5.0.1 at commit `06c5a54`.

**Owner.** `marp_lib/marp_parser.py`, [MARP_SYNTAX_GUIDE.md](MARP_SYNTAX_GUIDE.md),
[ROADMAP.md](ROADMAP.md), and [PIPELINE.md](PIPELINE.md).

### Slide-language requirements inform the Djot extension grammar

**Decision.** The future slide language must make recurring teaching structures directly
authorable: title; title and subtitle; ordinary body; nested bulleted and numbered lists; equal and
unequal panels; image/text on either side; three or four regions; image with caption; gallery;
quote or callout; and reusable named teaching layouts. The layout vocabulary must include every
default LibreOffice layout plus the custom `multiple-choice` layout. It must also support simple
Markdown images with predictable named-region placement and both inline and display equations through
LaTeX-compatible or similarly capable hand-writable syntax. It must support simple on-advance
teaching reveals: make an authored item appear or present an outline one bullet at a time.

**Why.** These are the lecture structures that classic Marp cannot express as portable semantic
source. They define the evidence needed to choose between a small extension and an adopted Markdown
presentation language without presupposing either outcome.

**Consequence.** The language survey uses those structures and equation support as literal source
examples. The Djot extension grammar must preserve ordinary nested Djot content, avoid routine
HTML-comment or container scaffolding when possible, and map text, lists, practical equations, and
images to typed editable native slide objects. Reveal semantics must remain bounded to authored
appearance order and map to editable native presentation animation objects; motion paths, timing
tracks, and complex choreography are outside this requirement. Equation support must not require a
scientific-publishing workflow. This decision does not approve a grammar, parser change, or future
guide.

**Owner.** [LAYOUT_LANGUAGE_SURVEY.md](LAYOUT_LANGUAGE_SURVEY.md),
[MARP_ADJACENT_PROJECT_COMPARISON.md](MARP_ADJACENT_PROJECT_COMPARISON.md), and a future
explicitly approved language guide. [LECTURE_LAYOUT_SURVEY.md](LECTURE_LAYOUT_SURVEY.md) records
the legacy-slide evidence behind the requirements.

### Component images and dollar-delimited mathematics are reserved

**Decision.** The future language's official component-image form is `![alt](path)`. Its official
mathematics forms are `$inline$` and `$$display$$`. These surfaces are unavailable for future slide,
layout, region, gallery, reveal, or styling syntax.

**Why.** The image form is familiar to current Marp authors and already has native Djot image meaning.
The dollar forms are the instructor's preferred hand-writable mathematics surface and can be mapped
by a repository-owned MathJax-compatible adapter. Reserving all three prevents slide syntax from
colliding with ordinary teaching content.

**Consequence.** This reserves ordinary component images only, not Marp-specific image modifiers for
backgrounds, sizing, position, or filters. The exploration record now has a provisional working
surface for slide starts, slots, and animations; `%%`, default-layout slot contracts, generic
overlay geometry outside `multiple-choice`, and parser adoption remain open.

**Owner.** [djot_slide_extension_exploration.md](active_plans/decisions/djot_slide_extension_exploration.md)
and the future approved language guide.

### Multiple-choice is the first official future layout

**Decision.** Add `multiple-choice` as the first official layout in the future-language catalog.
It requires exactly one `@question` slot and one `@answer` slot. The question contains the prompt
and its ordinary choice list; the answer appears automatically on the first advance in a fixed
bottom-right popup region.

**Why.** Multiple-choice questions have a short, revealable answer. The automatic behavior removes
redundant animation spelling while keeping open-ended questions out of a layout that would misstate
their teaching structure.

**Consequence.** Do not require `<= appear` or `=> appear` for this layout's answer, and reject them
there as redundant. This is a source-language and layout-catalog decision only: it does not add a
parser, exporter, native builder, or a generally available overlay slot to the current Marp system.

**Owner.** [djot_slide_extension_exploration.md](active_plans/decisions/djot_slide_extension_exploration.md)
and a future approved language guide.

### Static linter enforces the source contract

**Decision.** Provide a fast, source-only linter with pyflakes-level enforcement for the future
language.

**Why.** The author needs immediate, source-located feedback for structural mistakes without a
browser, LibreOffice, or a rendered deck.

**Consequence.** It runs after the required strict-Djot compatibility suite, then validates slide
declarations, selected layouts, permitted titles and subtitles, slot contracts, animation attachment,
and special-layout rules. It does not establish geometry, overflow, native animation export, or
visual quality; those remain renderer and acceptance checks. This requirement does not authorize
parser or linter implementation before the grammar has representative, documented source cases.
Permanent parser and linter tests keep those short inputs inline, as required by the pytest policy.

**Owner.** A future source-language package and its deterministic tests.

### Standard Djot content covers tables and sequences

**Decision.** The future language extends Djot and supports its normal content syntax: tables,
inline verbatim, and fenced code blocks. Use `$inline$` and `$$display$$` through MathJax or a
similar plugin for mathematics.

**Why.** The Lecture 02 survey shows all four forms in normal teaching content. They are ordinary
content needs, not evidence for a custom biological notation or another slide-extension marker.

**Consequence.** The future native implementation needs editable table, inline-verbatim,
monospace-block, and math owners. It must not introduce custom table, DNA-sequence, or math
delimiters.

**Owner.** [djot_slide_extension_exploration.md](active_plans/decisions/djot_slide_extension_exploration.md)
and [lect02_genetics_syntax_gap_survey.md](active_plans/decisions/lect02_genetics_syntax_gap_survey.md).

### ASCII character references project Unicode

**Decision.** Permit documented ASCII character references in ordinary Djot text and project them to
Unicode only in the native-output pipeline after strict Djot validation. The initial mapping is
`&prime;` to U+2032 PRIME (`′`).

**Why.** The author can keep source ASCII-only where typing literal Unicode is inconvenient without
abandoning Djot compatibility or accepting inaccurate curly quotes for biological 5′ and 3′ labels.

**Consequence.** `&prime;` remains ordinary valid Djot text until the project projection transforms
it. This is a small project-owned vocabulary, not an HTML-entity parser; add each mapping explicitly.
Never transform raw or verbatim content, whose literal spelling is part of its meaning. The future
compatibility suite and extension linter must test both the strict-Djot source and the Unicode native
output.

**Owner.** [djot_slide_extension_exploration.md](active_plans/decisions/djot_slide_extension_exploration.md)
and a future approved language guide.

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

### Comment-based cell markers are set aside

**Decision.** Do not use `<!-- _cell: <slot> -->` as the successor language's normal layout syntax.
The successor language remains unnamed and its visible region syntax is still open.

**Why.** The survey shows that comment structure is precise but costly to hand-write. The desired
source must remain legible in a GitHub Markdown view without routine HTML or comment scaffolding.

**Consequence.** Do not add or migrate `_cell` parsing, imports, decks, preview behavior, or tests.
Use the marker only as prior-art evidence in the survey. Define a visible, unambiguous layout and
slot grammar before creating a language guide or parser work.

**Owner.** [presentation_language_choices.md](active_plans/decisions/presentation_language_choices.md)
and [LAYOUT_LANGUAGE_SURVEY.md](LAYOUT_LANGUAGE_SURVEY.md).

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
