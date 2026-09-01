# marp-slides

Build editable classroom presentations from authoritative Marp Markdown.

## One source, native outputs

The repeatable production chain is:

```text
canonical Marp Markdown
  -> repository-owned Python Marp-subset parser
  -> typed native slide-object model
  -> marp_lib.layouts native layout builders
  -> python-pptx editable PPTX
  -> LibreOffice editable ODP
  -> LibreOffice PDF from that ODP
```

Every generated slide uses editable text, lists, shapes, component images, links, and presenter
notes. `marp_lib.layouts` implements all sixteen LibreOffice layout-grid patterns plus the
repository `gallery` layout. The LibreOffice grid is a catalog and visual target; Python builds the
objects.

Marp supplies the mature authoring-language specification only. The production graph contains no
Marp CLI, Marp Core, Node, browser, rendered-slide stage, or full-slide raster fallback.

## Quick start

Install the system and Python dependencies, then build one editable deck:

```bash
brew bundle
source source_me.sh && python3 -m pip install -r pip_requirements.txt
source source_me.sh && python3 tools/marp_to_odp.py genetics/lect01b-genetic_disorders.md
```

This writes native PPTX and editable ODP artifacts. Build all three artifacts, including the
ODP-derived PDF, for every deck directly in a folder:

```bash
./build_slides.sh genetics
```

See [docs/INSTALL.md](docs/INSTALL.md) for setup,
[docs/MARP_SYNTAX_GUIDE.md](docs/MARP_SYNTAX_GUIDE.md) for source syntax, and
[docs/USAGE.md](docs/USAGE.md) for imports and commands.

## One-time migration

Import an instructor-owned legacy ODP once, then edit the resulting Markdown and assets:

```bash
source source_me.sh && python3 tools/odp_to_marp.py genetics/lecture.odp
source source_me.sh && python3 tools/marp_to_odp.py genetics/lecture.md
```

The importer preserves structured content for human cleanup. It does not make legacy ODP a second
authoring source.

## Documentation

- [docs/PIPELINE.md](docs/PIPELINE.md) - component architecture and boundaries.
- [docs/INSTALL.md](docs/INSTALL.md) - macOS dependencies and trust boundary.
- [docs/MARP_SYNTAX_GUIDE.md](docs/MARP_SYNTAX_GUIDE.md) - supported Marp authoring syntax.
- [docs/USAGE.md](docs/USAGE.md) - authoring, layouts, migration, and builds.
- [docs/HUMAN_GUIDANCE.md](docs/HUMAN_GUIDANCE.md) - durable instructor requirements.
- [docs/DESIGN_DECISIONS.md](docs/DESIGN_DECISIONS.md) - settled architecture decisions.
- [docs/RELATED_PROJECTS.md](docs/RELATED_PROJECTS.md) - local reference projects and limits.

## License

Source code: [LICENSE.MIT](LICENSE.MIT).
