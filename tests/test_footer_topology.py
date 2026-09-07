"""Behavior tests for generic coarse-column and footer topology grouping."""

# Local Modules
import pytest

import marp_lib.importers.legacy_djot_emitter as legacy_djot_emitter
import marp_lib.importers.legacy_slide_plan as legacy_slide_plan


#============================================
def component(bounds: tuple[float, float, float, float], *, coarse: bool = False,
		source_kind: str = "text", kind: str = "text", reason: str = "", confidence: float = 0.0) -> legacy_djot_emitter.EmissionComponent:
	"""Build one concise geometric text component."""
	return legacy_djot_emitter.EmissionComponent(
		legacy_slide_plan.NormalizedBounds(*bounds), ("- item",), kind,
		coarse_text_container=coarse, source_kind=source_kind, classification_reason=reason,
		placeholder_confidence=confidence,
	)


#============================================
def test_coarse_columns_and_wide_footer_flow_match_existing_three_cell_layout() -> None:
	"""Two coarse columns plus aligned bottom text become the native footer topology."""
	components = [
		component((0.05, 0.20, 0.42, 0.70), coarse=True),
		component((0.58, 0.20, 0.95, 0.70), coarse=True),
		component((0.05, 0.67, 0.95, 0.75), source_kind="text-box"),
		component((0.05, 0.79, 0.95, 0.87), source_kind="text-box"),
	]

	grouped = legacy_djot_emitter.coalesce_bottom_footer(components)

	assert legacy_djot_emitter.component_layout(grouped)[0] == "two-over-one-panels"
	assert not legacy_djot_emitter.components_overlap(grouped)


#============================================
def test_bottom_footer_relation_accepts_its_bounded_local_score_only() -> None:
	"""A clear footer relation may exceed the ordinary matcher ceiling, but not .35."""
	reason = legacy_djot_emitter.BOTTOM_FOOTER_RELATION_REASON
	accepted = [
		component((0.1052, 0.1640, 0.3472, 0.7621)),
		component((0.6121, 0.1640, 0.8536, 0.7621)),
		component((0.0500, 0.7459, 0.9500, 0.7946), source_kind="text-box", kind="flow", reason=reason),
	]
	over_limit = [
		component((0.1635, 0.1690, 0.2767, 0.8735)),
		component((0.5094, 0.1690, 0.7944, 0.8735)),
		component((0.0500, 0.8696, 0.9500, 0.8923), source_kind="text-box", kind="flow", reason=reason),
	]
	competing = [
		accepted[0],
		component((0.6121, 0.5500, 0.8536, 0.7621)),
		accepted[2],
	]

	score, _order = legacy_djot_emitter.bottom_footer_layout(accepted) or (None, None)
	assert 0.32 < score <= legacy_djot_emitter.BOTTOM_FOOTER_SCORE_CEILING
	assert legacy_djot_emitter.component_layout(accepted)[0] == "two-over-one-panels"
	assert legacy_djot_emitter.bottom_footer_layout(over_limit) is None
	assert legacy_djot_emitter.bottom_footer_layout(competing) is None


#============================================
def test_asymmetric_explanatory_pair_selects_only_its_bounded_text_relation() -> None:
	"""One coarse panel and one aligned compact text shape may use the local .33 ceiling."""
	accepted = [
		component((0.0000, 0.2917, 0.6223, 0.7769), coarse=True),
		component((0.7521, 0.2917, 0.9470, 0.4684)),
	]
	over_limit = [
		component((0.00, 0.0680, 0.4005, 0.9811), coarse=True),
		component((0.7673, 0.0980, 0.8329, 0.2143)),
	]

	score, _order = legacy_djot_emitter.asymmetric_explanatory_pair_layout(accepted) or (None, None)
	assert legacy_djot_emitter.TOPOLOGY_MAX_SCORE < score <= legacy_djot_emitter.ASYMMETRIC_EXPLANATORY_PAIR_MAX_SCORE
	assert legacy_djot_emitter.component_layout(accepted)[0] == "two-panels"
	assert legacy_djot_emitter.asymmetric_explanatory_pair_layout(over_limit) is None


