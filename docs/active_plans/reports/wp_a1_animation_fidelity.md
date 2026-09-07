# WP-A1 animation fidelity evidence

Date: 2026-09-07

Status: reopened. The earlier PowerPoint-authored-deck premise is superseded; it recorded a real
host inventory but was not a project requirement.

## Current contract

LibreOffice Impress and ODP are the editing and playback contract. PPTX is a convenient native
builder and interchange artifact because Python support is stronger than ODP support. Microsoft
PowerPoint is neither a compatibility oracle nor an acceptance gate.

WP-A1 establishes the smallest useful evidence for the supported animation surface:

- `appear` and `fade` effects;
- `object` and `paragraphs` sequences;
- `on-click` trigger;
- a top-level list item and its descendants for a paragraph sequence.

Use official OOXML documentation and LibreOffice importer/exporter behavior to guide the builder.
`marp_lib/pptx_animation.py` will be the sole programmatic OOXML owner. It builds the required
timing tree directly; no runtime XML templates or PowerPoint-authored reference decks are needed.

## Historical evidence retained

The 2026-09-06 check found no PowerPoint app in the bounded macOS paths. LibreOffice 26.2.5.2 is
installed. A direct UNO Python route was killed after its local dependency/process route proved
unsuitable for this task; the existing headless LibreOffice bridge works. The command evidence is
retained in [ENVIRONMENT.md](../../../devel/animation_reference/ENVIRONMENT.md).

## Acceptance evidence

After implementation, run these one-time checks on minimal generated decks:

1. Inspect the generated PPTX package for the intended, bounded OOXML timing semantics.
2. Convert PPTX to ODP through the headless LibreOffice bridge and inspect ODP/package semantics.
3. Attend an Impress slideshow and confirm object appearance and ordered top-level-list reveals.
4. Export PDF from the ODP and confirm its final-state presentation.

The attended Impress check is the only visual playback gate. Package inspection and conversion are
one-time implementation evidence, not permanent pytest work. The permanent tests remain fast,
offline structural checks of the builder's supported semantic model.

## Follow-up placeholder

Record command versions, generated-deck paths, observed Impress behavior, ODP/package findings, and
PDF final-state findings here after WP-A2/A3 implementation. Do not claim animation acceptance until
that record exists.
