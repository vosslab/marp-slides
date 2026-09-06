"""Behavioral tests for the fast extended-Djot structural linter."""

# Standard Library
import pathlib

# Local modules
from tools import djot_slide_lint


#============================================
def write_source(tmp_path: pathlib.Path, content: str) -> pathlib.Path:
	"""Write one small source deck with its referenced local component image."""
	assets = tmp_path / "assets"
	assets.mkdir()
	(assets / "gene.png").write_bytes(b"source asset")
	path = tmp_path / "lecture.djot"
	path.write_text(content, encoding="utf-8")
	return path


#============================================
def test_valid_two_panel_source_has_no_structural_problems(tmp_path: pathlib.Path) -> None:
	"""The linter accepts a documented layout, slot, and local-image arrangement."""
	path = write_source(
		tmp_path,
		"""=== layout: two-panels

# Genes

@left

- Chromosomes carry genes.

@right

![Chromosome](assets/gene.png)
""",
	)

	problems, summary = djot_slide_lint.lint_paths([path])

	assert problems == []
	assert summary == djot_slide_lint.LintSummary(1, 1, 1)


#============================================
def test_linter_reports_slots_actions_and_traversal(tmp_path: pathlib.Path) -> None:
	"""Local failures identify slide-language misuse without rendering anything."""
	path = write_source(
		tmp_path,
		"""=== layout: two-panels

@left

- Incomplete action <= appear after this sentence.

@left

![Outside](../outside.png)
""",
	)

	problems, _summary = djot_slide_lint.lint_paths([path])
	messages = [problem.message for problem in problems]

	assert "duplicate @left slot" in messages
	assert "<= action must be an exact terminal suffix" in messages
	assert "image path must be a local relative path without traversal" in messages
	assert "layout 'two-panels' requires exactly one @right slot" in messages