#============================================
def test_asymmetric_explanatory_pair_leaves_nonrelations_to_ordinary_matching() -> None:
	"""Only direct, separated, aligned one-coarse text pairs enter the local path."""
	base = [
		component((0.05, 0.20, 0.55, 0.80), coarse=True),
		component((0.65, 0.21, 0.90, 0.40)),
	]
	vertical = [base[0], component((0.65, 0.50, 0.90, 0.69))]
	overlap = [base[0], component((0.50, 0.21, 0.75, 0.40))]
	short_gap = [base[0], component((0.58, 0.21, 0.83, 0.40))]
	misaligned = [base[0], component((0.65, 0.24, 0.90, 0.40))]
	two_coarse = [base[0], component((0.65, 0.21, 0.90, 0.40), coarse=True)]
	low_confidence_placeholder = [base[0], component((0.65, 0.21, 0.90, 0.40), confidence=0.50)]
	extra = [*base, component((0.20, 0.82, 0.30, 0.90))]
	visual = [base[0], component((0.65, 0.21, 0.90, 0.40), kind="image")]
	table = [base[0], component((0.65, 0.21, 0.90, 0.40), kind="table")]
	crop = [base[0], component((0.65, 0.21, 0.90, 0.40), kind="flow", source_kind="content-region")]
	flow = [base[0], component((0.65, 0.21, 0.90, 0.40), kind="flow")]

	for components in (vertical, overlap, short_gap, misaligned, two_coarse, low_confidence_placeholder, extra, visual, table, crop, flow):
		assert legacy_djot_emitter.asymmetric_explanatory_pair_layout(components) is None


#============================================
def test_non_text_box_footer_candidate_stays_atomic() -> None:
	"""A similar overlap without the proven source kind retains normal review behavior."""
	components = [
		component((0.05, 0.20, 0.42, 0.70), coarse=True),
		component((0.58, 0.20, 0.95, 0.70), coarse=True),
		component((0.05, 0.67, 0.95, 0.75), source_kind="text-box"),
		component((0.05, 0.79, 0.95, 0.87)),
	]

	assert len(legacy_djot_emitter.coalesce_bottom_footer(components)) == 4


#============================================
def test_mid_column_wide_text_boxes_do_not_qualify_as_footer() -> None:
	"""Wide editable text remains atomic until it reaches both column bottom bands."""
	components = [
		component((0.05, 0.20, 0.42, 0.70), coarse=True),
		component((0.58, 0.20, 0.95, 0.70), coarse=True),
		component((0.05, 0.43, 0.95, 0.51), source_kind="text-box"),
		component((0.05, 0.55, 0.95, 0.63), source_kind="text-box"),
	]

	assert len(legacy_djot_emitter.coalesce_bottom_footer(components)) == 4


#============================================
def test_unclustered_coarse_image_overlap_and_equal_top_footer_stay_reviewable() -> None:
	"""Only an ordered footer composition receives the narrow overlap allowance."""
	coarse = component((0.05, 0.20, 0.50, 0.75), coarse=True)
	image = legacy_djot_emitter.EmissionComponent(
		legacy_slide_plan.NormalizedBounds(0.25, 0.40, 0.75, 0.80), ("![image](asset.png)",), "image",
	)
	footer = [
		component((0.05, 0.20, 0.42, 0.70), coarse=True),
		component((0.58, 0.20, 0.95, 0.70), coarse=True),
		component((0.05, 0.74, 0.95, 0.82), source_kind="text-box"),
		component((0.05, 0.74, 0.95, 0.82), source_kind="text-box"),
	]

	assert legacy_djot_emitter.components_overlap([coarse, image])
	assert len(legacy_djot_emitter.coalesce_bottom_footer(footer)) == 4


#============================================
def test_wide_lower_component_preserves_top_peer_and_footer_axis_relations() -> None:
	"""A lower span across both peers selects the existing top-and-footer topology."""
	components = [
		component((0.05, 0.20, 0.42, 0.45)),
		component((0.58, 0.20, 0.95, 0.45)),
		component((0.05, 0.58, 0.95, 0.85)),
	]
	near_miss = [*components[:2], component((0.43, 0.58, 0.57, 0.85))]

	assert legacy_djot_emitter.component_layout(components)[0] == "two-over-one-panels"
	with pytest.raises(ValueError, match="ambiguous topology"):
		legacy_djot_emitter.component_layout(near_miss)
