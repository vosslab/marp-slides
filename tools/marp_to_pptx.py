#!/usr/bin/env python3
"""Create one native editable PPTX from repository Marp Markdown."""

# Standard Library
import argparse

# Local Modules
import marp_lib.native_export


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse the single-deck PPTX command arguments."""
	parser = argparse.ArgumentParser(
		description="Create one native editable PPTX from Marp Markdown.",
	)
	parser.add_argument("input_file", help="repository Markdown deck")
	args = parser.parse_args()
	return args


#============================================
def main() -> None:
	"""Write and print the native PPTX for one canonical deck."""
	args = parse_args()
	outputs = marp_lib.native_export.export_deck(args.input_file, "pptx")
	marp_lib.native_export.print_outputs(outputs)


if __name__ == "__main__":
	main()
