#!/usr/bin/env python3
"""Lint experimental extended-Djot slide structure without rendering slides."""

# Standard Library
import re
import sys
import shutil
import pathlib
import argparse
import subprocess
import dataclasses


LAYOUT_DIRECTIVE = re.compile(r"^=== layout: ([a-z][a-z0-9-]*)$")
SLOT_DIRECTIVE = re.compile(r"^@([a-z][a-z0-9-]*)$")
IMAGE_REFERENCE = re.compile(r"!\[[^]\n]*\]\(([^()\s]+)\)")
NEXT_ACTION = re.compile(r"^=> [a-z][a-z0-9-]*(?: [a-z][a-z0-9-]*)*$")
TERMINAL_ACTION = re.compile(r"^.* <= [a-z][a-z0-9-]*(?: [a-z][a-z0-9-]*)*$")
FENCE = re.compile(r"^`{3,}")
REQUIRED_SLOTS = {
	"gallery": frozenset({"gallery"}),
	"multiple-choice": frozenset({"question", "answer"}),
	"title-content": frozenset({"body"}),
	"two-panels": frozenset({"left", "right"}),
}


@dataclasses.dataclass(frozen=True)
class LintProblem:
	"""One deterministic source-located lint failure."""

	path: pathlib.Path
	line: int
	message: str


@dataclasses.dataclass(frozen=True)
class LintSummary:
	"""Aggregate source counts after a clean structural lint."""

	sources: int
	slides: int
	images: int


#============================================
def add_problem(
	problems: list[LintProblem],
	path: pathlib.Path,
	line: int,
	message: str,
) -> None:
	"""Record one problem without making lint execution fail-fast."""
	problems.append(LintProblem(path, line, message))


#============================================
def image_problem(path: pathlib.Path, line: int, image_path: str) -> str | None:
	"""Return a safe local-image reference failure, if any."""
	candidate = pathlib.PurePosixPath(image_path)
	if candidate.is_absolute() or ".." in candidate.parts:
		return "image path must be a local relative path without traversal"
	if not (path.parent / candidate).is_file():
		return f"image asset does not exist: {image_path}"
	return None


#============================================
def finalize_slide(
	path: pathlib.Path,
	line: int,
	layout: str | None,
	slots: dict[str, int],
	problems: list[LintProblem],
) -> None:
	"""Enforce only documented required-slot contracts for one finished slide."""
	if layout is None:
		return
	for slot_name in REQUIRED_SLOTS.get(layout, frozenset()):
		if slot_name not in slots:
			add_problem(
				problems,
				path,
				line,
				f"layout '{layout}' requires exactly one @{slot_name} slot",
			)


#============================================
def lint_source(path: pathlib.Path) -> tuple[list[LintProblem], int, int]:
	"""Lint one source file's extension structure and local image references."""
	problems: list[LintProblem] = []
	slide_count = 0
	image_count = 0
	current_layout: str | None = None
	slots: dict[str, int] = {}
	in_fence = False
	for line_number, source_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
		if FENCE.match(source_line):
			in_fence = not in_fence
			continue
		if in_fence:
			continue
		layout_match = LAYOUT_DIRECTIVE.match(source_line)
		if layout_match:
			finalize_slide(path, line_number, current_layout, slots, problems)
			current_layout = layout_match.group(1)
			slots = {}
			slide_count += 1
			continue
		if source_line.startswith("==="):
			add_problem(problems, path, line_number, "invalid slide declaration; use === layout: <name>")
			continue
		if current_layout is None and source_line.strip():
			add_problem(problems, path, line_number, "content appears before the first slide declaration")
		slot_match = SLOT_DIRECTIVE.match(source_line)
		if slot_match:
			slot_name = slot_match.group(1)
			if slot_name in slots:
				add_problem(problems, path, line_number, f"duplicate @{slot_name} slot")
			else:
				slots[slot_name] = line_number
		elif source_line.startswith("@"):
			add_problem(problems, path, line_number, "invalid slot declaration; use @<slot>")
		if "<=" in source_line and not TERMINAL_ACTION.match(source_line):
			add_problem(problems, path, line_number, "<= action must be an exact terminal suffix")
		if source_line.startswith("=>") and not NEXT_ACTION.match(source_line):
			add_problem(problems, path, line_number, "=> action must be a standalone prefix directive")
		for image_match in IMAGE_REFERENCE.finditer(source_line):
			image_count += 1
			failure = image_problem(path, line_number, image_match.group(1))
			if failure is not None:
				add_problem(problems, path, line_number, failure)
	if in_fence:
		add_problem(problems, path, line_number, "unclosed backtick fence")
	finalize_slide(path, line_number + 1, current_layout, slots, problems)
	if slide_count == 0:
		add_problem(problems, path, 1, "source contains no slide declaration")
	return problems, slide_count, image_count


