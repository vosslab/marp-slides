"""Convert an OpenDocument presentation into a simple Marp Markdown draft."""

# Standard Library
import os
import re
import json
import stat
import shutil
import zipfile
import pathlib
import argparse
import tempfile
import subprocess
import dataclasses
import sys
import xml.etree.ElementTree

# PIP3 modules
import defusedxml.ElementTree

# local repo modules
if __name__ == "__main__":
	sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import tools.odp_visibility as odp_visibility


NS = {
	"draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
	"office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
	"presentation": "urn:oasis:names:tc:opendocument:xmlns:presentation:1.0",
	"text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
	"xlink": "http://www.w3.org/1999/xlink",
}

ODP_MIMETYPE = "application/vnd.oasis.opendocument.presentation"
SUPPORTED_IMAGE_SUFFIXES = {".jpeg", ".jpg", ".png"}
IGNORED_PRESENTATION_CLASSES = {
	"date-time",
	"footer",
	"header",
	"notes",
	"page-number",
}
COMPLEX_DRAWING_TAGS = {
	"caption",
	"connector",
	"control",
	"custom-shape",
	"g",
	"line",
	"measure",
	"object",
	"object-ole",
	"plugin",
	"table",
}
MAX_INPUT_BYTES = 256 * 1024 * 1024
MAX_MEMBER_BYTES = 128 * 1024 * 1024
MAX_UNPACKED_BYTES = 512 * 1024 * 1024
MAX_ARCHIVE_MEMBERS = 2000
MAX_EDITABLE_LINES = 10
MAX_EDITABLE_CHARACTERS = 1200


@dataclasses.dataclass
class TextLine:
	"""One visible ODP text line and its source list depth."""

	text: str
	depth: int


@dataclasses.dataclass
class Slide:
	"""Content extracted from one ODP slide."""

	source_index: int
	name: str
	hidden: bool
	title_lines: list[TextLine]
	subtitle_lines: list[TextLine]
	outline_lines: list[TextLine]
	positioned_lines: list[TextLine]
	note_lines: list[TextLine]
	image_hrefs: list[str]
	unsupported_image_hrefs: list[str]
	drawing_tags: set[str]
	fallback_reasons: list[str]


@dataclasses.dataclass
class ConversionSummary:
	"""User-facing conversion counts."""

	visible_slides: int
	editable_slides: int
	fallback_slides: int
	hidden_slides: int
	extracted_images: int
	output_path: pathlib.Path


#============================================
def qname(prefix: str, local_name: str) -> str:
	"""Build a namespace-qualified XML name."""
	qualified_name = f"{{{NS[prefix]}}}{local_name}"
	return qualified_name


#============================================
def local_name(element: xml.etree.ElementTree.Element) -> str:
	"""Return the local name from an XML element tag."""
	tag_name = element.tag.split("}", 1)[-1]
	return tag_name


#============================================
def normalize_text(value: str) -> str:
	"""Collapse source whitespace without changing the words."""
	normalized_value = " ".join(value.split())
	return normalized_value


#============================================
def ascii_entity_text(value: str) -> str:
	"""Escape source text for a Markdown text context."""
	# ASVS 1.1.2 and 1.2.1: encode only at the final Markdown output boundary.
	escaped_value = value.replace("&", "&amp;")
	escaped_value = escaped_value.replace("<", "&lt;").replace(">", "&gt;")
	for markdown_character in ("\\", "`", "*", "[", "]"):
		escaped_value = escaped_value.replace(markdown_character, f"\\{markdown_character}")
	encoded_characters: list[str] = []
	for character in escaped_value:
		if ord(character) > 255:
			encoded_characters.append(f"&#{ord(character)};")
		else:
			encoded_characters.append(character)
	encoded_value = "".join(encoded_characters)
	return encoded_value


#============================================
def comment_text(value: str) -> str:
	"""Escape source text for a Marp presenter-note comment."""
	encoded_value = ascii_entity_text(value)
	safe_value = encoded_value.replace("--", "- -")
	return safe_value


