# Plan: Extended-Djot slide language in the native PPTX/ODP/PDF pipeline

## Context

The repository owns a complete native-object output pipeline. `marp_lib/native_model.py` holds a
typed, presentation-neutral IR, `marp_lib/layouts.py` owns slide geometry, `marp_lib/native_export.py`
writes PPTX through `python-pptx`, and `marp_lib/libreoffice.py` converts that PPTX to ODP and then
PDF. That half is settled and contains no Marp vocabulary.

The input half is mid-migration. `marp_lib/marp_parser.py` (markdown-it-py) is the only front end.
Extended Djot is the settled successor foundation per `docs/DESIGN_DECISIONS.md:14`, an ODP-derived
eight-deck corpus already exists in `genetics/djot/` (336 visible slides), and Jotdown 0.10.0 is
pinned as the strict-Djot gate. No successor parser or exporter has been authorized: `docs/TODO.md:33`
gates that work behind grammar approval, and `docs/ROADMAP.md:23` places it at milestones M1 and M2.

The instructor has now approved the provisional grammar and is continuing to exercise it against real
lecture material. This plan implements that grammar as a second front end so `.djot` decks build to
native editable PPTX, ODP, and PDF alongside the existing `.md` decks.

## Objectives

- Build any `.djot` deck in `genetics/djot/` to native editable PPTX, ODP, and PDF through the
  existing pipeline, with no regression to the Marp path.
- Give every accepted directive a typed representation in the presentation-neutral IR, satisfying the
  `docs/ROADMAP.md:47` M2 parse contract.
- Reveal a text box or image on click, and reveal an outline one top-level item plus its descendants
  at a time, as native OOXML animations validated in LibreOffice Impress.
- Keep the grammar surface confined to one module so continued instructor syntax testing stays a
  single-file edit.
- Close the `docs/TODO.md` and `docs/ROADMAP.md` M1/M2 design gates with recorded decisions.

## Design philosophy

The plan's central trade-off is **owning a small language rather than integrating a large one**, in
both directions at once. On the input side we hand-write a parser for a defined Djot subset instead
of adopting a general Djot library; on the output side we reproduce a handful of
programmatic OOXML timing builder instead of a commercial engine such as Aspose.Slides. Both choices
accept more authored code today to avoid a dependency that would own our semantics. This is
`docs/REPO_STYLE.md` **long-term over short-term** and **fix the design, not the symptom**.

The rejected alternative worth naming is **slide multiplication** for reveals: emitting one extra
native slide per reveal step. It needs no animation XML and behaves identically in all three formats,
but it inflates slide count, repeats slides in the PDF handout, and forces the instructor to edit N
copies of one slide in Impress. It is not selected unless a concrete future teaching need shows the
bounded animation model cannot serve it.

- Evidence strategy: official OOXML semantics guide a small builder, then LibreOffice headless
  conversion and attended Impress playback establish the local contract. WP-A1 records one-time
  evidence without creating a PowerPoint compatibility requirement.

## Scope

- Extend `marp_lib/native_model.py` with reveal, named-slot, code, table, and math nodes.
- Make `layouts.LAYOUTS` the single owner of the layout and slot catalog.
- Add `marp_lib/djot_grammar.py` holding every directive spelling and the action vocabulary.
- Add a hand-written parser for the supported Djot subset across `djot_inline.py`, `djot_blocks.py`,
  and `djot_parser.py`.
- Rename the layout vocabulary to short names across the registry, CSS, Marp decks, and tests.
- Add the `multiple-choice` layout and its builder.
- Dispatch on file suffix in `native_export.py` so `.md` and `.djot` both build.
- Add `marp_lib/pptx_animation.py` as the sole direct OOXML timing-tree builder.
- Extend `tools/djot_slide_lint.py` to the full grammar, sourcing its vocabulary from
  `djot_grammar.py`.
- Regenerate the `genetics/djot/` corpus with short layout names.
- Add pytest coverage, one E2E runner, and the documentation close-out.

## Non-goals

- Implement `<= blue overlay`. Run-level text geometry is not obtainable from `python-pptx`, the
  corpus contains zero occurrences, and the instructor has deferred it. The parser recognizes it and
  emits a source-located "not yet supported" diagnostic.
- Retire the Marp front end or migrate `genetics/*.md` to Djot.
- Rename the `marp_lib` package or split its source-agnostic half into a neutral package.
- Implement animation effects beyond appear and fade, or triggers beyond on-click. No wipe, zoom,
  spin, motion paths, exit effects, emphasis effects, or object-triggered animations.
- Modify user-authored PPTX files that already contain animation timing.
- Add a Python Djot library, a Node runtime, or a commercial presentation engine.

## Current state summary

The table below is the planning baseline retained for traceability. It is not the current M5 state.

