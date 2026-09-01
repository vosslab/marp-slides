# Design decisions

<!-- VENDORED HEADER: START -->
Record each durable decision about how this code and repository are shaped, once it is settled, with
the reasoning a later reader needs. Guidance Neil Voss states belongs in
[HUMAN_GUIDANCE.md](HUMAN_GUIDANCE.md), dated history in `docs/CHANGELOG.md`, open discussion in
`docs/active_plans/decisions/`. [PROPAGATED HEADER - ENTRIES BELOW ARE YOURS]
<!-- VENDORED HEADER: END -->

## Native presentation design

### Marp is an authoring-language specification

**Decision.** Retain canonical Marp Markdown and independently implement its supported language
subset in repository-owned Python.

**Why.** Marp offers a mature authoring language, while its runtime and browser render paths do not
meet the editable native-object product requirement.

**Consequence.** `OTHER_REPOS/marp-core` and `OTHER_REPOS/marp-cli` are conformance evidence only.
The production dependency graph contains no Marp code, CLI, Node, browser, or render stage.

**Owner.** `marp_lib/marp_parser.py` and `docs/PIPELINE.md`.

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

### ODP-derived PDF is the only PDF path

**Decision.** Generate PPTX first, convert it to editable ODP, then have LibreOffice create PDF from
that ODP.

**Why.** One ordered pathway avoids a second PDF implementation and makes the distributed PDF
represent the editable classroom artifact.

**Consequence.** `build_slides.sh` retains the PPTX, ODP, and ODP-derived PDF artifacts. PDF review
rendering remains evidence only and never becomes slide content.

**Owner.** `marp_lib/native_export.py`, `build_slides.sh`, and
`tests/e2e/e2e_native_odp_semantics.py`.

### Native objects replace slide rasterization

**Decision.** Native text, lists, shapes, component images, links, and notes are the only normal
output objects.

**Why.** A full-slide image loses editability, searchability, accessibility, and durable layout
ownership.

**Consequence.** Source features without an explicit native mapping fail with an actionable source
diagnostic. Temporary visual renders may support QA but never enter canonical Markdown or output.

**Owner.** `marp_lib/layouts.py`, `marp_lib/native_export.py`, and their tests.

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

**Owner.** `docs/RELATED_PROJECTS.md`.