#============================================
def inline_text_raw(element: xml.etree.ElementTree.Element) -> str:
	"""Extract text recursively while preserving span-boundary whitespace."""
	parts: list[str] = []
	if element.text:
		parts.append(element.text)
	for child in element:
		if child.tag == qname("text", "s"):
			count_text = child.get(qname("text", "c"), "1")
			space_count = int(count_text)
			parts.append(" " * space_count)
		elif child.tag == qname("text", "tab"):
			parts.append(" ")
		elif child.tag == qname("text", "line-break"):
			parts.append(" / ")
		else:
			parts.append(inline_text_raw(child))
		if child.tail:
			parts.append(child.tail)
	raw_text = "".join(parts)
	return raw_text


#============================================
def inline_text(element: xml.etree.ElementTree.Element) -> str:
	"""Extract visible text including ODF space and break elements."""
	visible_text = normalize_text(inline_text_raw(element))
	return visible_text


#============================================
def collect_list_lines(
	list_element: xml.etree.ElementTree.Element,
	depth: int,
	lines: list[TextLine],
) -> None:
	"""Collect list-item paragraphs recursively."""
	for list_item in list_element.findall("./text:list-item", NS):
		for child in list_item:
			if child.tag in (qname("text", "h"), qname("text", "p")):
				value = inline_text(child)
				if value:
					lines.append(TextLine(value, depth))
			elif child.tag == qname("text", "list"):
				collect_list_lines(child, depth + 1, lines)


#============================================
def collect_text_lines(element: xml.etree.ElementTree.Element) -> list[TextLine]:
	"""Collect paragraphs and nested list items from an ODF text container."""
	lines: list[TextLine] = []
	for child in element:
		if child.tag in (qname("text", "h"), qname("text", "p")):
			value = inline_text(child)
			if value:
				lines.append(TextLine(value, 0))
		elif child.tag == qname("text", "list"):
			collect_list_lines(child, 0, lines)
		else:
			lines.extend(collect_text_lines(child))
	return lines


#============================================
def validate_member_name(member_name: str) -> None:
	"""Reject unsafe archive member paths."""
	member_path = pathlib.PurePosixPath(member_name)
	if member_path.is_absolute() or ".." in member_path.parts:
		raise ValueError("ODP contains an unsafe archive member path")


#============================================
def validate_odp(input_path: pathlib.Path) -> list[zipfile.ZipInfo]:
	"""Validate an ODP file before XML or image processing.

	Args:
		input_path: Candidate ODP path.

	Returns:
		Validated archive member inventory.
	"""
	# ASVS 2.2.1 and 5.2.1: validate extension, type, and bounded size at the boundary.
	if input_path.suffix.lower() != ".odp":
		raise ValueError("input must use the .odp extension")
	if not input_path.is_file():
		raise ValueError("input ODP does not exist or is not a regular file")
	if input_path.stat().st_size > MAX_INPUT_BYTES:
		raise ValueError("input ODP exceeds the 256 MiB compressed size limit")
	if not zipfile.is_zipfile(input_path):
		raise ValueError("input does not contain a valid ZIP-based ODP package")

	with zipfile.ZipFile(input_path) as archive:
		members = archive.infolist()
		if len(members) > MAX_ARCHIVE_MEMBERS:
			raise ValueError("ODP contains too many archive members")
		member_names: set[str] = set()
		unpacked_bytes = 0
		for member in members:
			validate_member_name(member.filename)
			if member.filename in member_names:
				raise ValueError("ODP contains duplicate archive member names")
			member_names.add(member.filename)
			unpacked_bytes += member.file_size
			if member.file_size > MAX_MEMBER_BYTES:
				raise ValueError("ODP contains an oversized archive member")
			member_mode = member.external_attr >> 16
			if stat.S_IFMT(member_mode) == stat.S_IFLNK:
				raise ValueError("ODP contains a symbolic-link archive member")
		if unpacked_bytes > MAX_UNPACKED_BYTES:
			raise ValueError("ODP exceeds the 512 MiB unpacked size limit")
		if "content.xml" not in member_names or "mimetype" not in member_names:
			raise ValueError("ODP is missing required content.xml or mimetype members")
		mimetype = archive.read("mimetype").decode("ascii", errors="strict")
		if mimetype != ODP_MIMETYPE:
			raise ValueError("archive mimetype is not an OpenDocument presentation")
	return members