| Area | State |
| --- | --- |
| IR (`native_model.py`) | Complete and source-agnostic. No reveal, code, table, math, or named-slot nodes |
| Geometry (`layouts.py`) | 17 `LayoutSpec` entries, LibreOffice-derived long names. No slot names on the spec. `multiple-choice` absent |
| PPTX writer | Complete. `python-pptx`, explicit EMU geometry, no placeholders, no animation |
| ODP / PDF | Complete. `soffice` headless; PDF derives from ODP |
| Marp front end | Complete, the only front end. Hardcoded `.md` in `validate_input()` and `discover_decks()` |
| Djot front end | Absent |
| Djot corpus | 8 decks, 336 slides. Uses `=== layout:`, `@body/@left/@right/@gallery`, `#`/`##`, `![]()`. Zero `<=`, `=>`, or `multiple-choice` occurrences |
| Djot lint | `tools/djot_slide_lint.py` checks required slots only |
| Strict-Djot gate | Jotdown 0.10.0 pinned; all eight decks pass |

The corpus's untested surfaces matter for sequencing: `=== layout:`, `@slot`, `#`/`##`, and images
have 336 slides of real evidence behind them, while reveals and `multiple-choice` have none. The
milestone order therefore delivers a working build on the evidenced surface first.

### Current execution status

M1-M6 implementation is complete. M5's bounded OOXML builder, parser restrictions, permanent
structural tests, one-time LibreOffice bridge, ODP-derived PDF final-state check, and both explicit native
E2Es passed. M7's remaining M5-dependent item is an attended Impress click-playback observation.
The first attempt was blocked by macOS Screen Recording and Accessibility before slideshow control;
it is not a failed playback result and no PowerPoint check is required.

## Architecture boundaries and ownership

The seam is already cut: `native_model.Deck` is the contract, and everything downstream of
`native_export.render_native_pptx` is source-language agnostic. A Djot front end plugs in beside the
Marp one without touching the geometry or LibreOffice owners. `docs/PIPELINE.md:45` fixes the import
direction -- `terminal_output` invokes `native_export`, which imports the layout and LibreOffice
owners, and none of those import upward.

Two new boundaries this plan creates:

- `djot_grammar.py` derives its layout and slot catalog from `layouts.LAYOUTS`. The dependency runs
  grammar -> layouts, never the reverse, matching `marp_parser.py:17`.
- `pptx_animation.py` is the only module permitted to touch `python-pptx` internals
  (`slide._element`, `parse_xml`). No other module reaches past the public API.

### Mapping (milestones / workstreams -> components / patches)

| Milestone / Workstream | Component | Review boundary |
| --- | --- | --- |
| M1 / WS-CORE | `marp_lib/native_model.py`, `marp_lib/layouts.py` (`LayoutSpec` only), `marp_lib/djot_grammar.py` | IR additions are trailing defaulted fields; Marp path behavior unchanged |
| M2 / WS-LANG | `marp_lib/djot_inline.py`, `djot_blocks.py`, `djot_parser.py` | Source in, `Deck` out. No PPTX or geometry knowledge |
| M3 / WS-LAYOUT | `marp_lib/layouts.py`, `themes/genetics.css`, `genetics/*.md`, `marp_parser.py` | One atomic rename; CSS contract test never sees a half-renamed registry |
| M4 / WS-LANG | `marp_lib/native_export.py`, `marp_lib/terminal_output.py` | Suffix dispatch only; no parser logic |
| M5 / WS-ANIM | `marp_lib/pptx_animation.py`, builder signatures | Sole owner of python-pptx internals and of the `<p:timing>` tree |
| M6 / WS-QA | `tools/djot_slide_lint.py`, `genetics/djot/*.djot` | Lint vocabulary imported from `djot_grammar.py`, never restated |
| M7 / WS-QA | `tests/`, `docs/` | Repository hygiene gates and documentation close-out |

## Milestone plan

| M | Title | Summary | Goal |
| --- | --- | --- | --- |
| M1 | IR and catalog foundation | Reveal/slot/content nodes in the IR; `LayoutSpec` owns slot names; grammar table derives from it | One source of truth for layouts, slots, and directive spellings |
| M2 | Djot parser | Hand-written parser for the supported subset producing `Deck` | `.djot` source parses to the IR with source-located errors |
| M3 | Layout vocabulary and `multiple-choice` | Short-name rename across registry, CSS, decks, tests; new layout and builder | Short names are canonical everywhere; no alias layer |
| M4 | Export wiring | Suffix dispatch in `native_export`; `DjotParseError` in the terminal lane | A `.djot` deck builds to PPTX, ODP, and PDF |
| M5 | Animation backend | OOXML builder and LibreOffice evidence | Structural and bridge semantics pass; attended click playback remains open |
| M6 | Linter and corpus | Full-grammar lint; corpus regenerated on short names | Corpus and lint agree with the parser |
| M7 | Verification and close-out | Pytest modules, E2E runner, documentation | Permanent/native gates pass; attended M5 observation remains |

### Milestone: M1 IR and catalog foundation

