# Related projects

This guide records the 16 repositories evaluated on 2026-09-01 while designing this
repository's instructor-owned Markdown-to-classroom-slide workflow. They are idea
libraries, not dependencies or an adopted implementation. The product contract is authoritative
Marp Markdown with native editable PPTX, editable ODP, and an ODP-derived PDF. The repository-owned
Python exporter owns that contract.

## At-a-glance inventory

| Project | Category | Direction or purpose | Key stack | Strongest idea to adapt |
| --- | --- | --- | --- | --- |
| ai-lesson-planner | Course planner | Course to lessons | Agent prompts | Separate planning |
| awesome-marp | Ecosystem index | Marp discovery | Markdown catalog | Curated discovery |
| deck2video | Video companion | Marp to narrated MP4 | Python, Marp, ffmpeg | Notes to narration |
| marp-core | Language engine | Marp/Marpit language interpretation | TypeScript, Marpit | Conformance evidence |
| marp-cli | Renderer CLI | Marp output orchestration | TypeScript, Node, browser tools | Boundary evidence |
| marp-community-themes | Themes | CSS for Marp | CSS, Quarto | Theme previews and provenance |
| marp-deck-directory | Deck template | Markdown to deck site | Marp, Nix | Reproducible checks |
| marp-slides | Authoring examples | Prompt to Marp deck | Claude, SVG, HTML | Visual patterns |
| marp-slides-template | Publish template | Marp to Pages | Marp, Actions, CSS | Overflow review |
| marp-to-editable-pptx | PPTX experiment | Marp DOM to PPTX | Node tools | Native shape boundary |
| MarpX | Theme library | Marp to styled slides | CSS, Marp | Semantic classes |
| md2pptx | Direct renderer | Markdown dialect to PPTX | Python, python-pptx | Template geometry |
| my-marp-themes | Theme collection | CSS for Marp | CSS | Visual motifs |
| odpdown | ODP generator | Markdown to ODP | Python, odfdo | ODP writer ideas |
| ppt2asciidocslides | Legacy importer | PPTX to markup | Java, Apache POI | Intermediate model |
| slide-ai-agent | Deck builder | Sources to Marp/export | Python, TypeScript, Marp | Human review |

## Likely related projects

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

### md2pptx

- Relationship: Prior art or inspiration.
- Link: [Official repository](https://github.com/MartinPacker/md2pptx).
- Why visitors may care: The heavily edited local clone demonstrates native Python `python-pptx`
  construction techniques relevant to this repository's editable-output target.
- Evidence: `md2pptx.py` creates a slide with `addSlide()`, reads a template through
  `Presentation(slideTemplateFile)`, maps a bounded rectangle with `Rectangle`, fits component
  images through `scalePicture()`, builds list content in `createListBlock()`, and writes presenter
  notes with `createSlideNotes()` through `slide.notes_slide.notes_text_frame`. `runPython.py`
  demonstrates direct `slide.shapes.add_textbox()`, `add_picture()`, `add_shape()`, and
  `add_connector()` calls.
- Activity and license: The local clone's latest commit is 2026-08-31; it is MIT licensed.
- Adaptation idea: Adapt the demonstrated native-object techniques into the local exporter: fixed
  template geometry, bounded contain fitting, text/list population, and note assignment.
- Limitation: Its input parser, metadata syntax, global option state, and reference-template
  conventions form a separate Markdown dialect. The local exporter retains Marp front matter,
  slide separators, directives, and presenter-note comments instead.

#### md2pptx implementation boundary

The local clone is useful as implementation evidence rather than a drop-in library. Its important
inner workings are confined to four reusable ideas:

| Local evidence | Native-output use |
| --- | --- |
| `addSlide()` selects a PowerPoint layout and creates a slide | Select one repository-owned native template for each supported Marp layout. |
| `scalePicture()` calculates a bounded aspect-preserving fit | Place each authored component image with `contain` geometry. |
| `createListBlock()` sizes and populates a text shape | Map Marp bullet nesting to editable paragraph levels. |
| `createSlideNotes()` writes `notes_text_frame` | Preserve Marp presenter-note comments as editable speaker notes. |

This repository adapts the techniques, not the source or its Markdown dialect.
`marp_lib/layouts.py` owns one explicit native builder for every LibreOffice layout-grid entry plus
the repository `gallery` layout. `marp_lib/native_export.py` orchestrates parser input, PPTX output,
notes, pagination, and the downstream conversion chain.

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

Two bounded discovery rounds supplemented the clone evidence. The seed round checked the official
[Marp CLI repository](https://github.com/marp-team/marp-cli),
[marp-to-editable-pptx](https://github.com/KatsuYuzu/marp-to-editable-pptx), and
[md2pptx](https://github.com/MartinPacker/md2pptx). The widening round checked
[deck2video](https://github.com/pjdoland/deck2video),
[Marp documentation](https://github.com/marp-team/marp), and related format-conversion leads.
Marp's documentation confirms a broader HTML, PDF, PPTX, and image ecosystem. This repository
retains Marp syntax for authoring but intentionally owns native presentation output in Python so
classroom files preserve editable objects. The local `marp-core` and `marp-cli` clones are
conformance evidence only; they supply no production runtime code or renderer.

The widening round also found additional untraced projects, including `marp2pptx`, `marp-pptx`,
and `MarpToPptx`. They are deliberately excluded from the candidate list because they were not
cloned and evaluated against this repository's requirements.