#============================================
def read_content_root(input_path: pathlib.Path) -> xml.etree.ElementTree.Element:
	"""Read and safely parse ODP content.xml.

	Args:
		input_path: Validated ODP path.

	Returns:
		Parsed XML root.
	"""
	with zipfile.ZipFile(input_path) as archive:
		content_bytes = archive.read("content.xml")
	# ASVS 1.5.1: defusedxml rejects DTD and entity expansion in ODP XML.
	root = defusedxml.ElementTree.fromstring(content_bytes)
	return root


#============================================
def append_unique_lines(destination: list[TextLine], additions: list[TextLine]) -> None:
	"""Append text lines while removing exact duplicates."""
	existing_text = {line.text for line in destination}
	for line in additions:
		if line.text not in existing_text:
			destination.append(line)
			existing_text.add(line.text)


#============================================
def slide_fallback_reasons(slide: Slide) -> list[str]:
	"""Explain why a slide needs a source-rendered fallback."""
	reasons: list[str] = []
	simple_lead = (
		bool(slide.title_lines or slide.subtitle_lines)
		and not slide.outline_lines
		and not slide.positioned_lines
		and not slide.image_hrefs
		and not slide.unsupported_image_hrefs
	)
	complex_tags = sorted(slide.drawing_tags & COMPLEX_DRAWING_TAGS)
	if complex_tags and not simple_lead:
		reasons.append(f"positioned drawing objects: {', '.join(complex_tags)}")
	if slide.unsupported_image_hrefs:
		reasons.append("unsupported embedded image format")
	if len(slide.image_hrefs) > 2:
		reasons.append("more than two embedded images")
	visible_lines = (
		slide.title_lines
		+ slide.subtitle_lines
		+ slide.outline_lines
		+ slide.positioned_lines
	)
	if len(visible_lines) > MAX_EDITABLE_LINES:
		reasons.append("dense text layout")
	character_count = sum(len(line.text) for line in visible_lines)
	if character_count > MAX_EDITABLE_CHARACTERS:
		reasons.append("long text layout")
	if slide.image_hrefs and len(slide.positioned_lines) > 3:
		reasons.append("positioned figure labels")
	if not visible_lines and not slide.image_hrefs:
		reasons.append("no editable text or supported image")
	return reasons


