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
import marp_lib.layout_validation
import marp_lib.native_model


HEADER = "---\nmarp: true\ntheme: genetics\nsize: 16:10\n---\n"


#============================================
def native_slide(blocks: tuple[marp_lib.native_model.Block, ...]) -> marp_lib.native_model.Slide:
	"""Return a direct named one-panel IR slide for layout-validation tests."""
	location = marp_lib.native_model.SourceLocation(pathlib.Path("inline.ir"), 1)
	title_blocks = tuple(block for block in blocks if isinstance(block, marp_lib.native_model.Heading))
	body_blocks = tuple(block for block in blocks if not isinstance(block, marp_lib.native_model.Heading))
	cells = (marp_lib.native_model.Cell(body_blocks[0].location, body_blocks, "body"),) if body_blocks else ()
	return marp_lib.native_model.Slide(location, "one-panel", None, False, (), title_blocks, cells)


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
	if name == "multiple-choice":
		return HEADER + class_directive + "> Which molecule carries genetic information?\n>\n> - A. Lipid\n> - B. DNA\n\n> Answer: B. DNA\n"
	if spec.allows_root_body:
		return HEADER + class_directive + "# Layout title\n\n- Editable body\n"
	if spec.cell_count:
		return HEADER + class_directive + "# Layout title\n\n" + cells(spec.cell_count) + "\n"
	return HEADER + class_directive + "# Layout title\n\n- Editable body\n"


