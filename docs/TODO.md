# TODO

Use this file for small, concrete next actions. See [ROADMAP.md](ROADMAP.md) for milestone order,
feature boundaries, and acceptance gates. See [MARP_SYNTAX_GUIDE.md](MARP_SYNTAX_GUIDE.md) for the
syntax accepted today.

## Marp Core v5 baseline

- [ ] Audit current parser behavior against the Marp Core 5.0.1 Markdown contract.
- [ ] Classify every inherited Marpit directive and image form as accepted, planned, or a non-goal.
- [ ] Classify Core v5 tables, strikethrough, emoji, slide size, and title-fit behavior.
- [ ] Decide separately whether Shiki, Mermaid, KaTeX, or MathJax syntax belongs in Marp+.
- [ ] Keep conformance fixtures free of Marp Core v4, highlight.js, and removed legacy syntax.

## Explicit cell markers

- [ ] Inventory every blockquote cell in canonical decks, importers, tests, and preview CSS.
- [ ] Define the named-slot registry for every multi-cell layout.
- [ ] Add `<!-- _cell: <slot> -->` parsing with retained source locations.
- [ ] Store the slot name on each native cell instead of relying on source order.
- [ ] Make layout validation reject missing, duplicate, and unknown slots.
- [ ] Update PPTX and ODP importers to emit named `_cell` markers.
- [ ] Migrate canonical decks from `>` cell wrappers to `_cell` markers in one change.
- [ ] Return `>` to ordinary Markdown blockquote meaning with an editable native representation.
- [ ] Replace blockquote-specific preview CSS with a readable sequential Marp fallback.
- [ ] Update parser, layout, importer, preview, and native-output tests.
- [ ] Move `_cell` from planned to supported in [MARP_SYNTAX_GUIDE.md](MARP_SYNTAX_GUIDE.md) only
  after the migration and verification gates pass.

## Syntax expansion

- [ ] Add native editable table ownership before accepting Markdown tables.
- [ ] Add native editable code-block ownership before accepting fenced or indented code.
- [ ] Add native strikethrough, title-fit, and static fragmented-list semantics.
- [ ] Define mixed text-and-image flow rules for one cell or root body.
- [ ] Define native background-image fit, crop, description, and source-location behavior.
- [ ] Define bounded component-image geometry instead of accepting arbitrary pixel instructions.
- [ ] Design an explicit asset-localization step for remote or data-URL images.
- [ ] Build a capability registry for accepted front-matter keys and directives.
- [ ] Evaluate native header, footer, language, and `hold` or `skip` pagination semantics.
- [ ] Separate the required layout class from independently supported modifier classes.

## Close-out rule

When a task ships, remove it from this scratchpad, update the current contract in
[MARP_SYNTAX_GUIDE.md](MARP_SYNTAX_GUIDE.md), update the status in [ROADMAP.md](ROADMAP.md), and
record the behavior and evidence in [CHANGELOG.md](CHANGELOG.md).
