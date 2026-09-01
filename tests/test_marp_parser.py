"""Focused tests for the repository-owned Marp-subset semantic parser."""

# Standard Library
import pathlib

# PIP3 modules
import pytest

# Local Modules
import marp_lib.marp_parser
import marp_lib.native_model


HEADER = "---\nmarp: true\ntheme: genetics\nsize: '16:10'\npaginate: true\ntitle: \"Parser deck\"\n---\n"


#============================================
def write_deck(tmp_path: pathlib.Path, body: str, name: str = "deck.md") -> pathlib.Path:
	"""Write one canonical parser fixture and return its source path."""
	path = tmp_path / name
	path.write_text(HEADER + body, encoding="utf-8")
	return path


#============================================
def parse(tmp_path: pathlib.Path, body: str) -> marp_lib.native_model.Deck:
	"""Parse one compact valid fixture."""
	return marp_lib.marp_parser.parse_deck(write_deck(tmp_path, body))


#============================================
def test_parses_typed_slide_semantics_and_source_lines(tmp_path: pathlib.Path) -> None:
	"""Supported authored content becomes strongly typed native semantic objects."""
	deck = parse(tmp_path, "<!-- _class: title-two-content -->\n<!-- _paginate: false -->\n"
		"# Main **heading**\n\n> ## Cell\n>\n> 3. First [resource](https://example.edu)\n>    - "
		"Nested `code`  \n>      second line\n> 4. Last\n\n> ![Component image](component.png)\n"
	)
	slide = deck.slides[0]
	assert deck.title == "Parser deck"
	assert slide.layout_class == "title-two-content"
	assert slide.paginate is False
	assert slide.location.line == 8
	assert isinstance(slide.blocks[0], marp_lib.native_model.Heading)
	assert len(slide.cells) == 2
	assert isinstance(slide.cells[0].blocks[1], marp_lib.native_model.ListBlock)
	list_block = slide.cells[0].blocks[1]
	assert list_block.ordered is True and list_block.start == 3
	assert isinstance(slide.cells[1].blocks[0], marp_lib.native_model.Image)


#============================================
def test_parses_standalone_notes_and_autolinks(tmp_path: pathlib.Path) -> None:
	"""Standalone ordinary comments become presenter notes and URL text becomes a link."""
	deck = parse(tmp_path, "<!-- _class: title-content -->\n<!-- notes: Explain this live -->\n"
		"# Title\n\nVisit <https://example.edu/path>.\n")
	slide = deck.slides[0]
	assert slide.notes == ("Explain this live",)
	paragraph = slide.blocks[1]
	assert isinstance(paragraph, marp_lib.native_model.Paragraph)
	assert any(isinstance(item, marp_lib.native_model.Link) for item in paragraph.inlines)


#============================================
def test_preserves_inline_formatting_bare_urls_and_yaml_size(tmp_path: pathlib.Path) -> None:
	"""Typed inlines distinguish emphasis, code, links, breaks, and literal size metadata."""
	deck = parse(tmp_path, "<!-- _class: title-content -->\n# [Heading](https://example.edu)\n\n"
		"*Italic* and `code`  \nhttps://example.edu/path plus example.edu\n")
	assert deck.front_matter["size"] == "16:10"
	heading = deck.slides[0].blocks[0]
	paragraph = deck.slides[0].blocks[1]
	assert isinstance(heading, marp_lib.native_model.Heading)
	assert isinstance(heading.inlines[0], marp_lib.native_model.Link)
	assert isinstance(paragraph, marp_lib.native_model.Paragraph)
	assert any(isinstance(item, marp_lib.native_model.Emphasis) for item in paragraph.inlines)
	assert any(isinstance(item, marp_lib.native_model.InlineCode) for item in paragraph.inlines)
	assert any(isinstance(item, marp_lib.native_model.Break) for item in paragraph.inlines)
	links = [item for item in paragraph.inlines if isinstance(item, marp_lib.native_model.Link)]
	assert [item.url for item in links] == ["https://example.edu/path"]