- Depends on: none
- Deliverables: `Reveal`, `RevealEffect`, `RevealSequence`, `RevealTrigger` in `native_model.py`;
  `reveal` fields on five node types; `Cell.name`; `CodeBlock`, `Table`, `DisplayMath`, `InlineMath`;
  `LayoutSpec.slot_names` / `allows_title` / `allows_subtitle`; `djot_grammar.py`
- Workstreams: WS-CORE
- Entry criteria: none
- Exit criteria: `pytest tests/` green with the Marp path unchanged; `djot_grammar` imports its
  catalog from `layouts.LAYOUTS` with no restated layout or slot names anywhere
- Parallel-plan ready: no. Single-owner foundation; every later milestone depends on these type
  definitions, so splitting it would create churn rather than throughput.

### Milestone: M2 Djot parser

- Depends on: M1
- Deliverables: `djot_inline.py`, `djot_blocks.py`, `djot_parser.py`, `DjotParseError`
- Workstreams: WS-LANG
- Entry criteria: M1 exit criteria met
- Exit criteria: every deck in `genetics/djot/` parses to a `Deck`; each unsupported-but-valid Djot
  construct raises a source-located diagnostic naming the construct; `blue overlay` raises its
  deferral diagnostic
- Parallel-plan ready: yes. WP-L1 (inline) and WP-L2 (blocks) are independent given M1's types;
  WP-L3 depends on both.

### Milestone: M3 Layout vocabulary and `multiple-choice`

- Depends on: M1
- Deliverables: renamed `LAYOUTS` keys and `LayoutSpec.name` values; updated CSS selectors, Marp deck
  `_class` values, and `marp_parser.LAYOUT_CLASSES`; `build_multiple_choice`
- Workstreams: WS-LAYOUT
- Entry criteria: M1 exit criteria met; the twelve short spellings confirmed by the instructor
- Exit criteria: `pytest tests/` green; `./build_slides.sh genetics` preserves the selected native
  layout semantics
- Parallel-plan ready: no. The rename must land atomically across registry, CSS, decks, and tests.

### Milestone: M4 Export wiring

- Depends on: M2, M3
- Deliverables: suffix dispatch in `validate_input()` and `discover_decks()`; `export_deck()` routed
  through the dispatcher; `DjotParseError` in `terminal_output.py:150`
- Workstreams: WS-LANG
- Entry criteria: M2 and M3 exit criteria met
- Exit criteria: `tools/marp_export.py --format all` builds a `.djot` deck to all three formats;
  mixed `.md` and `.djot` folder discovery works
- Parallel-plan ready: no. Small, single-file-cluster change.

### Milestone: M5 Animation backend

- Depends on: M1, M3; WP-A1 may start immediately
- Deliverables: recorded LibreOffice evidence from WP-A1; `pptx_animation.py`; builder threading
- Workstreams: WS-ANIM
- Entry criteria: documented OOXML and LibreOffice bridge behavior reviewed
- Exit criteria: implementation, permanent structural tests, and headless PPTX-to-ODP/PDF evidence
  pass; an attended Impress slideshow records click-by-click object and top-level-list behavior.
- Current evidence: implementation, structural tests, bridge, and PDF final state passed. The
  attended check is open because macOS permissions blocked input and capture before any click.
- Parallel-plan ready: only after production stabilization. WP-A2 then WP-A3 are serialized under
  one production owner because they share the timing-tree seam. P2 parser validation, P3 structural
  validation, P4 architecture review, P5/P5b bridge checks, P8b permanent regression, and P9 native
  E2E form a safe independent fan-out after that owner finishes.

### Milestone: M6 Linter and corpus

- Depends on: M2, M3
- Deliverables: full-grammar `tools/djot_slide_lint.py`; regenerated `genetics/djot/*.djot`
- Workstreams: WS-QA
- Entry criteria: M2 and M3 exit criteria met
- Exit criteria: lint passes on the regenerated corpus with `--require-native`; every corpus deck
  parses and builds
- Parallel-plan ready: yes. WP-Q1 (lint) and WP-Q2 (corpus) are independent.

### Milestone: M7 Verification and close-out

- Depends on: M4, M5, M6
- Deliverables: four pytest modules; `tests/e2e/e2e_djot_native_layouts.py`; documentation updates
- Workstreams: WS-QA
- Entry criteria: M4, M6, and M5 implementation/headless evidence complete
- Exit criteria: every permanent and one-time command in the verification strategy passes; the
  attended Impress check is recorded; `docs/CHANGELOG.md` and roadmap gates updated
- Current evidence: 1,913 permanence-audited tests and both explicit native E2Es passed. Only the attended M5
  observation remains open.
- Parallel-plan ready: yes after production stabilization. Documentation and independent evidence
  review may run in parallel; they do not modify the timing implementation.

## Workstream breakdown

### Workstream: WS-CORE

- Goal: one authoritative set of types and one authoritative catalog.
- Owner: expert_coder
- Work packages: WP-C1, WP-C2
- Needs: nothing
- Provides: IR node types and the derived grammar catalog for every other workstream
- Review boundary, when modifying the repository: additions only; no change to existing field order
  or Marp path behavior.

