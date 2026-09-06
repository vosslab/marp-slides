# Plan: Djot slide-extension exploration

Status: exploratory working note. This page proposes a small Djot-compatible surface for classroom
slides. It neither selects Djot as the source foundation nor authorizes parser, exporter, preview,
or deck changes.

## Context

The repository needs explicit named layouts and regions while retaining ordinary authorable document
content. [presentation_language_choices.md](presentation_language_choices.md) identifies Djot's
deliberate grammar and low indentation burden as attractive, but Djot has no slide or region
semantics. The prior-art evidence remains in [LAYOUT_LANGUAGE_SURVEY.md](../../LAYOUT_LANGUAGE_SURVEY.md)
and [MARP_ADJACENT_PROJECT_COMPARISON.md](../../MARP_ADJACENT_PROJECT_COMPARISON.md).

The instructor is currently leaning toward extending Djot. This is a thought experiment about an
extension that can be parsed as ordinary Djot, not a claim that an unmodified Djot renderer produces
a useful slide deck.

## Objectives

- Identify a low-punctuation spelling for slide layout and named-region semantics.
- Distinguish raw-Djot parse validity from a Djot renderer's visible output.
- Reserve syntax that avoids collisions with documented Djot constructs.
- Define the smallest experiments that can select or reject this candidate surface.

## Design philosophy

Use the repository's **scientific method**: treat the directive spelling as a hypothesis and compare
it against real teaching fixtures and deliberately ambiguous inputs before adopting it. Prefer one
visible directive family over Djot containers or attributes that technically work but obscure a
region's scope.

- Evidence strategy for uncertain methods: parse candidate fixtures with a pinned Djot reference
  implementation, inspect the AST and ordinary rendered output, then compare source burden and
  diagnostics with the native Djot alternatives below.

## Scope

- Record a candidate `@` directive family and its intended source-level rules.
- Inventory Djot syntax that is available, reserved, or unsuitable for slide structure.
- Describe parse-validity experiments and acceptance conditions for a later grammar proposal.

## Non-goals

- Selecting Djot as the final language foundation before the fixture comparison.
- Implementing a Djot parser, preprocessor, exporter, renderer, preview, or deck migration.
- Defining the complete reveal, mathematics, notes, metadata, or image-caption grammar.
- Promising compatibility with an unspecified third-party Djot linter.

## Current state summary

Djot's block syntax says indentation is significant only for list-item and footnote nesting. It also
defines ordinary paragraphs as nonblank lines that do not match a documented block construct. The
current syntax reference therefore treats an otherwise ordinary line such as `@ comparison`
as paragraph text. The reference says that anything without a special meaning is literal text.

That is useful but limited compatibility: an unmodified Djot parser accepts the line, while an
unmodified Djot renderer displays it as visible text. The repository-owned slide-language parser
would need to recognize it as slide metadata and keep it out of the native content model.

Djot's own site says that the syntax is not completely stable. The current syntax reference
illustrates a nested list without a blank line, while its Markdown-user quick start still describes
a blank line before a sublist. Freeze the exact reference revision before the language depends on
either behavior.

## Djot design goals

The extension should preserve Djot's design goals as acceptance constraints, not merely borrow its
surface spelling. The candidate therefore has to meet every row below before it can become a grammar.

| Djot design goal | Constraint on the slide extension |
| --- | --- |
| Linear parsing without backtracking | Recognize a marker from its fixed prefix, ASCII name, and current line. Never scan forward to decide whether it is structural. |
| Local inline parsing | Keep slide directives block-level. Their recognition never depends on a later layout declaration or reference definition. |
| Simple emphasis rules | Preserve Djot inline parsing unchanged rather than adding slide-specific inline punctuation. |
| No expressive blind spots | Define a literal escape such as `\@` and reject malformed near-matches with a source location. |
| Simple list ownership | Retain Djot's list and footnote nesting rules unchanged; directives must not alter which content belongs to a list item. |
| No forced Unicode, HTML, entity, or case-folding recognition | Restrict directive keywords and layout/slot identifiers to case-sensitive ASCII. |
| Hard-wrap-friendly source | Require one complete directive line; wrapping ordinary content never manufactures a directive. |
| Uniform composition | Parse a directive node wherever Djot permits a block to begin, then validate whether that node is legal in its structural parent. |
| Arbitrary attributes | Preserve Djot attributes on content nodes without requiring braces for routine slide authoring. |
| Generic containers | Preserve Djot divs and spans for content even though they are not the preferred routine slide-layout syntax. |
| Minimal consistent syntax | Use `@ <layout>` for a slide and select an equally terse region form with no paired braces, containers, or closing fence. |

