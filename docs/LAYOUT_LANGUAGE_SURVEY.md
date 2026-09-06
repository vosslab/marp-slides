# Layout-language survey

## The decision this survey supports

Classic Marp is known not to express the required spatial layouts. This document therefore supports
the remaining language decision: define a small extension language for structured slides, or adopt
a different Markdown presentation language. It does not implement a parser or exporter, adopt
syntax, or create a future extension-language guide.

Markdown is strong at content hierarchy. Slides need spatial hierarchy. The language must bridge
that gap without making a hand-authored lecture deck a forest of comments, HTML, or containers.

Classic Marp Core v5 remains the upstream baseline. [MARP_SYNTAX_GUIDE.md](MARP_SYNTAX_GUIDE.md)
describes only source compatible with Marp CLI; it deliberately does not define local slide regions.
The repository-owned Python parser and native editable-object exporter are the future
interpretation and rendering boundary. A later extension need not run through Marp CLI. "Marp+"
below is a working label, not an approved name or decision.

For local-project inventory and broader relevance, see
[MARP_ADJACENT_PROJECT_COMPARISON.md](MARP_ADJACENT_PROJECT_COMPARISON.md). The broader visitor
guide remains [RELATED_PROJECTS.md](RELATED_PROJECTS.md).

## Method

Every candidate is checked against these fourteen one-slide fixtures. Source is literal where a
documented form exists. "No documented form" is a result, not an invitation to invent a CSS
convention. Assets are local and content is intentionally short so structural punctuation is clear.
The `<!-- Fixture ... -->` lines inside some specimens are survey labels only; they are not
required source unless the surrounding discussion identifies them as a candidate's real directive.

| Fixture | Structure |
| --- | --- |
| 1 | Title only |
| 2 | Title and subtitle |
| 3 | Ordinary title and body |
| 4 | Nested bulleted and numbered list |
| 5 | Two equal content panels |
| 6 | Two unequal content panels |
| 7 | Image left and text right |
| 8 | Text left and image right |
| 9 | Three or four content regions |
| 10 | Image and caption |
| 11 | Gallery |
| 12 | Quote or callout |
| 13 | Reusable custom named teaching layout |
| 14 | Minimal inline and display equation |

### Shared Markdown fixtures

Candidates that say "ordinary Markdown" use these literal forms for fixtures 1 through 4. A
candidate may give a heading special layout treatment, but list nesting remains ordinary and
readable.

```markdown
# Cytoskeleton
```

```markdown
# Cytoskeleton

The cell's structural system
```

```markdown
## Motor proteins

Motor proteins produce directed movement.
```

```markdown
## Polymer systems

- Microtubules
  1. Grow by tubulin addition
  2. Shrink by catastrophe
- Actin filaments
  - Support membrane shape
```

### Equation fixture

Every candidate is also screened for enough mathematics to support an ordinary biology or chemistry
lecture. The target is LaTeX-compatible syntax, or an equally capable hand-writable alternative,
for inline and display math. This fixture intentionally excludes equation numbering,
cross-references, citation syntax, and other scientific-publishing features:

```markdown
## ATP hydrolysis

The reaction has a negative free-energy change: $\Delta G < 0$.

$$
\Delta G = \Delta G^\circ + RT \ln Q
$$
```

## Established presentation languages

### Classic Marp: the baseline

Fixtures 1 through 4 use the shared Markdown. Fixture 2's second paragraph is not a standard Marp
subtitle, and Marp has no standard content-region vocabulary.

```markdown
<!-- Fixture 5: no portable equal-panel source exists. -->

<!-- Fixture 6: visual background split, not semantic panels. -->
![bg left:33%](assets/cytoskeleton.png)
## Motor proteins
Motor proteins produce directed movement.

<!-- Fixture 7: image left, text right. -->
![bg left:50%](assets/cytoskeleton.png)
## Motor proteins
Motor proteins produce directed movement.

<!-- Fixture 8: text left, image right. -->
![bg right:50%](assets/cytoskeleton.png)
## Motor proteins
Motor proteins produce directed movement.

<!-- Fixture 9: no portable three- or four-region source exists. -->

<!-- Fixture 10: text following an image is not a semantic caption. -->
![Mitotic spindle](assets/cytoskeleton.png)
*Figure: microtubules separate chromosomes.*

<!-- Fixture 11: gallery geometry is theme-specific. -->
![Actin](assets/actin.png) ![Tubulin](assets/tubulin.png) ![Myosin](assets/myosin.png)

<!-- Fixture 12: ordinary quote. -->
> Form follows biological function.

<!-- Fixture 13: standard directive, but class meaning is not standard. -->
<!-- _class: biology-comparison -->
## Cytoskeleton
```