### Workstream: WS-LANG

- Goal: turn `.djot` source into a `Deck` and route it into the exporter.
- Owner: coder
- Work packages: WP-L1, WP-L2, WP-L3, WP-L4
- Needs: WS-CORE types and catalog
- Provides: a working `.djot` build path
- Review boundary, when modifying the repository: no geometry, no PPTX, no python-pptx imports.

### Workstream: WS-LAYOUT

- Goal: short names canonical everywhere, plus the `multiple-choice` layout.
- Owner: coder
- Work packages: WP-Y1, WP-Y2
- Needs: WS-CORE `LayoutSpec` fields; instructor confirmation of the twelve spellings
- Provides: the layout and slot catalog the grammar derives from
- Review boundary, when modifying the repository: the rename lands as one change.

### Workstream: WS-ANIM

- Goal: real LibreOffice Impress reveals on native objects.
- Owner: expert_coder
- Work packages: WP-A1, WP-A2, WP-A3
- Needs: WS-CORE `Reveal` types; WS-LAYOUT builder set
- Provides: the animation backend and recorded LibreOffice evidence
- Review boundary, when modifying the repository: sole owner of `slide._element`, `parse_xml`, and
  the `<p:timing>` tree.

### Workstream: WS-QA

- Goal: prove the language works and record the decisions.
- Owner: tester
- Work packages: WP-Q1, WP-Q2, WP-Q3, WP-Q4
- Needs: all other workstreams
- Provides: repository-gate evidence and documentation close-out
- Review boundary, when modifying the repository: tests follow `docs/PYTEST_STYLE.md`; no new
  `tests/fixtures/` directory.

## Work packages

### Work package: WP-C1 IR extensions

- Owner: expert_coder
- Touch points: `marp_lib/native_model.py`, a rejection branch in `marp_lib/layouts.py`
- Depends on: none
- Acceptance criteria: all additions are trailing defaulted fields on existing frozen dataclasses;
  the IR carries no grammar token and no PowerPoint vocabulary (`nodeType`, `presetID`,
  `presetClass`); a layout that cannot place a new block type raises a source-located error rather
  than dropping it, per `docs/DESIGN_DECISIONS.md:272`.

The reveal vocabulary stays deliberately small, with room to grow:

```python
class RevealEffect(enum.Enum):
	APPEAR = "appear"
	FADE = "fade"

class RevealSequence(enum.Enum):
	OBJECT = "object"
	PARAGRAPHS = "paragraphs"

class RevealTrigger(enum.Enum):
	ON_CLICK = "on-click"
```

`RevealTrigger` carries one member today. `WITH_PREVIOUS` and `AFTER_PREVIOUS` are named in the
non-goals and cost one enum member plus one direct-builder branch each when a deck needs them.
`RevealSequence` is the extension point for a future by-outline-level build; adding
`OUTLINE_LEVEL_1` would not disturb the rest of the pipeline.

- Evidence or review, when useful: `pytest tests/` green with the Marp path unchanged proves the
  additions are non-breaking.
- Obvious follow-ons: none.

### Work package: WP-C2 Grammar table

- Owner: expert_coder
- Touch points: `marp_lib/djot_grammar.py`, `LayoutSpec` in `marp_lib/layouts.py`
- Depends on: WP-C1
- Acceptance criteria: `LayoutSpec` gains `slot_names`, `allows_title`, `allows_subtitle`, making
  `layouts.LAYOUTS` the sole catalog owner; `djot_grammar` derives its legal layouts and slots from
  it and restates nothing; the module holds the four whole-line-anchored directive patterns, the
  spelling-to-`Reveal` map, the deferred-action set containing `blue overlay`, and the `&prime;` ->
  U+2032 projection from `docs/DESIGN_DECISIONS.md:164`; every pattern is anchored to a whole line so
  hard-wrapping prose cannot create structure (`docs/HUMAN_GUIDANCE.md:122`).

Initial spelling map: `appear` -> `(APPEAR, OBJECT)`, `cascade appear` -> `(APPEAR, PARAGRAPHS)`. The
IR supports fade before the grammar spells it; `fade` and `cascade fade` are one table row each when
the instructor wants them.

- Evidence or review, when useful: a grep proving no layout or slot name literal exists outside
  `layouts.py`.
- Obvious follow-ons: none.

### Work package: WP-L1 Djot inline layer

- Owner: coder
- Touch points: `marp_lib/djot_inline.py`
- Depends on: WP-C1
- Acceptance criteria: parses `_emphasis_`, `*strong*`, `` `verbatim` ``, `[link](url)`,
  `![alt](path)`, `$inline$`, and hard breaks into `native_model` inline tuples; unsupported inline
  syntax raises rather than passing through as literal text.
- Evidence or review, when useful: table-driven pytest cases with inline source strings.
- Obvious follow-ons: none.