#============================================
def djot_sources(paths: list[pathlib.Path]) -> list[pathlib.Path]:
	"""Resolve explicit source files and recursively supplied source folders."""
	sources: list[pathlib.Path] = []
	for path in paths:
		if path.is_file():
			if path.suffix != ".djot":
				raise ValueError(f"source must use the .djot suffix: {path}")
			sources.append(path)
			continue
		if path.is_dir():
			sources.extend(child for child in path.rglob("*.djot") if not child.is_symlink())
			continue
		raise ValueError(f"source path does not exist: {path}")
	return sorted(set(sources))


#============================================
def native_validator(
	source: pathlib.Path,
	executable: str,
	arguments: list[str],
) -> LintProblem | None:
	"""Run a user-pinned native Djot tool without invoking a shell."""
	resolved_executable = shutil.which(executable)
	if resolved_executable is None:
		return LintProblem(source, 1, f"native Djot executable was not found: {executable}")
	try:
		result = subprocess.run(
			[resolved_executable, *arguments, str(source)],
			check=False,
			capture_output=True,
			text=True,
			timeout=30,
		)
	except subprocess.TimeoutExpired:
		return LintProblem(source, 1, "native Djot validator timed out after 30 seconds")
	if result.returncode == 0:
		return None
	detail = (result.stderr or result.stdout).strip().replace("\n", " ")[:400]
	return LintProblem(source, 1, f"native Djot validator failed: {detail or result.returncode}")


#============================================
def lint_paths(
	paths: list[pathlib.Path],
	*,
	native_executable: str | None = None,
	native_arguments: list[str] | None = None,
) -> tuple[list[LintProblem], LintSummary]:
	"""Run a pinned native Djot validator first, then structural checks."""
	problems: list[LintProblem] = []
	slide_count = 0
	image_count = 0
	sources = djot_sources(paths)
	for source in sources:
		if native_executable is not None:
			native_problem = native_validator(source, native_executable, native_arguments or [])
			if native_problem is not None:
				problems.append(native_problem)
		source_problems, source_slides, source_images = lint_source(source)
		problems.extend(source_problems)
		slide_count += source_slides
		image_count += source_images
	return problems, LintSummary(len(sources), slide_count, image_count)


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse deterministic, source-only lint arguments."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("sources", nargs="+", type=pathlib.Path, help=".djot source or folder")
	parser.add_argument(
		"--native-executable",
		help="pinned Djot parser, formatter, or lint executable run once per source",
	)
	parser.add_argument(
		"--native-argument",
		action="append",
		default=[],
		help="one fixed argument to pass before the source path; may be repeated",
	)
	parser.add_argument(
		"--require-native",
		action="store_true",
		help="fail unless --native-executable names a pinned strict-Djot tool",
	)
	return parser.parse_args()


#============================================
def main() -> None:
	"""Print pyflakes-scale findings and return nonzero only for actual failures."""
	args = parse_args()
	if args.require_native and args.native_executable is None:
		print("error: --require-native needs --native-executable", file=sys.stderr)
		raise SystemExit(2)
	try:
		problems, summary = lint_paths(
			args.sources,
			native_executable=args.native_executable,
			native_arguments=args.native_argument,
		)
	except ValueError as error:
		print(f"error: {error}", file=sys.stderr)
		raise SystemExit(2) from error
	for problem in problems:
		print(f"{problem.path}:{problem.line}: {problem.message}")
	if problems:
		raise SystemExit(1)
	print(f"Djot slide structure: {summary.sources} source(s), {summary.slides} slide(s), {summary.images} image(s)")
	if args.native_executable is None:
		print("Native Djot validation was not run; it remains required before source acceptance.")


if __name__ == "__main__":
	main()
