"""Convert trusted repository Marp Markdown into a rendered PPTX."""

# Standard Library
import argparse

# local repo modules
import marp_export


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments."""
	parser = argparse.ArgumentParser(
		description="Convert one trusted repository Marp Markdown deck into a PPTX.",
	)
	parser.add_argument("input_file", help="repository Markdown deck")
	args = parser.parse_args()
	return args


#============================================
def main() -> None:
	"""Render one Marp Markdown deck into a PPTX."""
	args = parse_args()
	outputs = marp_export.export_deck(args.input_file, "pptx")
	marp_export.print_outputs(outputs)


if __name__ == "__main__":
	main()
