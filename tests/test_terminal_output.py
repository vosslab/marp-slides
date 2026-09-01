"""Semantic tests for concise presentation-build terminal output."""

# Standard Library
import io
import pathlib
from unittest import mock

# PIP3 Modules
import pytest
import rich.console

# Local Modules
import marp_lib.terminal_output


HEADER = "---\nmarp: true\ntheme: genetics\nsize: 16:10\n---\n"


#============================================
def test_single_format_summary_is_relative_and_ansi_free(tmp_path: pathlib.Path) -> None:
	"""A redirected single-format summary stays concise, relative, and static."""
	deck_path = tmp_path / "deck.md"
	deck_path.write_text(HEADER, encoding="utf-8")
	output_path = tmp_path / "output" / "pptx" / "deck.pptx"
	output_path.parent.mkdir(parents=True)
	output_path.write_bytes(b"pptx")
	stdout_stream = io.StringIO()
	stderr_stream = io.StringIO()
	stdout = rich.console.Console(file=stdout_stream, force_terminal=False, color_system=None, width=100)
	stderr = rich.console.Console(file=stderr_stream, force_terminal=False, color_system=None, width=100)
	with mock.patch.object(marp_lib.terminal_output.marp_lib.native_export, "find_repo_root",
		return_value=tmp_path), mock.patch.object(
		marp_lib.terminal_output.marp_lib.native_export, "export_deck",
		return_value={"pptx": output_path}):
		status = marp_lib.terminal_output.run_build(str(deck_path), "pptx", allow_folder=False,
			output_console=stdout, error_console=stderr)
	text = stdout_stream.getvalue()
	assert status == 0 and "PPTX" in text and "ODP" not in text and "PDF" not in text
	assert str(tmp_path) not in text and "\x1b" not in text and stderr_stream.getvalue() == ""


#============================================
def test_expected_parse_failure_is_concise_relative_stderr(tmp_path: pathlib.Path) -> None:
	"""Expected parse failures return nonzero with deck, stage, reason, and completed count."""
	deck_path = tmp_path / "broken.md"
	deck_path.write_text("---\nmarp: true\n---\n", encoding="utf-8")
	stdout_stream = io.StringIO()
	stderr_stream = io.StringIO()
	stdout = rich.console.Console(file=stdout_stream, force_terminal=False, color_system=None, width=120)
	stderr = rich.console.Console(file=stderr_stream, force_terminal=False, color_system=None, width=120)
	with mock.patch.object(marp_lib.terminal_output.marp_lib.native_export, "find_repo_root",
		return_value=tmp_path):
		status = marp_lib.terminal_output.run_build(str(deck_path), "pptx", allow_folder=False,
			output_console=stdout, error_console=stderr)
	text = stderr_stream.getvalue()
	required = ("Build failed", "broken.md", "parsing", "front matter", "Completed decks", "0")
	assert status == 1 and all(value in text for value in required)
	assert str(tmp_path) not in text and "Done:" not in stdout_stream.getvalue()


#============================================
def test_unexpected_export_defect_retains_exception(tmp_path: pathlib.Path) -> None:
	"""Unexpected defects escape the expected-error interface for a normal traceback."""
	deck_path = tmp_path / "deck.md"
	deck_path.write_text(HEADER, encoding="utf-8")
	console = rich.console.Console(file=io.StringIO(), force_terminal=False, color_system=None)
	with mock.patch.object(marp_lib.terminal_output.marp_lib.native_export, "find_repo_root",
		return_value=tmp_path), mock.patch.object(
		marp_lib.terminal_output.marp_lib.native_export, "export_deck",
		side_effect=ValueError("unexpected defect")):
		with pytest.raises(ValueError, match="unexpected defect"):
			marp_lib.terminal_output.run_build(str(deck_path), "pptx",
				output_console=console, error_console=console)