The image forms make fixtures 6 through 8 look convenient, but they are visual instructions rather
than a durable model of `left`, `right`, image, or caption regions. A class alone is likewise not a
portable teaching-layout contract.

### Quarto Reveal and Quarto PowerPoint

Quarto gives fixtures 1 and 2 semantic metadata. Fixtures 3 and 4 are the shared Markdown with
level-two headings after metadata. The same fenced-div source works for Reveal and PowerPoint by
changing the format; PowerPoint then maps recognized structures to a reference presentation.

```markdown
---
title: "Cytoskeleton"
subtitle: "The cell's structural system"
format: revealjs
---
```

```markdown
<!-- Fixture 5: equal panels. -->
## Polymer systems

:::: {.columns}
::: {.column width="50%"}
Microtubules
:::
::: {.column width="50%"}
Actin filaments
:::
::::

<!-- Fixture 6: unequal panels. -->
## Motor proteins

:::: {.columns}
::: {.column width="40%"}
Motor head
:::
::: {.column width="60%"}
ATP hydrolysis drives a conformational change.
:::
::::

<!-- Fixture 7: image left, text right. Reverse source order for fixture 8. -->
## Mitotic spindle

:::: {.columns}
::: {.column width="50%"}
![Mitotic spindle](assets/cytoskeleton.png)
:::
::: {.column width="50%"}
Microtubules separate chromosomes.
:::
::::

<!-- Fixture 9: three regions. Add another column for four. -->
:::: {.columns}
::: {.column width="33%"}
Actin
:::
::: {.column width="33%"}
Tubulin
:::
::: {.column width="33%"}
Intermediate filaments
:::
::::

<!-- Fixture 10: figure caption. -->
![Mitotic spindle](assets/cytoskeleton.png){fig-cap="Microtubules separate chromosomes."}

<!-- Fixture 11: gallery. -->
:::: {.columns}
::: {.column width="33%"}
![Actin](assets/actin.png)
:::
::: {.column width="33%"}
![Tubulin](assets/tubulin.png)
:::
::: {.column width="33%"}
![Myosin](assets/myosin.png)
:::
::::

<!-- Fixture 12: callout. -->
::: {.callout-note}
## Key idea
Structure constrains cellular movement.
:::

<!-- Fixture 13: class requires a format extension to define its effect. -->
::: {.teaching-comparison}
## Cytoskeleton
:::
```

This is explicit and easy to parse, but a two-panel slide adds eight fence lines. It is an
excellent semantic benchmark, not an attractive smallest hand-written grammar. In Quarto
PowerPoint, Pandoc's writer selects a reference layout and does not honor the shown widths.

### Pandoc PowerPoint

Pandoc PowerPoint is separate because its reference-document and layout-inference model directly
informs native editable-PPTX work. Fixtures 1 through 4 use ordinary Pandoc metadata and shared
Markdown.

```markdown
---
title: "Cytoskeleton"
subtitle: "The cell's structural system"
---

<!-- Fixture 5: equal panels. -->
## Polymer systems

:::: {.columns}
::: {.column}
Microtubules
:::
::: {.column}
Actin filaments
:::
::::

<!-- Fixture 7: image left, text right. Reverse source order for fixture 8. -->
## Mitotic spindle

:::: {.columns}
::: {.column}
![Mitotic spindle](assets/cytoskeleton.png)
:::
::: {.column}
Microtubules separate chromosomes.
:::
::::

<!-- Fixture 10: normal image source. -->
![Mitotic spindle](assets/cytoskeleton.png)

<!-- Fixture 12: ordinary quote. -->
> Form follows biological function.
```

