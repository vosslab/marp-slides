"""Static contracts for the Genetics Marp authoring-preview stylesheet."""

# Standard Library
import pathlib


CSS_PATH = pathlib.Path(__file__).parents[1] / "themes" / "genetics.css"


#============================================
def stylesheet() -> str:
	"""Return the canonical authoring-preview stylesheet."""
	contents = CSS_PATH.read_text(encoding="utf-8")
	return contents


#============================================
def rule_contents(css: str, selector: str) -> str:
	"""Return declarations from one exact CSS selector rule."""
	exact_marker = f"{selector} {{"
	start = css.find(exact_marker)
	if start == -1:
		start = css.index(selector)
	body_start = css.index("{", start) + 1
	body_end = css.index("}", body_start)
	contents = css[body_start:body_end]
	return contents


#============================================
def test_titleless_gallery_uses_the_complete_component_region() -> None:
	"""A titleless gallery puts its direct image paragraph in its sole grid row."""
	css = stylesheet()
	gallery = rule_contents(css, "section.gallery:not(:has(> h1))")
	paragraph = rule_contents(css, "section.gallery:not(:has(> h1)) > p")
	assert "grid-template-rows: minmax(0, 1fr);" in gallery
	assert "grid-row: 1;" in paragraph


#============================================
def test_root_body_layouts_have_stable_preview_body_placement() -> None:
	"""Paragraph-plus-list source remains in each layout's intended body region."""
	css = stylesheet()
	title_content = rule_contents(css, "section.title-content")
	title_body = rule_contents(css, "section.title-content > :not(h1)")
	vertical = rule_contents(css, "section.title-vertical-text")
	vertical_body = rule_contents(css, "section.title-vertical-text > :not(h1)")
	vertical_title_body = rule_contents(css, "section.vertical-title-vertical-text > :not(h1)")
	assert "display: flex;" in title_content and "flex-direction: column;" in title_content
	assert "flex: 0 0 auto;" in title_body
	assert "display: flex;" in vertical and "flex-wrap: wrap;" in vertical
	assert "flex: 1 1 0;" in vertical_body and "writing-mode: vertical-rl;" in css
	assert "grid-column: 2;" in vertical_title_body


#============================================
def test_image_only_cells_have_a_full_height_contained_image_wrapper() -> None:
	"""Portrait component images have a centered, margin-free cell paragraph."""
	css = stylesheet()
	selector = "section.title-two-content > blockquote > p:only-child:has(> img:only-child)"
	image_cell = rule_contents(css, selector)
	assert "display: flex;" in image_cell
	assert "align-items: center;" in image_cell
	assert "justify-content: center;" in image_cell
	assert "height: 100%;" in image_cell
	assert "margin: 0;" in image_cell
