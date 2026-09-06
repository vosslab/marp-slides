"""Behavioral tests for experimental PPTX-to-extended-Djot conversion."""

# Standard Library
import json
import types
import pathlib

# PIP3 modules
import pytest
from PIL import Image
from pptx import Presentation
from pptx.util import Inches

# Local modules
from tools import pptx_to_djot


#============================================
def write_png(output_path: pathlib.Path) -> pathlib.Path:
	"""Write one bounded source image."""
	image = Image.new("RGB", (40, 30), (20, 90, 160))
	image.save(output_path)
	return output_path


#============================================
def test_conversion_uses_djot_layout_slots_and_omits_notes(tmp_path: pathlib.Path) -> None:
	"""One text-image slide becomes strict-Djot-shaped source without notes."""
	image_path = write_png(tmp_path / "chromosome.png")
	presentation = Presentation()
	slide = presentation.slides.add_slide(presentation.slide_layouts[5])
	assert slide.shapes.title is not None
	slide.shapes.title.text = "Genetics overview"
	text_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.7), Inches(5.2), Inches(3.0))
	text_box.text_frame.text = "Chromosomes carry genes"
	slide.shapes.add_picture(str(image_path), Inches(7.0), Inches(1.5), width=Inches(2.5))
	slide.notes_slide.notes_text_frame.text = "Presenter-only explanation"
	hidden = presentation.slides.add_slide(presentation.slide_layouts[5])
	hidden.element.set("show", "0")
	input_path = tmp_path / "lecture.pptx"
	presentation.save(input_path)
	output_path = tmp_path / "lecture.djot"

	summary = pptx_to_djot.convert_pptx(
		input_path,
		output_path,
		expected_slide_count=2,
		expected_hidden={2},
	)
	djot = output_path.read_text(encoding="utf-8")
	report = json.loads(summary.report_path.read_text(encoding="utf-8"))

	assert summary.visible_slides == 1
	assert summary.hidden_slides == 1
	assert summary.extracted_images == 1
	assert "=== layout: two-panels" in djot
	assert "# Genetics overview" in djot
	assert "@left" in djot
	assert "@right" in djot
	assert "- Chromosomes carry genes" in djot
	assert "![Slide image 1](assets/lecture/image_001.png)" in djot
	assert "Presenter-only explanation" not in djot
	assert "<!--" not in djot
	assert report["hidden_slides"] == [2]
	assert report["slides"][0]["notes_omitted"] == 1


#============================================
def test_empty_notes_part_is_treated_as_no_notes() -> None:
	"""An empty LibreOffice notes relationship never aborts a Djot import."""
	notes_relation = types.SimpleNamespace(reltype="http://example.test/notesSlide")
	slide = types.SimpleNamespace(
		part=types.SimpleNamespace(rels={"notes": notes_relation}),
		notes_slide=types.SimpleNamespace(notes_text_frame=None),
	)

	assert pptx_to_djot.slide_notes(slide) == ()


#============================================
def test_vector_media_is_validated_and_emf_type_is_normalized() -> None:
	"""Legacy vector blobs retain their actual type only after header validation."""
	wmf_blob = b"\xd7\xcd\xc6\x9a" + b"\x00" * 24
	emf_blob = b"\x01\x00\x00\x00" + b"\x00" * 36 + b" EMF" + b"\x00" * 8

	pptx_to_djot.validate_image_blob(wmf_blob, ".wmf")
	pptx_to_djot.validate_image_blob(emf_blob, ".emf")
	assert pptx_to_djot.image_suffix(emf_blob, ".wmf") == ".emf"
	with pytest.raises(ValueError, match="WMF image header"):
		pptx_to_djot.validate_image_blob(b"not a metafile", ".wmf")


#============================================
def test_dna_text_uses_inline_verbatim_and_ascii_prime_projection() -> None:
	"""Short DNA sequences use the settled source surface without a new delimiter."""
	assert pptx_to_djot.djot_text("5'-AGTACT-3'") == "5&prime;-`AGTACT`-3&prime;"
	assert pptx_to_djot.djot_text("Compare ATGC and CGTA") == "Compare `ATGC` and `CGTA`"


#============================================
def test_converter_refuses_non_djot_or_existing_output(tmp_path: pathlib.Path) -> None:
	"""The experimental importer never overwrites another source format."""
	with pytest.raises(ValueError, match=".djot"):
		pptx_to_djot.validate_output_path(tmp_path / "lecture.md")

	output_path = tmp_path / "lecture.djot"
	output_path.write_text("existing\n", encoding="utf-8")
	with pytest.raises(FileExistsError, match="will not overwrite"):
		pptx_to_djot.validate_output_path(output_path)
