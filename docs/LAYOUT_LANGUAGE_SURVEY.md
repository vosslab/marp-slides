# Layout-language survey

This survey asks how each of the 20 local projects responds to Marp's limited layout language. It
distinguishes a semantic authoring extension from a CSS visual catalog, an output transformation,
or an unrelated companion workflow. The repository-owned native exporter remains the rendering
boundary; this survey does not recommend copying source.

## Main findings

- [CDL Slides](OTHER_REPOS/CDL_SLIDES.md) supplies the broadest feature inventory: callouts,
  diagrams, charts, animations, table handling, and density warnings. Its preprocessor and renderer
  coupling are a counterexample, not the implementation model.
- [MarpX](OTHER_REPOS/MARPX.md) offers the clearest small vocabulary: semantic slide classes such
  as title, chapter, quote, references, and multicolumn. Its raw HTML containers are less suitable
  than the class idea itself.
- [Lectern Slides](OTHER_REPOS/LECTERN_SLIDES.md) has the strongest language-design mechanics:
  parser-safe comment directives, block classes, a nine-point anchor grid, source maps, and
  source-cited diagnostics. Its assembler, server, and renderer framework are outside this scope.
- [Marp Slides Template](OTHER_REPOS/MARP_SLIDES_TEMPLATE.md) solves validation rather than
  authoring: rendered browser measurement detects overflow at the real slide boundary.
- The theme galleries show considerable visual potential, but CSS alone does not provide a stable
  author-facing layout vocabulary.

## Twenty-project comparison

| Project | Layout or language approach | Role in the survey | Design lesson |
| --- | --- | --- | --- |
| [AI lesson planner](OTHER_REPOS/AI_LESSON_PLANNER.md) | Separates objectives, teaching discourse, and slide cues. | Planning boundary | Keep teaching intent separate from layout syntax. |
| [Awesome Marp](OTHER_REPOS/AWESOME_MARP.md) | Catalog of tools, themes, and examples. | Discovery only | Find candidates here; it has no layout model. |
| [CDL Slides](OTHER_REPOS/CDL_SLIDES.md) | Preprocessor adds callouts, flow blocks, charts, animations, tables, and scale classes. | Feature inventory | Define a small teaching grammar without automatic rewrites or renderer coupling. |
| [Deck2video](OTHER_REPOS/DECK2VIDEO.md) | Splits slides and notes for narration and video. | Downstream companion | Keep narration outside the slide-layout language. |
| [Lectern Slides](OTHER_REPOS/LECTERN_SLIDES.md) | CommonMark plus comment directives, block classes, anchors, placed boxes, and source maps. | Language-design reference | Keep extensions parser-safe and diagnostics source-cited. |
| [Marp2pptx](OTHER_REPOS/MARP2PPTX.md) | Alters rendered editable-PPTX shapes after export. | Output transformation | Postprocessing cannot substitute for expressive source layouts. |
| [MarpX](OTHER_REPOS/MARPX.md) | `_class` slide variants plus containers and multicolumn helpers. | Layout-vocabulary reference | Prefer named semantic layouts over ad hoc per-slide styling. |
| [Marp CLI](OTHER_REPOS/MARP_CLI.md) | Standard Marp directives, theme loading, and output options. | Feature ceiling | Preserve useful source concepts, but do not extend through this renderer. |
| [Marp community themes](OTHER_REPOS/MARP_COMMUNITY_THEMES.md) | CSS theme gallery and preview decks. | Visual evidence | Use galleries to test which teaching motifs deserve semantic names. |
| [Marp Core](OTHER_REPOS/MARP_CORE.md) | Core directives, theme metadata, named sizes, and auto-scaling. | Compatibility reference | Treat supported Marp behavior as the conformance baseline, not the whole language. |
| [Marp deck directory](OTHER_REPOS/MARP_DECK_DIRECTORY.md) | Maps deck paths and assets into reproducible outputs. | Build architecture | Layout language also needs deterministic asset ownership. |
| [Marp slides](OTHER_REPOS/MARP_SLIDES.md) | Example decks use per-deck CSS and raw HTML for visual patterns. | Visual evidence | Extract comparison, sequence, and dashboard needs; replace ad hoc styling. |
| [Marp slides template](OTHER_REPOS/MARP_SLIDES_TEMPLATE.md) | Custom themes and browser-measured overflow checks. | Validation reference | Test the rendered result rather than trusting a layout heuristic. |
| [Marp to editable PPTX](OTHER_REPOS/MARP_TO_EDITABLE_PPTX.md) | Captures computed DOM geometry into typed native-slide data. | Native-output comparison | Use it to compare typed-model and visual-check boundaries with the local exporter. |
| [My Marp themes](OTHER_REPOS/MY_MARP_THEMES.md) | Small CSS themes with border, graph-paper, and gradient motifs. | Visual evidence | Promote only recurring teaching motifs into shared layouts. |
| [Odpdown](OTHER_REPOS/ODPDOWN.md) | Own Markdown parser writes ODP shapes against master pages. | Direct-rendering reference | Keep layout geometry in templates and a defined model, not scattered source markup. |
| [PPT to AsciiDoc slides](OTHER_REPOS/PPT2ASCIIDOCSLIDES.md) | Extracts a renderer-neutral document model, then writes target formats. | Compiler-model reference | Separate source interpretation from target rendering. |
| [Pptx2marp](OTHER_REPOS/PPTX2MARP.md) | Extracts text, images, and simple tables into linear Markdown. | Negative baseline | A layout-aware language cannot rely on shape-order extraction alone. |
| [Slide AI agent](OTHER_REPOS/SLIDE_AI_AGENT.md) | Generates decks through an application platform and live preview. | Not a language model | AI generation needs explicit layout contracts, not opaque prompt output. |
| [SlideSonnet](OTHER_REPOS/SLIDESONNET.md) | Adds narration identity, caching, and diagnostics around a PDF deck. | Downstream companion | Keep media identity and timing separate from layout syntax. |

The evidence for each row remains in its linked individual review. The most promising language
inputs are CDL's feature set, MarpX's semantic names, and Lectern's parser-safe syntax and source
mapping. The native exporter supplies the rendering boundary for any approved language extension.
