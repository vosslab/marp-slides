#!/usr/bin/env python3
"""Render trusted repository Marp Markdown into presentation files."""

# Standard Library
import os
import re
import shutil
import pathlib
import tempfile
import argparse
import subprocess


MINIMUM_MARP_VERSION = (4, 5, 0)
BROWSER_CANDIDATES = (
	pathlib.Path("/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"),
	pathlib.Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
	pathlib.Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
	pathlib.Path("/Applications/Vivaldi.app/Contents/MacOS/Vivaldi"),
)
SOURCE_FALLBACK_PATTERNS = (
	re.compile(r"\bslide_\d+_source\.(?:png|jpe?g|webp)\b", re.IGNORECASE),
	re.compile(r"_class\s*:\s*source-fallback\b", re.IGNORECASE),
)


#============================================
def find_repo_root() -> pathlib.Path:
	"""Return the current Git repository root."""
	result = subprocess.run(
		["git", "rev-parse", "--show-toplevel"],
		check=True,
		capture_output=True,
		text=True,
	)
	repo_root = pathlib.Path(result.stdout.strip()).resolve()
	return repo_root


#============================================
def validate_input(input_value: str, repo_root: pathlib.Path) -> pathlib.Path:
	"""Resolve and validate one trusted repository Markdown input.

	Args:
		input_value: User-supplied Markdown path.
		repo_root: Trusted repository boundary.

	Returns:
		Resolved Markdown path inside the repository.

	Raises:
		ValueError: The input is missing, outside the repository, or not Markdown.
	"""
	input_path = pathlib.Path(input_value).expanduser().resolve()
	# ASVS 2.2.1 and 5.3.2: constrain file input to a real repository-owned Markdown path.
	if not input_path.is_file():
		raise ValueError(f"input is not a file: {input_value}")
	if not input_path.is_relative_to(repo_root):
		raise ValueError("input must be inside this repository")
	if input_path.suffix != ".md":
		raise ValueError("input must use the .md extension")
	markdown = input_path.read_text(encoding="utf-8")
	# ASVS 5.2.2: reject the retired full-slide fallback representation at the boundary.
	if any(pattern.search(markdown) for pattern in SOURCE_FALLBACK_PATTERNS):
		raise ValueError(
			"full-slide source images are failed conversions and cannot be exported",
		)
	return input_path


#============================================
def require_executable(command: str, install_message: str) -> pathlib.Path:
	"""Resolve one required executable from PATH.

	Args:
		command: Executable name.
		install_message: Error message when the executable is unavailable.

	Returns:
		Resolved executable path.

	Raises:
		RuntimeError: The command is unavailable.
	"""
	command_value = shutil.which(command)
	if command_value is None:
		raise RuntimeError(install_message)
	command_path = pathlib.Path(command_value).resolve()
	return command_path


#============================================
def require_marp() -> pathlib.Path:
	"""Return a supported Marp executable path.

	Raises:
		RuntimeError: Marp is missing, unreadable, or older than 4.5.0.
	"""
	marp_path = require_executable("marp", "Marp is not installed; run brew bundle")
	# ASVS 1.2.5: the executable and flags remain distinct subprocess arguments.
	result = subprocess.run(
		[str(marp_path), "--version"],
		check=True,
		capture_output=True,
		text=True,
	)
	version_match = re.search(r"\bv?(\d+)\.(\d+)\.(\d+)\b", result.stdout)
	if version_match is None:
		raise RuntimeError(f"unable to read Marp version: {result.stdout.strip()}")
	version = tuple(int(part) for part in version_match.groups())
	if version < MINIMUM_MARP_VERSION:
		version_text = ".".join(str(part) for part in version)
		raise RuntimeError(f"Marp 4.5.0 or newer is required; found {version_text}")
	return marp_path


#============================================
def find_browser() -> pathlib.Path:
	"""Return an installed Chromium-compatible browser path.

	Raises:
		RuntimeError: No supported browser is available.
	"""
	for candidate in BROWSER_CANDIDATES:
		if candidate.is_file() and os.access(candidate, os.X_OK):
			return candidate
	for command in ("chromium", "google-chrome", "brave-browser"):
		command_value = shutil.which(command)
		if command_value is not None:
			browser_path = pathlib.Path(command_value).resolve()
			return browser_path
	raise RuntimeError("no installed Chromium-compatible browser was found")


#============================================
def common_marp_args(
	marp_path: pathlib.Path,
	browser_path: pathlib.Path,
	repo_root: pathlib.Path,
) -> list[str]:
	"""Build the trusted local Marp command prefix.

	Args:
		marp_path: Supported Marp executable.
		browser_path: Chromium-compatible browser executable.
		repo_root: Repository containing the central themes directory.

	Returns:
		Parameterized Marp command prefix.
	"""
	theme_path = repo_root / "themes/genetics.css"
	if not theme_path.is_file():
		raise RuntimeError("missing Marp theme: themes/genetics.css")
	# Local-file access is limited to validated, repository-owned Markdown and assets.
	command = [
		str(marp_path),
		"--allow-local-files",
		"--browser",
		"chrome",
		"--browser-path",
		str(browser_path),
		"--no-parallel",
		"--theme-set",
		str(repo_root / "themes"),
	]
	return command


