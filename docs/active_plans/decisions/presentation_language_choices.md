# Presentation language choices

Status: open decision record. This is not a syntax guide and does not authorize parser work.

## Decision question

What language should an instructor hand-write for structured, editable teaching slides?

The survey concludes that classic Marp lacks required spatial semantics and that no surveyed external
format is a viable adoption target. The active direction is therefore a small extension over a
GitHub-readable GFM content surface. GitHub need not render the slides, but its source view must
remain clear and useful.

## Choices considered

| Choice | Status | Reason |
| --- | --- | --- |
| Classic Marp | Baseline only | It cannot name the required content regions or teaching builds. |
| Adopt a surveyed format | Set aside | Each sacrifices either ordinary authoring, explicit layout, or the native model. |
| Use Djot as the base | Reference only | Its grammar discipline is valuable, but its source would not display as Markdown on GitHub. |
| Extend GFM deliberately | Active direction | It preserves familiar content and adds only the missing spatial semantics. |

The supporting evidence is in [LAYOUT_LANGUAGE_SURVEY.md](../../LAYOUT_LANGUAGE_SURVEY.md) and
[MARP_ADJACENT_PROJECT_COMPARISON.md](../../MARP_ADJACENT_PROJECT_COMPARISON.md).

## Candidate surface

The smallest promising shape separates a named slide layout from named content regions:

```markdown
@layout comparison

# Actin and microtubules

:: left
- Actin filaments
  - Support membrane shape

:: right
- Microtubules
  - Form the mitotic spindle
```

This is an illustration, not selected syntax. A GitHub reader sees a legible layout name, title,
and labeled regions; the repository parser sees explicit semantics. The layout registry, not source
CSS, supplies geometry, reading order, and editable native-object construction.

## Grammar acceptance criteria

Before any spelling becomes public syntax, its specification must establish all of these rules.

| Area | Required rule |
| --- | --- |
| Layout selection | Every spatial slide names one registered layout; content shape never selects a layout implicitly. |
| Region selection | Every non-title content region has an explicit, registered slot name. |
| Directive scope | Structural lines are recognized only at column zero, outside YAML and fenced or indented code blocks. |
| Token form | Each directive has one exact ASCII form and an exact name grammar; near-matches remain ordinary text or produce a source error. |
| Slot scope | A slot ends at the next slot marker or slide boundary; duplicate, unknown, and missing required slots are errors. |
| Markdown content | Slot bodies use a named GFM/CommonMark version and extension set; ordinary nested lists remain unchanged. |
| No inference | Text position, heading level, image adjacency, and list shape do not silently create regions, captions, or layouts. |
| Diagnostics | Unknown directives, illegal placement, and unsupported combinations identify the source line and corrective action. |
| Native model | Every accepted construct maps to typed editable objects or is rejected before rendering. |

Normal layout structure must not depend on HTML tags or HTML comments. Deliberate visible directives
are preferable because they remain reviewable in GitHub's ordinary Markdown view.

## Questions to settle

- What explicitly divides slides without colliding with a GFM horizontal rule?
- Is `@layout NAME` required as the first structural line of every slide, and how do title-only
  slides work?
- Is `:: SLOT` the best visible marker, and how does an author write a literal matching line?
- Which slots are optional, repeated, or required for each layout?
- Does an image and caption always use explicit `image` and `caption` slots?
- What exact LaTeX-compatible inline and display math delimiters are accepted?
- What one short directive requests an item-by-item or arbitrary-item reveal?
- Which GFM extensions are part of the language, and which are rejected as unsupported?

## Next design step

Write a one-page grammar proposal that answers the questions above and expresses all fifteen survey
fixtures. Review its unambiguous parse and native-model mapping before naming the language or
creating a guide for it.
