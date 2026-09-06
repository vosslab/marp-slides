# Lecture 02 syntax-gap survey

Status: exploratory content survey. This records the authoring needs visible in the six local legacy
`genetics/lect02*` ODP/PDF pairs. It assumes every default LibreOffice layout and the custom
`multiple-choice` layout exist. It does not authorize a deck migration or a parser implementation.

## Evidence examined

The survey visually reviewed the current PDF exports and extracted text and animation metadata from
the editable ODP files. A fresh, temporary LibreOffice PDF export produced the same visible-page
counts as the supplied PDFs.

| Deck | Visible slides | ODP slides with animations | Observed animation use |
| --- | ---: | ---: | --- |
| `lect02a-2025_announcements` | 43 | 0 | None |
| `lect02b-genes_dogma` | 49 | 6 | Multiple-choice answers |
| `lect02c-genome_sizes` | 59 | 5 | Multiple-choice answers |
| `lect02d-dna_structure_overview` | 43 | 4 | Multiple-choice answers |
| `lect02e-restriction_enzymes` | 62 | 3 | Stepwise labels and highlights on sequence diagrams |
| `lect02f-dna_electrophoresis` | 26 | 1 | Stepwise gel-band labels |

The six decks contain 282 visible slides. The 15 animated multiple-choice slides use only an
on-click answer appearance; the remaining four use on-click appearance for individual diagram
elements.

## Already covered

These source forms need no new slide-extension syntax, given the assumed layout catalog.

| Authoring need | Examples in Lecture 02 | Existing surface or decision |
| --- | --- | --- |
| Title, subtitle, and section divider | Every deck | `#`, `##`, and selected layout |
| Ordinary and nested teaching lists | Agendas, definitions, quiz policy, problem prompts | Djot lists |
| Static photographs, screenshots, charts, and textbook figures | Announcements, genetics history, genome-size, and gel slides | Marp image syntax with descriptive alt text |
| Multiple-choice question followed by a short answer | Genes, genome-size, and DNA-sequence questions | `multiple-choice` with automatic `@answer` appearance |
| Worked reasoning shown one stage at a time | Palindrome, restriction-map, and gel problems | A normal series of slides, not reveal syntax |
| Links and cited clarifications | Zoom, YouTube, and textbook material | Djot links and audience-facing footnotes |

In particular, a multi-step worked problem should remain a series of slides. It does not justify a
clone, continuation, or step-by-step problem language feature.

## Settled content surface

These are settled parts of the Djot-compatible content surface, not syntax gaps or requests for new
extension punctuation. The future implementation must render them as native editable content.

| Need | Lecture 02 evidence | Required behavior |
| --- | --- | --- |
| Tables | Experimental-result grids, genome comparisons, recognition-site reference | Use Djot tables and render them as native readable tables. Table cells may remain static across a slide series. |
| Fixed-width sequence text | Complementary-DNA and restriction-site exercises | Use a native editable monospace block; no DNA-specific syntax is needed. |
| Inline and display mathematics | Base composition, genome-size values, and chemistry notation | Use reserved `$inline$` and `$$display$$` forms through MathJax or a similar plugin. |
## Conditional syntax gap

### Image-specific overlay anchoring

Several slides place explanatory labels, arrows, colored callouts, or highlighted bands over a
diagram. The clearest examples are the stepwise restriction-site diagrams in `lect02e` and the
electrophoresis problem in `lect02f`. The present `<=` action can apply to a preceding text block or
list item. It is sufficient when the selected layout places that preceding block in its standard
popup or overlay region.

There is no further syntax gap if `text <= blue overlay` always uses that standard layout-defined
position. The language needs one additional figure-annotation contract only when a popup must point
to or highlight a particular region inside a Marp image:

- An authored annotation is a semantic unit containing its text or highlight.
- It attaches to a figure or a declared diagram target, rather than an arbitrary page coordinate.
- It can receive a bounded terminal action such as `<= appear`.
- A layout or annotation recipe chooses native placement and any arrow or highlight treatment.

This is not a request for CSS-like `x`, `y`, `color`, or `size` attributes. Static legacy diagrams
remain Marp images; the contract is needed only for image-specific, on-click annotations.

### Candidate `blue overlay` action

The instructor wants to explore `<= blue overlay` for a popup highlight over an authored unit. It
would be a predefined terminal action, not a general styling language. A standard layout-defined
overlay position needs no additional target syntax; an image-specific overlay uses the conditional
annotation contract above.

## Deliberately not gaps

- The observed grids, two-panel slides, vertical title slides, galleries, and centered prompts do
  not establish a layout gap because this survey assumes the complete LibreOffice catalog.
- The multiple-choice answer reveals do not establish a general popup requirement; the selected
  `multiple-choice` layout already gives `@answer` its automatic first-advance behavior.
- The source does not justify presenter-note syntax, arbitrary timing tracks, motion paths, or a
  generic color or geometry attribute bag.
- Red and colored words in legacy slides are not yet a separate inline-language requirement. First
  test whether ordinary emphasis, named callout treatment, or the proposed annotation action keeps
  their intended teaching meaning.

## Survey outcome

Djot tables, monospace blocks, dollar-delimited math, Marp images, and accessible text are settled
coverage. No additional slide layout, worked-problem, or multiple-choice syntax is indicated. The
only conditional addition is a figure-annotation target for image-specific overlays; a standard
layout popup with `<= blue overlay` needs no further syntax.
