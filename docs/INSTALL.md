# Installation

This repository uses Python for one-time imports and native presentation output. Its production
chain creates editable PPTX, then editable ODP, then PDF from that ODP. It requires no browser,
Node, npm, Marp CLI, or Marp Core runtime.

## Requirements

The supported environment is macOS with Homebrew:

- Python 3.12 for import, parsing, and native PPTX writing;
- declared packages in `pip_requirements.txt`, including `python-pptx` for editable objects and
  Rich for concise build progress and summaries;
- LibreOffice Impress for ODP input, PPTX-to-ODP conversion, and ODP-to-PDF conversion; and
- Poppler for optional local PDF review.

## Install tools

```bash
brew bundle
source source_me.sh && python3 -m pip install -r pip_requirements.txt
```

## Verify installation

```bash
source source_me.sh && python3 tools/odp_to_marp.py --help
source source_me.sh && python3 tools/pptx_to_marp.py --help
source source_me.sh && python3 tools/odp_visibility.py --help
source source_me.sh && python3 tools/marp_to_pptx.py --help
source source_me.sh && python3 tools/marp_to_odp.py --help
./build_slides.sh --help
```

The build path is repository-owned Python and LibreOffice. `marp_lib/native_export.py` orchestrates
parsing and output; `marp_lib/layouts.py` owns native layout builders. LibreOffice receives the
completed native PPTX, writes ODP, and receives that ODP to write PDF.

Close the LibreOffice desktop application before importing ODP or building ODP/PDF output. Shared
batch conversion uses `--headless --norestore` and the established LibreOffice user profile.

## Trust boundary

Build only repository-owned Marp Markdown and local teaching assets. The exporter rejects source
features that lack a native-object mapping; it never uses a browser or a full-slide image fallback.

Import only instructor-owned, trusted legacy ODP or PPTX files. Archive validation bounds Python
processing, but ODP import invokes LibreOffice for temporary PPTX geometry extraction. Validation
does not sandbox LibreOffice or make an untrusted presentation safe to open.

Continue with [USAGE.md](USAGE.md) for migration and classroom commands.
