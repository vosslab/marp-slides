# Djot slide-extension syntax inventory

Status: exploratory inventory only. This page records Djot syntax and parse-valid surface space that
may be available to a future slide language. Component images and dollar-delimited mathematics are
reserved separately; no slide, layout, slot, gallery, reveal, caption, note, or styling meaning is
assigned to `@`, `=>`, or `%%`.

## Context

The instructor is leaning toward extending Djot because its source is readable when hard-wrapped and
does not have indented code blocks. Djot itself has no slide or spatial-layout semantics. The
prior-art evidence remains in [LAYOUT_LANGUAGE_SURVEY.md](../../LAYOUT_LANGUAGE_SURVEY.md) and
[MARP_ADJACENT_PROJECT_COMPARISON.md](../../MARP_ADJACENT_PROJECT_COMPARISON.md).

This is not a grammar proposal. In particular, it does not select a layout catalog, decide how
regions end, or make an ordinary Djot renderer a slide renderer.

## Available free block-level surface

| Surface form | Documented Djot behavior | Availability observation |
| --- | --- | --- |
| `@name: value` | Ordinary paragraph text; `@` has no documented block role. | Parse-valid ordinary text; an unmodified Djot renderer displays it. |
| `@name` | Ordinary paragraph text; `@` has no documented block role. | The same free block-level surface without a colon or value. |
| `=> name` | Ordinary paragraph text at block level. | Parse-valid ordinary text; `=` has other Djot uses but no documented `=>` block construct. |
| `=> name other` | Ordinary paragraph text at block level. | The same free block-level surface as above. |
| `=>layout: name` | Ordinary paragraph text at block level. | The same free block-level surface, with a visually distinctive fixed word and colon. |
| `&& name` | No documented Djot block construct begins with `&&`. | Parse-valid free surface to test; it is not used by the layout survey and visually suggests Boolean or shell-and in some contexts. |
| `%% name` or `%%name` | Ordinary paragraph text at block level. | Parse-valid one-sided surface; `%` is a comment delimiter inside attributes, but no closing marker is required by Djot. |
| `%%name%%` | Ordinary paragraph text at block level. | Marp Extended uses this paired form for custom markers; Djot itself gives it no block meaning. |
| Kova's three-vertical-bar delimiter | No documented one-line Djot table construct is formed by this line alone. | It is notable compact prior art but triple repeated characters are not preferred for ordinary authoring, and `|` is table punctuation. Its literal source is shown below the table. |
| `. . .` | No documented Djot block construct begins with this spaced line. | Quarto Reveal uses it as a bare pause; it remains an unassigned free surface here. |
| `::name::` | Not a Djot generic div fence, which begins with at least three colons. | Slidev uses forms such as `::right::` as named slots; Djot's inline symbol syntax also uses colons, so its exact AST needs testing. |

### Literal Kova delimiter

<pre>|||</pre>

`## name` is deliberately absent: it is already a Djot heading, not free extension surface. The same
is true of attributes, generic divs, definition lists, pipe tables, footnotes, native Djot math,
quotes, lists, code, links, spans, and inline-format delimiters.

The layout survey is evidence of source shapes, not an adoption list: `|||` appears in Kova,
`. . .` in Quarto Reveal, `::right::` in Slidev, and `%%marp-*%%` in Marp Extended. Their survey
semantics do not transfer to Djot merely because their raw lines parse. In particular, the one-sided
`%% name` form is available to test without importing Marp Extended's closing-marker requirement.

## Reserved forms

- `![alt](path)` is the official component-image form. It is unavailable for slide, layout, region,
  reveal, or other extension syntax. This reservation covers the ordinary Marp and Djot image
  surface only; it does not adopt Marp-specific background, sizing, positioning, or filter modifiers.
- `$inline$` and `$$display$$` are the official inline and display mathematics forms. They are
  unavailable for extension structure, even though they are ordinary text under native Djot math
  rules.

## Attribute scope

Djot attributes are metadata attached to an element. For example:

```djot
{source=electron-microscopy}
![Microtubule](assets/microtubule.png)
```

The attribute belongs to that image, not to a later sequence of blocks. A generic div can group
multiple blocks, but requires `:::` opening and closing fences. Djot permits multiline attributes;
that is a documented capability, not a recommendation for a future slide surface.

## Parse-validity boundaries

- Lines using `@`, `=>`, or `%%` are accepted as ordinary Djot paragraphs unless a future parser
  assigns them a different meaning.
- An ordinary Djot renderer displays those lines as content. Parse validity is not native slide
  support.
- Code fences and raw blocks remain opaque: a marker-looking line inside them is code, not a future
  language construct.
- Djot's syntax reference is not completely stable. A later experiment needs a pinned reference
  revision and parser implementation before it relies on any edge behavior.
- The Djot project does not advertise an official standalone linter. Compatibility claims therefore
  require naming and testing a particular parser, formatter, or editor rule.

## Deliberately unassigned questions

- Which available form, if any, starts a slide or selects a layout.
- How content regions, galleries, captions, and repeated images are represented.
- How an on-advance action or floating text box is represented.
- Whether the language uses Djot attributes only as native metadata or extends their scope.
- Which math plugin interprets the reserved dollar-delimited math surface.

## Evidence needed before assignment

1. Pin a Djot syntax-reference revision and implementation.
2. Parse specimens using every surface form above, including code, lists, quotes, footnotes, and divs.
3. Record the AST and ordinary rendered output.
4. Compare a small number of complete spellings against the teaching fixtures only after the syntax
   inventory has been reviewed.

## Primary sources

- [Djot syntax reference](https://htmlpreview.github.io/?https://github.com/jgm/djot/blob/master/doc/syntax.html):
  current block, list, attributes, div, symbol, and ordinary-text behavior.
- [Djot quick start](https://github.com/jgm/djot/blob/main/doc/quickstart-for-markdown-users.md):
  Markdown-user guidance, including list-indentation discussion.
- [Djot repository](https://github.com/jgm/djot): implementation status and rationale.
- [Jotdown](https://github.com/hellux/jotdown): a Rust Djot pull parser with an event interface;
  implementation and validation prior art, not a production dependency or renderer choice.
- [John MacFarlane interview notes](markdown_djot_interview_notes.md): local interview-derived
  design lessons, kept separate from the written primary specifications.
