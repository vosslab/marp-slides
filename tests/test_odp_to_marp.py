"""Behavioral tests for the one-time ODP-to-Marp importer."""

# Standard Library
import pathlib
import xml.etree.ElementTree
import zipfile

# PIP3 modules
import pytest

# local repo modules
from tools import odp_to_marp
from tools import pptx_to_marp


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
def test_minimal_odp_uses_temporary_pptx_contract(
	tmp_path: pathlib.Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""The ODP wrapper passes source visibility to the structured PPTX importer."""
	input_path = write_minimal_odp(tmp_path / "lecture.odp")
	output_path = tmp_path / "lecture.md"
	normalized_path = tmp_path / "normalized.pptx"
	received: dict[str, object] = {}

	def fake_normalize(_input_path: pathlib.Path, _temporary_root: pathlib.Path) -> pathlib.Path:
		normalized_path.write_bytes(b"temporary PPTX")
		return normalized_path

	def fake_convert(
		pptx_path: pathlib.Path,
		markdown_path: pathlib.Path,
		**kwargs: object,
	) -> pptx_to_marp.ConversionSummary:
		received.update(kwargs)
		markdown_path.write_text("# Genetics & inheritance\n", encoding="utf-8")
		report_path = tmp_path / "import_report.json"
		report_path.write_text("{}\n", encoding="utf-8")
		return pptx_to_marp.ConversionSummary(1, 1, 0, 0, 0, markdown_path, report_path)

	monkeypatch.setattr(odp_to_marp, "convert_odp_to_pptx", fake_normalize)
	monkeypatch.setattr(odp_to_marp.pptx_to_marp, "convert_pptx", fake_convert)

	summary = odp_to_marp.convert_odp(input_path, output_path)

	assert summary.editable_slides == 1
	assert received["expected_slide_count"] == 1
	assert received["expected_hidden"] == set()
	assert received["source_name"] == "lecture.odp"


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
def test_wrapper_passes_hidden_source_indexes(
	tmp_path: pathlib.Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""Original ODP visibility remains authoritative after PPTX normalization."""
	input_path = tmp_path / "hidden.odp"
	with zipfile.ZipFile(input_path, "w") as archive:
		archive.writestr("mimetype", odp_to_marp.ODP_MIMETYPE)
		archive.writestr("content.xml", HIDDEN_STYLE_CONTENT_XML)
	output_path = tmp_path / "hidden.md"
	received: dict[str, object] = {}

	def fake_normalize(_input_path: pathlib.Path, _temporary_root: pathlib.Path) -> pathlib.Path:
		return tmp_path / "hidden.pptx"

	def fake_convert(
		_pptx_path: pathlib.Path,
		markdown_path: pathlib.Path,
		**kwargs: object,
	) -> pptx_to_marp.ConversionSummary:
		received.update(kwargs)
		return pptx_to_marp.ConversionSummary(
			1,
			1,
			1,
			0,
			0,
			markdown_path,
			tmp_path / "report.json",
		)

	monkeypatch.setattr(odp_to_marp, "convert_odp_to_pptx", fake_normalize)
	monkeypatch.setattr(odp_to_marp.pptx_to_marp, "convert_pptx", fake_convert)

	summary = odp_to_marp.convert_odp(input_path, output_path)

	assert summary.hidden_slides == 1
	assert received["expected_slide_count"] == 2
	assert received["expected_hidden"] == {2}
