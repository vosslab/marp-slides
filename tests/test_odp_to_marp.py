"""Behavioral tests for the one-time ODP-to-Marp importer."""

# Standard Library
import pathlib
import xml.etree.ElementTree
import zipfile

# PIP3 modules
import pytest

# local repo modules
from tools import odp_to_marp


MINIMAL_CONTENT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
	xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
	xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
	xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
	xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">
	<office:body>
		<office:presentation>
			<draw:page draw:name="page1">
				<draw:frame presentation:class="title">
					<draw:text-box><text:p>Genetics &amp; inheritance</text:p></draw:text-box>
				</draw:frame>
			</draw:page>
		</office:presentation>
	</office:body>
</office:document-content>
"""

IMAGE_CONTENT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
	xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
	xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
	xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
	xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">
	<office:body><office:presentation><draw:page draw:name="page1">
		<draw:frame presentation:class="title"><draw:text-box><text:p>Image slide</text:p></draw:text-box></draw:frame>
		<draw:frame><draw:image xlink:href="Pictures/example.png" xmlns:xlink="http://www.w3.org/1999/xlink"/></draw:frame>
	</draw:page></office:presentation></office:body>
</office:document-content>
"""

HIDDEN_STYLE_CONTENT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
	xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
	xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
	xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
	xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
	xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">
	<office:automatic-styles><style:style style:name="hidden-page" style:family="drawing-page"><style:drawing-page-properties presentation:visibility="hidden"/></style:style></office:automatic-styles>
	<office:body><office:presentation>
		<draw:page draw:name="visible"><draw:frame presentation:class="title"><draw:text-box><text:p>Visible</text:p></draw:text-box></draw:frame></draw:page>
		<draw:page draw:name="hidden" draw:style-name="hidden-page"><draw:frame presentation:class="title"><draw:text-box><text:p>Hidden</text:p></draw:text-box></draw:frame></draw:page>
	</office:presentation></office:body>
</office:document-content>
"""

VISIBILITY_CASCADE_CONTENT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
	xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
	xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
	xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
	xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0">
	<office:automatic-styles><style:style style:name="child" style:family="drawing-page" style:parent-style-name="hidden-parent"/></office:automatic-styles>
	<office:body><office:presentation>
		<draw:page draw:name="inherited-hidden" draw:style-name="child"/>
		<draw:page draw:name="page-visible" draw:style-name="child" presentation:visibility="visible"/>
		<draw:page draw:name="page-hidden" presentation:visibility="hidden"/>
	</office:presentation></office:body>
</office:document-content>
"""

NAMED_HIDDEN_STYLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles
	xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
	xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
	xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0">
	<office:styles><style:style style:name="hidden-parent" style:family="drawing-page"><style:drawing-page-properties presentation:visibility="hidden"/></style:style></office:styles>
</office:document-styles>
"""

CYCLE_STYLE_CONTENT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
	xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
	xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
	xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0">
	<office:automatic-styles>
		<style:style style:name="first" style:family="drawing-page" style:parent-style-name="second"/>
		<style:style style:name="second" style:family="drawing-page" style:parent-style-name="first"/>
	</office:automatic-styles>
	<office:body><office:presentation><draw:page draw:name="cycle" draw:style-name="first"/></office:presentation></office:body>
</office:document-content>
"""

CONTENT_OVERRIDE_STYLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles
	xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
	xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
	xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0">
	<office:styles><style:style style:name="conflict" style:family="drawing-page"><style:drawing-page-properties presentation:visibility="hidden"/></style:style></office:styles>
</office:document-styles>
"""

CONTENT_OVERRIDE_CONTENT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
	xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
	xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
	xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
	xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0">
	<office:automatic-styles><style:style style:name="conflict" style:family="drawing-page"><style:drawing-page-properties presentation:visibility="visible"/></style:style></office:automatic-styles>
	<office:body><office:presentation><draw:page draw:name="content-wins" draw:style-name="conflict"/></office:presentation></office:body>
</office:document-content>
"""


#============================================
def write_minimal_odp(output_path: pathlib.Path) -> pathlib.Path:
	"""Write a one-slide ODP input entirely inside tmp_path."""
	with zipfile.ZipFile(output_path, "w") as archive:
		archive.writestr("mimetype", odp_to_marp.ODP_MIMETYPE)
		archive.writestr("content.xml", MINIMAL_CONTENT_XML)
	return output_path


