"""Focused behavior for multiple-choice source-region overlays."""

# PIP3 modules
import pytest

# local repo modules
import marp_lib.importers.legacy_geometry as legacy_geometry
import marp_lib.importers.legacy_slide_plan as legacy_slide_plan


#============================================
@pytest.mark.parametrize("visuals", [
	(legacy_slide_plan.SourceImageRegion(
		"source-connector-9", legacy_geometry.NormalizedBounds(0.01, 0.01, 0.05, 0.05), "connector", 9,
	),),
	(
		legacy_slide_plan.SourceImageRegion(
			"assets/figure.png", legacy_geometry.NormalizedBounds(0.30, 0.22, 0.70, 0.32), "picture", 10,
		),
		legacy_slide_plan.SourceImageRegion(
			"source-connector-11", legacy_geometry.NormalizedBounds(0.01, 0.01, 0.05, 0.05), "connector", 11,
		),
	),
])
def test_multiple_choice_declines_unconsumed_connector_visuals(
	visuals: tuple[legacy_slide_plan.SourceImageRegion, ...],
) -> None:
	"""Connector visuals never disappear behind a recognized structural question."""
	question = legacy_slide_plan.SourceTextRegion(
		((0, "Prompt"), (1, "Choice one")),
		legacy_geometry.NormalizedBounds(0.08, 0.20, 0.82, 0.68), False, 1.0, source_ordinal=4,
	)
	answer = legacy_slide_plan.SourceTextRegion(
		((0, "Answer"),), legacy_geometry.NormalizedBounds(0.72, 0.78, 0.92, 0.86),
		False, 0.0, source_ordinal=8,
	)

	assert legacy_slide_plan.plan_slide((question, answer), visuals).multiple_choice is None
