#!/usr/bin/env python3
"""Resolve ODP drawing-page visibility across page and style cascades."""

import sys
import pathlib

# local repo modules
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import marp_lib.importers.odp_visibility


#============================================
def main() -> None:
	"""Run the ODP visibility command."""
	marp_lib.importers.odp_visibility.main()


if __name__ == "__main__":
	main()
