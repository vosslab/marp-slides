#!/usr/bin/env python3
"""Verify native Marp export semantics through the editable ODP handoff."""

# Standard Library
import pathlib
import shutil
import subprocess
import sys
import tempfile
import uuid
import zipfile
import xml.etree.ElementTree as element_tree

# PIP3 modules
import PIL.Image
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE


NAMESPACES = {
	"draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
	"office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
	"presentation": "urn:oasis:names:tc:opendocument:xmlns:presentation:1.0",
	"svg": "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
	"text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
	"xlink": "http://www.w3.org/1999/xlink",
}


#============================================
def repo_root() -> pathlib.Path:
	"""Return the repository root containing this E2E runner."""
	return pathlib.Path(__file__).resolve().parents[2]


#============================================
def require(condition: bool, message: str) -> None:
	"""Raise a diagnostic error when one export contract is not present."""
	if not condition:
		raise RuntimeError(message)


#============================================
def write_component_image(image_path: pathlib.Path) -> None:
	"""Create a small local component image for the Marp deck."""
	image = PIL.Image.new("RGB", (120, 60), (36, 87, 143))
	image.save(image_path)


#============================================
def write_deck(deck_path: pathlib.Path) -> None:
	"""Create a two-slide canonical deck that covers editable components."""
	deck_path.write_text(
		"---\nmarp: true\ntheme: genetics\nsize: 16:10\n---\n"
		"# Native semantics\n\n"
		"- Linked [resource](https://example.edu/native-export)\n"
		"  - Nested editable detail\n"
		"1. Ordered editable step\n\n"
		"![bg right:35% contain](component.png)\n\n"
		"<!-- notes: Explain the editable component image. -->\n"
		"---\n"
		"<!-- _class: lead -->\n"
		"# Second native slide\n",
		encoding="utf-8",
	)


#============================================
def inspect_pptx(pptx_path: pathlib.Path) -> None:
	"""Confirm native PPTX objects preserve every authored component."""
	presentation = Presentation(pptx_path)
	require(len(presentation.slides) == 2, "PPTX contains the expected two native slides")
	first_slide = presentation.slides[0]
	shape_xml = "".join(shape.element.xml for shape in first_slide.shapes)
	shape_text = "\n".join(
		shape.text for shape in first_slide.shapes if shape.has_text_frame
	)
	pictures = [
		shape for shape in first_slide.shapes
		if shape.shape_type == MSO_SHAPE_TYPE.PICTURE
	]
	require("Native semantics" in shape_text, "PPTX includes editable title text")
	require("Nested editable detail" in shape_text, "PPTX includes editable nested list text")
	require("buChar" in shape_xml and "buAutoNum" in shape_xml,
		"PPTX includes native bullet and ordered-list structure")
	require("hlinkClick" in shape_xml, "PPTX includes a native hyperlink relationship")
	require(first_slide.notes_slide.notes_text_frame.text ==
		"Explain the editable component image.", "PPTX includes presenter-note text")
	require(len(pictures) == 1, "PPTX keeps the component image as one picture object")
	require(pictures[0].width < presentation.slide_width and
		pictures[0].height < presentation.slide_height,
		"PPTX component picture fits inside the slide canvas")


#============================================
def text_content(element: element_tree.Element) -> str:
	"""Return all text nodes in one ODF element."""
	return "".join(element.itertext())


#============================================
def inspect_odp(odp_path: pathlib.Path) -> None:
	"""Confirm ODP retains editable text, lists, links, notes, and image frames."""
	with zipfile.ZipFile(odp_path) as archive:
		content_root = element_tree.fromstring(archive.read("content.xml"))
	pages = content_root.findall("./office:body/office:presentation/draw:page", NAMESPACES)
	require(len(pages) == 2, "ODP contains the expected two editable slides")
	first_page = pages[0]
	page_text = text_content(first_page)
	require("Native semantics" in page_text, "ODP includes editable title text")
	require("Nested editable detail" in page_text, "ODP includes editable nested list text")
	require(first_page.findall(".//text:list", NAMESPACES),
		"ODP includes native list containers")
	require(first_page.findall(".//text:list-item", NAMESPACES),
		"ODP includes native list items")
	links = first_page.findall(".//text:a", NAMESPACES)
	require(any(link.get(f"{{{NAMESPACES['xlink']}}}href") ==
		"https://example.edu/native-export" for link in links),
		"ODP includes the authored hyperlink target")
	notes_text = text_content(first_page.find("presentation:notes", NAMESPACES))
	require("Explain the editable component image." in notes_text,
		"ODP includes presenter-note text")
	frames = first_page.findall(".//draw:frame", NAMESPACES)
	image_frames = [
		frame for frame in frames if frame.find(".//draw:image", NAMESPACES) is not None
	]
	require(len(image_frames) == 1, "ODP keeps the component image in one frame")
	for frame in image_frames:
		width = frame.get(f"{{{NAMESPACES['svg']}}}width", "")
		height = frame.get(f"{{{NAMESPACES['svg']}}}height", "")
		require(width != "33.866cm" or height != "21.166cm",
			"ODP component image frame is smaller than the complete slide canvas")


#============================================
def run() -> None:
	"""Export a temporary canonical deck and inspect its two editable formats."""
	root = repo_root()
	output_root = root / "output"
	output_root.mkdir(exist_ok=True)
	stem = f"native_odp_e2e_{uuid.uuid4().hex}"
	workspace = pathlib.Path(tempfile.mkdtemp(prefix=f"{stem}_", dir=output_root))
	deck_path = workspace / f"{stem}.md"
	pptx_path = output_root / "pptx" / f"{stem}.pptx"
	odp_path = output_root / "odp" / f"{stem}.odp"
	try:
		write_component_image(workspace / "component.png")
		write_deck(deck_path)
		require(not pptx_path.exists() and not odp_path.exists(),
			"E2E artifact names are available before export")
		command = [sys.executable, "tools/marp_export.py", str(deck_path), "--format", "all"]
		subprocess.run(command, cwd=root, check=True)
		require(pptx_path.is_file() and odp_path.is_file(),
			"Native export creates PPTX and ODP artifacts")
		inspect_pptx(pptx_path)
		inspect_odp(odp_path)
		print("PASS: native PPTX-to-ODP semantic preservation")
	finally:
		for artifact_path in (pptx_path, odp_path, output_root / "pdf" / f"{stem}.pdf"):
			artifact_path.unlink(missing_ok=True)
		shutil.rmtree(workspace, ignore_errors=True)


if __name__ == "__main__":
	run()
