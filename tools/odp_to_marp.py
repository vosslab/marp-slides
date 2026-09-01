#!/usr/bin/env python3
"""Convert a trusted legacy ODP into editable Marp through a temporary PPTX."""

# Standard Library
import stat
import sys
import shutil
import zipfile
import pathlib
import argparse
import tempfile
import subprocess
import dataclasses
import xml.etree.ElementTree

# PIP3 modules
import defusedxml.ElementTree

# local repo modules
if __name__ == "__main__":
	sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from tools import odp_visibility
from tools import pptx_to_marp


NS = {
	"draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
}
ODP_MIMETYPE = "application/vnd.oasis.opendocument.presentation"
MAX_INPUT_BYTES = 256 * 1024 * 1024
MAX_MEMBER_BYTES = 128 * 1024 * 1024
MAX_UNPACKED_BYTES = 512 * 1024 * 1024
MAX_ARCHIVE_MEMBERS = 2000
SOFFICE_CANDIDATES = (
	pathlib.Path("/Applications/LibreOffice.app/Contents/MacOS/soffice"),
	pathlib.Path("/Applications/LibreOffice-Still.app/Contents/MacOS/soffice"),
)


@dataclasses.dataclass(frozen=True)
class SourceSlide:
	"""Source slide identity and visibility retained from ODP XML."""

	source_index: int
	name: str
	hidden: bool


#============================================
def qname(prefix: str, local_name: str) -> str:
	"""Build one namespace-qualified XML name."""
	return f"{{{NS[prefix]}}}{local_name}"


#============================================
def validate_member_name(member_name: str) -> None:
	"""Reject absolute and traversal paths in an ODP archive."""
	# ASVS 5.3.3: archive member paths never control filesystem destinations.
	normalized = member_name.replace("\\", "/")
	parts = pathlib.PurePosixPath(normalized).parts
	if normalized.startswith("/") or ".." in parts:
		raise ValueError(f"unsafe archive member path: {member_name}")


#============================================
def validate_odp(input_path: pathlib.Path) -> list[zipfile.ZipInfo]:
	"""Validate a bounded OpenDocument presentation before conversion."""
	# ASVS 2.2.1, 5.2.1, 5.2.2, and 5.2.3: validate type and archive limits.
	if not input_path.is_file() or input_path.suffix.lower() != ".odp":
		raise ValueError("input must be an existing .odp file")
	if input_path.stat().st_size > MAX_INPUT_BYTES:
		raise ValueError("ODP exceeds the compressed input limit")
	with zipfile.ZipFile(input_path) as archive:
		members = archive.infolist()
		if len(members) > MAX_ARCHIVE_MEMBERS:
			raise ValueError("ODP contains too many archive members")
		total_size = 0
		member_names: set[str] = set()
		for member in members:
			validate_member_name(member.filename)
			mode = member.external_attr >> 16
			if mode and stat.S_ISLNK(mode):
				raise ValueError(f"ODP archive contains a symlink: {member.filename}")
			if member.file_size > MAX_MEMBER_BYTES:
				raise ValueError(f"ODP member exceeds size limit: {member.filename}")
			total_size += member.file_size
			if total_size > MAX_UNPACKED_BYTES:
				raise ValueError("ODP exceeds the expanded archive limit")
			member_names.add(member.filename)
		if not {"mimetype", "content.xml"}.issubset(member_names):
			raise ValueError("ODP is missing required members")
		if archive.read("mimetype").decode("ascii", errors="strict") != ODP_MIMETYPE:
			raise ValueError("ODP mimetype member is invalid")
		# ASVS 1.5.1: defusedxml disables DTD and external entity processing.
		defusedxml.ElementTree.fromstring(archive.read("content.xml"))
		if "styles.xml" in member_names:
			defusedxml.ElementTree.fromstring(archive.read("styles.xml"))
	return members


#============================================
def read_content_root(input_path: pathlib.Path) -> xml.etree.ElementTree.Element:
	"""Parse the validated ODP content XML with restrictive XML handling."""
	validate_odp(input_path)
	with zipfile.ZipFile(input_path) as archive:
		content_bytes = archive.read("content.xml")
	root = defusedxml.ElementTree.fromstring(content_bytes)
	return root


