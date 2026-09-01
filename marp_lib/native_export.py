"""Parse canonical Marp Markdown and export editable native presentations."""

# Standard Library
import os
import pathlib
import shutil
import subprocess
import tempfile

# PIP3 modules
from pptx import Presentation
from pptx.enum.text import PP_ALIGN

# Local Modules
from marp_lib import layouts
from marp_lib import marp_parser
import marp_lib.native_model


#============================================
def find_repo_root() -> pathlib.Path:
	"""Return the current Git repository root."""
	result = subprocess.run(["git", "rev-parse", "--show-toplevel"], check=True,
		capture_output=True, text=True)
	return pathlib.Path(result.stdout.strip()).resolve()


#============================================
def validate_input(input_value: str, repo_root: pathlib.Path) -> pathlib.Path:
	"""Resolve canonical Markdown and reject failed full-slide conversions."""
	input_path = pathlib.Path(input_value).expanduser().resolve()
	if not input_path.is_file():
		raise ValueError(f"input is not a file: {input_value}")
	if not input_path.is_relative_to(repo_root):
		raise ValueError("input must be inside this repository")
	if input_path.suffix != ".md":
		raise ValueError("input must use the .md extension")
	return input_path


#============================================
def parse_deck(input_path: pathlib.Path) -> marp_lib.native_model.Deck:
	"""Parse canonical Marp Markdown through the one typed semantic parser."""
	return marp_parser.parse_deck(input_path)


#============================================
def render_native_pptx(deck: marp_lib.native_model.Deck, output_path: pathlib.Path) -> pathlib.Path:
	"""Write every parsed slide as separate editable native PPTX objects."""
	presentation = Presentation()
	presentation.slide_width = layouts.px(layouts.SLIDE_WIDTH)
	presentation.slide_height = layouts.px(layouts.SLIDE_HEIGHT)
	presentation.core_properties.title = deck.title
	blank_layout = presentation.slide_layouts[6]
	for number, source in enumerate(deck.slides, start=1):
		slide = presentation.slides.add_slide(blank_layout)
		layouts.render_layout(slide, source, deck)
		if source.paginate:
			text_frame = layouts.add_textbox(slide, 1190, 762, 62, 22)
			text_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT
			layouts.write_run(text_frame.paragraphs[0].add_run(), str(number), 18, layouts.MUTED)
		if source.notes:
			slide.notes_slide.notes_text_frame.text = "\n\n".join(source.notes)
	output_path.parent.mkdir(parents=True, exist_ok=True)
	presentation.save(output_path)
	return output_path


#============================================
def require_executable(command: str, install_message: str) -> pathlib.Path:
	"""Resolve a required executable from PATH."""
	command_value = shutil.which(command)
	if command_value is None:
		raise RuntimeError(install_message)
	return pathlib.Path(command_value).resolve()


#============================================
def convert_presentation(input_path: pathlib.Path, output_path: pathlib.Path,
		output_format: str, repo_root: pathlib.Path) -> None:
	"""Use LibreOffice to convert one editable presentation artifact."""
	soffice_path = require_executable("soffice", "LibreOffice is not installed; run brew bundle")
	output_root = repo_root / "output"
	output_root.mkdir(parents=True, exist_ok=True)
	output_path.parent.mkdir(parents=True, exist_ok=True)
	with tempfile.TemporaryDirectory(prefix=".libreoffice.", dir=output_root) as temporary_value:
		temporary_root = pathlib.Path(temporary_value)
		profile_path = temporary_root / "profile"
		conversion_path = temporary_root / "converted"
		conversion_path.mkdir()
		command = [str(soffice_path), f"-env:UserInstallation={profile_path.as_uri()}",
			"--headless", "--convert-to", output_format, "--outdir", str(conversion_path),
			str(input_path)]
		subprocess.run(command, check=True)
		converted_path = conversion_path / f"{input_path.stem}.{output_format}"
		if not converted_path.is_file():
			raise RuntimeError(f"LibreOffice did not create the expected {output_format.upper()} output")
		os.replace(converted_path, output_path)


#============================================
def export_deck(input_value: str, output_format: str) -> dict[str, pathlib.Path]:
	"""Export PPTX, then editable ODP, then PDF from that ODP when requested."""
	if output_format not in ("all", "odp", "pdf", "pptx"):
		raise ValueError(f"unsupported output format: {output_format}")
	repo_root = find_repo_root()
	input_path = validate_input(input_value, repo_root)
	deck_name = input_path.stem
	outputs = {"pptx": repo_root / f"output/pptx/{deck_name}.pptx",
		"odp": repo_root / f"output/odp/{deck_name}.odp",
		"pdf": repo_root / f"output/pdf/{deck_name}.pdf"}
	generated = {"pptx": render_native_pptx(parse_deck(input_path), outputs["pptx"])}
	if output_format in ("all", "odp", "pdf"):
		convert_presentation(outputs["pptx"], outputs["odp"], "odp", repo_root)
		generated["odp"] = outputs["odp"]
	if output_format in ("all", "pdf"):
		convert_presentation(outputs["odp"], outputs["pdf"], "pdf", repo_root)
		generated["pdf"] = outputs["pdf"]
	return generated


#============================================
def print_outputs(outputs: dict[str, pathlib.Path]) -> None:
	"""Print generated artifact paths in their required dependency order."""
	for output_format in ("pptx", "odp", "pdf"):
		if output_format in outputs:
			print(f"{output_format.upper()}: {outputs[output_format]}")
