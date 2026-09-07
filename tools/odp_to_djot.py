#!/usr/bin/env python3
"""Convert a trusted legacy ODP into experimental extended-Djot slide source."""

import sys
import pathlib

# local repo modules
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import marp_lib.importers.odp_to_djot


#============================================
def main() -> None:
	"""Run the ODP-to-Djot importer command."""
	marp_lib.importers.odp_to_djot.main()


if __name__ == "__main__":
	main()
