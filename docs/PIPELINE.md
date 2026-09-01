# Pipeline architecture

This repository is built as a set of narrow presentation components rather than one large
converter. Marp CLI remains the Markdown renderer. Python supplies the semantic import and
orchestration layers, while LibreOffice bridges the formats Marp does not read or write.

The architecture is successful when each component owns one transformation, exchanges a clear
artifact with the next component, and leaves Marp Markdown as the only long-lived authoring source.

## Component map

```text
                         ONE-TIME IMPORT SIDE

 legacy ODP evidence
         |
         v
 ODP validation and visibility
         |
         v
 LibreOffice normalization bridge
         |
         v
 structured PPTX
         |
         v
 Python semantic importer
         |
         v
 Marp Markdown + assets + import report
         |
         v
 instructor cleanup
         |
         v
 authoritative Marp source package


                         REPEATABLE BUILD SIDE

 authoritative Marp source package
         |
         +---- central genetics theme
         |
         v
 shared Marp render adapter
         |
         +-----------------------+
         |                       |
         v                       v
       PDF                rendered PPTX
                                 |
                                 v
                       LibreOffice ODP bridge
                                 |
                                 v
                           classroom ODP
```

## Architectural components

### Legacy evidence

The original ODP is retained as evidence for a one-time migration. It is not forced to remain an
active source after conversion. This gives the importer a stable reference for slide order,
visibility, notes, and content without creating a permanent round trip.

### ODP boundary

`tools/odp_to_marp.py` owns the ODP-facing edge. It validates the source container, records the
original slide sequence and visibility, and asks LibreOffice for a temporary PPTX representation.

This component exists because LibreOffice understands ODP semantics and `python-pptx` provides a
more practical structured object model for extraction. The temporary PPTX is a normalization bridge,
not a new authoring format.

### Visibility resolver

`tools/odp_visibility.py` isolates ODP page and style visibility from the rest of the importer. The
ODP-derived result remains authoritative when LibreOffice creates the temporary PPTX.

Keeping visibility separate prevents an external format conversion from silently changing the
teaching sequence.

### Semantic importer

`tools/pptx_to_marp.py` is the center of the import side. It converts presentation objects into a
small internal semantic model:

- positioned text blocks;
- content images and their source geometry;
- slide titles and presenter notes;
- source order and visibility; and
- review reasons for content needing human polish.

The semantic model separates extraction from layout selection. Geometry informs which simple layout
fits the source content, but arbitrary source coordinates do not become permanent Markdown styling.

### Canonical source package

The durable authoring unit is:

```text
deck.md
assets/deck/<content images>
assets/deck/import_report.json
```

Markdown contains the teaching structure. The asset directory contains reusable content images.
The import report preserves machine-readable migration evidence without adding noise to the deck.

This package is the handoff between the one-time importer and the repeatable build engine.

### Layout classifier

The importer maps semantic slide content into a deliberately small vocabulary: title, body,
single-figure, left/right image, two-pane, and gallery layouts.

The classifier chooses the layout category. It does not own the final pixel geometry. This keeps the
importer mechanical and makes post-conversion layout improvements possible without re-reading ODP.

### Central theme

`themes/genetics.css` owns the visual system shared by every deck:

- the 16:10, 1280x800 frame;
- OpenDyslexic and long-URL typography;
- spacing, hierarchy, colors, and pagination;
- reusable layout geometry; and
- automatic image fitting inside bounded layout regions.

Separating layout classification from theme geometry lets Markdown stay readable while one CSS file
enforces consistency across lectures.

### Marp render adapter

`tools/marp_export.py` is the single integration point with Marp CLI. It owns renderer discovery,
the Marp 4.5 minimum, browser selection, theme registration, format selection, and generated output
locations.

The destination-named commands are thin facades over this adapter:

- `tools/marp_to_pptx.py` selects the PPTX output path; and
- `tools/marp_to_odp.py` selects the PPTX-to-ODP classroom path.

Centralizing Marp invocation prevents each public command from developing its own renderer flags,
version rules, or failure behavior.

### LibreOffice output bridge

Marp does not generate ODP. The build engine therefore treats Marp's rendered PPTX as an interchange
artifact and gives it to LibreOffice for the final classroom ODP.

This bridge is downstream of the authoritative source. It can be replaced or improved later without
changing the Markdown authoring contract.

