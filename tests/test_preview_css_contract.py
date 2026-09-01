"""Static contracts for the Genetics Marp authoring-preview stylesheet."""

# Standard Library
import pathlib
import re


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
def selector_specificity(selector: str) -> tuple[int, int, int]:
	"""Return the CSS specificity components used by this bounded selector family."""
	return (selector.count("#"), selector.count(".") + selector.count("["),
		len(re.findall(r"(?<![-\w])(?:section|h1)(?![-\w])", selector)))


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
	"""Each one-block vertical source form has one explicitly placed preview pane."""
	css = stylesheet()
	title_content = rule_contents(css, "section.title-content")
	title_body = rule_contents(css, "section.title-content > :not(h1)")
	vertical = rule_contents(css, "section.title-vertical-text")
	vertical_body = rule_contents(css, "section.title-vertical-text > :not(h1)")
	vertical_title_body = rule_contents(css, "section.vertical-title-vertical-text > :not(h1)")
	assert "display: flex;" in title_content and "flex-direction: column;" in title_content
	assert "flex: 0 0 auto;" in title_body
	assert "display: grid;" in vertical and "flex-wrap" not in vertical
	assert "grid-row: 2;" in vertical_body and "writing-mode: vertical-rl;" in css
	assert "grid-column: 3;" in vertical_title_body


#============================================
def test_vertical_title_layouts_match_fixed_native_geometry() -> None:
	"""Preview track widths and child placement match the native 1280px geometry."""
	css = stylesheet()
	vertical = rule_contents(css, "section.vertical-title-vertical-text")
	single_body = rule_contents(css, "section.vertical-title-vertical-text > :not(h1)")
	chart_first = rule_contents(css, "section.vertical-title-text-chart > blockquote:nth-of-type(1)")
	chart_second = rule_contents(css, "section.vertical-title-text-chart > blockquote:nth-of-type(2)")
	assert "grid-template-columns: 94px 24px 1042px;" in vertical
	assert "column-gap: 0;" in vertical
	assert "section.vertical-title-text-chart {\n\tcolumn-gap: 0;\n\tgrid-template-columns: 94px 24px 500px 42px 500px;" in css
	assert "section.vertical-title-vertical-text > h1,\nsection.vertical-title-text-chart > h1 {\n\tgrid-column: 1;" in css
	assert "grid-column: 3;" in single_body
	assert "grid-column: 3;" in chart_first
	assert "grid-column: 5;" in chart_second


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


#============================================
def test_h1_size_modifier_preview_selectors_are_bounded_and_direct() -> None:
	"""Each supported authoring modifier changes only a direct slide H1."""
	css = stylesheet()
	for value in (64, 80, 96, 120, 160, 200):
		selector = f"section.font-size-{value} > h1"
		assert f"{selector} {{" in css
		assert f"font-size: {value}px;" in rule_contents(css, selector)


#============================================
def test_h1_size_modifiers_follow_equal_specificity_layout_title_rules() -> None:
	"""Centered and title-slide modifiers win the authoring-preview CSS cascade."""
	css = stylesheet()
	for value in (64, 80, 96, 120, 160, 200):
		modifier = f"section.font-size-{value} > h1"
		for layout in ("section.title-slide h1", "section.centered-text h1"):
			assert selector_specificity(modifier) == selector_specificity(layout) == (0, 1, 2)
			assert css.index(f"{modifier} {{") > css.index(f"{layout} {{")