#============================================
def test_minimal_odp_converts_to_first_marp_slide(tmp_path: pathlib.Path) -> None:
	"""A simple title slide becomes the first Marp slide without a blank page."""
	input_path = write_minimal_odp(tmp_path / "lecture.odp")
	output_path = tmp_path / "lecture.md"

	summary = odp_to_marp.convert_odp(input_path, output_path)
	markdown_text = output_path.read_text(encoding="utf-8")

	assert summary.editable_slides == 1
	assert "---\n\n<!-- _class: lead -->\n<!-- _paginate: false -->\n# Genetics &amp; inheritance" in markdown_text


#============================================
def test_unsafe_archive_member_path_is_rejected(tmp_path: pathlib.Path) -> None:
	"""Archive traversal paths fail before any extraction or XML processing."""
	input_path = tmp_path / "unsafe.odp"
	with zipfile.ZipFile(input_path, "w") as archive:
		archive.writestr("mimetype", odp_to_marp.ODP_MIMETYPE)
		archive.writestr("content.xml", MINIMAL_CONTENT_XML)
		archive.writestr("../outside.png", b"not an image")

	with pytest.raises(ValueError, match="unsafe archive member path"):
		odp_to_marp.validate_odp(input_path)


#============================================
def test_presenter_note_comment_text_remains_safe() -> None:
	"""Source text cannot terminate the generated HTML comment early."""
	encoded_text = odp_to_marp.comment_text("A -- B \u2192 C")

	assert encoded_text == "A - - B &#8594; C"


#============================================
def test_drawing_page_style_hides_a_slide(tmp_path: pathlib.Path) -> None:
	"""Automatic drawing-page styles determine hidden ODP slides."""
	input_path = tmp_path / "hidden.odp"
	with zipfile.ZipFile(input_path, "w") as archive:
		archive.writestr("mimetype", odp_to_marp.ODP_MIMETYPE)
		archive.writestr("content.xml", HIDDEN_STYLE_CONTENT_XML)

	slides = odp_to_marp.read_slides(input_path)

	assert [slide.hidden for slide in slides] == [False, True]


#============================================
def test_page_visibility_overrides_inherited_named_style(tmp_path: pathlib.Path) -> None:
	"""A page setting wins over automatic and named drawing-page styles."""
	input_path = tmp_path / "cascade.odp"
	with zipfile.ZipFile(input_path, "w") as archive:
		archive.writestr("mimetype", odp_to_marp.ODP_MIMETYPE)
		archive.writestr("content.xml", VISIBILITY_CASCADE_CONTENT_XML)
		archive.writestr("styles.xml", NAMED_HIDDEN_STYLE_XML)

	slides = odp_to_marp.read_slides(input_path)

	assert [slide.hidden for slide in slides] == [True, False, True]


#============================================
def test_style_inheritance_cycle_is_rejected(tmp_path: pathlib.Path) -> None:
	"""Malformed visibility inheritance fails rather than guessing slide state."""
	input_path = tmp_path / "cycle.odp"
	with zipfile.ZipFile(input_path, "w") as archive:
		archive.writestr("mimetype", odp_to_marp.ODP_MIMETYPE)
		archive.writestr("content.xml", CYCLE_STYLE_CONTENT_XML)

	with pytest.raises(ValueError, match="inheritance contains a cycle"):
		odp_to_marp.read_slides(input_path)


#============================================
def test_content_style_definition_overrides_same_named_style_xml(tmp_path: pathlib.Path) -> None:
	"""A local automatic style wins when it redefines a named style identity."""
	input_path = tmp_path / "override.odp"
	with zipfile.ZipFile(input_path, "w") as archive:
		archive.writestr("mimetype", odp_to_marp.ODP_MIMETYPE)
		archive.writestr("content.xml", CONTENT_OVERRIDE_CONTENT_XML)
		archive.writestr("styles.xml", CONTENT_OVERRIDE_STYLE_XML)

	slides = odp_to_marp.read_slides(input_path)

	assert [slide.hidden for slide in slides] == [False]


