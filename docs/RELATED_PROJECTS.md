# Related projects

This guide indexes the 20 local repositories evaluated on 2026-09-01 while designing this
repository's instructor-owned Markdown-to-classroom-slide workflow. They are idea libraries, not
dependencies or an adopted implementation. The product contract is authoritative Marp Markdown
with native editable PPTX, editable ODP, and an ODP-derived PDF. The repository-owned Python
exporter owns that contract.

For a short practical comparison of task solutions, pipeline models, and theme possibilities, see
the [reuse decision matrix](REUSE_DECISION_MATRIX.md).

For the layout-language approaches across all 20 projects, see the
[LAYOUT_LANGUAGE_SURVEY.md](LAYOUT_LANGUAGE_SURVEY.md).

These projects are prior art, not dependencies. Marp Markdown remains authoritative, the native
Python exporter owns conversion, and the central theme owns presentation styling.

## Inventory

| Project | Content type | Strongest relevance | Review |
| --- | --- | --- | --- |
| MarpX | Theme suite | Named semantic layouts | [Review](OTHER_REPOS/MARPX.md) |
| ai-lesson-planner | Lesson-planning prompts | Planning boundary | [Review](OTHER_REPOS/AI_LESSON_PLANNER.md) |
| awesome-marp | Ecosystem catalog | Candidate discovery | [Review](OTHER_REPOS/AWESOME_MARP.md) |
| cdl-slides | Slide preprocessor | Bounded feature inventory | [Review](OTHER_REPOS/CDL_SLIDES.md) |
| deck2video | Narrated-video generator | Notes-to-narration lane | [Review](OTHER_REPOS/DECK2VIDEO.md) |
| lectern-slides | Multi-renderer CLI | Source-aware diagnostics | [Review](OTHER_REPOS/LECTERN_SLIDES.md) |
| marp-cli | Official CLI | Language-conformance boundary | [Review](OTHER_REPOS/MARP_CLI.md) |
| marp-community-themes | Theme gallery | Visual motif catalog | [Review](OTHER_REPOS/MARP_COMMUNITY_THEMES.md) |
| marp-core | Language engine | Marp Core v5 conformance | [Review](OTHER_REPOS/MARP_CORE.md) |
| marp-deck-directory | Deck builder | Output and asset ownership | [Review](OTHER_REPOS/MARP_DECK_DIRECTORY.md) |
| marp-slides | Example-deck collection | Teaching visual patterns | [Review](OTHER_REPOS/MARP_SLIDES.md) |
| marp-slides-template | Publishing template | Rendered-overflow checks | [Review](OTHER_REPOS/MARP_SLIDES_TEMPLATE.md) |
| marp-to-editable-pptx | Native PPTX experiment | Typed-native output comparison | [Review](OTHER_REPOS/MARP_TO_EDITABLE_PPTX.md) |
| marp2pptx | PPTX postprocessor | Limits of postprocessing | [Review](OTHER_REPOS/MARP2PPTX.md) |
| my-marp-themes | Theme collection | Compact teaching motifs | [Review](OTHER_REPOS/MY_MARP_THEMES.md) |
| odpdown | Direct ODP renderer | Template and shape-model ideas | [Review](OTHER_REPOS/ODPDOWN.md) |
| ppt2asciidocslides | PPTX importer | Renderer-neutral model | [Review](OTHER_REPOS/PPT2ASCIIDOCSLIDES.md) |
| pptx2marp | PPTX importer | Shape-order negative baseline | [Review](OTHER_REPOS/PPTX2MARP.md) |
| slide-ai-agent | AI deck application | Explicit review boundary | [Review](OTHER_REPOS/SLIDE_AI_AGENT.md) |
| slideSonnet | Narrated-video toolkit | Cached media companion | [Review](OTHER_REPOS/SLIDESONNET.md) |

## Best ideas for this repository

### marp-core