The PowerPoint writer ignores column widths, so it cannot state fixture 6's ratio. Fixtures 9, 11,
and 13 have no stable documented source-level layout selection. Pandoc is evidence for keeping
native geometry in an explicit layout registry, not for adopting its source grammar wholesale.

### Slidev

Slidev makes a layout explicit in YAML and gives selected layouts named slots. Fixtures 1 through 4
use normal Markdown inside the chosen layout, preserving the shared list nesting.

```markdown
---
layout: cover
---

# Cytoskeleton

The cell's structural system
```

```markdown
---
layout: two-cols
---

<!-- Fixture 5: equal panels. -->
## Polymer systems

Microtubules

::right::

Actin filaments
```

```markdown
---
layout: image-left
image: /assets/cytoskeleton.png
---

<!-- Fixture 7: image left, text right. -->
## Mitotic spindle

Microtubules separate chromosomes.
```

```markdown
---
layout: image-right
image: /assets/cytoskeleton.png
---

<!-- Fixture 8: text left, image right. -->
## Mitotic spindle

Microtubules separate chromosomes.
```

```markdown
---
layout: quote
---

<!-- Fixture 12: quote. -->
> Form follows biological function.
```

There is no built-in documented unequal two-column, three/four-region, or gallery source for
fixtures 6, 9, and 11. A custom theme component can supply a named layout:

```markdown
---
layout: teaching-comparison
---

<!-- Fixture 13: slots are defined by the custom component. -->
# Cytoskeleton

::left::
Microtubules

::right::
Actin filaments
```

This is a compelling source shape: a short layout name and short slot marker. Custom layouts and
slots are Vue/theme components, however, so their source contract is less portable than it appears.
Normal Markdown images have no separate documented caption or gallery semantic.

### Kova

Kova is inference-first. Fixture 1 is an H1; fixture 2 is an H1 followed by a paragraph. Fixtures
3 and 4 use the shared Markdown with an H2 and body, including ordinary nested lists.

```markdown
<!-- Fixture 5: equal panels. -->
## Polymer systems

Microtubules

|||

Actin filaments

<!-- Fixture 7: image then text infers image left, text right. -->
## Mitotic spindle

![Mitotic spindle](assets/cytoskeleton.png)

Microtubules separate chromosomes.

<!-- Fixture 9: three equal regions. -->
## Cytoskeletal polymers

Actin

|||

Tubulin

|||

Intermediate filaments

<!-- Fixture 10: alt text only; no separate caption form was found. -->
![Mitotic spindle](assets/cytoskeleton.png)

<!-- Fixture 11: four elements infer a grid. -->
![Actin](assets/actin.png)
![Tubulin](assets/tubulin.png)
![Myosin](assets/myosin.png)
![Kinesin](assets/kinesin.png)

<!-- Fixture 12: isolated quote. -->
> Form follows biological function.

<!-- Fixture 13: force an existing layout. -->
<!-- layout:grid -->
## Cytoskeletal proteins
```

There is no documented unequal-width source for fixture 6 or reverse-split source for fixture 8.
Four or more blocks trigger a grid but do not name its regions. `|||` is the lowest-noise panel
syntax surveyed, but layout is primarily heuristic. Its manual override uses an HTML comment, which
is an appropriate exception but a poor everyday language primitive.

### reveal.js Markdown

reveal.js is a useful FOSS baseline from the linked presentation list. It parses Markdown in an
HTML slide host; fixtures 1 through 4 are the shared Markdown inside the host.

```html
<section data-markdown>
  <textarea data-template>
# Cytoskeleton

---

## Polymer systems

- Microtubules
  1. Grow by tubulin addition
  2. Shrink by catastrophe
  </textarea>
</section>
```

It exposes HTML and comment attributes instead of a Markdown region grammar:

```markdown
<!-- Fixture 5: raw HTML panels. -->
<div class="columns">
  <div>Microtubules</div>
  <div>Actin filaments</div>
</div>

<!-- Fixture 7: comment-driven background. -->
<!-- .slide: data-background-image="assets/cytoskeleton.png" -->
## Mitotic spindle
Microtubules separate chromosomes.

<!-- Fixture 13: CSS class, not a named Markdown layout. -->
<!-- .slide: class="teaching-comparison" -->
```

It is flexible but confirms the core problem: when a slide needs regions, authors return to raw
HTML and comments.

