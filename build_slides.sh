#!/usr/bin/env bash

set -euo pipefail


usage() {
	cat <<'EOF'
Usage: ./build_slides.sh FOLDER

Build every Marp Markdown deck directly inside FOLDER as PDF, PPTX, and ODP.
Markdown files without "marp: true" in their YAML front matter are skipped.

For one deck and one destination, use tools/marp_to_pptx.py or
tools/marp_to_odp.py instead.
EOF
}


if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
	usage
	exit 0
fi

if [[ "$#" -ne 1 ]]; then
	usage >&2
	exit 2
fi

repo_root="$(git rev-parse --show-toplevel)"
source "$repo_root/source_me.sh"
exec python3 "$repo_root/tools/marp_export.py" --format all "$1"
