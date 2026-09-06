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

Both branches keep that repository-owned pipeline. "Adopt" means reuse or adapt another language's
source grammar and semantics, then implement them locally; it never means adopting the candidate's
renderer, browser, Node tooling, or output pipeline.

For local-project inventory and broader relevance, see
[MARP_ADJACENT_PROJECT_COMPARISON.md](MARP_ADJACENT_PROJECT_COMPARISON.md). The broader visitor
guide remains [RELATED_PROJECTS.md](RELATED_PROJECTS.md). Rendered legacy-deck evidence is recorded
separately in [LECTURE_LAYOUT_SURVEY.md](LECTURE_LAYOUT_SURVEY.md).

## Method

Every candidate must be checked against these fifteen one-slide fixtures. Source is literal where a
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
| 15 | Simple staged reveal: appear an authored item or outline one bullet at a time |

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

### Reveal fixture

Fixture 15 specifies teaching behavior, not a chosen spelling. It must keep the slide source
ordinary and readable while presenting the three outline items in source order on successive
advances. A future literal comparison must show the source each candidate requires for this fixture,
including a nested-list example.

```markdown
## Types of gene disorders

- Point mutation
- Chromosome deletion
- Chromosome duplication
```

The required behavior is intentionally narrow: reveal an authored content item or one list item at
a time. It does not require motion paths, timing tracks, coordinated effects, or a general-purpose
animation language. The rendered legacy-deck audit found no stored ODP animations, so this is a new
capability requirement rather than an inferred legacy syntax.

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
excellent semantic benchmark, not an attractive smallest hand-written grammar. The source can
express unequal widths; the local pipeline would map those semantics to its own layout registry
rather than inheriting Quarto PowerPoint's layout behavior.

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

Pandoc Markdown can state fixture 6's ratio with its column attributes, although its own PowerPoint
writer may not honor them. Fixtures 9, 11, and 13 have no stable documented source-level layout
selection. A local parser could retain the useful source semantics while mapping them to its own
native layout registry.

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

| System | Literal source for fixture 14 | Source-language boundary |
| --- | --- | --- |
| Classic Marp | `$...$` and `$$...$$` with an enabled KaTeX or MathJax plugin | Optional Marp Core source capability |
| Quarto Reveal and PowerPoint | The shared equation fixture | Pandoc mathematics is built into the authoring model |
| Pandoc PowerPoint | The shared equation fixture | Equation syntax is present; source layout remains limited |
| Slidev | The shared equation fixture | Math syntax is part of its extended Markdown authoring model |
| Kova | `$...$` and `$$...$$` | Its documented math layout recognizes display-math slides |
| reveal.js Markdown | The shared equation fixture plus a math plugin | Not part of Markdown layout syntax itself |
| MarpX and Marp Extended | Marp math source inherited by their Marp engine | Still depends on the Marp math capability |
| Lectern | The shared equation fixture | Its source form is compatible with its math extension |
| Awesome Marp Template | No compact equation contract surveyed | Plugin configuration would be another extension layer |
| MDPR | No equation-output contract surveyed | Intermediate model evidence is insufficient |
| MarkItDown | Not an equation renderer | Its Markdown output is a candidate input to the target parser |

## Simple staged-reveal handling

Fixture 15 asks only for an authored item to appear on advance or an outline to build one item at a
time. The source forms below are evidence for the language score; they do not imply that the
repository will adopt any candidate renderer, runtime, or animation model.

| System | Literal source or documented boundary | Hand-authoring result |
| --- | --- | --- |
| Classic Marp | No fragment or incremental-list construct is documented in the Marp Core v5 author guide. | No standard source form for a teaching build |
| Quarto Reveal | `::: {.incremental}` around a list, `::: {.fragment}` around one content block, or a bare `. . .` pause between blocks. | Global `incremental: true` keeps lists ordinary; the pause is a compact arbitrary-content form |
| Quarto PowerPoint | `incremental: true` in `format: pptx`, or `::: {.incremental}` around one list. | Strong list-only form; no compact arbitrary-item form documented |
| Pandoc PowerPoint | `incremental: true`, or `::: incremental` around one list. | Strong list-only form; fenced override is readable but structural |
| Slidev | `<v-clicks depth="2">` around a list; `<v-click>` around one item. | Covers nested lists and arbitrary items, but imports Vue-like tags |
| Kova | No incremental or fragment source form is documented in the current layout and feature guides. | No documented teaching build |
| reveal.js Markdown | `- Item <!-- .element: class="fragment" -->` for each list item. | Works, but routine comments make source noisy |
| MarpX | Its examples use GIFs and embedded content for animation, not authored stepped items. | Media animation is not a teaching-build form |
| Lectern | `::: incremental` around a list; each direct child is one build step. | Concise fence, but nested items ride with their parent |
| Marp Extended | No stepped-item form was found in the surveyed extension syntax. | No documented teaching build |
| Awesome Marp Template | No stepped-item form was found in the surveyed container syntax. | No documented teaching build |
| MDPR override model | No source-level build or reveal operation is documented. | No documented teaching build |
| MarkItDown output | Conversion output has no presentation-time reveal semantics. | Import format only |