### Minimal equation handling

The equation fixture is deliberately a separate requirement from layout. A language can have
excellent columns yet be unsuitable if it cannot handle a short inline equation and one displayed
equation without an external scientific-writing workflow.

| System | Literal source for fixture 14 | Boundary |
| --- | --- | --- |
| Classic Marp | `$...$` and `$$...$$` with an enabled KaTeX or MathJax plugin | Optional Marp Core capability; native editable mapping remains unchosen |
| Quarto Reveal and PowerPoint | The shared equation fixture | Pandoc mathematics is built into the authoring model |
| Pandoc PowerPoint | The shared equation fixture | PPTX rendering and editability depend on the writer's math route |
| Slidev | The shared equation fixture | Math support is renderer/theme configuration |
| Kova | `$...$` and `$$...$$` | Its documented math layout recognizes display-math slides |
| reveal.js Markdown | The shared equation fixture plus a math plugin | Not part of Markdown layout syntax itself |
| MarpX and Marp Extended | Marp math source inherited by their Marp engine | Still depends on the Marp math capability |
| Lectern | The shared equation fixture | Its renderer owns math output behavior |
| Awesome Marp Template | No compact equation contract surveyed | Plugin configuration would be another extension layer |
| MDPR | No equation-output contract surveyed | Intermediate model evidence is insufficient |
| MarkItDown | Not applicable | It is not a presentation language |

## Marp extensions and Marp-adjacent attempts

These projects are attempts to bridge a linear Marp document into a spatial slide model. Their added
punctuation and runtime coupling are part of the comparison, not a reason to keep Marp.

### MarpX: semantic classes plus HTML containers

Local [MarpX](OTHER_REPOS/MARPX.md) adds useful names such as `title`, `chapter`, and `quote`, but
uses raw HTML for title fields, callouts, and columns.

```html
<!-- Fixture 2: title and subtitle. -->
<!-- _class: title-academic -->
<div class="title">Cytoskeleton</div>
<div class="subtitle">The cell's structural system</div>

<!-- Fixture 5: equal panels. -->
<!-- _class: title -->
# Polymer systems
<div class="multicolumn" valign="center" align="center">
  <div>Microtubules</div>
  <div>Actin filaments</div>
</div>

<!-- Fixture 12: named quote treatment. -->
<!-- _class: quote dark -->
> Form follows biological function.
```

It proves the value of semantic names, but regions, ratios, captions, galleries, and custom layouts
remain HTML/CSS behavior rather than a compact Markdown model.

### Lectern: comments and placed containers

Local [Lectern](OTHER_REPOS/LECTERN_SLIDES.md) provides highly explicit source-aware placement:

```markdown
<!-- Fixture 2: title and subtitle. -->
<!-- slide: .center .middle .inverse -->
# Cytoskeleton
## The cell's structural system

<!-- Fixture 5: equal panels. -->
<!-- slide: #two-panels -->
# Polymer systems

::: {.place .middle .left}
Microtubules
:::

::: {.place .middle .right}
Actin filaments
:::

<!-- Fixture 10: image and placed caption. -->
![Mitotic spindle](assets/cytoskeleton.png)
::: {.place .bottom .right .footnote}
Microtubules separate chromosomes.
:::
```

More `.place` blocks make fixture 9 possible; unequal panels and image/text sides need further
classes or CSS. Lectern parses cleanly into a positional model, but free placement makes everyday
hand authoring comment and fence heavy.

### CDL Slides: broad preprocessor and CSS

Local [CDL Slides](OTHER_REPOS/CDL_SLIDES.md) turns Markdown into a broad preprocessor language.
Its examples use theme classes and raw flex containers for a two-panel source:

```html
<div style="display: flex; gap: 2rem;">
  <div>Microtubules</div>
  <div>Actin filaments</div>
</div>
```

It has a useful feature inventory, but layout is coupled to a preprocessor plus CSS/HTML. That is
the high-capability, high-complexity direction this decision should avoid.

### Marp Extended for Obsidian: preprocessed markers

[Marp Extended] adds an Obsidian-friendly preprocessor layer where Marp has no equivalent. Content
stays ordinary Markdown, but regions are opened, split, and closed with markers:

