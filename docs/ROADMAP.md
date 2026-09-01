# Plan: Marp syntax support roadmap

Status: planned. Marp Core v5 is the only upstream compatibility baseline.
[MARP_SYNTAX_GUIDE.md](MARP_SYNTAX_GUIDE.md) remains the authority for syntax accepted by the
production pipeline today.

## Context

The native pipeline accepts a deliberate Marp subset only when each source feature maps to an
editable PPTX object and survives conversion to editable ODP. The current multi-cell convention
overloads standard Markdown blockquotes, so `>` means a layout cell while `-` means a list item.

The target Marp+ contract replaces that overload with explicit named cell markers such as
`<!-- _cell: left -->`. The roadmap then expands useful Marp syntax in dependency order without
promising full browser-rendered Marp compatibility.

The upstream baseline is the author-facing contract of Marp Core v5, including its inherited
Marpit syntax. The local evidence snapshot is Marp Core 5.0.1 at commit `06c5a54`. Marp Core v4 and
earlier behavior is outside the compatibility target.

## Objectives

- Replace blockquote layout cells with explicit, named `_cell` markers.
- Classify every Marp Core v5 author-facing feature as accepted, planned, or a non-goal.
- Expand authoring syntax only after each feature has a native editable-object owner.
- Keep parser behavior, native output, importers, preview behavior, tests, and documentation
  aligned.
- Preserve source-located errors for every rejected or malformed construct.

## Design philosophy

Apply **Fix the design, not the symptom**: give each syntax feature a typed native representation
instead of accepting syntax and flattening it later. Apply **Long-term over short-term** by making
cell position explicit even though generic Marp will show the cell contents sequentially.

The production native-object contract takes priority over grid-accurate generic Marp preview.
Upstream Marp ignores `_cell` comments and leaves their content readable in source order; the build
pipeline interprets the comments without adding Node, a custom Marp plugin, or a browser dependency.

## Scope

- Define and migrate the explicit named-cell authoring contract.
- Maintain a Marp Core v5 conformance matrix for built-in and optional-plugin syntax.
- Restore `>` to ordinary Markdown blockquote meaning.
- Add selected editable text, table, code, image, background, and directive capabilities.
- Add focused parser tests and native PPTX/ODP evidence for every accepted feature.
- Update importers and canonical decks whenever accepted source syntax changes.

## Non-goals

- Promise complete Marp, Marpit, HTML, CSS, or browser-renderer compatibility.
- Support Marp Core v4 or earlier behavior or highlight.js-oriented theme contracts.
- Treat the Marp Core v5 `/full` entry point or optional plugins as automatically supported.
- Accept raw HTML or XML slide content.
- Accept arbitrary front-matter keys, directives, classes, or CSS without a native owner.
- Fetch remote assets during a canonical production build.
- Use full-slide rasterization or raster fallback for unsupported syntax.
- Preserve the old blockquote-as-cell dialect after the pre-production migration completes.
- Add a Node or browser runtime to production for preview fidelity.

## Current state summary

The roadmap classifies every item currently listed as unsupported.

| Current restriction | Target | Milestone |
| --- | --- | --- |
| Blockquotes identify layout cells | Named `_cell` markers; `>` becomes a quote | M1 |
| Nested layout cells | Explicit flat named slots; nesting remains unnecessary | M1 |
| Markdown tables | Editable native table objects | M2 |
| Fenced or indented code | Editable monospace code frames | M2 |
| Strikethrough and `fit` headings | Typed editable runs and bounded title fitting | M2 |
| Fragmented-list markers | Static editable lists in PPTX, ODP, and PDF | M2 |
| Inline text mixed with images | Typed block flow with explicit fit rules | M2 |
| Background images | Native background image with fit and description | M3 |
| Per-image pixel geometry | Bounded portable geometry owned by layouts | M3 |
| Remote or data-URL images | Explicit localization into repository assets | M3 |
| Additional front-matter keys | Selected keys with typed semantics | M4 |
| Unscoped or additional directives | Selected global and scoped native directives | M4 |
| Additional classes | One layout class plus registered independent modifiers | M4 |
| Emoji conversion | Explicit accessible native representation decision | M4 |
| Shiki, Mermaid, and math plugins | Separate capability decisions | M4 |
| Raw HTML or XML | Remains outside the canonical authoring contract | Non-goal |
| Marp Core v4 and highlight.js | Remain outside the compatibility contract | Non-goal |

