#!/usr/bin/env python3
"""Convert a trusted PPTX into simple, editable Marp Markdown layouts."""

import sys
import pathlib

# local repo modules
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import marp_lib.importers.pptx_to_marp


#============================================
def main() -> None:
	"""Run the PPTX-to-Marp importer command."""
	marp_lib.importers.pptx_to_marp.main()


if __name__ == "__main__":
	main()
