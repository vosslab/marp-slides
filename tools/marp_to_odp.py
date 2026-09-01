#!/usr/bin/env python3
"""Convert trusted repository Marp Markdown into a classroom ODP."""

# Standard Library
import argparse

# Local Modules
import marp_lib.native_export


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments."""
	parser = argparse.ArgumentParser(
		description="Convert one trusted repository Marp Markdown deck into an ODP.",
	)
	parser.add_argument("input_file", help="repository Markdown deck")
	args = parser.parse_args()
	return args


#============================================
def main() -> None:
	"""Render a PPTX interchange file and convert it into an ODP."""
	args = parse_args()
	outputs = marp_lib.native_export.export_deck(args.input_file, "odp")
	marp_lib.native_export.print_outputs(outputs)


if __name__ == "__main__":
	main()
