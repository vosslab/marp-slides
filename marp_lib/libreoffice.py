"""Run LibreOffice presentation conversions through one batch contract."""

# Standard Library
import pathlib
import shutil
import subprocess


SOFFICE_CANDIDATES = (
	pathlib.Path("/Applications/LibreOffice.app/Contents/MacOS/soffice"),
	pathlib.Path("/Applications/LibreOffice-Still.app/Contents/MacOS/soffice"),
)
SOFFICE_PROCESS_MARKER = ".app/Contents/MacOS/soffice"
IMPRESS_PDF_EXPORT = (
	'pdf:impress_pdf_Export:{'
	'"Quality":{"type":"long","value":"70"},'
	'"ReduceImageResolution":{"type":"boolean","value":"true"},'
	'"MaxImageResolution":{"type":"long","value":"150"},'
	'"SelectPdfVersion":{"type":"long","value":"3"}'
	'}'
)


#============================================
def require_soffice() -> pathlib.Path:
	"""Resolve the LibreOffice command used for local conversion."""
	command_value = shutil.which("soffice")
	if command_value is not None:
		return pathlib.Path(command_value).resolve()
	for candidate in SOFFICE_CANDIDATES:
		if candidate.is_file():
			return candidate
	raise RuntimeError("LibreOffice is not installed; run brew bundle")


#============================================
def require_libreoffice_closed() -> None:
	"""Require the desktop LibreOffice process to be closed before batch conversion."""
	result = subprocess.run(
		["ps", "-axo", "command="],
		check=True,
		capture_output=True,
		text=True,
	)
	for command in result.stdout.splitlines():
		if SOFFICE_PROCESS_MARKER in command:
			raise RuntimeError("LibreOffice is running; close it before building presentations")


#============================================
def convert_file(input_path: pathlib.Path, output_dir: pathlib.Path, output_format: str,
		timeout_seconds: int = 180) -> pathlib.Path:
	"""Convert one presentation using LibreOffice's established user profile."""
	require_libreoffice_closed()
	soffice_path = require_soffice()
	conversion_target = IMPRESS_PDF_EXPORT if output_format == "pdf" else output_format
	command = [
		str(soffice_path),
		"--headless",
		"--norestore",
		"--convert-to",
		conversion_target,
		"--outdir",
		str(output_dir),
		str(input_path),
	]
	# User paths remain separate subprocess arguments; no shell is used.
	subprocess.run(command, check=True, timeout=timeout_seconds)
	converted_path = output_dir / f"{input_path.stem}.{output_format}"
	if not converted_path.is_file():
		raise RuntimeError(
			f"LibreOffice did not create the expected {output_format.upper()} output"
		)
	return converted_path
