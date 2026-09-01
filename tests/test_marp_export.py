"""Behavioral tests for native editable Marp presentation export."""

# Standard Library
import pathlib

# PIP3 modules
import pytest
import PIL.Image
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

# Local Modules
import marp_lib.native_export


#============================================
def write_png(output_path: pathlib.Path) -> pathlib.Path:
	"""Write one component-image fixture for native picture tests."""
	image = PIL.Image.new("RGB", (80, 40), (36, 87, 143))
	image.save(output_path)
	return output_path


#============================================
def test_validate_input_accepts_auto_fitting_content_image(tmp_path: pathlib.Path) -> None:
	"""Accept a normal Marp image without a hard-coded dimension."""
	deck_path = tmp_path / "lecture.md"
	deck_path.write_text("# Figure\n\n![Cell](assets/cell.png)\n", encoding="utf-8")

	validated_path = marp_lib.native_export.validate_input(str(deck_path), tmp_path)

	assert validated_path == deck_path


#============================================
def test_validate_input_rejects_source_fallback_class(tmp_path: pathlib.Path) -> None:
	"""Reject the retired full-slide fallback layout marker."""
	deck_path = tmp_path / "lecture.md"
	deck_path.write_text("<!-- _class: source-fallback -->\n", encoding="utf-8")

	with pytest.raises(ValueError) as error:
		marp_lib.native_export.validate_input(str(deck_path), tmp_path)

	assert "failed conversions" in str(error.value)


#============================================
def test_validate_input_rejects_source_slide_image(tmp_path: pathlib.Path) -> None:
	"""Reject a full-slide source image even without the retired class."""
	deck_path = tmp_path / "lecture.md"
	deck_path.write_text("![Slide](assets/slide_012_source.png)\n", encoding="utf-8")

	with pytest.raises(ValueError) as error:
		marp_lib.native_export.validate_input(str(deck_path), tmp_path)

	assert "failed conversions" in str(error.value)


#============================================
def test_parse_deck_accepts_titleless_figure_continuation(tmp_path: pathlib.Path) -> None:
	"""The native parser keeps a titleless figure continuation self-contained."""
	deck_path = tmp_path / "lecture.md"
	deck_path.write_text(
		"---\nmarp: true\ntheme: genetics\nsize: 16:10\n---\n"
		"<!-- _class: figure -->\n"
		"<!-- Continuation: Carrier report -->\n"
		"![Carrier report](assets/carrier.png)\n",
		encoding="utf-8",
	)

	deck = marp_lib.native_export.parse_deck(deck_path)

	assert deck.slides[0].classes == {"figure"}
	assert deck.slides[0].content.startswith("![Carrier report]")


#============================================
def test_css_pixels_convert_once_at_the_office_boundary() -> None:
	"""Theme CSS pixels use the 96-DPI CSS-to-Office conversion."""
	assert marp_lib.native_export.css_px_to_pt(48) == 36
	assert marp_lib.native_export.css_px_to_pt(18) == 13.5


#============================================
def test_native_pptx_preserves_editable_semantics(tmp_path: pathlib.Path) -> None:
	"""Text, lists, links, notes, and component images stay separate native objects."""
	image_path = write_png(tmp_path / "chromosome.png")
	deck_path = tmp_path / "lecture.md"
	deck_path.write_text(
		"---\ntitle: Native semantics\nmarp: true\ntheme: genetics\nsize: 16:10\n---\n"
		"<!-- _class: url-list -->\n# Genetics overview\n\n"
		"- Linked [resource](https://example.edu/resource)\n"
		"  - Nested detail\n"
		"1. Ordered step\n\n"
		f"![bg right:40% contain]({image_path.name})\n\n"
		"<!-- notes: Explain the chromosome example.\nPause for questions. -->\n",
		encoding="utf-8",
	)
	output_path = tmp_path / "lecture.pptx"

	marp_lib.native_export.render_native_pptx(
		marp_lib.native_export.parse_deck(deck_path), output_path,
	)

	presentation = Presentation(output_path)
	slide = presentation.slides[0]
	shape_xml = "".join(shape.element.xml for shape in slide.shapes)
	pictures = [shape for shape in slide.shapes if shape.shape_type == MSO_SHAPE_TYPE.PICTURE]
	text = "\n".join(shape.text for shape in slide.shapes if shape.has_text_frame)
	assert "Genetics overview" in text and "Nested detail" in text
	assert "buChar" in shape_xml and "buAutoNum" in shape_xml
	assert "hlinkClick" in shape_xml
	assert presentation.core_properties.title == "Native semantics"
	assert slide.notes_slide.notes_text_frame.text == "Explain the chromosome example.\nPause for questions."
	assert pictures[0].element.nvPicPr.cNvPr.get("descr") == "bg right:40% contain"
	assert all(
		picture.width < presentation.slide_width and picture.height < presentation.slide_height
		for picture in pictures
	)


