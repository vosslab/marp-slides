"""Behavior tests for the format-neutral presentation application CLI."""

# Standard Library
import pathlib

# PIP3 Modules
import pytest

# Local Modules
import slide_lib.cli
import slide_lib.terminal_output
import slide_lib.importers.odp_to_djot
import slide_lib.importers.odp_to_marp
import slide_lib.importers.pptx_to_djot
import slide_lib.importers.pptx_to_marp


#============================================
def test_import_command_dispatches_source_target_and_output(monkeypatch: pytest.MonkeyPatch,
		tmp_path: pathlib.Path) -> None:
	"""Parsed import arguments select and reach the matching reusable operation."""
	received: list[tuple[str, pathlib.Path, pathlib.Path | None]] = []
	def record(importer_name: str) -> slide_lib.cli.ImportOperation:
		def run_import(input_file: pathlib.Path, output_file: pathlib.Path | None) -> None:
			received.append((importer_name, input_file, output_file))
		return run_import
	monkeypatch.setattr(slide_lib.importers.odp_to_djot, "run_import", record("odp-djot"))
	monkeypatch.setattr(slide_lib.importers.pptx_to_djot, "run_import", record("pptx-djot"))
	monkeypatch.setattr(slide_lib.importers.odp_to_marp, "run_import", record("odp-marp"))
	monkeypatch.setattr(slide_lib.importers.pptx_to_marp, "run_import", record("pptx-marp"))

	odp_path = tmp_path / "lecture.odp"
	pptx_path = tmp_path / "lecture.pptx"
	djot_path = tmp_path / "lecture.djot"
	marp_path = tmp_path / "lecture.md"
	statuses = (
		slide_lib.cli.main(["import", str(odp_path), "--output", str(djot_path)]),
		slide_lib.cli.main(["import", str(pptx_path)]),
		slide_lib.cli.main(["import", str(odp_path), "--to", "marp"]),
		slide_lib.cli.main(["import", str(pptx_path), "-t", "marp", "-o", str(marp_path)]),
	)
	assert statuses == (0, 0, 0, 0)
	assert received == [
		("odp-djot", odp_path, djot_path),
		("pptx-djot", pptx_path, None),
		("odp-marp", odp_path, None),
		("pptx-marp", pptx_path, marp_path),
	]


#============================================
def test_build_command_dispatches_path_and_format(monkeypatch: pytest.MonkeyPatch,
		tmp_path: pathlib.Path) -> None:
	"""Parsed build arguments reach the existing application build operation."""
	deck_path = tmp_path / "lecture.djot"
	deck_path.write_text("=== layout: blank\n", encoding="utf-8")
	received: list[tuple[str, str]] = []
	def record(input_value: str, output_format: str) -> int:
		received.append((input_value, output_format))
		return 0
	monkeypatch.setattr(slide_lib.terminal_output, "run_build", record)
	status = slide_lib.cli.main(["build", str(deck_path), "-f", "odp"])
	assert received == [(str(deck_path), "odp")]
	assert status == 0
