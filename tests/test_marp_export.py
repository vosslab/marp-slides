"""Focused tests for direct native Marp presentation export."""

# Standard Library
import pathlib
from unittest import mock

# PIP3 modules
import PIL.Image
import pytest
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

# Local Modules
from marp_lib import layouts
import marp_lib.native_export


HEADER = "---\nmarp: true\ntheme: genetics\nsize: 16:10\n---\n"


#============================================
def write_png(output_path: pathlib.Path) -> pathlib.Path:
	"""Write one small component image fixture."""
	image = PIL.Image.new("RGB", (80, 40), (36, 87, 143))
	image.save(output_path)
	return output_path


#============================================
def cells(count: int) -> str:
	"""Return valid reading-order quoted cells for a multi-content layout."""
	return "\n\n".join(f"> ## Cell {index}\n>\n> - Editable item {index}" for index in range(1, count + 1))


#============================================
def layout_markdown(name: str, spec: layouts.LayoutSpec) -> str:
	"""Return the smallest valid source fixture for one registered layout."""
	class_directive = f"<!-- _class: {name} -->\n"
	if name == "blank":
		return HEADER + class_directive
	if name in ("title-slide", "centered-text"):
		return HEADER + class_directive + "# Center title\n\n## Subtitle\n"
	if name == "title-only":
		return HEADER + class_directive + "# Title only\n"
	if name == "gallery":
		return HEADER + class_directive + "![One](one.png) ![Two](two.png)\n"
	if spec.cell_count:
		return HEADER + class_directive + "# Layout title\n\n" + cells(spec.cell_count) + "\n"
	return HEADER + class_directive + "# Layout title\n\n- Editable body\n"


#============================================
@pytest.mark.parametrize("name", sorted(layouts.LAYOUTS))
def test_every_registered_layout_renders_native_objects(tmp_path: pathlib.Path, name: str) -> None:
	"""Each canonical layout selects its own builder and retains editable objects."""
	spec = layouts.LAYOUTS[name]
	if name == "gallery":
		write_png(tmp_path / "one.png")
		write_png(tmp_path / "two.png")
	deck_path = tmp_path / f"{name}.md"
	deck_path.write_text(layout_markdown(name, spec), encoding="utf-8")
	output_path = tmp_path / f"{name}.pptx"
	marp_lib.native_export.render_native_pptx(marp_lib.native_export.parse_deck(deck_path), output_path)
	slide = Presentation(output_path).slides[0]
	assert layouts.LAYOUTS[name] is spec
	assert all(shape.shape_type != MSO_SHAPE_TYPE.PICTURE or
		(shape.width < Presentation(output_path).slide_width and shape.height < Presentation(output_path).slide_height)
		for shape in slide.shapes)
	if name not in ("blank", "gallery"):
		assert any(shape.has_text_frame for shape in slide.shapes)
	if spec.cell_count:
		text = "\n".join(shape.text for shape in slide.shapes if shape.has_text_frame)
		assert f"Cell {spec.cell_count}" in text


#============================================
def test_horizontal_grid_layout_keeps_bullets_numbers_and_links(tmp_path: pathlib.Path) -> None:
	"""Two-content cells retain independently editable native text semantics."""
	deck_path = tmp_path / "two-content.md"
	deck_path.write_text(HEADER + "<!-- _class: title-two-content -->\n# Overview\n\n"
		"> ## [Left](https://example.edu/left)\n>\n> - First\n>   - Nested\n> 1. Ordered\n\n"
		"> ## Right\n>\n> - Second\n", encoding="utf-8")
	output_path = tmp_path / "two-content.pptx"
	marp_lib.native_export.render_native_pptx(marp_lib.native_export.parse_deck(deck_path), output_path)
	shape_xml = "".join(shape.element.xml for shape in Presentation(output_path).slides[0].shapes)
	assert "buChar" in shape_xml and "buAutoNum" in shape_xml and "hlinkClick" in shape_xml


#============================================
def test_inline_runs_keep_native_formatting_and_url_typography(tmp_path: pathlib.Path) -> None:
	"""Typed emphasis, code, breaks, and bare URLs remain formatted editable runs."""
	deck_path = tmp_path / "formatting.md"
	deck_path.write_text(HEADER + "<!-- _class: title-content -->\n# [Heading](https://example.edu)\n\n"
		"*Italic* and `code`  \nhttps://example.edu/path\n", encoding="utf-8")
	output_path = tmp_path / "formatting.pptx"
	marp_lib.native_export.render_native_pptx(marp_lib.native_export.parse_deck(deck_path), output_path)
	runs = [run for shape in Presentation(output_path).slides[0].shapes if shape.has_text_frame
		for paragraph in shape.text_frame.paragraphs for run in paragraph.runs]
	assert any(run.text == "Italic" and run.font.italic for run in runs)
	assert any(run.text == "code" and run.font.name == "Courier New" for run in runs)
	assert any(run.text == "https://example.edu/path" and run.font.name == layouts.URL_FONT_NAME
		and run.hyperlink.address == "https://example.edu/path" for run in runs)