#============================================
@pytest.mark.parametrize(
	("content_xml", "error_message"),
	[
		(
			MINIMAL_CONTENT_XML.replace(
				'draw:name="page1"',
				'draw:name="page1" presentation:visibility="invalid"',
			),
			"drawing page has an invalid",
		),
		(
			HIDDEN_STYLE_CONTENT_XML.replace(
				'presentation:visibility="hidden"',
				'presentation:visibility="invalid"',
			),
			"drawing-page style has an invalid",
		),
	],
)
def test_invalid_visibility_values_are_rejected(
	tmp_path: pathlib.Path,
	content_xml: str,
	error_message: str,
) -> None:
	"""Unknown visibility values never become an arbitrary visible state."""
	input_path = tmp_path / "invalid-visibility.odp"
	with zipfile.ZipFile(input_path, "w") as archive:
		archive.writestr("mimetype", odp_to_marp.ODP_MIMETYPE)
		archive.writestr("content.xml", content_xml)

	with pytest.raises(ValueError, match=error_message):
		odp_to_marp.read_slides(input_path)


#============================================
def test_malformed_optional_styles_xml_is_rejected(tmp_path: pathlib.Path) -> None:
	"""An optional styles.xml is validated when present rather than ignored."""
	input_path = write_minimal_odp(tmp_path / "malformed-styles.odp")
	with zipfile.ZipFile(input_path, "a") as archive:
		archive.writestr("styles.xml", b"<office:document-styles")

	with pytest.raises(xml.etree.ElementTree.ParseError):
		odp_to_marp.read_slides(input_path)


#============================================
def test_rendered_page_mapping_accepts_visible_or_all_source_pages() -> None:
	"""Fallback images retain their source-slide identity across renderers."""
	rendered_pages = [pathlib.Path(f"slide-{index}.png") for index in range(1, 5)]
	all_pages = odp_to_marp.map_rendered_pages(
		rendered_pages,
		4,
		[1, 3, 4],
	)
	visible_pages = odp_to_marp.map_rendered_pages(
		[rendered_pages[0], rendered_pages[2], rendered_pages[3]],
		4,
		[1, 3, 4],
	)

	assert all_pages[3] == pathlib.Path("slide-3.png")
	assert visible_pages[3] == pathlib.Path("slide-3.png")


#============================================
def test_rendered_page_mapping_rejects_ambiguous_count() -> None:
	"""Unexpected page counts cannot silently attach the wrong fallback image."""
	with pytest.raises(RuntimeError, match="page count"):
		odp_to_marp.map_rendered_pages(
			[pathlib.Path("slide-1.png"), pathlib.Path("slide-2.png")],
			4,
			[1, 3, 4],
		)


#============================================
def test_importer_refuses_existing_markdown_or_asset_directory(tmp_path: pathlib.Path) -> None:
	"""The one-time importer protects both established canonical destinations."""
	input_path = write_minimal_odp(tmp_path / "lecture.odp")
	markdown_path = tmp_path / "lecture.md"
	markdown_path.write_text("existing", encoding="utf-8")
	with pytest.raises(FileExistsError, match="Markdown already exists"):
		odp_to_marp.convert_odp(input_path, markdown_path)

	markdown_path.unlink()
	asset_path = tmp_path / "assets" / "lecture"
	asset_path.mkdir(parents=True)
	with pytest.raises(FileExistsError, match="asset directory already exists"):
		odp_to_marp.convert_odp(input_path, markdown_path)


#============================================
def test_supported_image_is_extracted_to_canonical_asset_path(tmp_path: pathlib.Path) -> None:
	"""A valid embedded PNG is copied under the Markdown asset directory."""
	input_path = tmp_path / "image.odp"
	with zipfile.ZipFile(input_path, "w") as archive:
		archive.writestr("mimetype", odp_to_marp.ODP_MIMETYPE)
		archive.writestr("content.xml", IMAGE_CONTENT_XML)
		archive.writestr("Pictures/example.png", b"\x89PNG\r\n\x1a\nimage-data")
	output_path = tmp_path / "image.md"

	summary = odp_to_marp.convert_odp(input_path, output_path)

	assert summary.extracted_images == 1
	assert (tmp_path / "assets" / "image" / "image_001.png").read_bytes().startswith(b"\x89PNG")
