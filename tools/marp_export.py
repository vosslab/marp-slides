#!/usr/bin/env python3
"""Export repository Marp Markdown as native editable presentations."""

# Standard Library
import argparse

# Local Modules
import marp_lib.terminal_output


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse native presentation export command arguments."""
	parser = argparse.ArgumentParser(
		description="Export repository Marp Markdown into native presentation files.",
	)
	parser.add_argument("input_path", help="repository Markdown deck or folder")
	parser.add_argument("-f", "--format", dest="output_format",
		choices=("all", "odp", "pdf", "pptx"), default="all",
		help="output format (default: all)")
	args = parser.parse_args()
	return args


#============================================
def main() -> int:
	"""Run the direct native presentation export command."""
	args = parse_args()
	status = marp_lib.terminal_output.run_build(args.input_path, args.output_format)
	return status


if __name__ == "__main__":
	raise SystemExit(main())