#============================================
@pytest.mark.parametrize("name", ["title-vertical-text", "vertical-title-vertical-text",
	"title-two-vertical-text-clipart"])
def test_vertical_layouts_write_editable_ooxml_text_direction(tmp_path: pathlib.Path, name: str) -> None:
	"""Vertical layouts use editable text-body direction rather than a raster image."""
	spec = layouts.LAYOUTS[name]
	deck_path = tmp_path / f"{name}.md"
	deck_path.write_text(layout_markdown(name, spec), encoding="utf-8")
	output_path = tmp_path / f"{name}.pptx"
	marp_lib.native_export.render_native_pptx(marp_lib.native_export.parse_deck(deck_path), output_path)
	shape_xml = "".join(shape.element.xml for shape in Presentation(output_path).slides[0].shapes)
	assert 'vert="vert"' in shape_xml


#============================================
def test_gallery_images_keep_descriptions_and_are_not_full_slide(tmp_path: pathlib.Path) -> None:
	"""Gallery components retain their independent descriptions after PPTX export."""
	write_png(tmp_path / "one.png")
	write_png(tmp_path / "two.png")
	deck_path = tmp_path / "gallery.md"
	deck_path.write_text(HEADER + "<!-- _class: gallery -->\n# Components\n\n"
		"![First component](one.png) ![Second component](two.png)\n", encoding="utf-8")
	output_path = tmp_path / "gallery.pptx"
	marp_lib.native_export.render_native_pptx(marp_lib.native_export.parse_deck(deck_path), output_path)
	presentation = Presentation(output_path)
	pictures = [shape for shape in presentation.slides[0].shapes
		if shape.shape_type == MSO_SHAPE_TYPE.PICTURE]
	assert [picture.element.nvPicPr.cNvPr.get("descr") for picture in pictures] == [
		"First component", "Second component",
	]
	assert all(picture.width < presentation.slide_width and picture.height < presentation.slide_height
		for picture in pictures)


#============================================
def test_rejects_retired_layout_classes_directly(tmp_path: pathlib.Path) -> None:
	"""Retired layout and modifier vocabulary has no compatibility contract."""
	deck_path = tmp_path / "retired.md"
	deck_path.write_text(HEADER + "<!-- _class: lead -->\n# Retired\n", encoding="utf-8")
	with pytest.raises(ValueError, match="unsupported Marp slide class"):
		marp_lib.native_export.parse_deck(deck_path)


#============================================
def test_rejects_wrong_cell_count_and_mixed_cell_content(tmp_path: pathlib.Path) -> None:
	"""Cell source contracts account for every source block before rendering."""
	image_path = write_png(tmp_path / "component.png")
	wrong_count = tmp_path / "wrong-count.md"
	wrong_count.write_text(HEADER + "<!-- _class: title-four-content -->\n# Four\n\n" + cells(3),
		encoding="utf-8")
	with pytest.raises(ValueError, match=r"wrong-count\.md:\d+:.*require exactly 4"):
		marp_lib.native_export.render_native_pptx(marp_lib.native_export.parse_deck(wrong_count),
			tmp_path / "wrong-count.pptx")
	mixed = tmp_path / "mixed.md"
	mixed.write_text(HEADER + "<!-- _class: title-two-content -->\n# Mixed\n\n"
		"> ## First\n>\n> - Text\n>\n> ![Component](component.png)\n\n> ## Second\n>\n> - Text\n",
		encoding="utf-8")
	with pytest.raises(ValueError, match="cannot combine text"):
		marp_lib.native_export.render_native_pptx(marp_lib.native_export.parse_deck(mixed),
			tmp_path / "mixed.pptx")
	assert image_path.is_file()


#============================================
def test_presentation_chain_converts_odp_to_pdf(tmp_path: pathlib.Path) -> None:
	"""PDF export uses ODP as its required LibreOffice predecessor."""
	deck_path = tmp_path / "chain.md"
	deck_path.write_text(HEADER + "<!-- _class: title-content -->\n# Chain\n\n- Editable body\n", encoding="utf-8")
	with mock.patch.object(marp_lib.native_export, "find_repo_root", return_value=tmp_path), \
		mock.patch.object(marp_lib.native_export, "convert_presentation") as convert:
		outputs = marp_lib.native_export.export_deck(str(deck_path), "pdf")
	assert list(outputs) == ["pptx", "odp", "pdf"]
	assert convert.call_args_list[0].args[0] == outputs["pptx"]
	assert convert.call_args_list[0].args[2] == "odp"
	assert convert.call_args_list[1].args[0] == outputs["odp"]
	assert convert.call_args_list[1].args[2] == "pdf"