## User-facing contract

`_class` selects the slide layout. `_cell` begins one named content region within that layout and
ends at the next `_cell` marker or the slide boundary.

```markdown
<!-- _class: title-two-content -->

# Types of gene disorders

<!-- _cell: left -->

- Point mutation
- Chromosome deletion

<!-- _cell: right -->

- Duplication
- Translocation
```

The parser will reject missing, duplicate, and unknown slot names. Cell order in the source remains
the recommended reading order, but placement comes from the slot name rather than ordinal position.

The initial slot registry is:

| Layout class | Slots |
| --- | --- |
| `title-two-content` | `left`, `right` |
| `title-content-and-two-content` | `left`, `upper-right`, `lower-right` |
| `title-two-content-and-content` | `upper-left`, `lower-left`, `right` |
| `title-content-over-content` | `upper`, `lower` |
| `title-two-content-over-content` | `upper-left`, `upper-right`, `lower` |
| `title-four-content` | `upper-left`, `upper-right`, `lower-left`, `lower-right` |
| `title-six-content` upper row | `upper-left`, `upper-center`, `upper-right` |
| `title-six-content` lower row | `lower-left`, `lower-center`, `lower-right` |
| `vertical-title-text-chart` | `left`, `right` |
| `title-two-vertical-text-clipart` | `upper-left`, `lower-left`, `right` |

## Milestone plan

| M | Title | Summary | Goal |
| --- | --- | --- | --- |
| M1 | Explicit cells | Use named `_cell` markers | Make placement unambiguous |
| M2 | Editable content | Add tables, code, and mixed block flow | Cover common teaching content |
| M3 | Native images | Add portable image controls | Keep visual content editable |
| M4 | Directive registry | Register typed Marp+ capabilities | Grow compatibility deliberately |

### Milestone M1: Explicit cells

- Depends on: none.
- Deliverables: `_cell` grammar, named native cells, layout slot registry, migrated importers and
  decks, ordinary blockquote rendering, preview fallback, tests, and documentation.
- Entry criteria: the current blockquote-cell inventory is complete.
- Exit criteria: every canonical deck uses `_cell`; old cell wrappers fail clearly; native PPTX and
  ODP retain the intended cell content and placement.
- Parallel-plan ready: no - the grammar and typed model must settle before dependent migrations.

### Milestone M2: Editable content

- Depends on: M1, because tables, code, and mixed blocks need stable cell boundaries.
- Deliverables: typed table, code-block, strikethrough, title-fit, fragmented-list, and mixed-flow
  models with native renderers.
- Entry criteria: named cells pass parser, preview-fallback, importer, and native-output gates.
- Exit criteria: representative content remains editable in PPTX and ODP with source-located
  capacity errors.
- Parallel-plan ready: no - define the shared block-flow model before separate feature renderers.

### Milestone M3: Native images

- Depends on: M1, because background and component-image placement use stable named regions.
- Deliverables: background-image semantics, bounded component geometry, and explicit asset
  localization into repository-relative files.
- Entry criteria: image ownership and accessibility metadata are defined in the typed model.
- Exit criteria: builds remain offline and reproducible; images remain described component objects
  rather than full-slide raster output.
- Parallel-plan ready: no - fit, crop, and source ownership share one image contract.

### Milestone M4: Directive registry

- Depends on: M1, because directives and modifiers must not reintroduce ambiguous layout ownership.
- Deliverables: a v5 capability registry plus selected front-matter keys, global or scoped
  directives, pagination modes, independent modifier classes, emoji behavior, and explicit
  decisions for each optional v5 plugin.
- Entry criteria: each proposed capability names its native model and output owner.
- Exit criteria: accepted capabilities work globally or locally as documented and unsupported ones
  retain source-located errors.
- Parallel-plan ready: no - the registry API must land before individual capabilities.

## Work packages

