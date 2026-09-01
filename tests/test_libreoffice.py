"""Focused tests for the shared LibreOffice batch-conversion contract."""

# Standard Library
import pathlib
import subprocess
from unittest import mock

# PIP3 modules
import pytest

# Local Modules
from marp_lib import libreoffice


#============================================
def test_convert_file_uses_headless_norestore_and_established_profile(
		tmp_path: pathlib.Path) -> None:
	"""Normal conversion uses batch flags without a disposable user profile."""
	input_path = tmp_path / "deck.odp"
	input_path.write_bytes(b"source")
	output_dir = tmp_path / "converted"
	output_dir.mkdir()
	commands: list[list[str]] = []

	def write_converted_file(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
		"""Create the output that the mocked LibreOffice command represents."""
		commands.append(command)
		(output_dir / "deck.pdf").write_bytes(b"pdf")
		return subprocess.CompletedProcess(command, 0)

	with mock.patch.object(libreoffice, "require_libreoffice_closed"), \
		mock.patch.object(libreoffice, "require_soffice", return_value=pathlib.Path("/usr/bin/soffice")), \
		mock.patch.object(libreoffice.subprocess, "run", side_effect=write_converted_file):
		converted_path = libreoffice.convert_file(input_path, output_dir, "pdf")

	assert converted_path == output_dir / "deck.pdf"
	assert "--headless" in commands[0]
	assert "--norestore" in commands[0]
	assert all(not value.startswith("-env:UserInstallation=") for value in commands[0])


#============================================
def test_require_libreoffice_closed_rejects_desktop_process() -> None:
	"""A running main LibreOffice process receives an actionable batch-build error."""
	processes = "/Applications/LibreOffice.app/Contents/MacOS/soffice.bin --writer\n"
	result = subprocess.CompletedProcess(["ps"], 0, stdout=processes)
	with mock.patch.object(libreoffice.subprocess, "run", return_value=result):
		with pytest.raises(RuntimeError, match="LibreOffice is running; close it"):
			libreoffice.require_libreoffice_closed()


#============================================
def test_require_libreoffice_closed_ignores_quicklook_extension() -> None:
	"""The LibreOffice Quick Look extension does not block presentation builds."""
	processes = "/Applications/LibreOffice.app/Contents/PlugIns/QuickLookThumbnail.appex/helper\n"
	result = subprocess.CompletedProcess(["ps"], 0, stdout=processes)
	with mock.patch.object(libreoffice.subprocess, "run", return_value=result):
		libreoffice.require_libreoffice_closed()
