# Marp-adjacent project comparison

This is the focused inventory for the local `OTHER_REPOS/` snapshots and external FOSS candidates
that inform the language choice: define a small slide-authoring extension or adopt another Markdown
presentation language. They are prior art only: none is a runtime dependency, an adopted renderer,
or a source-language decision. Classic Marp is known not to provide the spatial-layout vocabulary
this repository needs. For literal syntax comparisons and the two decision branches, see
[LAYOUT_LANGUAGE_SURVEY.md](LAYOUT_LANGUAGE_SURVEY.md).

In either branch, the repository keeps its own parser and native editable-object pipeline. A source
grammar may be adapted from a candidate, but its runtime, renderer, and build stack are not adopted.

| Project | What it contributes | Decision for this repository | Review |
| --- | --- | --- | --- |
| AI lesson planner | Teaching objectives and slide cues | Keep planning separate from slide syntax | [AI_LESSON_PLANNER.md](OTHER_REPOS/AI_LESSON_PLANNER.md) |
| Awesome Marp | Ecosystem discovery catalog | Use only to find candidates | [AWESOME_MARP.md](OTHER_REPOS/AWESOME_MARP.md) |
| CDL Slides | Teaching feature inventory | Study bounded features; do not adopt compiler | [CDL_SLIDES.md](OTHER_REPOS/CDL_SLIDES.md) |
| Deck2video | Notes-to-narration workflow | Keep narration outside the layout language | [DECK2VIDEO.md](OTHER_REPOS/DECK2VIDEO.md) |
| Lectern Slides | Source maps and diagnostics | Adapt diagnostic ideas, not syntax or runtime | [LECTERN_SLIDES.md](OTHER_REPOS/LECTERN_SLIDES.md) |
| Marp2pptx | Rendered-PPTX postprocessing | Do not use as a substitute for source layout | [MARP2PPTX.md](OTHER_REPOS/MARP2PPTX.md) |
| MarpX | Semantic slide classes and themes | Study named layouts; do not take raw-HTML dependency | [MARPX.md](OTHER_REPOS/MARPX.md) |
| Marp CLI | Standard renderer and directives | Use as classic-language conformance evidence | [MARP_CLI.md](OTHER_REPOS/MARP_CLI.md) |
| Marp community themes | Theme gallery | Use for visual motif research | [MARP_COMMUNITY_THEMES.md](OTHER_REPOS/MARP_COMMUNITY_THEMES.md) |
| Marp Core | Upstream language and themes | Use as the Marp Core v5 reference | [MARP_CORE.md](OTHER_REPOS/MARP_CORE.md) |
| Marp deck directory | Deck and asset organization | Preserve deterministic asset ownership | [MARP_DECK_DIRECTORY.md](OTHER_REPOS/MARP_DECK_DIRECTORY.md) |
| Marp slides | Example visual patterns | Extract recurring teaching needs, not markup | [MARP_SLIDES.md](OTHER_REPOS/MARP_SLIDES.md) |
| Marp slides template | Rendered overflow checks | Keep rendered inspection as a validation lane | [MARP_SLIDES_TEMPLATE.md](OTHER_REPOS/MARP_SLIDES_TEMPLATE.md) |
| Marp to editable PPTX | Typed editable-output experiment | Compare native-output and QA boundaries | [MARP_TO_EDITABLE_PPTX.md](OTHER_REPOS/MARP_TO_EDITABLE_PPTX.md) |
| My Marp themes | Compact theme motifs | Promote only recurring teaching motifs | [MY_MARP_THEMES.md](OTHER_REPOS/MY_MARP_THEMES.md) |
| Odpdown | Template-based direct ODP rendering | Keep geometry in templates and a defined model | [ODPDOWN.md](OTHER_REPOS/ODPDOWN.md) |
| PPT to AsciiDoc slides | Renderer-neutral document model | Preserve the source-model boundary | [PPT2ASCIIDOCSLIDES.md](OTHER_REPOS/PPT2ASCIIDOCSLIDES.md) |
| Pptx2marp | Simple shape-order extraction | Retain as a negative importer baseline | [PPTX2MARP.md](OTHER_REPOS/PPTX2MARP.md) |
| Slide AI agent | Application platform | Do not adopt its opaque generator workflow | [SLIDE_AI_AGENT.md](OTHER_REPOS/SLIDE_AI_AGENT.md) |
| SlideSonnet | Media identity and cache | Keep it as a future narration companion | [SLIDESONNET.md](OTHER_REPOS/SLIDESONNET.md) |

