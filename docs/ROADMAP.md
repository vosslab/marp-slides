# Roadmap: language design before implementation

Status: open design work. Classic Marp Core v5 remains the migration and conformance baseline;
[MARP_SYNTAX_GUIDE.md](MARP_SYNTAX_GUIDE.md) remains its classic Marp / Marp CLI guide. The
successor language is independent, unnamed, and not yet implemented.

## Purpose

Classic Marp cannot express the required spatial teaching layouts. The language survey found no
external format suitable for adoption. The next work is to specify a small, GitHub-readable language
whose content remains ordinary GFM and whose layout structure is explicit, visible, and unambiguous.

The active choice record is
[presentation_language_choices.md](active_plans/decisions/presentation_language_choices.md). It
defines the questions that must be answered before parser, exporter, importer, deck, or guide work
begins.

## Milestone plan

| M | Title | Outcome | Gate |
| --- | --- | --- | --- |
| M1 | Grammar proposal | One concise candidate grammar covers every fixture | Instructor approval |
| M2 | Parse contract | Accepted and rejected source maps to a typed slide model | Grammar approval |
| M3 | Native layouts | Named slots become editable native layout objects | Parse-contract review |
| M4 | Teaching content | Images, math, and simple reveals have native mappings | Layout evidence |
| M5 | Guide and migration | Named language guide and canonical-deck migration | Independent verification |

## M1: grammar proposal

- Specify slide boundaries without a horizontal-rule ambiguity.
- Specify the exact layout and slot directives, including legal positions and literal escapes.
- Define title, subtitle, required slot, optional slot, repeated slot, image, and caption behavior.
- Select exact inline and display math delimiters.
- Select one short, bounded syntax for item-by-item and arbitrary-item reveals.
- State the GFM/CommonMark version and extensions accepted inside a slot.
- Express all fifteen language-survey fixtures and their invalid near-matches.

The candidate `@layout NAME` and `:: SLOT` surface is an illustration only. It has no special
status until M1 approval.

## M2: parse contract

- Give every accepted directive and GFM block a typed native-model representation.
- Reject unknown layouts, slots, directives, illegal placement, and unsupported combinations at the
  source line.
- Keep ordinary nested Markdown blocks unchanged inside slots.
- Prove that directive recognition does not occur inside YAML, indented code, or fenced code.
- Keep language parsing separate from geometry, which belongs to the native layout registry.

## M3 through M5: implementation

No implementation milestone begins until the preceding design gate is approved. Each accepted
feature requires parser, native PPTX, editable ODP, source diagnostic, canonical-deck, and guide
evidence. Independent review follows implementation.

## Non-goals

- Use comment-based cell markers, HTML tags, or raw XML for normal layout structure.
- Infer a layout, region, caption, or reveal from content shape or source order.
- Promise Marp, Marpit, CSS, browser, or external-renderer compatibility for the successor.
- Add a Node or browser runtime to production.
- Use full-slide rasterization or raster fallback for accepted source.

## Completion rule

After M1 approval, give the language its own name, create its own syntax guide, and update this
roadmap and [TODO.md](TODO.md). Keep [MARP_SYNTAX_GUIDE.md](MARP_SYNTAX_GUIDE.md) limited to
classic Marp compatibility.
