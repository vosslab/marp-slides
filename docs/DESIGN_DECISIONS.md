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
runs before the source-only extension linter and accepts every imported genetics source. It is the
suite's native parser-validation lane; a clean parse is a meaningful raw-Djot lint result. It does
not provide formatting, editor-rule, or slide-semantic diagnostics, so those remaining suite lanes
still need explicit selection.

**Owner.** [djot_slide_extension_exploration.md](active_plans/decisions/djot_slide_extension_exploration.md)
and a future approved language guide.

### Marp is an authoring-language specification

**Decision.** Retain canonical Marp Markdown as the migration baseline, adopt Marp Core v5 as the
only upstream compatibility baseline, and independently implement its supported language subset in
repository-owned Python beside the extended-Djot front end.

**Why.** Marp Core v5 offers a mature authoring language and separates built-in behavior from
optional plugins. Its runtime and browser render paths do not meet the editable native-object
product requirement.

**Consequence.** `OTHER_REPOS/marp-core` and `OTHER_REPOS/marp-cli` are conformance evidence only.
The production dependency graph contains no Marp code, CLI, Node, browser, or render stage.
`MARP_SYNTAX_GUIDE.md` describes only standard Marp Core v5 / Marp CLI-compatible syntax. Classic
Marp is known not to express the required spatial layouts; it remains a migration baseline beside
the extended-Djot grammar. The repository-owned parsers and native editable-output pipeline do not
adopt an external runtime or renderer. Marp Core v4 and earlier behavior is not
supported. Optional v5 Shiki, Mermaid, KaTeX, and MathJax features require explicit native
capability decisions rather than implicit `/full` compatibility. The current local evidence snapshot
is Marp Core 5.0.1 at commit `06c5a54`.

**Owner.** `marp_lib/marp_parser.py`, [MARP_SYNTAX_GUIDE.md](MARP_SYNTAX_GUIDE.md),
[ROADMAP.md](ROADMAP.md), and [PIPELINE.md](PIPELINE.md).

### Djot requirements inform the implemented grammar

**Decision.** The implemented Djot slide language makes recurring teaching structures directly
authorable: title; title and subtitle; ordinary body; nested bulleted and numbered lists; equal and
unequal panels; image/text on either side; three or four regions; image with caption; gallery;
quote or callout; and reusable named teaching layouts. The layout vocabulary must include every
default LibreOffice layout plus the custom `multiple-choice` layout. It must also support simple
Markdown images with predictable named-region placement and both inline and display equations through
LaTeX-compatible or similarly capable hand-writable syntax. It must support simple on-advance
teaching reveals: make an authored item appear or present an outline one bullet at a time.

**Why.** These are the lecture structures that classic Marp cannot express as portable semantic
source. They define the implemented grammar's required authoring surface and preserve room for
native-output capabilities that still need an explicit owner.

**Consequence.** The language survey uses those structures and equation support as literal source
examples. The Djot extension grammar preserves ordinary nested Djot content, avoids routine
HTML-comment or container scaffolding when possible, and map text, lists, practical equations, and
images to typed editable native slide objects. Reveal semantics remain bounded to authored
appearance order; motion paths, timing tracks, and complex choreography are outside this
requirement. Equation support must not require a scientific-publishing workflow. The 2026-09-05
exploration status is superseded by the 2026-09-06 implemented Djot parser, grammar, linter, and
native export path; native math and M5 timing still require their own acceptance evidence.

**Owner.** `marp_lib/djot_grammar.py`, `marp_lib/djot_parser.py`,
[PIPELINE.md](PIPELINE.md), and [LECTURE_LAYOUT_SURVEY.md](LECTURE_LAYOUT_SURVEY.md).

### Component images and dollar-delimited mathematics have fixed surfaces

**Decision.** The implemented language's component-image form is `![alt](path)`. Its official
mathematics forms are `$inline$` and `$$display$$`. These surfaces are unavailable for future slide,
layout, region, gallery, reveal, or styling syntax.

**Why.** The image form is familiar to current Marp authors and already has native Djot image meaning.
The dollar forms are the instructor's preferred hand-writable mathematics surface and can be mapped
by a repository-owned MathJax-compatible adapter. Reserving all three prevents slide syntax from
colliding with ordinary teaching content.

**Consequence.** This reserves ordinary component images only, not Marp-specific image modifiers for
backgrounds, sizing, position, or filters. The implemented grammar owns slide starts and named slots;
`%%`, generic overlay geometry outside `multiple-choice`, and native math rendering remain open.

**Owner.** [djot_slide_extension_exploration.md](active_plans/decisions/djot_slide_extension_exploration.md)
and the future approved language guide.