### Work package: WP-L2 Djot block layer

- Owner: coder
- Touch points: `marp_lib/djot_blocks.py`
- Depends on: WP-C1
- Acceptance criteria: parses headings, bullet and ordered lists under Djot's simpler indentation
  rule, block quotes, fenced code blocks, pipe tables, `$$display$$`, and one-line attributes;
  indented code blocks are not treated as code, which is the instructor's stated reason for
  preferring Djot.
- Evidence or review, when useful: a nested-list case proving indentation behavior differs from
  CommonMark.
- Obvious follow-ons: none.

### Work package: WP-L3 Deck assembly

- Owner: coder
- Touch points: `marp_lib/djot_parser.py`
- Depends on: WP-L1, WP-L2, WP-C2
- Acceptance criteria: `parse_deck(input_path) -> Deck` mirrors `marp_parser.parse_deck` so the front
  ends are interchangeable; splits on `=== layout:`; validates layout and slot names against the
  derived catalog; binds each `@slot` region to a named `Cell`; hoists `#`/`##` to title and subtitle
  and rejects both where the layout declares no title region; attaches `<=` and `=>` actions to the
  neighbouring block or list item; raises `DjotParseError` carrying `path:line`; `blue overlay`
  produces its deferral diagnostic.
- Evidence or review, when useful: an accepted specimen and a rejected near-match per construct, as
  required by `docs/ROADMAP.md:38`.
- Obvious follow-ons: none.

### Work package: WP-L4 Suffix dispatch

- Owner: coder
- Touch points: `marp_lib/native_export.py`, `marp_lib/terminal_output.py`
- Depends on: WP-L3, WP-Y1
- Acceptance criteria: `validate_input()` and `discover_decks()` dispatch over
  `{".md": marp_parser.parse_deck, ".djot": djot_parser.parse_deck}`; `has_marp_front_matter()` and
  `MARP_TRUE_PATTERN` apply to `.md` only, since `=== layout:` on line one makes a `.djot` file
  unambiguous without front matter; `export_deck()` calls the dispatcher rather than `validate_input`
  directly; `DjotParseError` joins the caught-error tuple at `terminal_output.py:150` so Djot
  failures print as source-located build failures rather than tracebacks.
- Evidence or review, when useful: a folder containing both suffixes discovers and builds both.
- Obvious follow-ons: none. `tools/marp_export.py` and `build_slides.sh` need no flag changes.

### Work package: WP-Y1 Short-name rename

- Owner: coder
- Touch points: `marp_lib/layouts.py`, `themes/genetics.css`, `genetics/*.md`,
  `marp_lib/marp_parser.py`
- Depends on: WP-C2; instructor confirmation of the twelve spellings
- Acceptance criteria: keys and `LayoutSpec.name` values renamed per the table below; builder function
  names unchanged; no alias layer anywhere; CSS selectors and source classes are updated atomically,
  while authoritative native behavior is verified by build/E2E rather than static CSS declaration tests.

| Current key | Short name |
| --- | --- |
| `title-content` | `one-panel` |
| `title-two-content` | `two-panels` |
| `title-content-and-two-content` | `one-plus-two-panels` |
| `title-two-content-and-content` | `two-plus-one-panels` |
| `title-content-over-content` | `stacked-panels` |
| `title-two-content-over-content` | `two-over-one-panels` |
| `title-four-content` | `four-panels` |
| `title-six-content` | `six-panels` |
| `vertical-title-vertical-text` | `vertical-panel` |
| `vertical-title-text-chart` | `vertical-title-two-panels` |
| `title-vertical-text` | `vertical-text-panel` |
| `title-two-vertical-text-clipart` | `two-panels-vertical-clipart` |
| `blank`, `title-only`, `title-slide`, `centered-text`, `gallery` | unchanged |

- Evidence or review, when useful: `./build_slides.sh genetics` produces the same geometry as before
  the rename.
- Obvious follow-ons: none.

### Work package: WP-Y2 `multiple-choice` layout

- Owner: coder
- Touch points: `marp_lib/layouts.py`
- Depends on: WP-Y1
- Acceptance criteria: `@question` renders in the main content rectangle and `@answer` in a fixed
  bottom-right popup region, each required exactly once; `@answer` carries an implicit whole-object
  appear on first advance, so `<= appear` or `=> appear` on its content is a source error, per
  `docs/DESIGN_DECISIONS.md:122`.
- Evidence or review, when useful: the layout appears in the M7 E2E runner.
- Obvious follow-ons: none.

### Work package: WP-A1 LibreOffice evidence

- Owner: expert_coder
- Touch points: `devel/animation_reference/` (new, evidence only)
- Depends on: none. It may establish environment/documentation evidence concurrently with M1-M4,
  but implementation acceptance uses a generated deck after WP-A3.