The positive forms reduce to four concise source shapes:

```markdown
::: {.incremental}
- Point mutation
- Chromosome deletion
:::
```

Quarto Reveal, Quarto PowerPoint, and Pandoc PowerPoint document this fenced-list override.
Quarto and Pandoc also document a global `incremental: true` setting when every list should build.

```markdown
## Slide with a pause

content before the pause

. . .

content after the pause
```

Quarto Reveal also recognizes the bare `. . .` line as a pause: the preceding content is visible
first and the following content appears on the next advance. Unlike a fragment fence, this puts no
container punctuation around either block. It raises Quarto Reveal's simple-reveal score to 5; the
language still carries the fenced-div and attribute cost for spatial layouts.

```markdown
<v-clicks depth="2">

- Point mutation
- Chromosome abnormality
  - Deletion
  - Duplication

</v-clicks>
```

Slidev uses its `v-clicks` component for an incremental outline and its `v-click` component for an
arbitrary individual item. The component is explicit but non-Markdown.

```markdown
::: incremental

- Point mutation
- Chromosome deletion

:::
```

Lectern makes each direct child of its `incremental` container a build step. The container keeps the
Markdown list readable, but a nested child remains attached to its parent.

```markdown
- Point mutation <!-- .element: class="fragment" -->
- Chromosome deletion <!-- .element: class="fragment" -->
```

reveal.js Markdown requires a comment on every element. It works but demonstrates why routine
comment-based structure is a poor default for hand-authored teaching slides.

The compact positive forms are intentionally narrower than general animation languages. Quarto
Reveal also permits a fragment fence for one arbitrary content item. Slidev's `v-clicks` documents a
`depth` control for nested lists, while Lectern deliberately treats a nested list as part of its
parent build. That difference matters: the future language must state whether a child item is a
separate advance or arrives with its parent.

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

This is valuable native-export architecture and an honest escape hatch. The YAML is structured,
readable, and reasonable to hand-write; the weakness is specifically its title-addressed,
per-slide override shape, which adds a second coordinated source for a gallery or reusable teaching
layout. A stable slide or layout identifier could improve that boundary. Its public repository had
no explicit license file or GitHub license label during this review, so it is excluded from the
FOSS adoption set.

### Microsoft MarkItDown: input format, not layout language

MarkItDown is MIT-licensed and converts PPTX to Markdown. Its output format can be accepted as
input to the repository's future parser, so it belongs in the source-import path rather than being
excluded from it. It does not itself define a presentation layout language, named regions, or a
renderer; the target parser must still recover or assign slide boundaries and spatial semantics.

## Wishlist-completeness scorecard

Scores are 1 (missing or poor fit) through 5 (strong fit) for the source language or format
against the instructor's wishlist. They do not score a renderer, import pipeline, parser, or native
PPTX/ODP output. Native editable objects remain a separate, non-negotiable acceptance requirement.
Average is the equal-weight mean of the nine numeric language dimensions, including simple staged
reveals. The table is sorted by that descriptive average; it is not a recommendation.

| System | Layout coverage | Named layouts | Nested lists | Image placement | Equations | Simple reveal | Low punctuation | Readable | Hand-write | Average |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Slidev | 4 | 5 | 5 | 5 | 4 | 4 | 4 | 4 | 4 | 4.3 |
| Quarto Reveal | 5 | 3 | 5 | 4 | 5 | 5 | 2 | 3 | 3 | 3.9 |
| Kova | 3 | 2 | 5 | 3 | 4 | 1 | 5 | 5 | 5 | 3.7 |
| Lectern | 5 | 4 | 5 | 4 | 4 | 3 | 2 | 3 | 2 | 3.6 |
| Quarto PowerPoint | 5 | 2 | 5 | 4 | 4 | 3 | 2 | 3 | 3 | 3.4 |
| Pandoc PowerPoint | 5 | 1 | 5 | 4 | 4 | 3 | 2 | 3 | 3 | 3.3 |
| Classic Marp | 1 | 2 | 5 | 2 | 3 | 1 | 5 | 5 | 5 | 3.2 |
| Marp Extended | 4 | 4 | 5 | 3 | 3 | 1 | 3 | 3 | 3 | 3.2 |
| MDPR override model | 4 | 4 | 5 | 2 | 1 | 1 | 3 | 4 | 3 | 3.0 |
| MarkItDown output | 1 | 1 | 5 | 2 | 2 | 1 | 5 | 5 | 5 | 3.0 |
| MarpX | 2 | 4 | 5 | 2 | 3 | 1 | 2 | 3 | 2 | 2.7 |
| Awesome Marp Template | 3 | 3 | 4 | 2 | 2 | 1 | 2 | 3 | 2 | 2.4 |
| reveal.js Markdown | 1 | 1 | 5 | 2 | 2 | 2 | 2 | 2 | 2 | 2.1 |