#============================================
def test_dividers_inside_fences_and_comments_do_not_split_slides(tmp_path: pathlib.Path) -> None:
	"""Top-level slide rulers ignore fence and comment interiors before rejection."""
	path = write_deck(tmp_path, "<!-- _class: title-content -->\n# First\n\n```text\n---\n```\n"
		"\n---\n<!-- _class: title-content -->\n<!-- note\n---\n-->\n# Second\n")
	with pytest.raises(marp_lib.marp_parser.MarpParseError, match="unsupported Markdown block: fence"):
		marp_lib.marp_parser.parse_deck(path)
	path.write_text(HEADER + "<!-- _class: title-content -->\n<!-- note\n---\n-->\n# First\n"
		"\n---\n<!-- _class: title-content -->\n# Second\n", encoding="utf-8")
	deck = marp_lib.marp_parser.parse_deck(path)
	assert len(deck.slides) == 2


#============================================
@pytest.mark.parametrize(("body", "message"), [
	("<!-- _class: title-content -->\n# Title\n\n| A | B |\n| - | - |\n| 1 | 2 |\n", "table"),
	("<!-- _class: title-content -->\n# Title\n\n    indented code\n", "code_block"),
	("<!-- _class: title-content -->\n# Title\n\n```text\ncode\n```\n", "fence"),
	("<!-- _class: title-content -->\n# Title\n\n<span>HTML</span>\n", "html"),
	("<!-- _class: title-content -->\n# Title\n\nText ![Component](part.png)\n", "mixed"),
	("<!-- _class: title-content -->\n![bg right:30%](part.png)\n", "background-image"),
	("<!-- _class: title-content -->\n<!-- _backgroundColor: red -->\n# Title\n", "unsupported Marp directive"),
	("<!-- _class: title-content dense -->\n# Title\n", "exactly one"),
	("<!-- _class: retired -->\n# Title\n", "unsupported Marp slide class"),
])
def test_rejects_unowned_authoring_features(tmp_path: pathlib.Path, body: str, message: str) -> None:
	"""Every unsupported source construct fails at its originating source location."""
	with pytest.raises(marp_lib.marp_parser.MarpParseError, match=message) as raised:
		parse(tmp_path, body)
	assert ":" in str(raised.value)


#============================================
@pytest.mark.parametrize(("front", "message"), [
	("---\nmarp: true\nmarp: true\ntheme: genetics\nsize: 16:10\n---\n", "duplicate key"),
	("---\nmarp: true\ntheme: genetics\nsize: 16:10\nauthor: Name\n---\n", "unsupported front-matter key"),
	("\n---\nmarp: true\ntheme: genetics\nsize: 16:10\n---\n", "must begin"),
])
def test_rejects_invalid_strict_front_matter(tmp_path: pathlib.Path, front: str, message: str) -> None:
	"""The semantic boundary has one strict and diagnosable YAML entry point."""
	path = tmp_path / "invalid.md"
	path.write_text(front + "<!-- _class: title-content -->\n# Title\n", encoding="utf-8")
	with pytest.raises(marp_lib.marp_parser.MarpParseError, match=message):
		marp_lib.marp_parser.parse_deck(path)


#============================================
def test_bom_and_hidden_provenance_fragment_preserve_real_slide_count(tmp_path: pathlib.Path) -> None:
	"""A UTF-8 BOM is accepted and trailing hidden-slide provenance makes no blank slide."""
	path = tmp_path / "bom.md"
	path.write_text("\ufeff" + HEADER + "<!-- _class: title-content -->\n# Kept\n\n---\n"
		"<!-- ODP hidden slide skipped: source 8 -->\n", encoding="utf-8")
	deck = marp_lib.marp_parser.parse_deck(path)
	assert len(deck.slides) == 1
	assert deck.slides[0].blocks[0].location.line == 9