### Batch coordinator

`build_slides.sh` composes the single-deck exporter across a folder. It owns deck discovery and
batch failure propagation, while all rendering and conversion remain in the shared Python adapter.

This separation keeps batch behavior from becoming a second implementation of the pipeline.

## Component interfaces

Each boundary uses an artifact that can be inspected independently.

| Producer | Interface artifact | Consumer |
| --- | --- | --- |
| Legacy authoring | ODP | ODP boundary |
| LibreOffice normalization | Temporary PPTX | Semantic importer |
| Semantic importer | Internal slide records | Layout classifier |
| Layout classifier | Markdown, assets, report | Instructor and build engine |
| Central theme | Named layout contracts | Marp renderer |
| Marp render adapter | PDF or rendered PPTX | Distribution or ODP bridge |
| LibreOffice output bridge | ODP | Classroom presentation |

Temporary artifacts exist only to connect components. Durable artifacts are limited to the original
legacy evidence, the canonical Marp source package, and regenerated presentation outputs.

## Design for pipeline success

### One canonical state

Only Marp Markdown and its assets are edited after migration. A single canonical state prevents ODP,
PPTX, and Markdown from drifting into competing versions of the lecture.

### Semantic conversion before visual polish

The importer first preserves text, images, notes, order, and visibility. Consistent presentation
geometry comes from the shared layout vocabulary and theme afterward. This prevents visual fidelity
work from destroying editability.

### External tools behind adapters

LibreOffice, Marp, and Chromium are invoked at narrow module boundaries. The rest of the repository
works with paths, semantic records, and explicit result objects rather than external-tool details.

This makes tool replacement possible without rewriting the entire pipeline.

### One renderer path

PDF, PPTX, and ODP builds all pass through the same Marp adapter. ODP adds one downstream bridge but
does not introduce another Markdown renderer or layout dialect.

### Theme-owned geometry

Layout dimensions live in the theme rather than individual decks. The engine emits semantic layout
names and lets CSS fit content into the frame. This is the main mechanism for keeping hand-authored
lectures consistent after migration.

### Fail at component boundaries

Each stage validates the artifact it receives and stops when a required invariant is lost. The
pipeline does not hide failures with source-slide screenshots, alternate renderers, older Marp
versions, or guessed visibility.

### Disposable build outputs

PDF, PPTX, and ODP are products of the canonical source package. Treating them as reproducible
output allows the rendering and ODP bridge to evolve without changing course content ownership.

## Verification architecture

Successful conversion has three distinct evidence lanes:

| Lane | Establishes |
| --- | --- |
| Fast Python tests | Validation, parsing, semantic extraction, and layout-selection behavior |
| End-to-end builds | Marp, Chromium, LibreOffice, counts, notes, and format interoperability |
| Rendered review | Text and images remain inside the frame and make visual teaching sense |

No single lane establishes the whole pipeline. Unit tests cannot prove LibreOffice fidelity, and a
good screenshot cannot prove that imported text and images remain editable semantic objects.

## Extension seams

The component boundaries intentionally leave room for later improvements:

- a neutral ODP archive reader can remove the current importer/visibility ownership cycle;
- a directory-preserving output mapper can replace flat generated filenames;
- a native or reference-template ODP writer can replace the LibreOffice output bridge;
- new recurring teaching layouts can enter through the classifier/theme interface; and
- a permanent E2E runner can formalize the existing measured build evidence.

These changes should replace one component behind an existing interface rather than create a second
authoring source or parallel rendering pipeline.

## Current architectural risks

- Same-named decks in different course folders currently target the same flat output filenames.
- The visibility command and ODP importer still share a cyclic ownership edge.
- Real Marp/LibreOffice builds have measured manual evidence but no permanent E2E runner.
- The rendered PPTX-to-ODP bridge favors visual fidelity over native slide-object editability.

These are explicit component-level debts for the next approved implementation plan.

## Related contracts

- [HUMAN_GUIDANCE.md](HUMAN_GUIDANCE.md) records instructor requirements.
- [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) records settled architecture decisions.
- [INSTALL.md](INSTALL.md) defines runtime dependencies and trust boundaries.
- [USAGE.md](USAGE.md) owns instructor-facing commands and examples.
- [RELATED_PROJECTS.md](RELATED_PROJECTS.md) inventories relevant prior art.