```markdown
%%marp-slide[class=cover]%%

%%marp-lead%%
# Cytoskeleton
%%/marp-lead%%

%%marp-subtitle%%
The cell's structural system
%%/marp-subtitle%%

%%marp-columns%%
### Microtubules
- Grow by tubulin addition

%%marp-column%%
### Actin filaments
- Support membrane shape
%%/marp-columns%%

%%marp-callout[variant=note]%%
Structure constrains cellular movement.
%%/marp-callout%%
```

This is a clear existing Marp+ attempt: it names columns, cards, callouts, metadata, and subtitle
behavior. It also exposes the cost of nesting and closing every region with `%%marp-*%%`
punctuation, and of tight Obsidian and Marp CLI integration.

### Awesome Marp Template: Markdown-it containers

[Awesome Marp Template] loads a custom Marp engine and Markdown-it plugins. It uses container
fences and CSS classes to turn sequential content into columns:

```markdown
:::c
:::_
## Microtubules
Grow by tubulin addition.
:::
:::_
## Actin filaments
Support membrane shape.
:::
:::
```

Nesting means increasing the number of colons. That is mechanically clear but becomes visually
dense for fixture 9 or a gallery. Its output remains CSS/theme dependent, and its engine is not
ordinary Marp CLI or editor syntax.

### MDPR: intermediate model plus separate overrides

MDPR's ordinary Markdown covers fixtures 1 through 4 and then derives presentation and layout
intermediate representations. It exposes no compact in-Markdown region syntax for the remaining
fixtures. Its documented manual choice is a separate YAML operation:

```yaml
version: "1.0"
operations:
  - op: setLayout
    target:
      title: "Polymer systems"
    value:
      preset: comparison
      direction: horizontal
      columns: 2
      reason: "Keep the two polymers visually comparable."
```

This is valuable native-export architecture and an honest escape hatch, but a title-addressed
override file is not pleasant source for a hand-authored gallery or reusable teaching layout. Its
public repository had no explicit license file or GitHub license label during this review, so it is
excluded from the FOSS adoption set.

### Microsoft MarkItDown: not a presentation language

MarkItDown is MIT-licensed, but it converts files to Markdown for text analysis. It has no
deck-input syntax for fixtures 1 through 14, no layout language, and no presentation renderer. It
belongs only in a later import/evidence comparison.

## Authoring-property scorecard

Scores are 1 (weak or high burden) through 5 (strong or low burden). They rate source language for
these fixtures, not the overall quality of a project. The final column says whether structural HTML
comments are a normal authoring mechanism.

| System | Overhead | Readable | Hand-write | Nesting | Equations | Semantic clarity | Reuse | Native parse | Comments |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Classic Marp | 5 | 5 | 5 | 5 | 3 | 1 | 2 | 2 | Optional directives |
| Quarto Reveal | 2 | 3 | 3 | 5 | 5 | 5 | 4 | 5 | Not normal |
| Quarto PowerPoint | 2 | 3 | 3 | 5 | 4 | 4 | 4 | 4 | Not normal |
| Pandoc PowerPoint | 2 | 3 | 3 | 5 | 4 | 3 | 3 | 4 | Not normal |
| Slidev | 4 | 4 | 4 | 5 | 4 | 4 | 5 | 4 | Not normal |
| Kova | 5 | 5 | 5 | 5 | 4 | 3 | 3 | 3 | Override only |
| reveal.js Markdown | 2 | 2 | 2 | 5 | 2 | 1 | 4 | 2 | Normal for attributes |
| MarpX | 2 | 3 | 2 | 5 | 3 | 3 | 3 | 2 | Normal for classes |
| Lectern | 2 | 3 | 2 | 5 | 4 | 5 | 4 | 5 | Normal for placement |
| Marp Extended | 3 | 3 | 3 | 5 | 3 | 4 | 4 | 4 | Marker syntax |
| Awesome Marp Template | 2 | 3 | 2 | 4 | 2 | 3 | 3 | 4 | No, but nested fences |
| MDPR override model | 1 | 3 | 1 | 5 | 1 | 3 | 4 | 4 | Separate YAML |
| MarkItDown | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

