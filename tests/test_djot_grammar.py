"""Durable contracts for the small, registry-derived Djot grammar."""

# Third-Party Modules
import pytest

# Local Modules
import marp_lib.djot_grammar
import marp_lib.layouts
import marp_lib.native_model


#============================================
@pytest.mark.parametrize(("pattern", "source", "group", "value"), (
	(marp_lib.djot_grammar.LAYOUT_DIRECTIVE_PATTERN, "=== layout: one-panel", "layout", "one-panel"),
	(marp_lib.djot_grammar.SLOT_DIRECTIVE_PATTERN, "@body", "slot", "body"),
	(marp_lib.djot_grammar.PREFIX_ACTION_PATTERN, "=> cascade appear", "action", "cascade appear"),
	(marp_lib.djot_grammar.TERMINAL_ACTION_PATTERN, "<= appear", "action", "appear"),
))
def test_directive_patterns_accept_only_whole_supported_lines(pattern: object, source: str,
		group: str, value: str) -> None:
	"""Every directive recognizer exposes its authored value from a full line."""
	match = pattern.fullmatch(source)  # type: ignore[union-attr]
	assert match is not None and match.group(group) == value


#============================================
@pytest.mark.parametrize(("pattern", "source"), (
	(marp_lib.djot_grammar.LAYOUT_DIRECTIVE_PATTERN, " === layout: one-panel"),
	(marp_lib.djot_grammar.SLOT_DIRECTIVE_PATTERN, "@body prose"),
	(marp_lib.djot_grammar.PREFIX_ACTION_PATTERN, "=> appear "),
	(marp_lib.djot_grammar.TERMINAL_ACTION_PATTERN, "<= appear "),
))
def test_directive_patterns_reject_near_matches(pattern: object, source: str) -> None:
	"""Whitespace and trailing prose never become directives by accident."""
	assert pattern.fullmatch(source) is None  # type: ignore[union-attr]


#============================================
def test_grammar_derives_layout_and_slot_names_from_registry() -> None:
	"""Grammar catalog remains an API projection of the layout owner."""
	layout_name = next(name for name, spec in marp_lib.layouts.LAYOUTS.items() if spec.slot_names)
	assert (layout_name in marp_lib.djot_grammar.legal_layout_names() and
		marp_lib.djot_grammar.legal_slot_names(layout_name) == marp_lib.layouts.LAYOUTS[layout_name].slot_names)


#============================================
def test_action_vocabulary_and_text_projection_are_typed() -> None:
	"""Accepted actions and normal-text entities project through stable IR types."""
	cascade = marp_lib.djot_grammar.ACTION_REVEALS["cascade appear"]
	assert (cascade.sequence is marp_lib.native_model.RevealSequence.PARAGRAPHS and
		marp_lib.djot_grammar.project_text("5&prime;") == "5\u2032")