#============================================
def read_slide(
	page: xml.etree.ElementTree.Element,
	source_index: int,
	hidden: bool,
) -> Slide:
	"""Extract one ODP slide without its notes-layer placeholders.

	Args:
		page: ODF draw:page element.
		source_index: One-based ODP page index.

	Returns:
		Extracted slide model.
	"""
	notes_element = page.find("./presentation:notes", NS)
	note_element_ids: set[int] = set()
	if notes_element is not None:
		note_element_ids = {id(element) for element in notes_element.iter()}

	title_lines: list[TextLine] = []
	subtitle_lines: list[TextLine] = []
	outline_lines: list[TextLine] = []
	positioned_lines: list[TextLine] = []
	note_lines: list[TextLine] = []
	image_hrefs: list[str] = []
	unsupported_image_hrefs: list[str] = []
	drawing_tags: set[str] = set()

	for element in page.iter():
		if id(element) in note_element_ids:
			continue
		if element.tag.startswith(f"{{{NS['draw']}}}"):
			drawing_tags.add(local_name(element))

	for frame in page.findall(".//draw:frame", NS):
		if id(frame) in note_element_ids:
			continue
		presentation_class = frame.get(qname("presentation", "class"), "none")
		text_box = frame.find("./draw:text-box", NS)
		frame_lines: list[TextLine] = []
		if text_box is not None:
			frame_lines = collect_text_lines(text_box)
		if presentation_class == "title":
			append_unique_lines(title_lines, frame_lines)
		elif presentation_class == "subtitle":
			append_unique_lines(subtitle_lines, frame_lines)
		elif presentation_class == "outline":
			append_unique_lines(outline_lines, frame_lines)
		elif presentation_class not in IGNORED_PRESENTATION_CLASSES:
			append_unique_lines(positioned_lines, frame_lines)

		frame_image_hrefs: list[str] = []
		for image in frame.findall(".//draw:image", NS):
			href = image.get(qname("xlink", "href"), "")
			if href:
				frame_image_hrefs.append(href)
		supported_frame_images = [
			href for href in frame_image_hrefs
			if pathlib.PurePosixPath(href).suffix.lower() in SUPPORTED_IMAGE_SUFFIXES
		]
		if supported_frame_images:
			selected_href = supported_frame_images[0]
			if selected_href not in image_hrefs:
				image_hrefs.append(selected_href)
		elif frame_image_hrefs:
			for href in frame_image_hrefs:
				if href not in unsupported_image_hrefs:
					unsupported_image_hrefs.append(href)

	if notes_element is not None:
		for frame in notes_element.findall(".//draw:frame", NS):
			presentation_class = frame.get(qname("presentation", "class"), "none")
			if presentation_class != "notes":
				continue
			text_box = frame.find("./draw:text-box", NS)
			if text_box is not None:
				append_unique_lines(note_lines, collect_text_lines(text_box))

	slide_name = page.get(qname("draw", "name"), f"slide_{source_index:03d}")
	slide = Slide(
		source_index=source_index,
		name=slide_name,
		hidden=hidden,
		title_lines=title_lines,
		subtitle_lines=subtitle_lines,
		outline_lines=outline_lines,
		positioned_lines=positioned_lines,
		note_lines=note_lines,
		image_hrefs=image_hrefs,
		unsupported_image_hrefs=unsupported_image_hrefs,
		drawing_tags=drawing_tags,
		fallback_reasons=[],
	)
	slide.fallback_reasons = slide_fallback_reasons(slide)
	return slide


#============================================
def read_slides(input_path: pathlib.Path) -> list[Slide]:
	"""Read every slide from a validated ODP.

	Args:
		input_path: Validated ODP path.

	Returns:
		Slides in source order.
	"""
	root = read_content_root(input_path)
	style_definitions = odp_visibility.read_style_definitions(input_path, root)
	pages = root.findall(".//draw:page", NS)
	slides = [
		read_slide(
			page,
			index,
			odp_visibility.page_is_hidden(page, style_definitions),
		)
		for index, page in enumerate(pages, start=1)
	]
	if not slides:
		raise ValueError("ODP contains no presentation slides")
	return slides


#============================================
def validate_image_bytes(suffix: str, image_bytes: bytes) -> None:
	"""Confirm that image content matches its expected extension."""
	# ASVS 5.2.2: verify image magic bytes rather than trusting the member extension.
	if suffix == ".png" and not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
		raise ValueError("embedded .png member has invalid content")
	if suffix in {".jpeg", ".jpg"} and not image_bytes.startswith(b"\xff\xd8\xff"):
		raise ValueError("embedded JPEG member has invalid content")


#============================================
def asset_slug(output_path: pathlib.Path) -> str:
	"""Create a safe asset-directory name from an output filename."""
	slug = re.sub(r"[^a-z0-9]+", "_", output_path.stem.lower()).strip("_")
	if not slug:
		raise ValueError("output filename must contain an ASCII letter or number")
	return slug


