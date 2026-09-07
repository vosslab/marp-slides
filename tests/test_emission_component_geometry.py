"""Focused geometry behavior for immutable emitter component members."""

# local repo modules
import slide_lib.importers.legacy_djot_emitter as legacy_djot_emitter
import slide_lib.importers.legacy_geometry as legacy_geometry
import slide_lib.importers.legacy_slide_plan as legacy_slide_plan
import slide_lib.importers.pptx_to_marp as pptx_to_marp


#============================================
def bounds(values: tuple[float, float, float, float]) -> legacy_geometry.NormalizedBounds:
	"""Build concise normalized geometry for component behavior checks."""
	return legacy_geometry.NormalizedBounds(*values)


#============================================
def test_member_footprints_avoid_false_collision_from_union_bounds() -> None:
	"""Disjoint grouped members do not turn their enclosing union into a collision."""
	first = legacy_djot_emitter.EmissionComponent(
		bounds((0.10, 0.10, 0.90, 0.90)), ("- flow",), "flow",
		member_footprints=(bounds((0.10, 0.10, 0.20, 0.20)), bounds((0.80, 0.80, 0.90, 0.90))),
	)
	second = legacy_djot_emitter.EmissionComponent(bounds((0.45, 0.45, 0.55, 0.55)), ("- item",), "text")

	assert not legacy_djot_emitter.components_overlap([first, second])


#============================================
def test_only_coarse_direct_picture_peer_tolerates_raw_overlap() -> None:
	"""One coarse text and one direct picture retain their uniquely matched peer layout."""
	coarse = legacy_djot_emitter.EmissionComponent(
		bounds((0.05, 0.20, 0.60, 0.80)), ("- prose",), "text",
		coarse_text_container=True, member_footprints=(bounds((0.05, 0.20, 0.60, 0.80)),),
	)
	image = legacy_djot_emitter.EmissionComponent(
		bounds((0.45, 0.30, 0.95, 0.70)), ("![Figure](figure.png)",), "image",
		source_kind="picture", member_footprints=(bounds((0.45, 0.30, 0.95, 0.70)),),
	)

	assert legacy_djot_emitter.component_layout([coarse, image])[0] == "two-panels"
	assert not legacy_djot_emitter.components_overlap([coarse, image])


#============================================
def test_footer_padding_is_not_general_text_flow_tolerance() -> None:
	"""Only full-width ordered footer members accept a small vertical source overlap."""
	first = legacy_djot_emitter.EmissionComponent(bounds((0.05, 0.70, 0.95, 0.80)), ("- first",), "text")
	second = legacy_djot_emitter.EmissionComponent(bounds((0.05, 0.76, 0.95, 0.84)), ("- second",), "text")

	assert legacy_djot_emitter.follows_footer_lane(first, second)
	assert not legacy_djot_emitter.follows_text_lane(first, second)


#============================================
def test_caption_footer_and_shared_footer_relations_are_individually_bounded() -> None:
	"""Caption and shared-footer padding use their distinct native topology mappings."""
	left = legacy_djot_emitter.EmissionComponent(bounds((0.05, 0.20, 0.40, 0.50)), ("- left",), "text")
	caption_footer = legacy_djot_emitter.EmissionComponent(
		bounds((0.05, 0.55, 0.69, 0.65)), ("- footer",), "text", source_kind="text-box",
	)
	image_caption = legacy_djot_emitter.EmissionComponent(
		bounds((0.64, 0.20, 0.95, 0.59)), ("![image](image.png)", "", "- caption"), "image",
		source_kind="picture", member_footprints=(bounds((0.74, 0.20, 0.95, 0.50)), bounds((0.64, 0.51, 0.90, 0.59))),
	)
	coarse = legacy_djot_emitter.EmissionComponent(bounds((0.05, 0.20, 0.40, 0.55)), ("- left",), "text", coarse_text_container=True)
	shared_footer = legacy_djot_emitter.EmissionComponent(
		bounds((0.05, 0.55, 0.95, 0.65)), ("- footer",), "text", source_kind="text-box",
	)
	raw_image = legacy_djot_emitter.EmissionComponent(
		bounds((0.60, 0.20, 0.95, 0.58)), ("![image](image.png)",), "image", source_kind="picture",
	)

	assert not legacy_djot_emitter.components_overlap([left, caption_footer, image_caption])
	assert not legacy_djot_emitter.components_overlap(legacy_djot_emitter.coalesce_bottom_footer([coarse, shared_footer, raw_image]))


#============================================
def test_content_crop_retains_individual_source_member_footprints() -> None:
	"""A rendered crop keeps source members for collisions while using their union as bounds."""
	text = legacy_slide_plan.SourceTextRegion(((0, "Label"),), bounds((0.20, 0.20, 0.30, 0.30)), False, 0.0)
	image = legacy_slide_plan.SourceImageRegion("source.png", bounds((0.60, 0.60, 0.80, 0.80)))
	content = legacy_slide_plan.ContentRegionPlan("crop", bounds((0.20, 0.20, 0.80, 0.80)), (text,), (image,))
	plan = legacy_slide_plan.LegacySlidePlan(legacy_slide_plan.TitleDecision(None, "test"), (), content)
	planned = legacy_djot_emitter.PlannedSlide(pptx_to_marp.SlideData(1, False, (), (), (), (), ()), plan)

	components, _reasons = legacy_djot_emitter.emit_components(planned, "assets/crop.png")
	gap = legacy_djot_emitter.EmissionComponent(bounds((0.40, 0.40, 0.50, 0.50)), ("- outside",), "text")

	assert not legacy_djot_emitter.components_overlap([components[0], gap])


#============================================
def text_box(values: tuple[float, float, float, float], ordinal: int, *, coarse: bool = False,
		rotation: float = 0.0) -> legacy_djot_emitter.EmissionComponent:
	"""Build one direct editable text-box component for shallow-flow behavior."""
	box = bounds(values)
	return legacy_djot_emitter.EmissionComponent(box, (f"- text {ordinal}",), "text",
		coarse_text_container=coarse, source_kind="text-box", source_ordinals=(ordinal,),
		member_footprints=(box,), rotation_degrees=rotation)


#============================================
def test_shallow_same_lane_text_boxes_form_a_two_panel_flow() -> None:
	"""Aligned editable text boxes become one right-side flow beside another panel."""
	left = legacy_djot_emitter.EmissionComponent(bounds((0.05, 0.20, 0.42, 0.65)), ("- left",), "text")
	first, second = text_box((0.58, 0.20, 0.945, 0.450), 10), text_box((0.585, 0.426, 0.945, 0.635), 11)

	result = legacy_djot_emitter.coalesce_text_flows([left, first, second])
	flow = next(component for component in result if component.kind == "flow")

	assert flow.lines == ("- text 10", "", "- text 11")
	assert legacy_djot_emitter.component_layout(result)[0] == "two-panels"