The individual reviews retain version, license, source, and implementation evidence. A comparison
row is not permission to copy code, assets, themes, or syntax.

## External FOSS language candidates

| Project | What it is | Language-design evidence | Relevance |
| --- | --- | --- | --- |
| [Quarto Reveal] | MIT Markdown-to-Reveal authoring system | Explicit fenced columns, figure/callout syntax, document title metadata | Strong semantic benchmark; too container-heavy to copy directly |
| [Quarto PowerPoint] | MIT Markdown-to-PPTX authoring system | Same source can select inferred template layouts through Pandoc | Strong reference-layout and editable-output comparison |
| [Pandoc PowerPoint] | GPL Markdown-to-PPTX writer | Columns and reference-document inference; widths do not map to PPTX | Useful native-layout boundary, not a full spatial grammar |
| [Slidev] | MIT web slide system | Named layouts plus named slots in slide front matter | Strong candidate syntax pattern; Vue/theme coupling remains outside scope |
| [Kova] | GPL-3.0 desktop Markdown presenter | H1/H2 and content shape infer layouts; `|||` splits equal columns | Best low-punctuation panel precedent, but too heuristic |
| [reveal.js Markdown] | MIT browser framework | Markdown is hosted in HTML; layout returns to HTML and comment attributes | Negative baseline for comment/HTML-driven spatial syntax |
| [Marp Extended] | MIT Obsidian Marp preprocessor | `%%marp-*%%` markers add columns, cards, callouts, and subtitle blocks | Real Marp-adjacent extension; useful evidence of marker and closing-block burden |
| [Awesome Marp Template] | MIT custom Marp engine/template | Markdown-it container fences and CSS classes create columns | Real Marp extension route; useful nesting-cost counterexample |
| [Microsoft MarkItDown] | MIT PPTX-to-Markdown converter | Its output can become target-language parser input; it has no layout vocabulary | Source-import bridge, not a hand-authoring layout language |

## External project screened out of the FOSS set

| Project | Evidence | Disposition |
| --- | --- | --- |
| [MDPR] | Markdown-to-presentation intermediate model and a separate YAML layout override mechanism | Syntax and architecture are surveyed, but the public repository showed no explicit license file or GitHub license label during this review |

## Marp-extension patterns found

Existing Marp extensions do not resolve spatial layout in one common way. They fall into five
distinct patterns:

| Pattern | Examples | What the author writes | Hand-authoring consequence |
| --- | --- | --- | --- |
| Theme classes | MarpX and custom templates | Comment class followed by ordinary Markdown | Names a slide treatment but not durable child regions |
| Raw HTML/CSS | MarpX, CDL, reveal.js | `div` containers, inline styling, or custom classes | Precise but makes source renderer-specific |
| Preprocessed markers | Marp Extended | Open, split, and close `%%marp-*%%` blocks | Keeps bodies Markdown, but punctuation grows with nesting |
| Markdown containers | Awesome Marp Template | Nested `:::` fences and classes | Parseable but visually dense for multi-region teaching slides |
| Intermediate-model overrides | MDPR | Markdown plus title-addressed YAML operations | Strong architecture; sidecar coordination is the main authoring cost |

The layout survey tests these patterns against the same classroom fixtures. The comparison document
does not choose between a new language and adoption. The required outcome also includes minimal
inline/display equations, simple staged reveals, and editable native text, list, equation, image,
and animation objects.

[Quarto Reveal]: https://quarto.org/docs/presentations/revealjs/
[Quarto PowerPoint]: https://quarto.org/docs/presentations/powerpoint.html
[Pandoc PowerPoint]: https://pandoc.org/MANUAL.html
[Slidev]: https://sli.dev/guide/layout
[Kova]: https://kova.md/
[reveal.js Markdown]: https://revealjs.com/markdown/
[Marp Extended]: https://github.com/shuuul/obsidian-marp-extended
[Awesome Marp Template]: https://github.com/yKicchan/awesome-marp-template
[Microsoft MarkItDown]: https://github.com/microsoft/markitdown
[MDPR]: https://github.com/ch040602/MdPr