- Acceptance criteria: document the official OOXML animation model and existing LibreOffice bridge;
  after the builder exists, use minimal generated object and paragraph decks to inspect timing/package
  semantics, headlessly convert PPTX to ODP, attend an Impress slideshow, and inspect the ODP-derived
  PDF final state. Record the results in `docs/active_plans/reports/`.
- Evidence or review, when useful: package and bridge checks are one-time evidence; attended Impress
  playback is the visual acceptance gate.
- Obvious follow-ons: after implementation stabilization, run the independent P2/P3/P4/P5 fan-out.

### Work package: WP-A2 Timing model

- Owner: expert_coder
- Touch points: `marp_lib/pptx_animation.py`
- Depends on: WP-A1 and the settled M1 reveal types
- Acceptance criteria: define direct builder functions for appear/fade object and paragraph timing
  from official OOXML semantics. Keep the model small and explicit: on-click only, with a paragraph
  sequence advancing each top-level item and its descendants. No runtime XML template files.
- Evidence or review, when useful: a focused structural test verifies supported timing semantics;
  package inspection remains one-time evidence.
- Obvious follow-ons: WP-A3, owned by the same production owner; do not overlap edits to the timing
  seam.

### Work package: WP-A3 Animation writer

- Owner: expert_coder
- Touch points: `marp_lib/pptx_animation.py`, builder signatures in `marp_lib/layouts.py`,
  `marp_lib/native_export.py`
- Depends on: WP-A2, WP-Y1; starts only after WP-A2's production edit is stable
- Acceptance criteria:
  - `PptxAnimationWriter(slide)` is created once per native slide in
    `native_export.render_native_pptx`. It is the one controlled mutation point: `.register(shape,
    reveal, paragraph_range=None)` records a whole-shape or inclusive paragraph-range step, and
    `.finalize()` allocates timing IDs, constructs OOXML elements programmatically, assembles exactly
    one `<p:timing>` tree, and appends it to `slide._element`. No runtime template or post-save package
    mutation reaches the slide.
  - Timing-node IDs are allocated independently and must be unique within the timing graph. Shape
    targets use each actual same-slide `<p:cNvPr id=...>` as `<p:spTgt spid=...>`; their numeric values
    need not be disjoint from timing-node IDs.
  - `.finalize()` enforces the generated-slide invariant: these slides are compiler-generated and
    start blank, so any pre-existing `<p:timing>` -- including one wrapped in `<mc:AlternateContent>`,
    the shape that has corrupted presentations in a known python-pptx issue -- is a bug. Raise rather
    than merge.
  - `ParagraphRevealRange` carries the source projection's inclusive paragraph groups. A paragraph
    build stays one native text shape; top-level groups include descendants, keeping the outline
    editable rather than creating one shape per bullet.
  - `layouts.render_layout` receives the writer and attaches it to the slide for shared helper use;
    existing `LayoutSpec.builder` signatures remain unchanged. `native_export.render_native_pptx`
    finalizes the writer after layout rendering, page-number and notes creation, and before saving.
- Evidence or review, when useful: independent reviewer agent check that python-pptx internals appear
  in no other module.
- Obvious follow-ons: fan out P2 parser validation, P3 structural validation, P4 architecture
  review, P5/P5b bridge evidence, P8b permanent regression, and P9 native E2E. These are
  independent read-only or disposable checks, not concurrent production edits.

### Work package: WP-Q1 Full-grammar linter

- Owner: tester
- Touch points: `tools/djot_slide_lint.py`
- Depends on: WP-C2, WP-L3
- Acceptance criteria: checks slide declarations, known layouts, title and subtitle permission, slot
  names, required and duplicate slots, action attachment, and the `multiple-choice` contract; reads
  its vocabulary from `djot_grammar.py` so lint and parser cannot drift; stays source-only and never
  opens LibreOffice (`docs/DESIGN_DECISIONS.md:131`).
- Evidence or review, when useful: lint and parser agree on every corpus deck.
- Obvious follow-ons: none.

### Work package: WP-Q2 Corpus regeneration

- Owner: coder
- Touch points: `tools/odp_to_djot.py`, `genetics/djot/*.djot`
- Depends on: WP-Y1
- Acceptance criteria: the importer emits short layout names and the eight decks are regenerated; the
  corpus's multiple consecutive `##` lines on `title-slide` are resolved against the one-subtitle rule
  at `djot_slide_extension_exploration.md:117`; all eight decks still pass the Jotdown gate.
- Evidence or review, when useful: `import_report.json` slide and image counts unchanged from
  `genetics/djot/README.md:14`.
- Obvious follow-ons: this rule decision belongs in `docs/DESIGN_DECISIONS.md` (WP-Q4).

### Work package: WP-Q3 Test suite

- Owner: tester
- Touch points: `tests/test_djot_parser.py`, `tests/test_djot_grammar.py`,
  `tests/test_pptx_animation.py`, `tests/test_marp_export.py`,
  `tests/e2e/e2e_djot_native_layouts.py`
