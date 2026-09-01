# Pipeline architecture

This repository is built as narrow presentation components rather than one large converter. Python
supplies the semantic import, native-output, and orchestration layers, while LibreOffice bridges
the final native PPTX to editable ODP. Marp Markdown remains the authoring syntax; no browser
renders the presentation build.

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
 native Marp-to-PPTX exporter
         |
         v
 native editable PPTX
         +-----------------------+
         |                       |
         v                       v
 LibreOffice PDF bridge   LibreOffice ODP bridge
                                 |
                                 v
                         classroom editable ODP
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

`themes/genetics.css` keeps the authoring-side visual vocabulary shared by every deck:

- the 16:10, 1280x800 frame;
- OpenDyslexic and long-URL typography;
- spacing, hierarchy, colors, pagination, and semantic layout names; and
- authoring-side image-fitting guidance.

The CSS theme is the canonical authoring vocabulary and visual reference. Until shared theme data is
explicitly implemented, `marp_lib/native_export.py` independently owns exported object geometry and
typography. This keeps Markdown readable while exports use one consistent native template set.

### Native Marp exporter

`marp_lib/native_export.py` is the shared native exporter. `marp_lib/__init__.py` establishes its
package boundary. The module owns the supported Marp source reader, native PPTX writer, template
geometry, and output selection. It reads front matter, slide boundaries, headings, lists, images,
class directives, and presenter-note comments, then writes native PowerPoint text, list, shape, and
component-image objects into a small set of templates.

The destination-named commands remain thin command owners:

- `tools/marp_to_pptx.py` selects the native PPTX output path; and
- `tools/marp_to_odp.py` selects the native-PPTX-to-ODP classroom path.

The three executable CLIs import the same shared implementation, so every public command uses one
source reader, template mapping, and native-object contract. The package is code organization, not
an additional conversion stage.

### LibreOffice output bridge

LibreOffice receives native PPTX as an interchange artifact and writes the final editable classroom
ODP. It also derives the PDF review and distribution output from that native PPTX. The bridge
preserves the native-object product contract; it is not a rendered-page conversion.

This bridge is downstream of the authoritative source. It can be replaced or improved later without
changing the Markdown authoring contract.

### Batch coordinator

`build_slides.sh` composes the single-deck exporter across a folder. It owns deck discovery and
batch failure propagation, while all rendering and conversion remain in the shared Python module.

This separation keeps batch behavior from becoming a second implementation of the pipeline.

## Component interfaces

Each boundary uses an artifact that can be inspected independently.

| Producer | Interface artifact | Consumer |
| --- | --- | --- |
| Legacy authoring | ODP | ODP boundary |
| LibreOffice normalization | Temporary PPTX | Semantic importer |
| Semantic importer | Internal slide records | Layout classifier |
| Layout classifier | Markdown, assets, report | Instructor and build engine |
| `marp_lib/native_export.py` templates | Named layout contracts | Native exporter |
| Native Marp exporter | Editable PPTX | LibreOffice PDF or ODP bridge |
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

LibreOffice is invoked at a narrow output boundary. The rest of the repository works with paths,
semantic records, and explicit result objects rather than a browser-rendering tool.

This makes tool replacement possible without rewriting the entire pipeline.

### One output path

PPTX and ODP builds pass through the same direct native exporter. ODP adds one downstream bridge
but does not introduce another Markdown dialect or a rendered-slide fallback.

### Template-owned geometry

Layout dimensions live in native templates rather than individual decks. The engine maps semantic
Marp layout names to title slide, section header, title-only, title/body, two-content, gallery, and
multi-content regions within the 16:10 frame. This is the main mechanism for keeping lectures
consistent after migration.

### Fail at component boundaries

Each stage validates the artifact it receives and stops when a required invariant is lost. The
native exporter reports an unsupported construct rather than emitting a full-slide raster image.

### Disposable build outputs

PDF, PPTX, and ODP are products of the canonical source package. Treating them as reproducible
output allows the rendering and ODP bridge to evolve without changing course content ownership.

## Verification architecture

Successful conversion has three distinct evidence lanes:

| Lane | Establishes |
| --- | --- |
| Fast Python tests | Validation, parsing, semantic extraction, and layout-selection behavior |
| Native semantic E2E gate | Native PPTX and ODP text, lists, links, notes, component images, counts, and no full-slide image |
| Object and rendered review | Text and images remain editable, inside the frame, and teach clearly |

No single lane establishes the whole pipeline. Unit tests cannot prove LibreOffice fidelity, and a
good screenshot cannot prove that imported text and images remain editable semantic objects.

## Extension seams

The component boundaries intentionally leave room for later improvements:

- a neutral ODP archive reader can remove the current importer/visibility ownership cycle;
- a directory-preserving output mapper can replace flat generated filenames;
- a native ODP writer can replace the LibreOffice output bridge;
- new recurring teaching layouts can enter through the classifier/template interface; and
- the native semantic E2E gate can gain visual-layout assertions for additional recurring templates.

These changes should replace one component behind an existing interface rather than create a second
authoring source or parallel rendering pipeline.

## Current architectural risks

- Same-named decks in different course folders currently target the same flat output filenames.
- The visibility command and ODP importer still share a cyclic ownership edge.
- The permanent native semantic E2E gate verifies object semantics; rendered review remains the
  evidence for visual clarity and frame containment.
- Native template coverage must grow only when a recurring teaching layout has an explicit contract.

These are explicit component-level debts for the next approved implementation plan.

## Related contracts

- [HUMAN_GUIDANCE.md](HUMAN_GUIDANCE.md) records instructor requirements.
- [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) records settled architecture decisions.
- [INSTALL.md](INSTALL.md) defines runtime dependencies and trust boundaries.
- [USAGE.md](USAGE.md) owns instructor-facing commands and examples.
- [RELATED_PROJECTS.md](RELATED_PROJECTS.md) inventories relevant prior art.
