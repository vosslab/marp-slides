#!/usr/bin/env bash

set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
source "$repo_root/source_me.sh"
python3 "$repo_root/tools/marp_export.py" --format all "$@"