### Multiple-choice is an implemented bounded layout

**Decision.** `multiple-choice` is an official layout in the implemented language catalog.
It requires exactly one `@question` slot and one `@answer` slot. The question contains the prompt
and its ordinary choice list; the answer contains one or two short, flat paragraphs in a fixed
bottom-right popup region. It carries implicit reveal intent only.

**Why.** Multiple-choice questions have a short, revealable answer. Implicit intent removes redundant
animation spelling while keeping open-ended questions out of a layout that would misstate their
teaching structure.

**Consequence.** The parser, linter, exporter, and native builder own its `@question` and `@answer`
contract. The answer occupies an editable popup region; OOXML timing and Impress first-advance
playback remain M5 acceptance questions. No generally available overlay slot follows from this
bounded layout.

**Owner.** [djot_slide_extension_exploration.md](active_plans/decisions/djot_slide_extension_exploration.md)
and a future approved language guide.

### Static linter enforces the implemented source contract

**Decision.** Provide a fast, source-only linter with pyflakes-level enforcement for the implemented
Djot language.

**Why.** The author needs immediate, source-located feedback for structural mistakes without a
browser, LibreOffice, or a rendered deck.

**Consequence.** It runs after the required strict-Djot compatibility suite, then validates slide
declarations, selected layouts, permitted titles and subtitles, slot contracts, animation attachment,
and special-layout rules. It does not establish geometry, overflow, native animation export, or
visual quality; those remain renderer and acceptance checks. Permanent parser and linter tests keep
short inputs inline, as required by the pytest policy.

**Owner.** `marp_lib/djot_lint.py`, `marp_lib/djot_parser.py`, and their deterministic tests.

### Standard Djot content covers tables and sequences

**Decision.** The implemented language extends Djot and supports its normal content syntax: tables,
inline verbatim, and fenced code blocks. Use `$inline$` and `$$display$$` through MathJax or a
similar plugin for mathematics.

**Why.** The Lecture 02 survey shows all four forms in normal teaching content. They are ordinary
content needs, not evidence for a custom biological notation or another slide-extension marker.

**Consequence.** Editable tables have a native owner; inline verbatim, monospace blocks, and math
continue to require their explicit supported-output owners. The language does not introduce custom
table, DNA-sequence, or math delimiters.

**Owner.** [djot_slide_extension_exploration.md](active_plans/decisions/djot_slide_extension_exploration.md)
and [lect02_genetics_syntax_gap_survey.md](active_plans/decisions/lect02_genetics_syntax_gap_survey.md).

### ASCII character references project Unicode

**Decision.** Permit the documented ASCII token `&prime;` in ordinary Djot text and map it to the
Unicode code point U+2032 PRIME only in the native-output pipeline after strict Djot validation.

**Why.** The author can keep source ASCII-only where typing literal Unicode is inconvenient without
abandoning Djot compatibility or accepting inaccurate curly quotes for biological prime labels.

**Consequence.** The literal ASCII token remains valid Djot source until the project projection maps
it. This is a small project-owned vocabulary, not an HTML-entity parser; add each mapping explicitly.
Never transform raw or verbatim content, whose literal spelling is part of its meaning. The strict
Djot gate and extension linter test the ASCII source separately from native-output projection.

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

**Decision.** `vertical-text-panel` and `vertical-panel` accept exactly one root body
block after the level-one title: a paragraph, list, or component image.

**Why.** The one authored block maps directly to one native vertical text frame or contained image
region without inventing a repository-specific Markdown wrapper language.

**Consequence.** Preview and native geometry share the fixed 94px title, 24px spacer, and 1042px
body tracks. `vertical-title-two-panels` uses 94px, 24px, 500px, 42px, and 500px tracks with
explicit child placement.

**Owner.** `marp_lib/layouts.py`, `themes/genetics.css`, and their contract tests.

### Extended-Djot is a parallel native source front end

**Decision.** Parse `.djot` decks with repository-owned Djot modules and dispatch them beside `.md`
decks into the same presentation-neutral IR and native PPTX -> ODP -> PDF pipeline.

**Why.** The native renderer, geometry, and conversion chain remain source-language agnostic.
Keeping the input seam explicit lets the Djot grammar evolve without migrating existing Marp decks
or duplicating native-output behavior.

**Consequence.** `native_export` selects parsers by suffix. `marp_parser` preserves the Marp
baseline, while `djot_parser`, `djot_blocks`, and `djot_inline` own the supported Djot subset.
One deck has one selected canonical source form; front-end coexistence does not create a second
authority for existing course content.

**Owner.** `marp_lib/native_export.py`, `marp_lib/marp_parser.py`, `marp_lib/djot_parser.py`, and
[PIPELINE.md](PIPELINE.md).