#============================================
def render_pdf(
	command: list[str],
	input_path: pathlib.Path,
	output_path: pathlib.Path,
) -> None:
	"""Render one Marp Markdown deck as a PDF with notes.

	Args:
		command: Parameterized Marp command prefix.
		input_path: Validated Markdown source.
		output_path: Internally generated PDF destination.
	"""
	output_path.parent.mkdir(parents=True, exist_ok=True)
	# ASVS 1.2.5: no user-controlled value is interpolated into a shell command.
	subprocess.run(
		[*command, "--pdf", "--pdf-notes", str(input_path), "--output", str(output_path)],
		check=True,
	)


#============================================
def render_pptx(
	command: list[str],
	input_path: pathlib.Path,
	output_path: pathlib.Path,
) -> None:
	"""Render one Marp Markdown deck as a PPTX.

	Args:
		command: Parameterized Marp command prefix.
		input_path: Validated Markdown source.
		output_path: Internally generated PPTX destination.
	"""
	output_path.parent.mkdir(parents=True, exist_ok=True)
	# ASVS 1.2.5: no user-controlled value is interpolated into a shell command.
	subprocess.run(
		[*command, "--pptx", str(input_path), "--output", str(output_path)],
		check=True,
	)


#============================================
def convert_pptx_to_odp(
	pptx_path: pathlib.Path,
	odp_path: pathlib.Path,
	repo_root: pathlib.Path,
) -> None:
	"""Convert one generated PPTX into an ODP using LibreOffice.

	Args:
		pptx_path: Generated PPTX interchange file.
		odp_path: Internally generated ODP destination.
		repo_root: Repository containing the output directory.

	Raises:
		RuntimeError: LibreOffice is unavailable or creates no ODP.
	"""
	soffice_path = require_executable(
		"soffice",
		"LibreOffice is not installed; run brew bundle",
	)
	output_root = repo_root / "output"
	output_root.mkdir(parents=True, exist_ok=True)
	odp_path.parent.mkdir(parents=True, exist_ok=True)
	with tempfile.TemporaryDirectory(prefix=".libreoffice.", dir=output_root) as temporary_value:
		temporary_root = pathlib.Path(temporary_value)
		profile_path = temporary_root / "profile"
		conversion_path = temporary_root / "converted"
		conversion_path.mkdir()
		# ASVS 1.2.5 and 5.3.2: paths are internal and passed as distinct arguments.
		subprocess.run(
			[
				str(soffice_path),
				f"-env:UserInstallation={profile_path.as_uri()}",
				"--headless",
				"--convert-to",
				"odp",
				"--outdir",
				str(conversion_path),
				str(pptx_path),
			],
			check=True,
		)
		converted_path = conversion_path / f"{pptx_path.stem}.odp"
		if not converted_path.is_file():
			raise RuntimeError("LibreOffice did not create the expected ODP output")
		os.replace(converted_path, odp_path)


#============================================
def export_deck(input_value: str, output_format: str) -> dict[str, pathlib.Path]:
	"""Export one trusted Marp Markdown deck.

	Args:
		input_value: User-supplied repository Markdown path.
		output_format: One of all, odp, pdf, or pptx.

	Returns:
		Generated artifact paths keyed by format.

	Raises:
		ValueError: The requested output format is unsupported.
	"""
	allowed_formats = ("all", "odp", "pdf", "pptx")
	if output_format not in allowed_formats:
		raise ValueError(f"unsupported output format: {output_format}")
	repo_root = find_repo_root()
	input_path = validate_input(input_value, repo_root)
	marp_path = require_marp()
	browser_path = find_browser()
	command = common_marp_args(marp_path, browser_path, repo_root)
	deck_name = input_path.stem
	outputs = {
		"pdf": repo_root / f"output/pdf/{deck_name}.pdf",
		"pptx": repo_root / f"output/pptx/{deck_name}.pptx",
		"odp": repo_root / f"output/odp/{deck_name}.odp",
	}
	generated: dict[str, pathlib.Path] = {}
	if output_format in ("all", "pdf"):
		render_pdf(command, input_path, outputs["pdf"])
		generated["pdf"] = outputs["pdf"]
	if output_format in ("all", "pptx", "odp"):
		render_pptx(command, input_path, outputs["pptx"])
		generated["pptx"] = outputs["pptx"]
	if output_format in ("all", "odp"):
		convert_pptx_to_odp(outputs["pptx"], outputs["odp"], repo_root)
		generated["odp"] = outputs["odp"]
	return generated


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments."""
	parser = argparse.ArgumentParser(
		description="Export trusted repository Marp Markdown into presentation files.",
	)
	parser.add_argument("input_file", help="repository Markdown deck")
	parser.add_argument(
		"-f",
		"--format",
		dest="output_format",
		choices=("all", "odp", "pdf", "pptx"),
		default="all",
		help="output format (default: all)",
	)
	args = parser.parse_args()
	return args


#============================================
def print_outputs(outputs: dict[str, pathlib.Path]) -> None:
	"""Print generated artifact paths in classroom workflow order.

	Args:
		outputs: Generated artifact paths keyed by format.
	"""
	for output_format in ("pdf", "pptx", "odp"):
		if output_format in outputs:
			print(f"{output_format.upper()}: {outputs[output_format]}")


#============================================
def main() -> None:
	"""Run the Marp export command."""
	args = parse_args()
	outputs = export_deck(args.input_file, args.output_format)
	print_outputs(outputs)


if __name__ == "__main__":
	main()