Kova and Slidev offer the strongest authoring lessons. Kova shows that a one-line separator is
pleasant but too implicit for asymmetry and durable output mapping. Slidev shows that a named
layout plus named slot can stay short. Quarto, Marp Extended, and Lectern show the opposite
tradeoff: explicit grouping parses well but becomes fence or marker heavy. MarpX, CDL, and
reveal.js show that CSS classes, comments, and raw HTML do not solve the source-language problem.

## Decision branches, not a recommendation

Standard Marp is a compatibility baseline and migration reference, not a viable final language for
spatial slides. The remaining choices are to extend it or to adopt another Markdown presentation
language. This survey does not recommend either branch.

### Branch A: define a small extension

Existing Marp extensions expose several viable mechanisms. Each has a different tradeoff:

| Mechanism | Existing evidence | Strength | Cost |
| --- | --- | --- | --- |
| Theme classes | MarpX and Marp templates | Familiar, concise slide treatment names | Does not name child regions |
| Comment directives | Existing `_cell` transition candidate and Lectern | Linear source, precise named placement | Comments become routine structure |
| Visible split delimiter | Kova's `|||` | Extremely quick equal panels | Cannot name regions or express asymmetry |
| Marker blocks | Marp Extended | Explicit columns, cards, callouts, and metadata | Open/split/close punctuation grows with nesting |
| Fenced containers | Quarto and Markdown-it extensions | Complete nested structure and easy AST | Verbose for a simple two-panel slide |
| Layout plus slots | Slidev | Concise named layout with explicit regions | Current examples couple it to Vue/theme components |

One possible, deliberately unadopted, container-free design is a layout line plus named slots:

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

Here, `@layout NAME` would select a registered teaching layout and `:: SLOT` would begin a named
region through the next slot or slide boundary. The layout registry would own slot names, geometry,
reading order, and the editable PPTX/ODP builder. This illustrates a low-punctuation option; it is
not a proposal that has been selected over comment markers, delimiters, or fenced containers.

### Branch B: adopt another language

The FOSS candidates provide different complete answers rather than interchangeable syntax:

| Candidate | What would be adopted with the source grammar |
| --- | --- |
| Quarto Reveal | Pandoc document model, fenced-div layout syntax, and browser presentation route |
| Quarto PowerPoint | Pandoc source and reference-PPTX inference model |
| Pandoc PowerPoint | Reference-document-driven PPTX writer with limited source geometry |
| Slidev | YAML layouts, named slots, Vue/theme components, and Node tooling |
| Kova | Desktop presentation application and inference-first layout engine |
| reveal.js Markdown | Browser host, HTML slide structure, and Markdown plugin |

Before either branch is chosen, use the complete fourteen-fixture deck for source review, parser
diagnostics, editable native-object evidence, and rendered teaching-slide review. Create neither an
extension-language guide nor implementation changes until the instructor selects a branch and
language form.

## Primary sources

- [Kova layout reference]
- [Quarto Reveal presentation guide]
- [Quarto PowerPoint presentation guide]
- [Pandoc PowerPoint writer]
- [Slidev layout guide]
- [Slidev built-in layouts]
- [reveal.js Markdown guide]
- [Marp Extended]
- [Awesome Marp Template]
- [MDPR]
- [Microsoft MarkItDown]
- [Markdown-presentation list]

[Kova layout reference]: https://wiki.kova.md/layouts/
[Quarto Reveal presentation guide]: https://quarto.org/docs/presentations/revealjs/
[Quarto PowerPoint presentation guide]: https://quarto.org/docs/presentations/powerpoint.html
[Pandoc PowerPoint writer]: https://pandoc.org/MANUAL.html
[Slidev layout guide]: https://sli.dev/guide/layout
[Slidev built-in layouts]: https://sli.dev/builtin/layouts
[reveal.js Markdown guide]: https://revealjs.com/markdown/
[Marp Extended]: https://github.com/shuuul/obsidian-marp-extended
[Awesome Marp Template]: https://github.com/yKicchan/awesome-marp-template
[MDPR]: https://github.com/ch040602/MdPr
[Microsoft MarkItDown]: https://github.com/microsoft/markitdown
[Markdown-presentation list]: https://gist.github.com/johnloy/27dd124ad40e210e91c70dd1c24ac8c8
