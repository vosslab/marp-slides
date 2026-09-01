#!/usr/bin/env python3
"""Create one native editable PPTX from repository Marp Markdown."""

# Standard Library
import argparse

# Local Modules
import marp_lib.terminal_output


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
def main() -> int:
	"""Write and print the native PPTX for one canonical deck."""
	args = parse_args()
	status = marp_lib.terminal_output.run_build(args.input_file, "pptx", allow_folder=False)
	return status


if __name__ == "__main__":
	raise SystemExit(main())