## Candidate slide boundary

The leading candidate couples the slide boundary with its required layout. A single `@` followed by
one space and the layout name starts every slide:

```djot
@ comparison

# Actin and microtubules
```

Proposed reading, deliberately not yet a contract:

- `@ comparison` starts a new slide and selects exactly one named layout. Every slide therefore
  declares its required layout at its boundary, with no second boundary spelling.
- The following H1 is the slide title when the selected layout accepts a title. The
  layout contract, not source position alone, decides whether it is required.
- The slide marker begins at the current Djot block's left edge and has a blank line before and after
  it. At the root this is column zero; inside a container it follows that container's prefix.
- The extension parses a slide marker node wherever Djot permits a block. Semantic validation then
  permits `@ <layout>` only in the deck body; a marker in a list, quote, footnote, or div receives a
  source-located illegal-placement error, never a silent alternate meaning.
- Fenced and raw code remain opaque and never contain markers. A literal slide-looking line begins
  with `\@`; Djot recognizes the backslash escape and the extension recognizes only an unescaped
  marker at the current block's left edge.

This form settles the slide boundary only. It makes every canonical slide choose one explicit layout,
matching the existing native-layout requirement, while leaving the region spelling open.

## Symbol inventory

The table separates "Djot can parse it" from "the spelling is a good namespace for our extension."
The latter requires avoiding constructs that Djot has already given a block, inline, or filterable
meaning.

| Surface | Djot meaning today | Slide-extension assessment |
| --- | --- | --- |
| `@ name` | Ordinary paragraph text; `@` has no documented block role. | Recommended slide marker. It both starts a slide and selects its layout. |
| `## name` | A standard Djot level-two heading. | Strong region candidate: no new punctuation and a useful raw-Djot document outline. It reserves root H2 for slots. |
| `! name` | Ordinary paragraph text unless followed by `[` as an image. | Candidate one-character region marker. It is distinct, unpaired, and parse-valid, but visually emphatic. |
| `=> name` | Ordinary paragraph text; Djot reserves `=` only in other contexts. | Candidate unpaired mapping marker. It is explicit but costs two characters. |
| `| name` | Ordinary paragraph text unless it forms a complete pipe-table row. | Candidate partition marker, but it visually suggests a table. |
| `: name` | A Djot definition-list item. | Reject: it needs indentation to include definition content. |
| `:: name` | Ordinary paragraph text; Djot generic divs require three or more colons. | Candidate, but too easily confused with a Djot div fence. |
| `:name:` | A Djot inline symbol that a filter may interpret. | Avoid for block structure. |
| `:::` | Opens and closes a Djot generic div. | Available as native Djot, but closing fences add routine punctuation. |
| `{key=value}` | Attaches attributes to the following Djot block. | Preserve for content compatibility, but avoid in normal slide authoring. |
| `#`, `>`, `-`, `+`, `*` | Heading, quote, list, thematic-break, or inline-format syntax. | Reserve for Djot. |
| `^`, `[]`, `|`, backticks | Caption or footnote, link/span, table, and code syntax. | Reserve for Djot. |
| `$` and `$$` | Math prefixes when paired with a verbatim span. | Reserve for mathematics. |
| `%` | Comment delimiter inside Djot attributes. | Avoid as a directive namespace. |

The selected region form should use only lower-case ASCII names made from letters, digits, and
hyphens. It must make malformed near-matches a source-located error instead of inferring intent.

## Native Djot alternatives

The candidate should be compared with syntaxes that are already semantically meaningful to Djot:

```djot
{layout=comparison}
# Actin and microtubules

{slot=left}
- Actin filaments

{slot=right}
- Microtubules
```

This is pure Djot attribute syntax, but each attribute belongs only to the immediately following
block. It cannot delimit a slot containing a list, a paragraph, and an image without inventing more
rules or a container.

An attribute is metadata attached to one parsed element. For example, `{#actin .concept
audience=advanced}` immediately before a heading can give that heading an identifier, a class, and
an application-defined `audience` value. Inline attributes work the same way after an inline element,
such as `ATP{abbr="adenosine triphosphate"}`. Djot preserves the attributes for a renderer or AST
filter to use; it does not require a separate grammar rule for every possible metadata key.

