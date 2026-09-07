"""Convert a trusted legacy ODP into experimental extended-Djot slide source."""

# Standard Library
import pathlib
import argparse
import tempfile

# local repo modules
import marp_lib.importers.odp_to_marp as odp_to_marp
import marp_lib.importers.pptx_to_djot as pptx_to_djot


#============================================
def convert_odp(
	input_path: pathlib.Path,
	output_path: pathlib.Path,
) -> pptx_to_djot.ConversionSummary:
	"""Convert trusted ODP through a temporary PPTX while retaining visibility."""
	input_path = input_path.resolve()
	output_path = output_path.resolve()
	pptx_to_djot.validate_output_path(output_path)
	source_slides = odp_to_marp.read_slides(input_path)
	if not source_slides:
		raise ValueError("ODP contains no presentation slides")
	hidden_indexes = {slide.source_index for slide in source_slides if slide.hidden}
	if len(hidden_indexes) == len(source_slides):
		raise ValueError("ODP contains no visible presentation slides")
	output_path.parent.mkdir(parents=True, exist_ok=True)
	with tempfile.TemporaryDirectory(prefix=".odp_to_djot_", dir=output_path.parent) as name:
		temporary_root = pathlib.Path(name)
		pptx_path = odp_to_marp.convert_odp_to_pptx(input_path, temporary_root)
		summary = pptx_to_djot.convert_pptx(
			pptx_path,
			output_path,
			expected_slide_count=len(source_slides),
			expected_hidden=hidden_indexes,
			source_name=input_path.name,
			render_source_path=input_path,
		)
	return summary


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse standalone ODP-to-Djot importer arguments."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("input_file", type=pathlib.Path, help="trusted legacy ODP")
	parser.add_argument("--output", type=pathlib.Path, help="new extended-Djot source path")
	return parser.parse_args()


#============================================
def main() -> None:
	"""Run one ODP-to-Djot conversion."""
	args = parse_args()
	output_path = args.output or args.input_file.with_suffix(".djot")
	summary = convert_odp(args.input_file, output_path)
	print(
		f"Converted {summary.visible_slides} visible slides: "
		f"{summary.editable_slides} editable, {summary.review_slides} layout review, "
		f"{summary.hidden_slides} hidden, {summary.extracted_images} content images"
	)
	print(f"Djot: {summary.output_path}")
	print(f"Import report: {summary.report_path}")


if __name__ == "__main__":
	main()
