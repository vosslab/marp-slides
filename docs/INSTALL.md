# Installation

This repository uses Python for one-time ODP imports and Homebrew Marp for rendering. It does not
use npm, TypeScript, or a local `node_modules` directory.

## Requirements

The supported development environment is macOS with Homebrew. The build requires:

- Python 3.12 for the importer;
- `python-pptx` for structured text, image, note, and geometry extraction;
- Marp CLI 4.5.0 or newer;
- LibreOffice Impress for ODP input and output;
- Poppler for optional rendered-output review; and
- an installed Chromium-compatible browser such as Brave, Chrome, Chromium, or Vivaldi.

## Install system tools

Install the repository-owned Homebrew dependencies:

```bash
brew bundle
```

The `marp-cli` formula brings Node as its own transitive dependency. Node is not an application
dependency of this repository.

## Install Python requirements

Activate the pinned Python 3.12 environment before running Python or pip:

```bash
source source_me.sh && python3 -m pip install -r pip_requirements.txt
```

## Verify the installation

```bash
marp --version
source source_me.sh && python3 tools/odp_to_marp.py --help
./build_slides.sh --help
source source_me.sh && python3 tools/marp_to_pptx.py --help
source source_me.sh && python3 tools/marp_to_odp.py --help
```

The Marp version must be 4.5.0 or newer. Every converter enforces that floor before rendering.

## Dependency security boundary

Homebrew installs the same upstream Marp package distributed through npm; it does not patch Marp's
transitive packages. Marp is therefore treated as a local build tool for trusted repository-owned
Markdown. The build wrapper rejects files outside the repository and enables local-file access only
so those trusted decks can load their own images.

Only import legacy ODP files that are instructor-owned and trusted. The importer validates the
archive before invoking LibreOffice to create a temporary PPTX for structured geometry extraction.
Those checks do not sandbox LibreOffice, so they do not make an untrusted ODP safe to open.

Do not run `npm audit fix --force` in this repository. There is no npm dependency tree here, and the
forced audit solver previously alternated between incompatible Marp versions without resolving the
upstream advisory.

For the migration and classroom commands, continue with [USAGE.md](USAGE.md).