The slide extension should retain attributes on content nodes but must not use arbitrary attributes
as a second layout language. Braces are too costly for routine slide authoring. An attribute like
`{layout=comparison}` is useful prior art and a comparison fixture, not an invisible substitute for
an explicit low-punctuation slide and region surface.

```djot
::: left
- Actin filaments
:::
```

This is a valid Djot div. It supplies a clear container boundary, but its paired fences are the
routine structure the teaching-authoring requirements aim to minimize. It is a comparison fixture,
not the leading surface.

## Compatibility contract

`@ comparison` should be described as **parse-valid Djot**, not as a standard Djot directive. Each
slot candidate must independently meet the same compatibility standard before it is selected.
The official syntax reference documents no `@` block directive, and the Djot repository and syntax
reference do not advertise a separate official linter. A particular editor, formatter, or
third-party lint rule may impose additional policy, so no universal linter-pass promise is possible
without naming and testing that tool.

For the reference parser, a directive line has these expected outcomes:

| Input treatment | Expected ordinary-Djot result | Expected slide-language result |
| --- | --- | --- |
| `@ comparison` at top level | Paragraph containing that literal text. | Start a new slide using `comparison`. |
| `\@ comparison` | Paragraph beginning with literal `@`. | Literal text, never a marker. |
| Slide marker-looking line in a fence or raw block | Literal code content. | Literal content, never a marker. |
| Slide marker in a list, quote, footnote, or div | Paragraph text in that Djot construct. | Marker node followed by an illegal-placement error. |

An ordinary Djot renderer will show directive paragraphs. That is expected during source-only
validation and is not a fallback rendering path. A future repository-owned parser must consume the
markers before mapping Djot content to the typed native-slide model.

## Approach

1. Pin a Djot syntax-reference commit and parser package version for the experiment.
2. Create accepted and rejected specimens for `@ <layout>`, each viable region form, escaped slide
   markers, and marker-looking text in each protected Djot context.
3. Parse every specimen through the pinned Djot implementation and record AST shape plus rendered
   text, without treating successful parsing as slide-language acceptance.
4. Express the fifteen teaching fixtures with the `@` form and each viable region form; compare
   source length, punctuation, layout clarity, diagnostics, and typed native-model mapping.
5. Ask the instructor to select a candidate only after reviewing the fixture evidence and exact
   grammar, including the error cases.

## Files to modify

- `docs/active_plans/decisions/djot_slide_extension_exploration.md` owns this exploratory record.
- `docs/active_plans/decisions/presentation_language_choices.md` remains the cross-foundation
  decision record and links to this narrower exploration.
- `docs/CHANGELOG.md` records this documentation and design-research change.

## Verification

- Run `git diff --check` after the documentation patch.
- Run the repository Markdown-link test after adding the cross-link.
- Treat a reference-parser experiment as required evidence before claiming that the marker surface
  passes a named Djot tool.

## Open questions and decisions needed

- Instructor decision: is the normal-Djot renderer visibly displaying `@ comparison` acceptable for
  source validation, or must an experimental source projection hide slide markers? The one-canonical-
  source rule remains in force regardless.
- Region decision: compare H2 headings, `!`, `=>`, `|`, and other viable unpaired forms across the
  existing teaching fixtures; reject forms that require indentation, look like an existing Djot form,
  or make the raw source harder to read.
- Fixture decision procedure: compare the viable forms above across the existing teaching fixtures.
  Keep the form only if it remains low-punctuation, gives source-located errors, and maps every
  accepted construct to editable native objects.

## Primary sources

- [Djot syntax reference](https://htmlpreview.github.io/?https://github.com/jgm/djot/blob/master/doc/syntax.html):
  current block, list, attributes, div, symbol, and ordinary-text behavior.
- [Djot quick start](https://github.com/jgm/djot/blob/main/doc/quickstart-for-markdown-users.md):
  current Markdown-user guidance, including its list-indentation discussion.
- [Djot repository](https://github.com/jgm/djot): implementation status and rationale.
- [Jotdown](https://github.com/hellux/jotdown): a Rust Djot pull parser with an event interface;
  implementation and validation prior art, not a production dependency or renderer choice.
- [markdown_djot_interview_notes.md](markdown_djot_interview_notes.md): local interview-derived
  design lessons, kept distinct from the written primary specifications.