- Relationship: Language-specification reference.
- Link: [Official repository](https://github.com/marp-team/marp-core).
- Why visitors may care: The local clone records the adopted Marp Core v5 and inherited Marpit
  interpretation of front matter, directives, CommonMark, tables, code, images, and comments.
- Evidence: `docs/markdown.md`, `docs/migration-v5.md`, `src/marp.ts`, themes, and tests document
  author syntax and parser behavior used to build local Python conformance fixtures.
- Activity and license: The checked-out conformance snapshot is Marp Core 5.0.1 at commit
  `06c5a54`; it uses the repository's MIT license.
- Adaptation idea: Translate selected language semantics into explicit Python parser behavior and
  tests with source-line diagnostics.
- Limitation: It is not imported, executed, packaged, or rendered in this project. Its JavaScript
  engine remains outside the production dependency and runtime graph.

### marp-cli

- Relationship: Language-conformance and renderer-boundary reference.
- Link: [Official repository](https://github.com/marp-team/marp-cli).
- Why visitors may care: The local clone shows Marp CLI metadata handling, BOM behavior, comment
  collection, and the upstream browser/PDF/image/PPTX routes this repository replaces.
- Evidence: `src/converter.ts` and engine metadata tests identify behavior useful for local parser
  fixtures and show that ordinary upstream PPTX output routes through rendered slide images.
- Activity and license: The checked-out clone is source evidence; consult its top-level license and
  Git history for its snapshot details.
- Adaptation idea: Use it to compare accepted Marp language behavior and speaker-note treatment.
- Limitation: Its Node, browser, PDF, HTML, and raster conversion machinery is not a production
  dependency or runtime here. This repository creates native PPTX objects before LibreOffice writes
  editable ODP and then PDF from ODP.

### awesome-marp

- Relationship: Domain standard, guide, dataset, or other visitor resource.
- Link: [Official repository](https://github.com/marp-team/awesome-marp).
- Why visitors may care: It is a maintained index for choosing Marp themes, examples, and
  ecosystem tools while retaining a local authoring workflow.
- Evidence: Its README describes a curated list of Marp resources and links the official CLI,
  theme sources, plugins, and examples.
- Activity and license: The local clone's latest commit is 2026-04-25; it declares CC0-1.0.
- Adaptation idea: Use it as a discovery source for narrowly scoped experiments.
- Limitation: It is a catalog, not a converter or a classroom-output design.

### marp-community-themes

- Relationship: Companion project, extension, or interoperability tool.
- Link: [Official repository](https://github.com/rnd195/marp-community-themes).
- Why visitors may care: It supplies inspectable CSS examples for a central Marp theme without
  putting layout markup into every slide.
- Evidence: Its README calls it a community-maintained Marp theme gallery and documents using
  downloaded CSS through the Marp CLI.
- Activity and license: The local clone's latest commit is 2026-08-02; the gallery is MIT.
- Adaptation idea: Borrow the gallery's theme-preview and local-CSS distribution pattern.
- Limitation: Evaluate individual theme licenses and remote-font behavior before copying ideas.

### MarpX

- Relationship: Companion project, extension, or interoperability tool.
- Link: [Official repository](https://github.com/cunhapaulo/MarpX).
- Why visitors may care: It demonstrates named slide classes for title, chapter, reference, and
  layout variants in a CSS-centered Marp workflow.
- Evidence: Its README describes a Marp theme suite and documents semantic classes and layouts.
- Activity and license: The local clone's latest commit is 2026-08-12; it is MIT licensed.
- Adaptation idea: Compare names and semantic cues while keeping the local full native layout
  registry as the authoritative class vocabulary.
- Limitation: Many examples use raw HTML; retain the local Markdown-first named-cell contract.

### my-marp-themes

- Relationship: Companion project, extension, or interoperability tool.
- Link: [Official repository](https://github.com/rnd195/my-marp-themes).
- Why visitors may care: It offers small CSS theme examples that help an instructor compare
  visual directions without changing slide content.
- Evidence: Its README describes custom themes for the Marp presentation framework.
- Activity and license: The local clone's latest commit is 2026-03-06; most files are MIT but
  the repository documents exceptions.
- Adaptation idea: Reuse the idea of compact, named CSS motifs after local accessibility review.
- Limitation: Its mixed-license notice means no wholesale copying.

### marp-slides-template

- Relationship: Same-workflow project or independent implementation.
- Link: [Official repository](https://github.com/codebytes/marp-slides-template).
- Why visitors may care: It shows how a Marp deck can have a repeatable build, theme, and
  rendered review surface.
- Evidence: Its README describes a Marp presentation site with CSS theming and automated build
  and publish support; its current project documentation includes headless overflow review.
- Activity and license: The local clone's latest commit is 2026-07-18; it is MIT licensed.
- Adaptation idea: Adapt only the build-verification and overflow-detection ideas.
- Limitation: GitHub Pages, Actions, DevContainers, and VS Code preview are not requirements
  for this local classroom pipeline.

### marp-deck-directory

- Relationship: Same-workflow project or independent implementation.
- Link: [Official repository](https://github.com/nicolas-goudry/marp-deck-directory).
- Why visitors may care: It explores reproducible Marp rendering for a directory of decks,
  which is useful when a course accumulates many lectures.
- Evidence: Its README describes a zero-configuration environment that builds Markdown decks
  into HTML, PDF, and cover images reproducibly.
- Activity and license: The local clone's latest commit is 2026-05-14; it is MIT licensed.
- Adaptation idea: Adopt manifest-like deck discovery and repeatable rendered-output checks.
- Limitation: Nix is an alternative packaging choice, not a dependency for this macOS project.

### marp-to-editable-pptx

- Relationship: Prior art or inspiration.
- Link: [Official repository](https://github.com/KatsuYuzu/marp-to-editable-pptx).
- Why visitors may care: It explores a route from rendered Marp layout to native text, image,
  and shape objects when a classroom deck needs limited post-export editability.
- Evidence: Its README says that each text box, image, and shape becomes an individual native
  PowerPoint object; its package declares Marp CLI, Puppeteer, and PptxGenJS.
- Activity and license: The local clone's latest commit is 2026-07-12; it is MIT licensed.
- Adaptation idea: Study its DOM-walking to native-PPTX boundary as architecture inspiration.
- Limitation: Its core conversion mechanism is VS Code-independent, but the project still uses
  Node, Puppeteer, PptxGenJS, and raster fallbacks. It is not a dependency and does not establish
  the final Marp-to-ODP implementation.

### odpdown

- Relationship: Prior art or inspiration.
- Link: [Official repository](https://github.com/thorstenb/odpdown).
- Why visitors may care: It exposes direct Markdown-to-ODP authoring as a useful comparison when
  evaluating what the LibreOffice conversion step does and does not preserve.
- Evidence: Its project metadata says it generates OpenDocument Presentation files from Markdown
  using Python and identifies LibreOffice and office workflows.
- Activity and license: The local clone's latest commit is 2025-04-08; its metadata declares a
  BSD license.
- Adaptation idea: Study ODP writer vocabulary and test fixtures for future narrowly scoped work.
- Limitation: It is not Marp-aware, and direct ODP generation is an alternative to evaluate, not
  the current source-of-truth contract.

### ppt2asciidocslides

- Relationship: Prior art or inspiration.
- Link: [Official repository](https://github.com/ullenboom/ppt2asciidocslides).
- Why visitors may care: It demonstrates a migration architecture that separates a legacy-slide
  parser from writers for target markup formats.
- Evidence: Its README says it reads PPTX through Apache POI into a renderer-neutral DOM and can
  write AsciiDoc or Marp Markdown.
- Activity and license: The local clone's latest commit is 2026-07-02; it is GPL licensed.
- Adaptation idea: Keep the importer-to-intermediate-model separation in mind as ODP support
  broadens.
- Limitation: It imports PPTX, not ODP, uses Java, and is not source code to copy into this repo.

## Possible related projects

### deck2video

- Relationship: Companion project, extension, or interoperability tool.
- Link: [Official repository](https://github.com/pjdoland/deck2video).
- Why visitors may care: It can turn Marp speaker notes into a narrated video for remote students
  after a classroom deck is already authored.
- Evidence: Its README documents Marp and Slidev detection, note extraction, rendering, text to
  speech, and MP4 assembly.
- Activity and license: The local clone's latest commit is 2026-06-28; no license file is present.
- Adaptation idea: Preserve clean presenter notes so a future video lane remains possible.
- Limitation: Voice cloning, ffmpeg, and Node tooling exceed the current class-slide scope.

### marp-slides

- Relationship: Prior art or inspiration.
- Link: [Official repository](https://github.com/robonuggets/marp-slides).
- Why visitors may care: Its example decks can inspire visual explanation patterns for image-rich
  teaching slides.
- Evidence: Its README describes a Claude Code skill with 22 curated Marp example decks, SVG
  charts, and light/dark themes.
- Activity and license: The local clone's latest commit is 2026-04-08; its README claims MIT but
  the local clone has no license file.
- Adaptation idea: Adapt visual storytelling principles after rebuilding assets locally.
- Limitation: It relies heavily on raw HTML and agent prompting, which conflicts with the local
  preference for simple Markdown and central CSS.

### ai-lesson-planner

- Relationship: Companion project, extension, or interoperability tool.
- Link: [Official repository](https://github.com/saniales/ai-lesson-planner).
- Why visitors may care: It separates course planning and lesson artifacts from final rendering,
  a useful upstream boundary for an instructor designing a lecture sequence.
- Evidence: Its README describes a chat-first toolkit with specialized agents for course plans
  and lesson artifacts.
- Activity and license: The local clone's latest commit is 2026-02-14; it is GPLv3 licensed.
- Adaptation idea: Borrow the separation of planning artifacts from deck-authoring artifacts.
- Limitation: It is an AI planning system, not a Marp or ODP conversion tool.

### slide-ai-agent

- Relationship: Companion project, extension, or interoperability tool.
- Link: [Official repository](https://github.com/leminhnguyen/slide-ai-agent).
- Why visitors may care: It is a broad example of keeping Marp Markdown editable while offering
  preview and export choices.
- Evidence: Its README lists a manual Marp editor, live preview, retrieval, chart generation,
  and exports including Markdown and PPTX.
- Activity and license: The local clone's latest commit is 2026-06-14; its README claims MIT but
  the local clone has no license file.
- Adaptation idea: Keep a human review step between assisted content creation and export.
- Limitation: Its agent, retrieval, and web application architecture are outside this local,
  instructor-authored pipeline.

## Evidence notes

The project-purpose, stack, license, and local activity statements come from the cloned
repositories' README files, manifests, top-level license files, Git origins, and latest local
commits. Those commit dates describe the checked-out snapshots, not a claim about live activity.

The survey covers every checked-out clone. The local `marp-core` and `marp-cli` repositories are
conformance evidence only; they supply no production runtime code or renderer.
