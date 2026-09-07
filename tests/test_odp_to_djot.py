"""Behavioral test for the ODP-to-extended-Djot import boundary."""

# Standard Library
import pathlib
import zipfile

# PIP3 modules
import pytest

# Local modules
import marp_lib.importers.odp_to_djot as odp_to_djot
import marp_lib.importers.odp_to_marp as odp_to_marp
import marp_lib.importers.pptx_to_djot as pptx_to_djot


MINIMAL_CONTENT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
	xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
	xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
	xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">
	<office:body><office:presentation><draw:page draw:name="page1">
		<draw:frame><draw:text-box><text:p>Genetics</text:p></draw:text-box></draw:frame>
	</draw:page></office:presentation></office:body>
</office:document-content>
"""


#============================================
def test_minimal_odp_preserves_visibility_contract_for_djot(
	tmp_path: pathlib.Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""The Djot wrapper passes ODP source identity and visibility to its importer."""
	input_path = tmp_path / "lecture.odp"
	with zipfile.ZipFile(input_path, "w") as archive:
		archive.writestr("mimetype", odp_to_marp.ODP_MIMETYPE)
		archive.writestr("content.xml", MINIMAL_CONTENT_XML)
	output_path = tmp_path / "lecture.djot"
	normalized_path = tmp_path / "normalized.pptx"
	received: dict[str, object] = {}

	def fake_normalize(_input_path: pathlib.Path, _temporary_root: pathlib.Path) -> pathlib.Path:
		normalized_path.write_bytes(b"temporary PPTX")
		return normalized_path

	def fake_convert(
		pptx_path: pathlib.Path,
		djot_path: pathlib.Path,
		**kwargs: object,
	) -> pptx_to_djot.ConversionSummary:
		assert pptx_path == normalized_path
		received.update(kwargs)
		djot_path.write_text("=== layout: title-only\n", encoding="utf-8")
		report_path = tmp_path / "import_report.json"
		report_path.write_text("{}\n", encoding="utf-8")
		return pptx_to_djot.ConversionSummary(1, 1, 0, 0, 0, djot_path, report_path)

	monkeypatch.setattr(odp_to_marp, "convert_odp_to_pptx", fake_normalize)
	monkeypatch.setattr(odp_to_djot.pptx_to_djot, "convert_pptx", fake_convert)

	summary = odp_to_djot.convert_odp(input_path, output_path)

	assert summary.editable_slides == 1
	assert received["expected_slide_count"] == 1
	assert received["expected_hidden"] == set()
	assert received["source_name"] == "lecture.odp"
	assert received["render_source_path"] == input_path.resolve()