### Scorecard context

The averages are compact navigation, not a claim that the highest-scoring grammar is the right
choice. The rationale below keeps the scorecard readable while recording the material tradeoff for
each source form.

| System | Context for the score |
| --- | --- |
| Slidev | Named layouts and slots, image handling, math, and click components are unusually complete. Its layout and reveal constructs are Vue-like extensions, rather than plain Markdown. |
| Quarto Reveal | Supports columns, equations, list builds, fragment blocks, and the bare `. . .` pause. Fenced divs and attributes make multi-region source denser than ordinary Markdown. |
| Kova | Content-shape inference and the `|||` separator keep ordinary prose exceptionally light. The source cannot explicitly describe much asymmetry, named regions, or a teaching build. |
| Lectern | Directives name layouts and regions and its `incremental` container handles direct-child builds. Deeply nested or multi-region material becomes directive-heavy. |
| Quarto PowerPoint | Strong document, column, equation, and list-build syntax. Its reference-presentation model offers fewer source-level named teaching layouts. |
| Pandoc PowerPoint | Provides ordinary Markdown, equations, columns, and incremental lists. Named reusable teaching layouts are mainly a reference-layout concern, not a compact source construct. |
| Classic Marp | Ideal ordinary Markdown readability, but its theme classes do not define content regions and it has no standard teaching-build syntax. |
| Marp Extended | Adds named structures through visible markers, cards, and columns. Those markers improve parseability while adding repeated structural punctuation. |
| MDPR override model | The YAML override is readable and can name a layout. It is a separate, title-addressed source that must stay coordinated with the Markdown slide. |
| MarkItDown output | A readable Markdown import format for existing PPTX content. It does not preserve or express presentation layouts, equations, or reveals by itself. |
| MarpX | Semantic classes offer layout names, but region structure remains CSS/HTML-oriented; surveyed animation is media, not a teaching build. |
| Awesome Marp Template | Markdown-it containers can express layout structure, but nesting introduces increasingly dense fence punctuation. |
| reveal.js Markdown | Markdown remains familiar, but attributes and per-item fragments use HTML comments, which makes structural source noisy. |

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

### Branch B: adopt another source grammar

The FOSS candidates provide different source grammars and semantic models. In every case, the
repository reimplements the selected semantics in its own parser and native editable-object output
pipeline:

| Candidate | Source semantics to adapt into the local parser |
| --- | --- |
| Quarto Reveal | Pandoc document model, fenced-div regions, figures, and callouts |
| Quarto PowerPoint | Pandoc source model, columns, figures, and template-oriented layout semantics |
| Pandoc PowerPoint | Pandoc headings, divs, attributes, and reference-layout vocabulary |
| Slidev | YAML layout selector and named slot syntax |
| Kova | Content-shape inference and the `|||` equal-panel delimiter |
| reveal.js Markdown | Markdown slide boundaries and HTML-attribute extension boundary |

Before either branch is chosen, complete the fifteen-fixture deck for source review, parser
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
- [Slidev animation guide]
- [reveal.js Markdown guide]
- [Marp Core v5 Markdown]
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
[Slidev animation guide]: https://sli.dev/guide/animations
[reveal.js Markdown guide]: https://revealjs.com/markdown/
[Marp Core v5 Markdown]: https://github.com/marp-team/marp-core/blob/main/docs/markdown.md
[Marp Extended]: https://github.com/shuuul/obsidian-marp-extended
[Awesome Marp Template]: https://github.com/yKicchan/awesome-marp-template
[MDPR]: https://github.com/ch040602/MdPr
[Microsoft MarkItDown]: https://github.com/microsoft/markitdown
[Markdown-presentation list]: https://gist.github.com/johnloy/27dd124ad40e210e91c70dd1c24ac8c8