#============================================
def extract_images(
	input_path: pathlib.Path,
	slides: list[Slide],
	staging_assets: pathlib.Path,
	markdown_asset_root: pathlib.PurePosixPath,
) -> dict[str, str]:
	"""Extract supported embedded images with internally generated names.

	Args:
		input_path: Validated ODP path.
		slides: Parsed slides.
		staging_assets: Temporary destination directory.
		markdown_asset_root: Relative asset path used in Markdown.

	Returns:
		Map from ODP member href to Markdown asset path.
	"""
	ordered_hrefs: list[str] = []
	for slide in slides:
		for href in slide.image_hrefs:
			if href not in ordered_hrefs:
				ordered_hrefs.append(href)

	staging_assets.mkdir(parents=True)
	asset_paths: dict[str, str] = {}
	with zipfile.ZipFile(input_path) as archive:
		member_names = {member.filename for member in archive.infolist()}
		for image_index, href in enumerate(ordered_hrefs, start=1):
			validate_member_name(href)
			if not href.startswith("Pictures/") or href not in member_names:
				raise ValueError("slide references an invalid embedded image path")
			suffix = pathlib.PurePosixPath(href).suffix.lower()
			if suffix not in SUPPORTED_IMAGE_SUFFIXES:
				raise ValueError("unsupported image reached the extraction stage")
			image_bytes = archive.read(href)
			validate_image_bytes(suffix, image_bytes)
			asset_name = f"image_{image_index:03d}{suffix}"
			# ASVS 5.3.2 and 5.3.3: archive names never control output paths.
			asset_path = staging_assets / asset_name
			asset_path.write_bytes(image_bytes)
			markdown_path = markdown_asset_root / asset_name
			asset_paths[href] = markdown_path.as_posix()
	return asset_paths


#============================================
def require_command(command_name: str) -> str:
	"""Resolve a required local command."""
	command_path = shutil.which(command_name)
	if command_path is None:
		raise RuntimeError(f"required command is unavailable: {command_name}")
	return command_path


#============================================
def run_checked(command: list[str], failure_message: str, timeout_seconds: int) -> None:
	"""Run a parameterized local command without a shell."""
	result = subprocess.run(
		command,
		capture_output=True,
		check=False,
		text=True,
		timeout=timeout_seconds,
	)
	if result.returncode != 0:
		detail = normalize_text(result.stderr or result.stdout)
		if detail:
			raise RuntimeError(f"{failure_message}: {detail}")
		raise RuntimeError(failure_message)


#============================================
def map_rendered_pages(
	rendered_pages: list[pathlib.Path],
	source_slide_count: int,
	visible_source_indexes: list[int],
) -> dict[int, pathlib.Path]:
	"""Map renderer pages to visible ODP source indexes without ambiguity.

	LibreOffice versions may include every source slide or omit slides whose
	drawing-page style marks them hidden.  Any other PDF page count is unsafe:
	falling back to the wrong slide would silently alter teaching content.
	"""
	if source_slide_count < 1:
		raise ValueError("source slide count must be positive")
	expected_indexes = list(range(1, source_slide_count + 1))
	if visible_source_indexes != sorted(set(visible_source_indexes)):
		raise ValueError("visible source indexes must be unique and ordered")
	if any(index not in expected_indexes for index in visible_source_indexes):
		raise ValueError("visible source indexes must belong to the source inventory")
	if len(rendered_pages) == source_slide_count:
		page_indexes = expected_indexes
	elif len(rendered_pages) == len(visible_source_indexes):
		page_indexes = visible_source_indexes
	else:
		raise RuntimeError(
			"LibreOffice page count does not match all or visible ODP slide inventory"
		)
	mapped_pages = dict(zip(page_indexes, rendered_pages, strict=True))
	visible_pages = {index: mapped_pages[index] for index in visible_source_indexes}
	return visible_pages


#============================================
def render_source_pages(
	input_path: pathlib.Path,
	temporary_root: pathlib.Path,
	source_slide_count: int,
	visible_source_indexes: list[int],
) -> dict[int, pathlib.Path]:
	"""Render ODP pages to PNGs and return pages keyed by visible source index."""
	soffice_path = require_command("soffice")
	pdftoppm_path = require_command("pdftoppm")
	libreoffice_output = temporary_root / "libreoffice"
	libreoffice_profile = temporary_root / "libreoffice_profile"
	render_output = temporary_root / "rendered_pages"
	libreoffice_output.mkdir()
	libreoffice_profile.mkdir()
	render_output.mkdir()
	profile_argument = f"-env:UserInstallation={libreoffice_profile.resolve().as_uri()}"
	soffice_command = [
		soffice_path,
		profile_argument,
		"--headless",
		"--convert-to",
		"pdf",
		"--outdir",
		str(libreoffice_output),
		str(input_path.resolve()),
	]
	run_checked(soffice_command, "LibreOffice could not render the ODP", 180)
	pdf_path = libreoffice_output / f"{input_path.stem}.pdf"
	if not pdf_path.is_file():
		raise RuntimeError("LibreOffice did not create the expected PDF")
	render_prefix = render_output / "slide"
	pdftoppm_command = [
		pdftoppm_path,
		"-png",
		"-r",
		"120",
		str(pdf_path),
		str(render_prefix),
	]
	run_checked(pdftoppm_command, "Poppler could not render the source PDF", 180)
	rendered_pages = sorted(render_output.glob("slide-*.png"))
	mapped_pages = map_rendered_pages(
		rendered_pages,
		source_slide_count,
		visible_source_indexes,
	)
	return mapped_pages