- Depends on: WP-L3, WP-A3, WP-Y2
- Acceptance criteria: all pytest modules follow `docs/PYTEST_STYLE.md` -- inline source strings,
  `tmp_path` only, no LibreOffice, no network, well under one second each, and no new
  `tests/fixtures/` directory. Coverage: source-to-`Deck` per directive plus a rejected near-match per
  construct and the `blue overlay` deferral; spelling-to-`Reveal` mapping and unknown-action
  rejection; timing IDs unique within their graph and independently allocated, targets matching actual
  same-slide shape IDs, a pre-existing timing tree raising, and a supported OOXML structure and
  paragraph grouping; suffix dispatch. The E2E
  runner covers every short-named layout plus `multiple-choice` through the real PPTX/ODP/PDF chain.
- Evidence or review, when useful: assertions target behavior, not collection sizes or key lists.
- Obvious follow-ons: none.

### Work package: WP-Q4 Documentation close-out

- Owner: planner
- Touch points: `docs/CHANGELOG.md`, `docs/DESIGN_DECISIONS.md`, `docs/HUMAN_GUIDANCE.md`,
  `docs/PIPELINE.md`, `docs/TODO.md`, `docs/ROADMAP.md`
- Depends on: WP-Q3
- Acceptance criteria: changelog entry under today's date using the repository's section order, with
  the `blue overlay` deferral under `### Decisions and Failures`; the resolved decisions promoted into
  `docs/DESIGN_DECISIONS.md` with `Decision` / `Why` / `Consequence` / `Owner` fields; the
  instructor's animation-route and deferral statements recorded in `docs/HUMAN_GUIDANCE.md` in his own
  voice; `docs/PIPELINE.md` component map and ownership table updated for the second front end;
  `docs/TODO.md` and `docs/ROADMAP.md` M1/M2 gates ticked.
- Evidence or review, when useful: `pytest tests/test_markdown_links.py`.
- Obvious follow-ons: name the language, which `docs/HUMAN_GUIDANCE.md:180` defers until the grammar
  is selected. That gate is now closed, so naming is unblocked but out of this plan's scope.

## Acceptance criteria and gates

- Per-patch gate: `source source_me.sh && pytest tests/` green, plus the hygiene lints
  (`test_pyflakes_code_lint`, `test_function_typing`, `test_indentation`, `test_ascii_compliance`,
  `test_source_file_line_limit`, `test_import_requirements`). No new pip dependency is introduced, so
  `test_import_requirements` must stay green without edits.
- Integration gate: a `.djot` deck builds to all three formats; `./build_slides.sh genetics` still
  builds the Marp decks; M5's generated PPTX converts to ODP through LibreOffice and preserves its
  bounded package semantics.
- Independent review gate, when useful: a reviewer agent confirms python-pptx internals are confined
  to `pptx_animation.py` and that no layout or slot name is restated outside `layouts.py`.

## Test and verification strategy

Three lanes, matching `docs/PIPELINE.md:104`.

Fast pytest lane:

```bash
source source_me.sh && pytest tests/
source source_me.sh && pytest tests/test_pyflakes_code_lint.py tests/test_function_typing.py \
	tests/test_source_file_line_limit.py tests/test_ascii_compliance.py
```

Source-only lint and build lane:

```bash
source source_me.sh && python3 tools/djot_slide_lint.py --require-native \
	--native-executable "$(command -v jotdown)" genetics/djot
source source_me.sh && python3 tools/marp_export.py --format all \
	genetics/djot/lect02d-dna_structure_overview.djot
source source_me.sh && ./build_slides.sh genetics
```

Native semantic E2E lane:

```bash
source source_me.sh && python3 tests/e2e/e2e_djot_native_layouts.py
```

Manual checks, which carry the claims automation cannot make:

1. Inspect the generated PPTX and converted ODP packages for the supported timing semantics.
2. Attend an Impress slideshow and confirm a shape appears on click and an outline advances by
   top-level item plus descendants.
3. Confirm text, lists, and images are selectable native objects, never a full-slide image.
4. Confirm the ODP-derived PDF presents the final reveal state.

## Migration and compatibility policy

- Both front ends run in parallel for the life of this plan. `.md` decks keep building unchanged.
- The layout rename is a breaking vocabulary change applied atomically across the registry, CSS, Marp
  decks, and tests. No alias layer is introduced, so a stale `_class` value fails loudly at parse
  time rather than silently selecting a default.
- `genetics/djot/` is regenerable importer output, not hand-authored source, so rewriting it carries
  no authoring cost.
- The strict-Djot gate is unconditional: no slide feature waives a Jotdown failure
  (`docs/HUMAN_GUIDANCE.md:112`).

## Risk register

