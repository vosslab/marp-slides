#!/usr/bin/env python3
"""Convert trusted repository Marp Markdown into a classroom ODP."""

# Standard Library
import argparse

# Local Modules
import marp_lib.terminal_output


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
def main() -> int:
	"""Render a PPTX interchange file and convert it into an ODP."""
	args = parse_args()
	status = marp_lib.terminal_output.run_build(args.input_file, "odp", allow_folder=False)
	return status


if __name__ == "__main__":
	raise SystemExit(main())
