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


is_marp_deck() {
	awk '
		BEGIN { status = 1 }
		NR == 1 {
			if ($0 != "---") {
				exit
			}
			next
		}
		$0 == "---" {
			if (found) {
				status = 0
			}
			exit
		}
		$0 ~ /^[[:space:]]*marp:[[:space:]]*true[[:space:]]*$/ {
			found = 1
		}
		END { exit status }
	' "$1"
}


if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
	usage
	exit 0
fi

if [[ "$#" -ne 1 ]]; then
	usage >&2
	exit 2
fi

slide_folder="$1"
if [[ ! -d "$slide_folder" ]]; then
	printf 'error: slide folder is not a directory: %s\n' "$slide_folder" >&2
	exit 2
fi

shopt -s nullglob
markdown_files=("$slide_folder"/*.md)
shopt -u nullglob

marp_decks=()
for markdown_file in "${markdown_files[@]}"; do
	if is_marp_deck "$markdown_file"; then
		marp_decks+=("$markdown_file")
	fi
done

if [[ "${#marp_decks[@]}" -eq 0 ]]; then
	printf 'error: no Marp Markdown decks found in: %s\n' "$slide_folder" >&2
	exit 1
fi

repo_root="$(git rev-parse --show-toplevel)"
source "$repo_root/source_me.sh"

for marp_deck in "${marp_decks[@]}"; do
	printf 'Building %s\n' "$marp_deck"
	python3 "$repo_root/tools/marp_export.py" --format all "$marp_deck"
done

printf 'Built %d Marp deck(s) from %s\n' "${#marp_decks[@]}" "$slide_folder"