#============================================
def render_bullets(lines: list[TextLine]) -> list[str]:
	"""Render ODP outline lines as CommonMark bullets."""
	markdown_lines: list[str] = []
	for line in lines:
		indent = "  " * line.depth
		markdown_lines.append(f"{indent}- {ascii_entity_text(line.text)}")
	return markdown_lines


#============================================
def presenter_note_block(heading: str, lines: list[str]) -> list[str]:
	"""Build one Marp presenter-note comment.

	Args:
		heading: Note block heading.
		lines: Plain source note lines.

	Returns:
		Markdown HTML-comment lines.
	"""
	if not lines:
		return []
	comment_lines = ["", "<!--", comment_text(heading)]
	comment_lines.extend(f"- {comment_text(line)}" for line in lines)
	comment_lines.append("-->")
	return comment_lines


#============================================
def visible_source_text(slide: Slide) -> list[str]:
	"""Return deduplicated visible source text for fallback notes."""
	ordered_lines = (
		slide.title_lines
		+ slide.subtitle_lines
		+ slide.outline_lines
		+ slide.positioned_lines
	)
	visible_text: list[str] = []
	for line in ordered_lines:
		if line.text not in visible_text:
			visible_text.append(line.text)
	return visible_text


#============================================
def render_fallback_slide(slide: Slide, fallback_asset_path: str) -> list[str]:
	"""Render one complex slide as a source-page background with notes.

	Args:
		slide: Complex extracted slide.
		fallback_asset_path: Relative PNG path for the rendered source page.

	Returns:
		Marp Markdown slide lines.
	"""
	markdown_lines = [
		"<!-- _class: source-fallback -->",
		"<!-- _paginate: false -->",
		f"![bg contain]({fallback_asset_path})",
	]
	reason_lines = [f"Import fallback: {reason}" for reason in slide.fallback_reasons]
	note_lines = reason_lines + visible_source_text(slide)
	if slide.note_lines:
		note_lines.append("ODP speaker notes:")
		note_lines.extend(line.text for line in slide.note_lines)
	markdown_lines.extend(presenter_note_block("ODP source text", note_lines))
	return markdown_lines


