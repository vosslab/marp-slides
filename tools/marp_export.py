#!/usr/bin/env python3
"""Export repository Marp Markdown as native editable presentations."""

# Standard Library
import argparse

# Local Modules
import marp_lib.native_export


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse native presentation export command arguments."""
	parser = argparse.ArgumentParser(
		description="Export repository Marp Markdown into native presentation files.",
	)
	parser.add_argument("input_file", help="repository Markdown deck")
	parser.add_argument("-f", "--format", dest="output_format",
		choices=("all", "odp", "pdf", "pptx"), default="all",
		help="output format (default: all)")
	args = parser.parse_args()
	return args


#============================================
def main() -> None:
	"""Run the direct native presentation export command."""
	args = parse_args()
	outputs = marp_lib.native_export.export_deck(args.input_file, args.output_format)
	marp_lib.native_export.print_outputs(outputs)


if __name__ == "__main__":
	main()