#============================================
def test_native_pptx_keeps_pane_paragraphs_links_and_list_markers(tmp_path: pathlib.Path) -> None:
	"""Pane headings, bullets, numbering, and links retain independent native semantics."""
	deck_path = tmp_path / "panes.md"
	deck_path.write_text(
		"---\nmarp: true\ntheme: genetics\nsize: 16:10\n---\n"
		"<!-- _class: two-pane url-list -->\n"
		"# [Overview](https://example.edu/overview)\n\n"
		"> ## [Left pane](https://example.edu/left)\n"
		">\n"
		"> - First item\n"
		">   - Nested item\n"
		"> 1. Ordered item\n\n"
		"> ## Right pane\n"
		">\n"
		"> - Second item\n",
		encoding="utf-8",
	)
	output_path = tmp_path / "panes.pptx"
	marp_lib.native_export.render_native_pptx(
		marp_lib.native_export.parse_deck(deck_path), output_path,
	)

	slide = Presentation(output_path).slides[0]
	left_shape = next(shape for shape in slide.shapes if shape.has_text_frame and "Left pane" in shape.text)
	paragraphs = left_shape.text_frame.paragraphs
	bullet = paragraphs[1]._p.xpath(".//a:buChar")[0]
	nested_bullet = paragraphs[2]._p.xpath(".//a:buChar")[0]
	ordered = paragraphs[3]._p.xpath(".//a:buAutoNum")[0]

	assert [paragraph.text for paragraph in paragraphs[:4]] == [
		"Left pane", "First item", "Nested item", "Ordered item",
	]
	assert paragraphs[0]._p.xpath(".//a:buChar") == []
	assert bullet.get("char") == "\u2022"
	assert nested_bullet.get("char") == "\u2022"
	assert paragraphs[2].level == 1
	assert ordered.get("type") == "arabicPeriod"
	assert paragraphs[0].runs[0].hyperlink.address == "https://example.edu/left"
	assert paragraphs[0].runs[0].font.name == "PT Sans Narrow"


#============================================
def test_native_text_frames_request_editable_autofit(tmp_path: pathlib.Path) -> None:
	"""Native text boxes carry an Office text-fit safeguard without flattening text."""
	deck_path = tmp_path / "autofit.md"
	deck_path.write_text(
		"---\nmarp: true\ntheme: genetics\nsize: 16:10\n---\n# Autofit\n\n- Editable text\n",
		encoding="utf-8",
	)
	output_path = tmp_path / "autofit.pptx"
	marp_lib.native_export.render_native_pptx(
		marp_lib.native_export.parse_deck(deck_path), output_path,
	)
	shape_xml = "".join(shape.element.xml for shape in Presentation(output_path).slides[0].shapes)
	assert "normAutofit" in shape_xml


#============================================
def test_balance_list_columns_keeps_nested_children_with_their_parent() -> None:
	"""Column balancing preserves order and keeps each nested group intact."""
	items = [
		("Short parent", 0, False, False),
		("Attached child", 1, False, False),
		("Another parent", 0, False, False),
		("A longer parent with enough words to influence the height balance", 0, False, False),
		("Its attached child", 1, False, False),
	]
	left, right = marp_lib.native_export.balance_list_columns(items, 20, 539)
	assert left + right == items
	assert any(item[0] == "Attached child" for item in left)
	assert any(item[0] == "Its attached child" for item in right)


#============================================
def test_list_columns_reject_content_below_the_readable_minimum(tmp_path: pathlib.Path) -> None:
	"""Over-capacity content reports the supported readable minimum clearly."""
	deck_path = tmp_path / "over-capacity.md"
	too_long = " ".join(["unavoidable"] * 4000)
	deck_path.write_text(
		"---\nmarp: true\ntheme: genetics\nsize: 16:10\n---\n"
		"<!-- _class: list-columns -->\n# Capacity\n\n"
		f"- {too_long}\n\n- Second group\n",
		encoding="utf-8",
	)
	with pytest.raises(ValueError, match="supported readable minimum"):
		marp_lib.native_export.render_native_pptx(
			marp_lib.native_export.parse_deck(deck_path), tmp_path / "over-capacity.pptx",
		)


#============================================
def test_figure_picture_keeps_alt_text_and_rejects_body_text(tmp_path: pathlib.Path) -> None:
	"""Figure images carry authored descriptions and require image-only body content."""
	image_path = write_png(tmp_path / "figure.png")
	deck_path = tmp_path / "figure.md"
	deck_path.write_text(
		"---\nmarp: true\ntheme: genetics\nsize: 16:10\n---\n"
		"<!-- _class: figure -->\n# Karyotype\n\n"
		f"![Karyotype diagram]({image_path.name})\n",
		encoding="utf-8",
	)
	output_path = tmp_path / "figure.pptx"
	marp_lib.native_export.render_native_pptx(
		marp_lib.native_export.parse_deck(deck_path), output_path,
	)

	slide = Presentation(output_path).slides[0]
	picture = next(shape for shape in slide.shapes if shape.shape_type == MSO_SHAPE_TYPE.PICTURE)
	assert picture.element.nvPicPr.cNvPr.get("descr") == "Karyotype diagram"

	deck_path.write_text(
		"---\nmarp: true\ntheme: genetics\nsize: 16:10\n---\n"
		"<!-- _class: figure -->\n# Karyotype\n\n"
		f"This body paragraph requires a layout.\n\n![Karyotype diagram]({image_path.name})\n",
		encoding="utf-8",
	)
	with pytest.raises(ValueError, match="figure slides support headings"):
		marp_lib.native_export.render_native_pptx(
			marp_lib.native_export.parse_deck(deck_path), output_path,
		)


#============================================
def test_ordinary_slide_rejects_overlapping_body_and_component_image(tmp_path: pathlib.Path) -> None:
	"""Ordinary layouts require an explicit split class for text and an image."""
	image_path = write_png(tmp_path / "component.png")
	deck_path = tmp_path / "ordinary.md"
	deck_path.write_text(
		"---\nmarp: true\ntheme: genetics\nsize: 16:10\n---\n"
		"# Explicit layout required\n\n"
		f"- Body text\n\n![Component image]({image_path.name})\n",
		encoding="utf-8",
	)

	with pytest.raises(ValueError, match="ordinary slides support one component image"):
		marp_lib.native_export.render_native_pptx(
			marp_lib.native_export.parse_deck(deck_path), tmp_path / "ordinary.pptx",
		)