#============================================
def render_editable_slide(
	slide: Slide,
	image_paths: dict[str, str],
	is_first_slide: bool,
) -> list[str]:
	"""Render one simple slide as editable Marp Markdown.

	Args:
		slide: Simple extracted slide.
		image_paths: Map from ODP image href to Markdown path.
		is_first_slide: Whether this is the first visible slide.

	Returns:
		Marp Markdown slide lines.
	"""
	body_lines = slide.outline_lines + slide.positioned_lines
	lead_slide = is_first_slide or (
		not body_lines and not slide.image_hrefs and bool(slide.title_lines or slide.subtitle_lines)
	)
	markdown_lines: list[str] = []
	if lead_slide:
		markdown_lines.append("<!-- _class: lead -->")
		markdown_lines.append("<!-- _paginate: false -->")

	if slide.title_lines:
		title = " ".join(line.text for line in slide.title_lines)
		markdown_lines.append(f"# {ascii_entity_text(title)}")
		for subtitle_line in slide.subtitle_lines:
			markdown_lines.append(f"## {ascii_entity_text(subtitle_line.text)}")
	elif slide.subtitle_lines:
		subtitle = " ".join(line.text for line in slide.subtitle_lines)
		markdown_lines.append(f"# {ascii_entity_text(subtitle)}")

	if slide.outline_lines:
		markdown_lines.append("")
		markdown_lines.extend(render_bullets(slide.outline_lines))
	if slide.positioned_lines:
		markdown_lines.append("")
		if len(slide.positioned_lines) == 1:
			markdown_lines.append(ascii_entity_text(slide.positioned_lines[0].text))
		else:
			markdown_lines.extend(render_bullets(slide.positioned_lines))

	resolved_images = [image_paths[href] for href in slide.image_hrefs]
	if len(resolved_images) == 1 and body_lines:
		markdown_lines.insert(0, "<!-- _class: split -->")
		markdown_lines.append(f"![bg right:42% contain]({resolved_images[0]})")
	elif len(resolved_images) == 1 and (slide.title_lines or slide.subtitle_lines):
		markdown_lines.extend(["", f"![h:500]({resolved_images[0]})"])
	elif len(resolved_images) == 1:
		markdown_lines.append(f"![bg contain]({resolved_images[0]})")
	elif len(resolved_images) == 2:
		image_line = " ".join(f"![w:520]({path})" for path in resolved_images)
		markdown_lines.extend(["", image_line])

	if slide.note_lines:
		note_text = [line.text for line in slide.note_lines]
		markdown_lines.extend(presenter_note_block("ODP speaker notes", note_text))
	return markdown_lines


#============================================
def deck_title(slides: list[Slide], input_path: pathlib.Path) -> str:
	"""Choose a deck title from the first visible slide.

	Args:
		slides: Parsed slide list.
		input_path: Source filename fallback.

	Returns:
		Plain deck title.
	"""
	for slide in slides:
		if slide.hidden:
			continue
		if slide.title_lines:
			title = " ".join(line.text for line in slide.title_lines)
			return title
		if slide.subtitle_lines:
			return slide.subtitle_lines[0].text
	fallback_title = input_path.stem.replace("_", " ").replace("-", " ")
	return fallback_title


#============================================
def render_deck_markdown(
	input_path: pathlib.Path,
	slides: list[Slide],
	image_paths: dict[str, str],
	fallback_paths: dict[int, str],
) -> str:
	"""Render a complete Marp Markdown deck.

	Args:
		input_path: Source ODP path.
		slides: Parsed slides.
		image_paths: Embedded-image path map.
		fallback_paths: Source slide index to fallback PNG path.

	Returns:
		Complete Marp Markdown source.
	"""
	title = deck_title(slides, input_path)
	frontmatter = [
		"---",
		"marp: true",
		"theme: genetics",
		"size: 16:10",
		"paginate: true",
		f"title: {json.dumps(title, ensure_ascii=True)}",
		"---",
	]
	visible_slides = [slide for slide in slides if not slide.hidden]
	markdown_lines = frontmatter
	for visible_index, slide in enumerate(visible_slides):
		if visible_index > 0:
			markdown_lines.extend(["", "---", ""])
		else:
			markdown_lines.append("")
		if slide.fallback_reasons:
			fallback_path = fallback_paths[slide.source_index]
			slide_lines = render_fallback_slide(slide, fallback_path)
		else:
			slide_lines = render_editable_slide(
				slide,
				image_paths,
				is_first_slide=visible_index == 0,
			)
		markdown_lines.extend(slide_lines)
	for hidden_slide in (slide for slide in slides if slide.hidden):
		markdown_lines.extend(
			[
				"",
				f"<!-- ODP hidden slide skipped: {comment_text(hidden_slide.name)} -->",
			]
		)
	markdown_text = "\n".join(markdown_lines).rstrip() + "\n"
	return markdown_text


#============================================
def validate_output_path(output_path: pathlib.Path) -> None:
	"""Validate a new Markdown destination."""
	if output_path.suffix.lower() != ".md":
		raise ValueError("output must use the .md extension")
	if output_path.exists():
		raise FileExistsError(
			"output Markdown already exists; the one-time importer will not overwrite it"
		)