| Risk | Impact | Trigger | Owner | Mitigation |
| --- | --- | --- | --- | --- |
| LibreOffice alters PPTX animation during ODP conversion | High. ODP is the instructor's editing format | One-time bridge or attended Impress evidence changes the supported behavior | expert_coder | Keep direct OOXML construction isolated in `pptx_animation.py`; update the small semantic model only for observed LibreOffice behavior |
| python-pptx internals shift under `slide._element` | Medium. Animation export breaks on dependency bump | Structural animation test fails after an upgrade | expert_coder | Internals remain confined to one module; fast tests assert semantic structure, not serialized bytes |
| Grammar changes during implementation | Medium. Rework across parser modules | Instructor revises a spelling mid-flight | coder | Every spelling lives in `djot_grammar.py`; patterns must not leak into parser modules |
| Layout rename half-lands | Medium. CSS contract test fails confusingly | Registry renamed before CSS and decks | coder | WP-Y1 is explicitly atomic and is its own non-parallel milestone |
| Reveals and `multiple-choice` have zero corpus evidence | Medium. Grammar may not survive contact with real lectures | A real deck needs a form the grammar cannot spell | planner | Milestones deliver the evidenced surface (M1-M4) before the unevidenced one (M5); the instructor is exercising the grammar concurrently |
| Hand-written parser diverges from strict Djot | Medium. Accepts source Jotdown rejects | Jotdown gate fails on a deck the parser accepted | coder | Jotdown decides syntactic validity and runs first; our parser only decides supported semantics |

## Rollout and release checklist

- [x] WP-A1 LibreOffice evidence recorded in `docs/active_plans/reports/`
- [x] Twelve short layout spellings confirmed by the instructor
- [ ] All milestone exit criteria met (attended M5 playback remains open)
- [x] Fast pytest lane green, including every hygiene gate
- [x] Lint and build lane green on all eight corpus decks
- [x] E2E lane green across every layout including `multiple-choice`
- [x] One-time headless PPTX-to-ODP/package evidence recorded
- [ ] Attended Impress playback recorded (macOS permissions blocked the attempt before clicks)
- [x] ODP-derived PDF final-state evidence recorded
- [x] Marp decks still build via `./build_slides.sh genetics`
- [x] `docs/CHANGELOG.md` entry written
- [x] `docs/ROADMAP.md` M1 and M2 gates closed
- [ ] Human review, then human commit (agents do not run `git commit`)

## Documentation close-out requirements

- Active plan / progress tracker: keep this plan in place until M7 closes. Git is out of scope for
  this implementation, so no staging, moving, or archiving action is part of this work.
- docs/CHANGELOG.md entry: today's date block using the repository's canonical section order.
  `### Additions and New Features` for the language, parser, and animation backend;
  `### Behavior or Interface Changes` for the layout rename; `### Decisions and Failures` for the
  `blue overlay` deferral and the attended Impress finding, once recorded.
- Archive / closure notes: record the closure of the `docs/TODO.md:33` grammar gate and the
  `docs/ROADMAP.md` M1/M2 gates, and note that naming the language is now unblocked.

## Open questions and decisions needed

- Manager/subagent decision procedure:
  - Decision owner or dedicated class: expert_coder for the bounded OOXML builder; instructor for
    the layout spellings and attended Impress acceptance.
  - Evidence and decision rule: official OOXML guides the implementation; actual LibreOffice bridge
    and Impress behavior decide its supported semantics. The twelve short spellings need one
    instructor confirmation before WP-Y1 begins; everything else in M1 and M2 proceeds without it.
- Non-blocking follow-up:
  - Naming the language, unblocked once the grammar gate closes but out of scope here.
  - Adding `fade` and `cascade fade` spellings to the grammar; the IR and direct builder support fade
    before the grammar spells it.
  - Selecting the formatter, editor-rule, and standalone-linter lanes of the strict compatibility
    suite, still open at `docs/DESIGN_DECISIONS.md:34`.
  - Reconsidering `blue overlay` if a rendering contract that avoids run-level geometry emerges.

## Resolved decisions

| Decision | Resolution | Source |
| --- | --- | --- |
| Grammar gate | Lifted for `=== layout:`, `@slot`, `#`/`##`, `<= appear`, `=> appear`, `=> cascade appear`, `multiple-choice` | Instructor |
| `<= blue overlay` | Deferred; parsed and rejected with a source-located diagnostic | Instructor: "I decided it was too hard" |
| Front-end coexistence | Parallel; the Marp path is untouched | Instructor |
| Djot parsing | Hand-written parser over a defined supported subset; no new pip dependency | Instructor |
| Layout vocabulary | Short names, canonical everywhere, no alias layer; the twelve spellings remain provisional | Instructor: "the shorter names win" |
| Animation route | Programmatic OOXML in `pptx_animation.py`, appended as one `<p:timing>` tree before save; LibreOffice/Impress is the contract | Instructor |
| Animation surface | Appear and fade, on click, targeting a whole object or an outline's paragraphs | Instructor: "text boxes or images to appear or sometimes do outline items one at a time" |
| Outline builds | One native text shape with each top-level item and its descendants advancing together | Instructor |
| Animation specification source | Official OOXML plus LibreOffice importer/exporter and attended Impress evidence | Instructor |