### The registry defines Djot layout and slot contracts

**Decision.** `marp_lib.layouts.LAYOUTS` is the authoritative catalog for canonical short layout
names and named Djot slots. The grammar derives its legal vocabulary from that registry and provides
no aliases.

**Why.** Source validation and native geometry must describe the same layouts. Derived vocabulary
keeps a later layout change local to the layout owner rather than creating parallel spelling tables.

**Consequence.** The canonical names are `one-panel`, `two-panels`, `one-plus-two-panels`,
`two-plus-one-panels`, `stacked-panels`, `two-over-one-panels`, `four-panels`, `six-panels`,
`vertical-panel`, `vertical-title-two-panels`, `vertical-text-panel`, and
`two-panels-vertical-clipart`; `blank`, `title-only`, `title-slide`, `centered-text`, and `gallery`
remain. The asymmetric layouts use named slots rather than source position.

**Owner.** `marp_lib/layouts.py` and `marp_lib/djot_grammar.py`.

### Djot normalizes headings and cells before geometry

**Decision.** Djot parses global H1/H2 headings separately from named `Cell` content. All H2 lines
on a `title-slide` form one subtitle region, and cells bind by declared slot name rather than source
order.

**Why.** A normalized IR lets both source front ends share geometry while preserving imported
title-slide subtitles and allowing authors to order named regions for readability.

**Consequence.** Layouts validate title/subtitle permission and named-cell completeness. Missing,
duplicate, unknown, and unnamed cells fail source-located. Multiple H2 lines are preserved rather
than collapsed into a single source line.

**Owner.** `marp_lib/native_model.py`, `marp_lib/djot_parser.py`, and `marp_lib/layouts.py`.

### Supported Djot constructs fail explicitly at the native boundary

**Decision.** Retain typed representations for supported Djot blocks, attributes, and reveal intent;
raise source-located errors for valid Djot constructs that have no editable native mapping.

**Why.** Silent loss would make source look accepted while omitting teaching content. A narrow,
explicit subset can expand safely when a native owner and acceptance evidence exist.

**Consequence.** One-line attributes precede their element, standalone image paragraphs become
components, and mixed image paragraphs are unsupported. `$inline$` and `$$display$$` are intentional
local math extensions after strict-Djot validation, but math is rejected until rendered natively.
Quotes, attributes, and unsupported inline forms receive the same source-located treatment.

**Owner.** `marp_lib/djot_blocks.py`, `marp_lib/djot_inline.py`, `marp_lib/djot_parser.py`, and
`marp_lib/layouts.py`.

### Multiple-choice carries reveal intent, not timing proof

**Decision.** `multiple-choice` requires `question` and `answer` cells. The question contains a
visible choice list; the answer is one or two short editable flat paragraphs with implicit
object-appear reveal intent and no explicit action directive.

**Why.** The layout communicates the instructional structure without making the author repeat a
redundant answer action or turning a popup into a general overlay system.

**Consequence.** The answer is placed in the fixed popup region and rejects explicit `<=` or `=>`
actions. The intent becomes a bounded OOXML animation request only when M5 builds it; attended
Impress playback remains the final visual acceptance evidence.

**Owner.** `marp_lib/layouts.py`, `marp_lib/djot_parser.py`, and
[wp_a1_animation_fidelity.md](active_plans/reports/wp_a1_animation_fidelity.md).

### Animation uses OOXML and Impress evidence

**Decision.** Build the bounded `appear` and `fade`, `object` and `paragraphs`, `on-click` animation
surface as OOXML in `marp_lib/pptx_animation.py`. LibreOffice Impress and ODP are the editing and
playback contract; PPTX is the native-builder and interchange artifact.

**Why.** Python provides stronger practical PPTX construction support, while the instructor uses
LibreOffice rather than Microsoft products. Official OOXML semantics plus observed LibreOffice
importer/exporter and Impress behavior provide a stable, replaceable boundary without external deck
templates.

**Consequence.** M5 is in progress. `pptx_animation.py` is the sole timing-tree owner and builds
OOXML directly; runtime XML templates and PowerPoint-authored decks are not contracts. Fast tests
cover structural semantics. Headless PPTX-to-ODP/package inspection and PDF final state are one-time
evidence; attended Impress playback is the only visual gate. `blue overlay` remains deferred.

**Owner.** `marp_lib/pptx_animation.py`, [PIPELINE.md](PIPELINE.md), and
[wp_a1_animation_fidelity.md](active_plans/reports/wp_a1_animation_fidelity.md).

## Canonical source design

### Geometry-first legacy plans preserve editable intent

