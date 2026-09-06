# Djot slide-extension syntax inventory

Status: exploratory grammar note. This page records Djot syntax and parse-valid surface space for a
future slide language. The instructor has designated provisional roles for `===`, `@`, `<=`, and
`=>`; they are not parser adoption. Component images and dollar-delimited mathematics are reserved
separately, while `%%` and the other forms below remain unassigned.

## Context

The instructor is leaning toward extending Djot because its source is readable when hard-wrapped and
does not have indented code blocks. Djot itself has no slide or spatial-layout semantics. The
prior-art evidence remains in [LAYOUT_LANGUAGE_SURVEY.md](../../LAYOUT_LANGUAGE_SURVEY.md) and
[MARP_ADJACENT_PROJECT_COMPARISON.md](../../MARP_ADJACENT_PROJECT_COMPARISON.md).

The future layout catalog will include every default LibreOffice layout plus the custom
`multiple-choice` layout. This does not settle every slot contract or action rule, or make an
ordinary Djot renderer a slide renderer.

## Future ownership boundary

The reusable slide-language work may eventually move to a separate repository from this personal
lecture-content repository. That future split does not authorize a migration, duplicate content, or
a new current source of truth. This page records language exploration where it is happening now.

## Provisional slide surface

These roles are the current working grammar direction. They require representative source cases, a
pinned Djot implementation, and an explicit language-adoption decision before parser or exporter
work.

| Surface form | Provisional role | Constraint |
| --- | --- | --- |
| `=== layout: <name>` | Starts a slide and selects its layout. | It is the sole slide-start spelling; the catalog contains default LibreOffice layouts plus `multiple-choice`. |
| `@<slot>` | Selects a predefined content slot in the selected layout. | The slot name must be declared by that layout; for example, `@left` and `@right`. |
| `<= <action>` | A terminal animation directive applying to the preceding block or list item. | It is an action only as an exact final suffix; otherwise it is ordinary text. |
| `=> <action>` | A prefix animation directive applying to the following block. | It has no closing marker. |
| `=> cascade appear` | A prefix animation directive for the following outline or list. | It reveals that list's top-level items in source order. |

## Candidate figure action

The instructor wants to explore `<= blue overlay` as a terminal action for an authored annotation
or popup highlight. It would be a predefined visual treatment, not a generic `color` or geometry
attribute. A selected layout may give the preceding block a standard overlay position. A future
figure-annotation unit is needed only when an overlay must attach to a particular image region.

## Titles and subtitles

The language retains familiar Marp heading spelling inside a slide:

```djot
# Slide title
## Slide subtitle
```

In a layout with a title region, `#` supplies the title. In a layout with a subtitle region, `##`
supplies the subtitle. A layout without title placement rejects both headings rather than silently
drawing them somewhere else.

## Marp content baseline

Preserve familiar Marp content where it is compatible with Djot: headings, ordinary lists, links,
quotes, monospace blocks, and component images. Djot tables are the official tabular surface. The
documented differences stay explicit: `=== layout:` replaces Marp's `---` slide separator, Djot
supplies the underlying markup rules, and Marp-specific image modifiers are not adopted.

## Linter boundary

The future language needs a fast, deterministic, source-only linter at roughly the enforcement
level of `pyflakes`. It reports source-located structural errors without opening LibreOffice or
rendering a slide. It checks slide declarations, known layouts, title/subtitle permission, slot
names and required/duplicate slots, action attachment, and special layout contracts such as
`multiple-choice`. Geometry, overflow, animation export, and visual quality remain separate checks.

## Official layout: multiple-choice

`multiple-choice` is the first official future-language layout. It has exactly these predefined
slots:

- `@question` contains the question prompt and its ordinary choice list. It is visible
  when the slide opens.
- `@answer` contains the short answer. It appears automatically on the first advance in the
  layout's fixed bottom-right popup region.

`@question` and `@answer` are each required once. The answer slot has its own reveal behavior, so
`<= appear` and `=> appear` are invalid on its content. Open-ended questions use another layout;
the multiple-choice layout does not pretend their answers are short popup text.

Examples:

```djot
=== layout: multiple-choice

@question

- Which molecule carries genetic information?
- A. Lipid
- B. Carbohydrate
- C. DNA
- D. RNA

@answer

Answer: C. DNA
```

## Remaining free block-level surface

| Surface form | Documented Djot behavior | Availability observation |
| --- | --- | --- |
| `@name: value` | Ordinary paragraph text; `@` has no documented block role. | The provisional slot form has no colon; this remains ordinary Djot text. |
| `===== layout: name` | Ordinary paragraph text at block level. | Parse-valid but not an alias of the provisional three-equals slide start. |
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
  rules. The repository math adapter will interpret them with MathJax or a similar plugin.

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

- Native Djot accepts all provisional and free forms above as ordinary paragraphs. The future slide
  parser, not Djot itself, gives the provisional forms their roles.
- The same is true of `=== layout: name` and `===== layout: name`: even an equals-only line has no
  Djot block meaning.
  Djot thematic breaks use three or more `*` or `-` characters with no other content; it has no
  Setext-style equal-sign heading underline.
- `----- layout: name` is likewise not a thematic break, but it is not glyph-stable: Djot smart
  punctuation converts a run of hyphens in ordinary text to en and em dashes. It is therefore not
  a useful visual-boundary candidate.
- An ordinary Djot renderer displays those lines as content. Parse validity is not native slide
  support.
- Code fences and raw blocks remain opaque: a marker-looking line inside them is code, not a future
  language construct.
- Djot's syntax reference is not completely stable. A later experiment needs a pinned reference
  revision and parser implementation before it relies on any edge behavior.
- The Djot project does not advertise an official standalone linter. Compatibility claims therefore
  require naming and testing a particular parser, formatter, or editor rule.

## Deliberately unassigned questions

- How content regions, galleries, captions, and repeated images are represented.
- Which action words beyond `appear` and `cascade appear` are supported, and how their targets are
  bounded in nested content.
- How a floating text box is represented without turning ordinary authoring into a style-attribute
  language.
- Whether the language uses Djot attributes only as native metadata or extends their scope.

## Evidence needed before adoption

1. Pin a Djot syntax-reference revision and implementation.
2. Parse specimens using every surface form above, including code, lists, quotes, footnotes, and divs.
3. Record the AST and ordinary rendered output.
4. Compare the provisional spellings against the teaching source examples before adopting a grammar.

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
