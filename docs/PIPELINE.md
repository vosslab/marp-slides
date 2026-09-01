# Presentation pipeline

This repository wraps Marp CLI with Python import, validation, batch-build, and LibreOffice
conversion tools. Marp Markdown and its local assets are the authoritative teaching source.
Generated PDF, PPTX, and ODP files are disposable classroom outputs.

## End-to-end map

```text
One-time legacy import

trusted ODP
    |
    | bounded validation and visibility inspection (Python)
    v
temporary PPTX (LibreOffice)
    |
    | structured text, image, note, and geometry extraction (python-pptx)
    v
Marp Markdown + local assets + import report
    |
    | instructor cleanup using simple shared layouts
    v
authoritative Marp Markdown


Classroom build

authoritative Marp Markdown + local assets + genetics.css
    |
    | Marp CLI 4.5+ rendered through Chromium
    +--------------------------+
    |                          |
    v                          v
PDF                         rendered PPTX
                                |
                                | LibreOffice conversion
                                v
                           classroom ODP
```

A trusted PPTX may enter the import lane directly at the `python-pptx` extraction stage. The normal
legacy path begins with ODP because the original ODP remains the migration evidence.

## Source-of-truth boundary

The lifecycle is deliberately one-way:

```text
legacy ODP -> one-time import -> Marp Markdown becomes authoritative -> generated ODP for class
```

After import and cleanup:

- edit the Markdown and its local assets;
- rebuild PDF, PPTX, and ODP outputs as needed;
- do not import edits from a generated ODP back into Markdown; and
- do not use a rendered source slide as Marp content.

The generated ODP is for LibreOffice Impress presentation. It is not the editable content source.

## Marp CLI boundary

Marp CLI is the central Markdown renderer; the Python tools do not replace it. The build invokes
the Homebrew `marp` executable to:

- parse the authoritative Marp Markdown;
- apply `themes/genetics.css`;
- render through an installed Chromium-compatible browser;
- produce PDF with presenter notes; and
- produce the rendered PPTX used for PowerPoint and ODP conversion.

The repository-owned tools supply capabilities outside Marp's scope:

- importing ODP and PPTX presentations;
- extracting structured text, images, notes, visibility, and geometry;
- selecting a small, consistent Marp layout vocabulary;
- validating trusted local file boundaries and processing limits;
- batch-building every deck in a selected folder; and
- converting Marp's PPTX output into classroom ODP.

Removing Marp CLI would require a replacement Markdown parser, CSS layout engine, browser renderer,
PDF generator, and PPTX generator. This repository has not built those components.

## Command ownership

| Command | Scope | Input | Output |
| --- | --- | --- | --- |
| `tools/odp_visibility.py` | One file, read-only | Trusted ODP | Slide visibility report |
| `tools/odp_to_marp.py` | One deck | Trusted ODP | Markdown, assets, import report |
| `tools/pptx_to_marp.py` | One deck | Trusted PPTX | Markdown, assets, import report |
| `tools/marp_to_pptx.py` | One deck | Marp Markdown | Rendered PPTX |
| `tools/marp_to_odp.py` | One deck | Marp Markdown | Rendered PPTX and classroom ODP |
| `build_slides.sh` | One folder | Every direct Marp Markdown child | PDF, PPTX, and ODP per deck |

All export commands share `tools/marp_export.py`. It owns Marp discovery, the 4.5.0 minimum,
browser discovery, central-theme registration, input validation, output paths, and LibreOffice
conversion.

## Normal workflows

Import one trusted ODP once:

```bash
source source_me.sh && python3 tools/odp_to_marp.py genetics/lecture.odp
```

After reviewing and cleaning the resulting Markdown, build the classroom ODP for one deck:

```bash
source source_me.sh && python3 tools/marp_to_odp.py genetics/lecture.md
```

Build every Marp deck directly inside one course folder:

```bash
./build_slides.sh genetics
```

The folder scan is non-recursive. It skips Markdown files without `marp: true` in their YAML front
matter and stops when a deck fails to build.

## Artifact ownership

One-time import creates:

```text
genetics/lecture.md
genetics/assets/lecture/<content images>
genetics/assets/lecture/import_report.json
```

Classroom builds currently create flat, format-specific output paths:

```text
output/pdf/lecture.pdf
output/pptx/lecture.pptx
output/odp/lecture.odp
```

These build products can be regenerated from Markdown. Temporary LibreOffice profiles, normalized
PPTX files used during ODP import, and staging directories are removed after successful conversion.

### Current output-name limitation

Output paths currently use only the Markdown filename stem. Two decks such as
`genetics/lecture.md` and `biochemistry/lecture.md` therefore target the same generated filenames.
Use unique deck basenames across course folders until a directory-preserving output contract is
approved and implemented.

## Layout contract

Every deck uses the 16:10, 1280x800 frame. Authored text and teaching images must remain within
that frame. The preferred vocabulary is deliberately small:

- title slide;
- section header;
- title only;
- title and body;
- title and two columns;
- title with one auto-fitting figure; and
- title with an auto-fitting image gallery.

OpenDyslexic is the exclusive authored-text font. Slides that visibly print long URLs may opt into
PT Sans Narrow. Image sizing belongs to the shared theme and uses `contain`; individual slides do
not hard-code pixel dimensions.

## Trust and validation

Only process instructor-owned, trusted ODP, PPTX, Markdown, and image files.

- ODP and PPTX importers bound compressed size, expanded size, member size, and archive count.
- The PPTX importer validates supported image types and decoded pixel dimensions.
- ODP XML uses restrictive parsing, and archive member paths cannot control extraction paths.
- Marp local-file access is restricted to validated repository-owned Markdown and teaching assets.
- Subprocess commands receive file paths as distinct arguments rather than interpolated shell text.

Validation reduces malformed-input and resource-exhaustion risk. It does not sandbox LibreOffice,
Chromium, Marp, or `python-pptx`, and it does not make an unknown presentation safe to open.

See [INSTALL.md](INSTALL.md) for exact dependencies and [USAGE.md](USAGE.md) for defensive limits.

## Known presentation limits

- The normal Marp PPTX is visually faithful but flattened rather than natively editable.
- Marp's editable-PPTX experiment lost presenter notes and broke tested two-pane layouts.
- The PPTX-to-ODP lane does not create native click animations.
- Classroom reveals use successive slides that progressively add bullets, images, or answers.
- The importer maps source geometry into simple layouts; it does not reproduce arbitrary ODP
  coordinates.
- OCR is not part of normal import because the legacy slides contain structured authored objects.

These are deliberate boundaries of the current tested baseline, not claims that future output
experiments are prohibited.

## Related contracts

- [HUMAN_GUIDANCE.md](HUMAN_GUIDANCE.md) records instructor requirements.
- [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) records settled implementation decisions.
- [INSTALL.md](INSTALL.md) defines dependencies and security boundaries.
- [USAGE.md](USAGE.md) provides detailed authoring and conversion examples.
- [RELATED_PROJECTS.md](RELATED_PROJECTS.md) inventories prior art that may inform future work.