#============================================
def convert_odp(input_path: pathlib.Path, output_path: pathlib.Path) -> ConversionSummary:
	"""Convert one ODP to Marp Markdown and migration assets.

	Args:
		input_path: Source ODP path.
		output_path: New Marp Markdown destination.

	Returns:
		Conversion counts and output path.
	"""
	input_path = input_path.resolve()
	output_path = output_path.resolve()
	validate_output_path(output_path)
	validate_odp(input_path)
	slides = read_slides(input_path)
	visible_slides = [slide for slide in slides if not slide.hidden]
	if not visible_slides:
		raise ValueError("ODP contains no visible presentation slides")

	output_path.parent.mkdir(parents=True, exist_ok=True)
	slug = asset_slug(output_path)
	assets_parent = output_path.parent / "assets"
	final_assets = assets_parent / slug
	if final_assets.exists():
		raise FileExistsError("output asset directory already exists")

	with tempfile.TemporaryDirectory(
		prefix=".odp_to_marp_",
		dir=output_path.parent,
	) as temporary_name:
		temporary_root = pathlib.Path(temporary_name)
		staging_assets = temporary_root / "assets"
		markdown_asset_root = pathlib.PurePosixPath("assets") / slug
		image_paths = extract_images(
			input_path,
			slides,
			staging_assets,
			markdown_asset_root,
		)

		fallback_slides = [slide for slide in visible_slides if slide.fallback_reasons]
		fallback_paths: dict[int, str] = {}
		if fallback_slides:
			visible_source_indexes = [
				slide.source_index for slide in visible_slides
			]
			rendered_pages = render_source_pages(
				input_path,
				temporary_root,
				len(slides),
				visible_source_indexes,
			)
			for slide in fallback_slides:
				rendered_page = rendered_pages[slide.source_index]
				asset_name = f"slide_{slide.source_index:03d}_source.png"
				asset_path = staging_assets / asset_name
				shutil.copyfile(rendered_page, asset_path)
				markdown_path = markdown_asset_root / asset_name
				fallback_paths[slide.source_index] = markdown_path.as_posix()

		markdown_text = render_deck_markdown(
			input_path,
			slides,
			image_paths,
			fallback_paths,
		)
		staging_markdown = temporary_root / output_path.name
		staging_markdown.write_text(markdown_text, encoding="utf-8")

		assets_parent.mkdir(exist_ok=True)
		shutil.move(str(staging_assets), str(final_assets))
		os.replace(staging_markdown, output_path)

	editable_count = len(visible_slides) - len(fallback_slides)
	summary = ConversionSummary(
		visible_slides=len(visible_slides),
		editable_slides=editable_count,
		fallback_slides=len(fallback_slides),
		hidden_slides=len(slides) - len(visible_slides),
		extracted_images=len(image_paths),
		output_path=output_path,
	)
	return summary


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments.

	Returns:
		Validated argparse namespace.
	"""
	parser = argparse.ArgumentParser(
		description="Convert one ODP into a simple Marp Markdown migration draft.",
	)
	parser.add_argument(
		"input_file",
		type=pathlib.Path,
		help="source .odp presentation",
	)
	parser.add_argument(
		"-o",
		"--output",
		dest="output_file",
		type=pathlib.Path,
		help="new .md output path (default: beside the input)",
	)
	args = parser.parse_args()
	return args


#============================================
def main() -> None:
	"""Run the one-time ODP-to-Marp importer."""
	args = parse_args()
	input_path = args.input_file
	output_path = args.output_file
	if output_path is None:
		output_path = input_path.with_suffix(".md")
	summary = convert_odp(input_path, output_path)
	print(f"Marp Markdown: {summary.output_path}")
	print(
		f"Slides: {summary.visible_slides} visible, "
		f"{summary.editable_slides} editable, "
		f"{summary.fallback_slides} source-rendered fallback, "
		f"{summary.hidden_slides} hidden skipped"
	)
	print(f"Embedded images extracted: {summary.extracted_images}")


if __name__ == "__main__":
	main()
