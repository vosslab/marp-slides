# Installation

This repository uses Python for one-time ODP and PPTX imports and for native presentation output.
It does not require a browser, npm, TypeScript, or a local `node_modules` directory.

## Requirements

The supported development environment is macOS with Homebrew. The build requires:

- Python 3.12 for import and native presentation output;
- `python-pptx` for structured text, image, note, and geometry extraction plus native PPTX writing;
- LibreOffice Impress for ODP input and output;
- Poppler for optional PDF review.

## Install system tools

Install the repository-owned Homebrew dependencies:

```bash
brew bundle
```

Homebrew installs LibreOffice and optional review utilities. The presentation build itself uses the
repository-owned Python exporter and LibreOffice; it does not launch a browser.

## Install Python requirements

Activate the pinned Python 3.12 environment before running Python or pip:

```bash
source source_me.sh && python3 -m pip install -r pip_requirements.txt
```

## Verify the installation

```bash
source source_me.sh && python3 tools/odp_to_marp.py --help
source source_me.sh && python3 tools/pptx_to_marp.py --help
source source_me.sh && python3 tools/odp_visibility.py --help
./build_slides.sh --help
source source_me.sh && python3 tools/marp_export.py --help
source source_me.sh && python3 tools/marp_to_pptx.py --help
source source_me.sh && python3 tools/marp_to_odp.py --help
```

The native export commands require Python 3.12, `python-pptx`, and LibreOffice. They create native
PPTX slide objects first, then LibreOffice writes the editable ODP. `marp_lib/native_export.py`
provides their shared implementation, and the executable commands in `tools/` import it.

## Dependency security boundary

The exporter accepts only repository-owned Marp Markdown and its local teaching assets. It rejects
source constructs outside the supported layout vocabulary instead of invoking a general browser
renderer or falling back to a full-slide image.

Only import legacy ODP or PPTX files that are instructor-owned and trusted. The importers validate
archive structure and processing limits. ODP import then invokes LibreOffice to create a temporary
PPTX for structured geometry extraction. Those checks do not sandbox LibreOffice or make an
untrusted presentation safe to open.

Do not run `npm audit fix --force` in this repository. There is no npm dependency tree here, and the
forced audit solver previously alternated between incompatible Marp versions without resolving the
upstream advisory.

For the migration and classroom commands, continue with [USAGE.md](USAGE.md).