| ID | Owner | Outcome | Depends on |
| --- | --- | --- | --- |
| WP-V1 | Architect | Audit the parser against Marp Core v5 | none |
| WP-C1 | Architect | Freeze `_cell` grammar and slot registry | none |
| WP-C2 | Coder | Implement named cells in parser, model, and layouts | WP-C1 |
| WP-C3 | Coder | Update importers, canonical decks, and preview fallback | WP-C2 |
| WP-C4 | Tester | Verify parser, native output, migration, and docs | WP-C3 |
| WP-T1 | Coder | Add native editable tables | WP-C4 |
| WP-T2 | Coder | Add native editable code blocks | WP-T1 |
| WP-T3 | Coder | Add typed mixed text-and-image flow | WP-T2 |
| WP-T4 | Coder | Add v5 inline, fit, and fragmented-list semantics | WP-T3 |
| WP-I1 | Coder | Add native background-image semantics | WP-C4 |
| WP-I2 | Coder | Add bounded component-image geometry | WP-I1 |
| WP-I3 | Coder | Add explicit remote/data asset localization | WP-I2 |
| WP-D1 | Architect | Define the directive capability registry | WP-C4 |
| WP-D2 | Coder | Add selected keys, directives, and pagination modes | WP-D1 |
| WP-D3 | Coder | Add registered independent modifier classes | WP-D2 |
| WP-D4 | Architect | Decide emoji, Shiki, Mermaid, and math support | WP-D1 |

Every work package finishes by updating the syntax guide, this roadmap, [TODO.md](TODO.md), and
[CHANGELOG.md](CHANGELOG.md). Implementation and independent verification remain separate owners.

## Acceptance criteria and gates

- Parser gate: accepted and rejected forms report the correct source line with actionable text.
- Native-object gate: each accepted construct remains editable in PPTX and converted ODP.
- Raster gate: no accepted construct creates a full-slide image or raster fallback.
- Importer gate: ODP and PPTX importers emit only the accepted canonical syntax.
- Preview gate: generic Marp fallback remains readable; grid fidelity is not required for `_cell`.
- V5 gate: every Marp Core v5 feature is classified as accepted, planned, or a non-goal.
- Documentation gate: current syntax moves into the guide only after implementation passes.
- Independent review gate: a reviewer compares behavior, tests, and documentation before closure.

## Migration and compatibility policy

This pre-production repository uses a direct replacement. M1 migrates the parser, typed model,
layout validation, importers, preview CSS, tests, and every canonical deck in one coordinated
change. The old blockquote-as-cell interpretation receives no permanent compatibility alias.

Each later feature stays rejected until its typed model, native renderer, error behavior, tests,
ODP evidence, and documentation land together.

Only Marp Core v5.x evidence may refine the baseline without a new design decision. A future v6
release does not change the contract automatically. Versioned official links and the local
conformance snapshot prevent the upstream `main` branch from silently redefining behavior.

## Risk register

| Risk | Impact | Trigger | Owner | Mitigation |
| --- | --- | --- | --- | --- |
| Comment cells lack grouping | Medium | Preview is linear | Architect | Use readable fallback |
| Syntax outruns native ownership | High | Content is dropped | Architect | Enforce owner gate |
| Importers emit stale syntax | High | Imported decks fail | Coder | Migrate with grammar |
| Geometry becomes arbitrary | Medium | Decks need pixel tuning | Architect | Bound layout values |
| Remote assets break builds | High | Builds need a network | Coder | Localize assets first |
| Upstream `main` moves beyond v5 | High | Reference behavior changes | Architect | Pin v5 sources |

## Documentation close-out requirements

- Update [MARP_SYNTAX_GUIDE.md](MARP_SYNTAX_GUIDE.md) only with behavior that has shipped.
- Keep [TODO.md](TODO.md) limited to small next actions; remove completed entries.
- Record completed behavior and verification in [CHANGELOG.md](CHANGELOG.md).
- Record any changed durable architecture in [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md).
- Keep official conformance references pinned to the adopted Marp Core v5 major version.

## Open questions and decisions needed

- Non-blocking follow-up: decide the visual treatment for ordinary Markdown blockquotes when M1
  restores their standard meaning.