#============================================
def read_slides(input_path: pathlib.Path) -> list[SourceSlide]:
	"""Read source slide order and visibility from ODP XML."""
	root = read_content_root(input_path)
	definitions = odp_visibility.read_style_definitions(input_path, root)
	pages = root.findall(".//draw:page", NS)
	slides: list[SourceSlide] = []
	for source_index, page in enumerate(pages, start=1):
		slide_name = page.get(qname("draw", "name"), f"slide_{source_index:03d}")
		slides.append(
			SourceSlide(
				source_index=source_index,
				name=slide_name,
				hidden=odp_visibility.page_is_hidden(page, definitions),
			)
		)
	return slides


#============================================
def require_soffice() -> pathlib.Path:
	"""Resolve the LibreOffice command used for trusted local conversion."""
	command_value = shutil.which("soffice")
	if command_value is not None:
		return pathlib.Path(command_value).resolve()
	for candidate in SOFFICE_CANDIDATES:
		if candidate.is_file():
			return candidate
	raise RuntimeError("LibreOffice is not installed; run brew bundle")


#============================================
def convert_odp_to_pptx(input_path: pathlib.Path, temporary_root: pathlib.Path) -> pathlib.Path:
	"""Normalize ODP geometry into a temporary PPTX with LibreOffice."""
	soffice_path = require_soffice()
	converted_dir = temporary_root / "converted"
	profile_dir = temporary_root / "libreoffice_profile"
	converted_dir.mkdir()
	profile_dir.mkdir()
	profile_argument = f"-env:UserInstallation={profile_dir.resolve().as_uri()}"
	command = [
		str(soffice_path),
		profile_argument,
		"--headless",
		"--convert-to",
		"pptx",
		"--outdir",
		str(converted_dir),
		str(input_path),
	]
	# ASVS 1.2.5: user paths remain separate subprocess arguments; no shell is used.
	result = subprocess.run(
		command,
		capture_output=True,
		check=False,
		text=True,
		timeout=180,
	)
	if result.returncode != 0:
		raise RuntimeError("LibreOffice could not normalize the trusted ODP")
	pptx_path = converted_dir / f"{input_path.stem}.pptx"
	if not pptx_path.is_file():
		raise RuntimeError("LibreOffice did not create the expected temporary PPTX")
	return pptx_path


#============================================
def convert_odp(
	input_path: pathlib.Path,
	output_path: pathlib.Path,
) -> pptx_to_marp.ConversionSummary:
	"""Convert one trusted ODP into a new editable Marp deck."""
	input_path = input_path.resolve()
	output_path = output_path.resolve()
	pptx_to_marp.validate_output_path(output_path)
	source_slides = read_slides(input_path)
	if not source_slides:
		raise ValueError("ODP contains no presentation slides")
	hidden_indexes = {slide.source_index for slide in source_slides if slide.hidden}
	if len(hidden_indexes) == len(source_slides):
		raise ValueError("ODP contains no visible presentation slides")
	output_path.parent.mkdir(parents=True, exist_ok=True)
	with tempfile.TemporaryDirectory(prefix=".odp_to_marp_", dir=output_path.parent) as name:
		temporary_root = pathlib.Path(name)
		pptx_path = convert_odp_to_pptx(input_path, temporary_root)
		summary = pptx_to_marp.convert_pptx(
			pptx_path,
			output_path,
			expected_slide_count=len(source_slides),
			expected_hidden=hidden_indexes,
			source_name=input_path.name,
		)
	return summary


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse the one-time ODP importer arguments."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("input_file", type=pathlib.Path, help="trusted legacy ODP")
	parser.add_argument("--output", type=pathlib.Path, help="new Marp Markdown path")
	return parser.parse_args()


#============================================
def main() -> None:
	"""Run one ODP-to-Marp import."""
	args = parse_args()
	output_path = args.output or args.input_file.with_suffix(".md")
	summary = convert_odp(args.input_file, output_path)
	print(
		f"Converted {summary.visible_slides} visible slides: "
		f"{summary.editable_slides} editable, {summary.review_slides} layout review, "
		f"{summary.hidden_slides} hidden, {summary.extracted_images} content images"
	)
	print(f"Markdown: {summary.output_path}")
	print(f"Import report: {summary.report_path}")


if __name__ == "__main__":
	main()
