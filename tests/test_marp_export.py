"""Behavioral tests for trusted Marp export input validation."""

# Standard Library
import pathlib

# PIP3 modules
import pytest

# local repo modules
from tools import marp_export


#============================================
def test_validate_input_accepts_auto_fitting_content_image(tmp_path: pathlib.Path) -> None:
	"""Accept a normal Marp image without a hard-coded dimension."""
	deck_path = tmp_path / "lecture.md"
	deck_path.write_text("# Figure\n\n![Cell](assets/cell.png)\n", encoding="utf-8")

	validated_path = marp_export.validate_input(str(deck_path), tmp_path)

	assert validated_path == deck_path


#============================================
def test_validate_input_rejects_source_fallback_class(tmp_path: pathlib.Path) -> None:
	"""Reject the retired full-slide fallback layout marker."""
	deck_path = tmp_path / "lecture.md"
	deck_path.write_text("<!-- _class: source-fallback -->\n", encoding="utf-8")

	with pytest.raises(ValueError) as error:
		marp_export.validate_input(str(deck_path), tmp_path)

	assert "failed conversions" in str(error.value)


#============================================
def test_validate_input_rejects_source_slide_image(tmp_path: pathlib.Path) -> None:
	"""Reject a full-slide source image even without the retired class."""
	deck_path = tmp_path / "lecture.md"
	deck_path.write_text("![Slide](assets/slide_012_source.png)\n", encoding="utf-8")

	with pytest.raises(ValueError) as error:
		marp_export.validate_input(str(deck_path), tmp_path)

	assert "failed conversions" in str(error.value)