**Decision.** Normalize trusted legacy ODP/PPTX content into `LegacySlidePlan` before emitting
extended-Djot. The plan carries source geometry, title evidence, independent editable components,
true table metadata, and a bounded spatial component only when the original relationship cannot be
represented as separate native objects.

**Why.** Legacy teaching slides mix ordinary semantic content with diagrams whose labels depend on
their original arrangement. Geometry-first planning preserves the editable majority while retaining
the coupled minority as one traceable component. It allows new layouts and source shapes to gain a
native owner without changing the import authority.

**Consequence.** The importer chooses titles from bounded upper-lane geometry, assigns components
atomically, and stops ambiguous arrangements for review. Ordinary text and pictures remain editable.
When a coupled region is necessary, an ODP import uses the original ODP and a direct PPTX import uses
the trusted input PPTX to supply a title-excluded, bounded raster crop; an exact full-slide crop
fails before publication. Poppler's fixed 144 DPI rendering, decoded-image validation, source-slide
provenance, digest-named assets, and staged all-or-nothing publication make the retained component
reproducible and auditable.

**Owner.** `marp_lib/importers/legacy_slide_plan.py`,
`marp_lib/importers/source_region_render.py`, `marp_lib/importers/pptx_to_djot.py`, and
[PIPELINE.md](PIPELINE.md).

### Source table metadata controls native tables

**Decision.** Emit an editable native table only from actual source table metadata. Preserve its
source-derived header status and intentional blanks; send merged or spanned cells to review before
publication.

**Why.** A visual grid does not establish table semantics. Retaining genuine source structure keeps
native tables editable without misclassifying diagram labels as rows and columns.

**Consequence.** Inferred lattices remain diagrams or review cases. A merged or spanned source table
fails source-located rather than receiving an invented table projection. Native table rendering
therefore has a bounded, extensible input contract for future span support.

**Owner.** `marp_lib/importers/legacy_slide_plan.py`,
`marp_lib/importers/legacy_djot_emitter.py`, and `marp_lib/layouts.py`.

### Ordinary layouts preflight optional titles and local headings

**Decision.** Ordinary panel layouts accept zero or one global H1, and each ordinary cell accepts
at most one local H2. Preflight title, heading, table, image, and text capacity before creating
native shapes.

**Why.** Imported slides sometimes have an absent global title or a component-local heading. The
same source allocation must remain readable whether the title is present or absent.

**Consequence.** A titleless layout receives its full content region. Local H2 allocation adapts
from 28 down to 14 CSS px before body placement. An unsupported combination or unreadable allocation
reports the relevant source location and leaves no partial shapes.

**Owner.** `marp_lib/layout_validation.py`, `marp_lib/layouts.py`, and [PIPELINE.md](PIPELINE.md).

### Legacy evidence keeps relations adaptable

**Decision.** Preserve direct source evidence for shape style, placeholder role, actual top/group
z-paths, and signed rotation beside normalized geometry. Route through the shared registry-topology
matcher before special relations; do not duplicate layout geometry in individual import relations.

**Why.** Style and ordering distinguish explanatory callouts and labels from ordinary prose, while a
single topology authority lets the importer gain layouts without changing each relation classifier.

**Consequence.** The importer may retain a visible degenerate connector through a bounded normalized
footprint and may recognize only positive, bounded relation classes. A narrow coarse-body and
picture-inset pair stays as direct editable objects in `two-panels`, with exact provenance and one
explicit permission. Caption pairing is one shared positive relation, grouped before topology and
reusing the existing `two-plus-one` and footer permission. Adaptive vertical image flow reserves text
at 28 through 14 CSS px, then scales every image uniformly. A private source crop must remain
bounded, protect a selected title, and retain only coupled source members; global or crop exceptions
are not a routing mechanism. Ambiguous arrangements remain editable components or stop for review.

**Owner.** `marp_lib/importers/legacy_geometry.py`,
`marp_lib/importers/legacy_topology.py`, `marp_lib/importers/legacy_new_visual_relations.py`, and
`marp_lib/importers/legacy_slide_plan.py`.

### Imported assets follow source reachability

**Decision.** Publish only generated assets reachable from the parsed Djot deck and keep them below
that deck's local `assets/` directory.

**Why.** Reachability makes a regenerated deck self-contained and prevents stale extracted files from
becoming unreviewed source dependencies.

**Consequence.** Missing, unsafe, or symlinked asset references stop publication. The staged importer
prunes unreachable files before its atomic publication step; future component owners can replace a
raster asset without changing this containment rule.

**Owner.** `marp_lib/importers/pptx_to_djot.py` and
`marp_lib/importers/source_region_render.py`.

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
