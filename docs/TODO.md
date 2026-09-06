# TODO

Use this file for small, concrete extended-Djot language-design tasks. Classic Marp remains the
migration compatibility baseline but cannot express the required spatial layouts. The active grammar
record is [djot_slide_extension_exploration.md](active_plans/decisions/djot_slide_extension_exploration.md);
the historical rationale is
[presentation_language_choices.md](active_plans/decisions/presentation_language_choices.md), and
the literal evidence remains [LAYOUT_LANGUAGE_SURVEY.md](LAYOUT_LANGUAGE_SURVEY.md).

## Language design

- [x] Review the fifteen-fixture source comparison with the instructor.
- [x] Set aside surveyed presentation formats as direct-adoption targets.
- [x] Select Djot as the source-language foundation.
- [ ] Pin the Djot revision and every parser, formatter, editor rule, and linter in the strict
  compatibility suite.
- [ ] Write a one-page candidate grammar for explicit named layouts and regions.
- [ ] Define slide boundaries, directive scope, token syntax, slot closure, and literal escaping.
- [ ] Specify title, subtitle, caption, required/optional/repeated slot, math, and reveal behavior.
- [ ] Add an accepted-source and rejected-near-match specimen for every grammar construct.
- [ ] Verify every accepted and rejected specimen with every applicable Djot compatibility tool.
- [ ] Review the grammar against all fifteen fixtures before naming the language or writing a guide.

## Classic Marp baseline

- [ ] Audit current parser behavior against the Marp Core 5.0.1 Markdown contract.
- [ ] Classify inherited Marpit directives and image forms as accepted, planned, or a non-goal.
- [ ] Classify Core v5 tables, strikethrough, emoji, slide size, and title-fit behavior.
- [ ] Keep conformance fixtures free of Marp Core v4, highlight.js, and removed legacy syntax.

## Deferred implementation

- [ ] Start parser, exporter, importer, preview, test, or deck migration only after the instructor
  approves the grammar and language name.
- [ ] Give every accepted construct a typed native-model and editable PPTX/ODP mapping.
- [ ] Keep the layout registry as geometry owner and preserve ordinary nested Markdown inside slots.
- [ ] Update the new language guide, [ROADMAP.md](ROADMAP.md), and [CHANGELOG.md](CHANGELOG.md)
  with the approved grammar and evidence.

## Exclusions

- [x] Do not pursue comment-based `_cell` markers as normal layout syntax.
- [x] Do not use raw HTML or XML tags for normal layout syntax.
- [x] Do not name the successor Marp+ before its grammar is selected.