#============================================
def test_horizontal_grid_layout_keeps_bullets_numbers_and_links(tmp_path: pathlib.Path) -> None:
	"""Two-content cells retain independently editable native text semantics."""
	deck_path = tmp_path / "two-content.md"
	deck_path.write_text(HEADER + "<!-- _class: two-panels -->\n# Overview\n\n"
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
	deck_path.write_text(HEADER + "<!-- _class: one-panel -->\n# [Heading](https://example.edu)\n\n"
		"*Italic* and `code` [Course resource](https://example.edu/resource)  \nhttps://example.edu/path\n", encoding="utf-8")
	output_path = tmp_path / "formatting.pptx"
	marp_lib.native_export.render_native_pptx(marp_lib.native_export.parse_deck(deck_path), output_path)
	runs = [run for shape in Presentation(output_path).slides[0].shapes if shape.has_text_frame
		for paragraph in shape.text_frame.paragraphs for run in paragraph.runs]
	assert any(run.text == "https://example.edu/path" and run.font.name == layouts.URL_FONT_NAME
		and run.hyperlink.address == "https://example.edu/path" for run in runs)
	assert any(run.text == "Italic" and run.font.italic for run in runs)


#============================================
def test_h1_size_modifier_reports_native_title_capacity(tmp_path: pathlib.Path) -> None:
	"""A requested display title fails rather than receiving an implicit size reduction."""
	deck_path = tmp_path / "too-large.md"
	deck_path.write_text(HEADER + "<!-- _class: one-panel font-size-200 -->\n# Too large\n\n"
		"- Editable body\n", encoding="utf-8")
	with pytest.raises(ValueError, match=r"too-large\.md:7:.*one-panel H1 font-size-200 does not fit"):
		marp_lib.native_export.render_native_pptx(marp_lib.native_export.parse_deck(deck_path),
			tmp_path / "too-large.pptx")


#============================================
def test_long_default_title_reports_the_causal_h1_before_mutating_content(tmp_path: pathlib.Path) -> None:
	"""A default H1 that crowds named cells reports its own authored source line."""
	deck_path = tmp_path / "long-title.md"
	title = " ".join("adaptable" for _ in range(260))
	deck_path.write_text(HEADER + "<!-- _class: two-panels -->\n# " + title +
		"\n\n> - Left\n\n> - Right\n", encoding="utf-8")
	deck = marp_lib.native_export.parse_deck(deck_path)
	presentation = Presentation()
	slide = presentation.slides.add_slide(presentation.slide_layouts[6])
	with pytest.raises(ValueError, match=r"long-title\.md:7:.*H1 allocation leaves left"):
		layouts.render_layout(slide, deck.slides[0], deck)
	assert not slide.shapes


#============================================
def test_titleless_one_panel_uses_its_full_editable_body_region(tmp_path: pathlib.Path) -> None:
	"""An ordinary body-only slide remains native editable text without an H1."""
	location = marp_lib.native_model.SourceLocation(tmp_path / "titleless-body.ir", 7)
	body = marp_lib.native_model.Paragraph(location, (marp_lib.native_model.Text("Editable body"),))
	source = native_slide((body,))
	deck = marp_lib.native_model.Deck(location.path, tmp_path, tmp_path, "Titleless", False, (source,), {})
	presentation = Presentation()
	slide = presentation.slides.add_slide(presentation.slide_layouts[6])
	layouts.render_layout(slide, source, deck)
	assert [shape.text for shape in slide.shapes if shape.has_text_frame and shape.text] == ["Editable body"]


#============================================
def test_titleless_named_panels_keep_their_editable_slot_content(tmp_path: pathlib.Path) -> None:
	"""A titleless ordinary panel layout keeps every named cell independently native."""
	location = marp_lib.native_model.SourceLocation(tmp_path / "titleless-panels.ir", 7)
	def paragraph(value: str) -> marp_lib.native_model.Paragraph:
		return marp_lib.native_model.Paragraph(location, (marp_lib.native_model.Text(value),))
	source = marp_lib.native_model.Slide(location, "two-panels", None, False, (), (), (
		marp_lib.native_model.Cell(location, (paragraph("Left"),), "left"),
		marp_lib.native_model.Cell(location, (paragraph("Right"),), "right"),
	))
	deck = marp_lib.native_model.Deck(location.path, tmp_path, tmp_path, "Titleless", False, (source,), {})
	presentation = Presentation()
	slide = presentation.slides.add_slide(presentation.slide_layouts[6])
	layouts.render_layout(slide, source, deck)
	assert {shape.text for shape in slide.shapes if shape.has_text_frame and shape.text} == {"Left", "Right"}


#============================================
@pytest.mark.parametrize("with_title", (False, True))
def test_root_body_allows_one_local_h2_with_or_without_a_global_title(tmp_path: pathlib.Path,
		with_title: bool) -> None:
	"""A root body subtitle shares the same native heading/body rendering as named cells."""
	location = marp_lib.native_model.SourceLocation(tmp_path / f"body-h2-{with_title}.ir", 7)
	local_heading = marp_lib.native_model.Heading(location, 2, (marp_lib.native_model.Text("Local heading"),))
	body = marp_lib.native_model.Paragraph(location, (marp_lib.native_model.Text("Editable body"),))
	global_blocks = ((marp_lib.native_model.Heading(location, 1,
		(marp_lib.native_model.Text("Global title"),)),) if with_title else ())
	source = marp_lib.native_model.Slide(location, "one-panel", None, False, (), global_blocks, (
		marp_lib.native_model.Cell(location, (local_heading, body), "body"),))
	deck = marp_lib.native_model.Deck(location.path, tmp_path, tmp_path, "Body heading", False, (source,), {})
	presentation = Presentation()
	slide = presentation.slides.add_slide(presentation.slide_layouts[6])
	layouts.render_layout(slide, source, deck)
	visible_text = {shape.text for shape in slide.shapes if shape.has_text_frame and shape.text}
	assert visible_text == ({"Global title", "Local heading", "Editable body"} if with_title else
		{"Local heading", "Editable body"})


#============================================
def test_root_body_rejects_multiple_local_h2_headings_before_mutating_a_slide(tmp_path: pathlib.Path) -> None:
	"""Root-body headings retain the same one-optional-heading contract as named slots."""
	location = marp_lib.native_model.SourceLocation(tmp_path / "many-body-h2.ir", 7)
	heading = marp_lib.native_model.Heading(location, 2, (marp_lib.native_model.Text("First"),))
	second = marp_lib.native_model.Heading(marp_lib.native_model.SourceLocation(location.path, 10), 2,
		(marp_lib.native_model.Text("Second"),))
	body = marp_lib.native_model.Paragraph(location, (marp_lib.native_model.Text("Editable body"),))
	source = marp_lib.native_model.Slide(location, "one-panel", None, False, (), (), (
		marp_lib.native_model.Cell(location, (heading, second, body), "body"),))
	deck = marp_lib.native_model.Deck(location.path, tmp_path, tmp_path, "Body heading", False, (source,), {})
	presentation = Presentation()
	slide = presentation.slides.add_slide(presentation.slide_layouts[6])
	with pytest.raises(ValueError, match=r"many-body-h2\.ir:10:.*one optional level-two heading"):
		layouts.render_layout(slide, source, deck)
	assert not slide.shapes


#============================================
@pytest.mark.parametrize("layout_name", ("one-panel", "two-panels"))
def test_a_lone_local_h2_is_visible_editable_cell_content(tmp_path: pathlib.Path,
		layout_name: str) -> None:
	"""A local H2 is valid visible content in root and named ordinary panel cells."""
	location = marp_lib.native_model.SourceLocation(tmp_path / f"h2-only-{layout_name}.ir", 7)
	def heading(value: str) -> marp_lib.native_model.Heading:
		return marp_lib.native_model.Heading(location, 2, (marp_lib.native_model.Text(value),))
	if layout_name == "one-panel":
		source = marp_lib.native_model.Slide(location, layout_name, None, False, (), (), (
			marp_lib.native_model.Cell(location, (heading("Body heading"),), "body"),))
	else:
		source = marp_lib.native_model.Slide(location, layout_name, None, False, (), (), (
			marp_lib.native_model.Cell(location, (heading("Left heading"),), "left"),
			marp_lib.native_model.Cell(location, (heading("Right heading"),), "right"),
		))
	deck = marp_lib.native_model.Deck(location.path, tmp_path, tmp_path, "Local heading", False, (source,), {})
	presentation = Presentation()
	slide = presentation.slides.add_slide(presentation.slide_layouts[6])
	layouts.render_layout(slide, source, deck)
	assert {shape.text for shape in slide.shapes if shape.has_text_frame and shape.text} == (
		{"Body heading"} if layout_name == "one-panel" else {"Left heading", "Right heading"})


#============================================
def test_unreadable_local_h2_fails_before_background_or_shapes(tmp_path: pathlib.Path) -> None:
	"""An assigned cell rejects an H2 that cannot fit even at the readable floor."""
	location = marp_lib.native_model.SourceLocation(tmp_path / "dense-h2.ir", 7)
	heading = marp_lib.native_model.Heading(location, 2,
		(marp_lib.native_model.Text(" ".join("adaptable" for _ in range(800))),))
	source = marp_lib.native_model.Slide(location, "one-panel", None, False, (), (), (
		marp_lib.native_model.Cell(location, (heading,), "body"),))
	deck = marp_lib.native_model.Deck(location.path, tmp_path, tmp_path, "Local heading", False, (source,), {})
	presentation = Presentation()
	slide = presentation.slides.add_slide(presentation.slide_layouts[6])
	with pytest.raises(ValueError, match=r"dense-h2\.ir:7:.*local H2 cannot fit"):
		layouts.render_layout(slide, source, deck)
	assert not slide.shapes


#============================================
def test_two_over_one_reserves_readable_footer_space(tmp_path: pathlib.Path) -> None:
	"""A dense full-width footer receives height from two short upper components."""
	deck_path = tmp_path / "footer.md"
	footer = "\n".join(f"> - Footer line {index}" for index in range(24))
	deck_path.write_text(HEADER + "<!-- _class: two-over-one-panels -->\n# Title\n\n"
		"> - Left\n\n> - Right\n\n" + footer + "\n", encoding="utf-8")
	source = marp_lib.native_export.parse_deck(deck_path).slides[0]
	plan = layouts.plan_content(source, layouts.LAYOUTS["two-over-one-panels"])
	canonical = layouts.cell_rectangles(layouts.LAYOUTS["two-over-one-panels"], plan.content_rectangle)
	responsive = layouts.content_cell_rectangles(source, layouts.LAYOUTS["two-over-one-panels"], plan.content_rectangle)

	assert responsive[2][3] > canonical[2][3]
	assert responsive[0][3] < canonical[0][3]


#============================================
@pytest.mark.parametrize("case", ("component-image", "vertical-title"))
def test_titleless_panel_variants_keep_native_content(tmp_path: pathlib.Path, case: str) -> None:
	"""Titleless component and title-strip panels retain their native body objects."""
	location = marp_lib.native_model.SourceLocation(tmp_path / f"{case}.ir", 7)
	if case == "component-image":
		write_png(tmp_path / "component.png")
		image = marp_lib.native_model.Image(location, "Component", "component.png", None)
		source = native_slide((image,))
	else:
		def paragraph(value: str) -> marp_lib.native_model.Paragraph:
			return marp_lib.native_model.Paragraph(location, (marp_lib.native_model.Text(value),))
		source = marp_lib.native_model.Slide(location, "vertical-title-two-panels", None, False, (), (), (
			marp_lib.native_model.Cell(location, (paragraph("Text"),), "text"),
			marp_lib.native_model.Cell(location, (paragraph("Chart"),), "chart"),
		))
	deck = marp_lib.native_model.Deck(location.path, tmp_path, tmp_path, "Titleless", False, (source,), {})
	presentation = Presentation()
	slide = presentation.slides.add_slide(presentation.slide_layouts[6])
	layouts.render_layout(slide, source, deck)
	visible_text = {shape.text for shape in slide.shapes if shape.has_text_frame and shape.text}
	if case == "component-image":
		assert len([shape for shape in slide.shapes if shape.shape_type == MSO_SHAPE_TYPE.PICTURE]) == 1 and not visible_text
	else:
		assert visible_text == {"Text", "Chart"}


#============================================
def test_title_only_still_requires_its_h1_before_mutating_a_slide(tmp_path: pathlib.Path) -> None:
	"""Titleless support does not weaken the intentionally title-only layout."""
	location = marp_lib.native_model.SourceLocation(tmp_path / "missing-title.ir", 7)
	source = marp_lib.native_model.Slide(location, "title-only", None, False, (), (), ())
	deck = marp_lib.native_model.Deck(location.path, tmp_path, tmp_path, "Titleless", False, (source,), {})
	presentation = Presentation()
	slide = presentation.slides.add_slide(presentation.slide_layouts[6])
	with pytest.raises(ValueError, match=r"missing-title\.ir:7:.*require exactly one level-one title"):
		layouts.render_layout(slide, source, deck)
	assert not slide.shapes


#============================================
def test_native_table_keeps_headers_blank_cells_and_editable_runs(tmp_path: pathlib.Path) -> None:
	"""A typed table remains one native, selectable table rather than a flattened picture."""
	location = marp_lib.native_model.SourceLocation(tmp_path / "table.ir", 7)
	title = marp_lib.native_model.Heading(location, 1, (marp_lib.native_model.Text("Results"),))
	table = marp_lib.native_model.Table(location, (
		(marp_lib.native_model.Strong((marp_lib.native_model.Text("Condition"),)),),
		(marp_lib.native_model.Text("Value"),),
	), (
		((marp_lib.native_model.Text("Control"),), (marp_lib.native_model.Text(""),)),
		((marp_lib.native_model.Text("Treatment"),), (marp_lib.native_model.Link(
			(marp_lib.native_model.Text("Readout"),), "https://example.test/readout"),)),
	))
	source = native_slide((title, table))
	deck = marp_lib.native_model.Deck(location.path, tmp_path, tmp_path, "Tables", False, (source,), {})
	presentation = Presentation()
	slide = presentation.slides.add_slide(presentation.slide_layouts[6])
	layouts.render_layout(slide, source, deck)
	table_shapes = [shape.table for shape in slide.shapes if shape.has_table]
	assert len(table_shapes) == 1
	assert [(cell.text, bool(cell.text_frame.paragraphs[0].runs[0].font.bold),
		cell.text_frame.paragraphs[0].runs[0].hyperlink.address)
		for row in table_shapes[0].rows for cell in row.cells] == [
		("Condition", True, None), ("Value", True, None), ("Control", False, None),
		("", False, None), ("Treatment", False, None),
		("Readout", False, "https://example.test/readout"),
	]


#============================================
def test_mixed_table_content_fails_before_mutating_a_slide(tmp_path: pathlib.Path) -> None:
	"""A table's one-destination contract diagnoses the mixed authored block."""
	table_location = marp_lib.native_model.SourceLocation(tmp_path / "mixed-table.ir", 7)
	paragraph_location = marp_lib.native_model.SourceLocation(tmp_path / "mixed-table.ir", 10)
	title = marp_lib.native_model.Heading(table_location, 1, (marp_lib.native_model.Text("Results"),))
	table = marp_lib.native_model.Table(table_location, ((marp_lib.native_model.Text("Header"),),), (
		((marp_lib.native_model.Text("Value"),),),))
	paragraph = marp_lib.native_model.Paragraph(paragraph_location, (marp_lib.native_model.Text("Context"),))
	source = native_slide((title, table, paragraph))
	deck = marp_lib.native_model.Deck(table_location.path, tmp_path, tmp_path, "Tables", False, (source,), {})
	presentation = Presentation()
	slide = presentation.slides.add_slide(presentation.slide_layouts[6])
	with pytest.raises(ValueError, match=r"mixed-table\.ir:10:.*table cannot mix"):
		layouts.render_layout(slide, source, deck)
	assert not slide.shapes


#============================================
@pytest.mark.parametrize(("case", "line", "message"), (
	("second", 10, "supports one table"),
	("ragged", 7, "same number of columns"),
	("zero-column", 7, "at least one column"),
	("no-destination", 7, "do not have a native table destination"),
))
def test_table_contract_boundaries_fail_before_mutating_a_slide(tmp_path: pathlib.Path,
		case: str, line: int, message: str) -> None:
	"""Unsupported table destinations and shapes fail at their authored source."""
	path = tmp_path / f"{case}.ir"
	table_location = marp_lib.native_model.SourceLocation(path, 7)
	second_location = marp_lib.native_model.SourceLocation(path, 10)
	title = marp_lib.native_model.Heading(table_location, 1, (marp_lib.native_model.Text("Results"),))
	table = marp_lib.native_model.Table(table_location, ((marp_lib.native_model.Text("Header"),),), (
		((marp_lib.native_model.Text("Value"),),),))
	if case == "second":
		source = native_slide((title, table, marp_lib.native_model.Table(second_location,
			((marp_lib.native_model.Text("Header"),),), (((marp_lib.native_model.Text("Later"),),),))))
	elif case == "ragged":
		ragged = marp_lib.native_model.Table(table_location, (
			(marp_lib.native_model.Text("First"),), (marp_lib.native_model.Text("Second"),),),
			(((marp_lib.native_model.Text("Only"),),),))
		source = native_slide((title, ragged))
	elif case == "zero-column":
		source = native_slide((title, marp_lib.native_model.Table(table_location, (), ())))
	else:
		source = marp_lib.native_model.Slide(table_location, "title-only", None, False, (),
			(title, table), ())
	deck = marp_lib.native_model.Deck(path, tmp_path, tmp_path, "Tables", False, (source,), {})
	presentation = Presentation()
	slide = presentation.slides.add_slide(presentation.slide_layouts[6])
	with pytest.raises(ValueError, match=rf"{case}\.ir:{line}:.*{message}"):
		layouts.render_layout(slide, source, deck)
	assert not slide.shapes


#============================================
def test_named_slots_keep_their_tables_as_distinct_native_shapes(tmp_path: pathlib.Path) -> None:
	"""Separate table cells retain separately selectable table objects."""
	location = marp_lib.native_model.SourceLocation(tmp_path / "two-tables.ir", 7)
	title = marp_lib.native_model.Heading(location, 1, (marp_lib.native_model.Text("Comparison"),))
	def table(value: str) -> marp_lib.native_model.Table:
		return marp_lib.native_model.Table(location, ((marp_lib.native_model.Text("Header"),),), (
			((marp_lib.native_model.Text(value),),),))
	source = marp_lib.native_model.Slide(location, "two-panels", None, False, (), (title,), (
		marp_lib.native_model.Cell(location, (table("Left"),), "left"),
		marp_lib.native_model.Cell(location, (table("Right"),), "right"),
	))
	deck = marp_lib.native_model.Deck(location.path, tmp_path, tmp_path, "Tables", False, (source,), {})
	presentation = Presentation()
	slide = presentation.slides.add_slide(presentation.slide_layouts[6])
	layouts.render_layout(slide, source, deck)
	tables = [shape.table for shape in slide.shapes if shape.has_table]
	assert len(tables) == 2
	assert [table.cell(1, 0).text for table in tables] == ["Left", "Right"]


#============================================
def test_titleless_table_readability_fails_before_mutating_a_slide(tmp_path: pathlib.Path) -> None:
	"""A body-only overfull table fails rather than reducing native text below 14px."""
	location = marp_lib.native_model.SourceLocation(tmp_path / "dense-table.ir", 7)
	cell = (marp_lib.native_model.Text(" ".join("adaptable" for _ in range(100))),)
	table = marp_lib.native_model.Table(location, ((marp_lib.native_model.Text("Header"),),),
		tuple((cell,) for _ in range(30)))
	source = native_slide((table,))
	deck = marp_lib.native_model.Deck(location.path, tmp_path, tmp_path, "Tables", False, (source,), {})
	presentation = Presentation()
	slide = presentation.slides.add_slide(presentation.slide_layouts[6])
	with pytest.raises(ValueError, match=r"dense-table\.ir:7:.*table cannot fit"):
		layouts.render_layout(slide, source, deck)
	assert not slide.shapes


#============================================
def test_two_panel_title_and_cells_remain_editable_and_nonoverlapping(tmp_path: pathlib.Path) -> None:
	"""A normal title preserves independently editable, non-overlapping native cells."""
	deck_path = tmp_path / "planned-two-panels.md"
	deck_path.write_text(HEADER + "<!-- _class: two-panels -->\n# Overview\n\n> - Left\n\n> - Right\n",
		encoding="utf-8")
	output_path = tmp_path / "planned-two-panels.pptx"
	marp_lib.native_export.render_native_pptx(marp_lib.native_export.parse_deck(deck_path), output_path)
	shapes = [shape for shape in Presentation(output_path).slides[0].shapes if shape.has_text_frame]
	title = next(shape for shape in shapes if shape.text == "Overview")
	cells = [shape for shape in shapes if shape.text in ("Left", "Right")]
	assert all(title.top + title.height <= cell.top for cell in cells)


#============================================
@pytest.mark.parametrize("name", ["vertical-text-panel", "vertical-panel",
	"two-panels-vertical-clipart"])
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
def test_rejects_wrong_cell_count_and_keeps_mixed_flow_in_source_order(tmp_path: pathlib.Path) -> None:
	"""Panel cells reject missing required named slots at the source."""
	wrong_count = tmp_path / "wrong-count.md"
	wrong_count.write_text(HEADER + "<!-- _class: four-panels -->\n# Four\n\n" + cells(3),
		encoding="utf-8")
	with pytest.raises(ValueError, match=r"wrong-count\.md:\d+:.*named slot"):
		marp_lib.native_export.render_native_pptx(marp_lib.native_export.parse_deck(wrong_count),
			tmp_path / "wrong-count.pptx")
#============================================
@pytest.mark.parametrize(("case", "line", "message"), (
	("table-image", 10, "table cannot mix with Image"),
	("multiple-choice-second-image", 10, "supports one optional top component image"),
	("multiple-choice-nonfirst-image", 10, "must be the first question block"),
))
def test_flow_boundaries_reject_ambiguous_image_modes_before_shapes(tmp_path: pathlib.Path,
		case: str, line: int, message: str) -> None:
	"""Table/image and invalid MC image order have no native destination ambiguity."""
	path = tmp_path / f"{case}.ir"
	first = marp_lib.native_model.SourceLocation(path, 7)
	second = marp_lib.native_model.SourceLocation(path, 10)
	image = marp_lib.native_model.Image(second, "Component", "component.png", None)
	if case == "table-image":
		table = marp_lib.native_model.Table(first, ((marp_lib.native_model.Text("Header"),),), (
			((marp_lib.native_model.Text("Value"),),),))
		source = native_slide((table, image))
	else:
		choice = marp_lib.native_model.ListBlock(first, False, 1, (
			marp_lib.native_model.ListItem(first, (marp_lib.native_model.Text("A. Choice"),)),))
		question_blocks = (image, image, choice) if case.endswith("second-image") else (choice, image)
		answer = marp_lib.native_model.Cell(first, (
			marp_lib.native_model.Paragraph(first, (marp_lib.native_model.Text("Answer"),)),), "answer")
		source = marp_lib.native_model.Slide(first, "multiple-choice", None, False, (), (), (
			marp_lib.native_model.Cell(first, question_blocks, "question"), answer))
	deck = marp_lib.native_model.Deck(path, tmp_path, tmp_path, "Flow", False, (source,), {})
	presentation = Presentation()
	slide = presentation.slides.add_slide(presentation.slide_layouts[6])
	with pytest.raises(ValueError, match=rf"{case}\.ir:{line}:.*{message}"):
		layouts.render_layout(slide, source, deck)
	assert not slide.shapes


#============================================
def test_native_layout_rejects_nested_bare_attributes_at_their_source() -> None:
	"""Nested bare attributes receive a source-located native-layout diagnostic."""
	location = marp_lib.native_model.SourceLocation(pathlib.Path("nested.ir"), 11)
	nested_item = marp_lib.native_model.ListItem(location, (marp_lib.native_model.Text("Body"),),
		attributes=(marp_lib.native_model.Attribute("bare"),))
	nested_list = marp_lib.native_model.ListBlock(location, False, 1, (nested_item,))
	root_item = marp_lib.native_model.ListItem(location, (marp_lib.native_model.Text("Parent"),),
		children=(nested_list,))
	root_list = marp_lib.native_model.ListBlock(location, False, 1, (root_item,))
	with pytest.raises(ValueError, match=r"nested\.ir:11:.*attributes on ListItem"):
		layouts.validate_layout_source(native_slide((root_list,)))


#============================================
def test_native_layout_rejects_quote_blocks_at_their_source() -> None:
	"""Quote blocks retain the explicit unsupported-block diagnostic."""
	location = marp_lib.native_model.SourceLocation(pathlib.Path("quote.ir"), 19)
	quote = marp_lib.native_model.QuoteBlock(location, ())
	with pytest.raises(ValueError, match=r"quote\.ir:19:.*QuoteBlock blocks"):
		layouts.validate_layout_source(native_slide((quote,)))


#============================================
def test_native_layout_rejects_nested_inline_math_at_its_source() -> None:
	"""Inline math in nested formatted list content waits for a native adapter."""
	title_location = marp_lib.native_model.SourceLocation(pathlib.Path("math.ir"), 1)
	math_location = marp_lib.native_model.SourceLocation(pathlib.Path("math.ir"), 9)
	math = marp_lib.native_model.InlineMath("x^2")
	formatted = marp_lib.native_model.Strong((marp_lib.native_model.Emphasis((
		marp_lib.native_model.Link((math,), "https://example.test/math"),)),))
	nested_item = marp_lib.native_model.ListItem(math_location, (formatted,))
	nested_list = marp_lib.native_model.ListBlock(math_location, False, 1, (nested_item,))
	root_item = marp_lib.native_model.ListItem(math_location, (marp_lib.native_model.Text("Parent"),),
		children=(nested_list,))
	root_list = marp_lib.native_model.ListBlock(math_location, False, 1, (root_item,))
	title = marp_lib.native_model.Heading(title_location, 1, (marp_lib.native_model.Text("Title"),))
	with pytest.raises(ValueError, match=r"math\.ir:9:.*InlineMath until a native math adapter exists"):
		layouts.validate_layout_source(native_slide((title, root_list)))


#============================================
def test_missing_component_image_reports_its_authored_image_line(tmp_path: pathlib.Path) -> None:
	"""Image-resolution failures retain the precise component image location."""
	deck_path = tmp_path / "missing-image.md"
	deck_path.write_text(HEADER + "<!-- _class: one-panel -->\n# Missing\n\n"
		"![Absent component](absent.png)\n", encoding="utf-8")
	with pytest.raises(ValueError, match=r"missing-image\.md:9:.*component image is missing"):
		marp_lib.native_export.render_native_pptx(marp_lib.native_export.parse_deck(deck_path),
			tmp_path / "missing-image.pptx")


#============================================
@pytest.mark.parametrize("name", ["vertical-text-panel", "vertical-panel"])
@pytest.mark.parametrize("body", ["Vertical paragraph\n", "- Vertical list item\n"])
def test_vertical_root_body_layouts_accept_one_text_block(tmp_path: pathlib.Path, name: str,
		body: str) -> None:
	"""Each root-body vertical layout creates exactly one editable vertical body frame."""
	deck_path = tmp_path / f"{name}.md"
	deck_path.write_text(HEADER + f"<!-- _class: {name} -->\n# Vertical\n\n" + body, encoding="utf-8")
	output_path = tmp_path / f"{name}.pptx"
	marp_lib.native_export.render_native_pptx(marp_lib.native_export.parse_deck(deck_path), output_path)
	vertical_frames = [shape for shape in Presentation(output_path).slides[0].shapes if shape.has_text_frame
		and 'vert="vert"' in shape.element.xml and shape.text != "Vertical"]
	assert len(vertical_frames) == 1


#============================================
@pytest.mark.parametrize("name", ["vertical-text-panel", "vertical-panel"])
def test_vertical_root_body_layouts_accept_one_component_image(tmp_path: pathlib.Path, name: str) -> None:
	"""A single component image is the legal native picture form of a vertical body."""
	write_png(tmp_path / "component.png")
	deck_path = tmp_path / f"{name}-image.md"
	deck_path.write_text(HEADER + f"<!-- _class: {name} -->\n# Vertical\n\n"
		"![Vertical component](component.png)\n", encoding="utf-8")
	output_path = tmp_path / f"{name}-image.pptx"
	marp_lib.native_export.render_native_pptx(marp_lib.native_export.parse_deck(deck_path), output_path)
	pictures = [shape for shape in Presentation(output_path).slides[0].shapes
		if shape.shape_type == MSO_SHAPE_TYPE.PICTURE]
	assert len(pictures) == 1


#============================================
@pytest.mark.parametrize("name", ["vertical-text-panel", "vertical-panel"])
def test_vertical_root_body_layouts_reject_multiple_blocks_at_the_second_block(tmp_path: pathlib.Path,
		name: str) -> None:
	"""A second root body block receives its own actionable source location."""
	deck_path = tmp_path / f"{name}-invalid.md"
	deck_path.write_text(HEADER + f"<!-- _class: {name} -->\n# Vertical\n\nFirst paragraph\n\n- Second block\n",
		encoding="utf-8")
	with pytest.raises(ValueError, match=rf"{name}-invalid\.md:11:.*exactly one body block"):
		marp_lib.native_export.render_native_pptx(marp_lib.native_export.parse_deck(deck_path),
			tmp_path / "invalid.pptx")


#============================================
@pytest.mark.parametrize(("names", "message"), [
	(("left", "left"), "duplicate cell slot"),
	(("left", "other"), "unknown slot"),
	(("left", None), "must name a declared slot"),
])
def test_layout_validation_rejects_invalid_named_cells_at_their_source(
		names: tuple[str | None, str | None], message: str) -> None:
	"""Direct IR cannot bypass the named-slot contract used by rendering."""
	location = marp_lib.native_model.SourceLocation(pathlib.Path("named.ir"), 7)
	title = marp_lib.native_model.Heading(location, 1, (marp_lib.native_model.Text("Title"),))
	body = marp_lib.native_model.Paragraph(location, (marp_lib.native_model.Text("Text"),))
	source = marp_lib.native_model.Slide(location, "two-panels", None, False, (), (title,), (
		marp_lib.native_model.Cell(location, (body,), names[0]),
		marp_lib.native_model.Cell(location, (body,), names[1]),
	))
	with pytest.raises(ValueError, match=rf"named\.ir:7:.*{message}"):
		layouts.validate_layout_source(source)


#============================================
def test_named_cells_render_in_their_declared_slots_not_source_order(tmp_path: pathlib.Path) -> None:
	"""Named cells retain their semantic positions when their source order changes."""
	location = marp_lib.native_model.SourceLocation(tmp_path / "named.ir", 1)
	title = marp_lib.native_model.Heading(location, 1, (marp_lib.native_model.Text("Title"),))
	cells_by_name = tuple(marp_lib.native_model.Cell(location, (
		marp_lib.native_model.Paragraph(location, (marp_lib.native_model.Text(name),)),), name)
		for name in ("bottom-right", "left", "top-right"))
	source = marp_lib.native_model.Slide(location, "one-plus-two-panels", None, False, (), (title,), cells_by_name)
	deck = marp_lib.native_model.Deck(location.path, tmp_path, tmp_path, "Named slots", False, (source,), {})
	output_path = tmp_path / "named-slots.pptx"
	marp_lib.native_export.render_native_pptx(deck, output_path)
	placements = {shape.text: (shape.left, shape.top) for shape in Presentation(output_path).slides[0].shapes
		if shape.has_text_frame and shape.text in ("left", "top-right", "bottom-right")}
	assert placements["left"][0] < placements["top-right"][0] and \
		placements["top-right"][1] < placements["bottom-right"][1]


#============================================
def test_multiple_choice_renders_a_native_question_and_answer_popup(tmp_path: pathlib.Path) -> None:
	"""The automatic answer remains one editable popup object beside its visible question."""
	location = marp_lib.native_model.SourceLocation(tmp_path / "choice.ir", 7)
	question = marp_lib.native_model.Cell(location, (
		marp_lib.native_model.Paragraph(location, (marp_lib.native_model.Text("Which molecule stores heredity?"),)),
		marp_lib.native_model.ListBlock(location, False, 1, (
			marp_lib.native_model.ListItem(location, (marp_lib.native_model.Text("A. Lipid"),)),
			marp_lib.native_model.ListItem(location, (marp_lib.native_model.Text("B. DNA"),)),
		)),
	), "question")
	implicit_appear = marp_lib.native_model.Reveal(marp_lib.native_model.RevealEffect.APPEAR,
		marp_lib.native_model.RevealSequence.OBJECT)
	answer = marp_lib.native_model.Cell(location, (
		marp_lib.native_model.Paragraph(location, (marp_lib.native_model.Text("Answer: B. DNA"),), implicit_appear),
		marp_lib.native_model.Paragraph(location, (marp_lib.native_model.Text("DNA stores hereditary information."),)),
	), "answer")
	source = marp_lib.native_model.Slide(location, "multiple-choice", None, False, (), (), (question, answer))
	deck = marp_lib.native_model.Deck(location.path, tmp_path, tmp_path, "Choice", False, (source,), {})
	output_path = tmp_path / "choice.pptx"
	marp_lib.native_export.render_native_pptx(deck, output_path)
	shapes = [shape for shape in Presentation(output_path).slides[0].shapes if shape.has_text_frame]
	popups = [shape for shape in shapes if shape.text == "Answer: B. DNA\nDNA stores hereditary information."]
	assert len(popups) == 1


#============================================
@pytest.mark.parametrize(("case", "line", "message"), [
	("paragraph-only", 11, "at least one visible editable choice ListBlock"),
	("empty", 7, "at least one visible editable choice ListBlock"),
	("heading", 13, "at least one visible editable choice ListBlock"),
	("global-content", 3, "do not accept source-global title, subtitle, or body blocks"),
	("question-reveal", 17, "question content is visible when the slide opens"),
	("answer-reveal", 19, "only accepts its implicit on-click object appear reveal"),
])
def test_multiple_choice_rejects_invalid_source_at_the_authored_location(
		case: str, line: int, message: str) -> None:
	"""Question, global, and reveal contracts identify the authored offending block."""
	path = pathlib.Path("choice.ir")
	question_location = marp_lib.native_model.SourceLocation(path, 7)
	paragraph_location = marp_lib.native_model.SourceLocation(path, 11)
	heading_location = marp_lib.native_model.SourceLocation(path, 13)
	list_location = marp_lib.native_model.SourceLocation(path, 17)
	answer_location = marp_lib.native_model.SourceLocation(path, 19)
	choices = marp_lib.native_model.ListBlock(list_location, False, 1, (
		marp_lib.native_model.ListItem(list_location, (marp_lib.native_model.Text("A. Lipid"),)),
	))
	if case == "paragraph-only":
		question_blocks = (marp_lib.native_model.Paragraph(paragraph_location,
			(marp_lib.native_model.Text("Which molecule?"),)),)
	elif case == "empty":
		question_blocks = ()
	elif case == "heading":
		question_blocks = (marp_lib.native_model.Heading(heading_location, 2,
			(marp_lib.native_model.Text("Which molecule?"),)),)
	else:
		question_blocks = (choices,)
	if case == "question-reveal":
		question_blocks = (marp_lib.native_model.ListBlock(list_location, False, 1, choices.items,
			marp_lib.native_model.Reveal(marp_lib.native_model.RevealEffect.APPEAR,
				marp_lib.native_model.RevealSequence.OBJECT)),)
	answer_reveal = marp_lib.native_model.Reveal(marp_lib.native_model.RevealEffect.APPEAR,
		marp_lib.native_model.RevealSequence.PARAGRAPHS) if case == "answer-reveal" else None
	answer = marp_lib.native_model.Cell(answer_location, (
		marp_lib.native_model.Paragraph(answer_location, (marp_lib.native_model.Text("Answer: DNA"),), answer_reveal),
	), "answer")
	root_blocks = (marp_lib.native_model.Paragraph(marp_lib.native_model.SourceLocation(path, 3),
		(marp_lib.native_model.Text("Global"),)),) if case == "global-content" else ()
	source = marp_lib.native_model.Slide(question_location, "multiple-choice", None, False, (), root_blocks, (
		marp_lib.native_model.Cell(question_location, question_blocks, "question"), answer))
	with pytest.raises(ValueError, match=rf"choice\.ir:{line}:.*{message}"):
		layouts.validate_layout_source(source)


#============================================
def test_multiple_choice_reports_the_forbidden_question_block_location() -> None:
	"""A valid choice list does not hide the later forbidden heading location."""
	path = pathlib.Path("choice.ir")
	question_location = marp_lib.native_model.SourceLocation(path, 7)
	choice_location = marp_lib.native_model.SourceLocation(path, 11)
	heading_location = marp_lib.native_model.SourceLocation(path, 13)
	answer_location = marp_lib.native_model.SourceLocation(path, 17)
	choices = marp_lib.native_model.ListBlock(choice_location, False, 1, (
		marp_lib.native_model.ListItem(choice_location, (marp_lib.native_model.Text("A. Lipid"),)),
	))
	heading = marp_lib.native_model.Heading(heading_location, 2, (marp_lib.native_model.Text("Nope"),))
	question = marp_lib.native_model.Cell(question_location, (choices, heading), "question")
	answer = marp_lib.native_model.Cell(answer_location, (
		marp_lib.native_model.Paragraph(answer_location, (marp_lib.native_model.Text("Answer: DNA"),)),
	), "answer")
	source = marp_lib.native_model.Slide(question_location, "multiple-choice", None, False, (), (),
		(question, answer))
	with pytest.raises(ValueError, match=r"choice\.ir:13:.*optional prompt paragraph"):
		layouts.validate_layout_source(source)


#============================================
def test_title_slide_keeps_multiple_subtitle_lines_in_one_text_shape(tmp_path: pathlib.Path) -> None:
	"""Consecutive level-two source headings share the title slide's subtitle region."""
	deck_path = tmp_path / "multiple-subtitles.md"
	deck_path.write_text(HEADER + "<!-- _class: title-slide -->\n# Title\n\n## First subtitle\n\n## Second subtitle\n",
		encoding="utf-8")
	output_path = tmp_path / "multiple-subtitles.pptx"
	marp_lib.native_export.render_native_pptx(marp_lib.native_export.parse_deck(deck_path), output_path)
	subtitle_shapes = [shape for shape in Presentation(output_path).slides[0].shapes if shape.has_text_frame
		and "First subtitle" in shape.text]
	assert len(subtitle_shapes) == 1 and "Second subtitle" in subtitle_shapes[0].text


#============================================
def test_presentation_chain_converts_odp_to_pdf(tmp_path: pathlib.Path) -> None:
	"""PDF export uses ODP as its required LibreOffice predecessor."""
	deck_path = tmp_path / "chain.md"
	deck_path.write_text(HEADER + "<!-- _class: one-panel -->\n# Chain\n\n- Editable body\n", encoding="utf-8")
	with mock.patch.object(marp_lib.native_export, "find_repo_root", return_value=tmp_path), \
		mock.patch.object(marp_lib.native_export, "convert_presentation"):
		outputs = marp_lib.native_export.export_deck(str(deck_path), "pdf")
	assert list(outputs) == ["pptx", "odp", "pdf"]


#============================================
def test_folder_discovery_selects_sorted_direct_supported_children(tmp_path: pathlib.Path) -> None:
	"""Folder builds retain direct Marp and Djot decks in stable filename order."""
	folder = tmp_path / "slides"
	folder.mkdir()
	(folder / "z_deck.md").write_text(HEADER, encoding="utf-8")
	(folder / "notes.md").write_text("# Notes\n", encoding="utf-8")
	(folder / "a_deck.md").write_text(HEADER, encoding="utf-8")
	(folder / "b_deck.djot").write_text("=== layout: blank\n", encoding="utf-8")
	nested = folder / "nested"
	nested.mkdir()
	(nested / "hidden_deck.md").write_text(HEADER, encoding="utf-8")
	(nested / "hidden_deck.djot").write_text("=== layout: blank\n", encoding="utf-8")
	def detect_marp(path: pathlib.Path) -> bool:
		"""Limit Marp front-matter detection to Markdown candidates."""
		if path.suffix != ".md":
			raise AssertionError("Djot discovery must not inspect Marp front matter")
		return path.name != "notes.md"
	with mock.patch.object(marp_lib.native_export, "has_marp_front_matter", side_effect=detect_marp):
		decks = marp_lib.native_export.discover_decks(str(folder), tmp_path)
	assert [path.name for path in decks] == ["a_deck.md", "b_deck.djot", "z_deck.md"]


#============================================
def test_folder_discovery_rejects_an_empty_source_selection(tmp_path: pathlib.Path) -> None:
	"""A folder without a direct presentation source receives an actionable input error."""
	folder = tmp_path / "slides"
	folder.mkdir()
	(folder / "notes.md").write_text("---\ntitle: Notes\n---\n", encoding="utf-8")
	with pytest.raises(ValueError, match="no presentation source decks found"):
		marp_lib.native_export.discover_decks(str(folder), tmp_path)


#============================================
def test_export_progress_follows_artifact_dependency_order(tmp_path: pathlib.Path) -> None:
	"""Progress reports parsing before the unchanged PPTX, ODP, and PDF chain."""
	deck_path = tmp_path / "stages.md"
	deck_path.write_text(HEADER + "<!-- _class: blank -->\n", encoding="utf-8")
	stages: list[str] = []
	with mock.patch.object(marp_lib.native_export, "find_repo_root", return_value=tmp_path), \
		mock.patch.object(marp_lib.native_export, "convert_presentation"):
		marp_lib.native_export.export_deck(str(deck_path), "all", stages.append)
	assert stages == ["parsing", "pptx", "odp", "pdf"]
