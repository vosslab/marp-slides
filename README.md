# marp-slides

Convert legacy biology lectures into simple, reviewable Marp Markdown and regenerate native,
editable PowerPoint and LibreOffice classroom presentations.

## One source, classroom-ready outputs

The migration deliberately closes the old editing loop:

```text
legacy ODP -> one-time import -> authoritative Marp Markdown -> generated ODP for class
```

- Simple title, bullet, and figure slides become editable Markdown.
- Structured text, images, notes, visibility, and geometry survive through a temporary PPTX.
- One command rebuilds PDF, native PPTX, and editable ODP from the same Markdown source.
- Repository-owned Python maps the supported Marp vocabulary to native slide objects without a
  browser or rendered-slide fallback.
- `marp_lib` provides the shared native-export implementation; the commands in `tools/` remain
  small executable entry points.

The two migrated genetics examples preserve their original 31-slide and 23-slide teaching
sequences without embedding a rendered source slide as converted content.

## Quick start

Install the system and Python dependencies, then build the migrated example:

```bash
brew bundle
source source_me.sh && python3 -m pip install -r pip_requirements.txt
source source_me.sh && python3 tools/marp_to_odp.py genetics/lect01b-genetic_disorders.md
```

The conversion writes the classroom file under `output/odp/` and its native PPTX source under
`output/pptx/`. Use `./build_slides.sh genetics` to rebuild PDF, PPTX, and ODP files for every
Marp deck in that folder. See [docs/INSTALL.md](docs/INSTALL.md) for supported tools and the
local-file security boundary.

## Import another lecture

Run the importer once on a legacy ODP:

```bash
source source_me.sh && python3 tools/odp_to_marp.py genetics/lecture.odp
source source_me.sh && python3 tools/marp_to_odp.py genetics/lecture.md
```

After import, edit the Markdown and its assets rather than the generated ODP. The importer refuses
to overwrite an existing Markdown deck or asset directory. See [docs/USAGE.md](docs/USAGE.md) for
the direct trusted-PPTX importer, ODP visibility report, defensive limits, auto-fitting layouts,
and click-to-reveal build slides.

## Documentation

- [docs/PIPELINE.md](docs/PIPELINE.md) - component architecture and transformation boundaries.
- [docs/INSTALL.md](docs/INSTALL.md) - Homebrew and Python setup.
- [docs/USAGE.md](docs/USAGE.md) - migration, cleanup, builds, and classroom presentation.
- [docs/HUMAN_GUIDANCE.md](docs/HUMAN_GUIDANCE.md) - durable instructor requirements.
- [docs/DESIGN_DECISIONS.md](docs/DESIGN_DECISIONS.md) - source ownership and fallback rationale.
- [docs/RELATED_PROJECTS.md](docs/RELATED_PROJECTS.md) - local prior art and ideas to adapt.
- [docs/PALETTE_CONTRAST_AUDIT.md](docs/PALETTE_CONTRAST_AUDIT.md) - measured theme contrast.

## Status and limitations

The importer is a migration aid, not a general ODP layout engine. It maps structured objects into a
small layout vocabulary and flags dense text or unsupported drawing geometry for post-conversion
polish. The native exporter creates editable text, list, shape, and component-image objects; it
rejects unsupported constructs rather than replacing a slide with a raster image. Use successive
build slides for classroom reveals.

## License

Source code: [LICENSE.MIT](LICENSE.MIT).
