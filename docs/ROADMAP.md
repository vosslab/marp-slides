# Roadmap: extended-Djot native presentations

Status: M1-M4 and M6 are implemented, including one-time all-eight corpus acceptance and private
regeneration reproducibility and one-time native acceptance. M5 animation remains blocked because
PowerPoint and reference timing XML are absent; final close-out remains open until manual timing
evidence is recorded. Classic Marp Core v5 remains the migration baseline, while extended-Djot is a
parallel source front end to the shared native editable-object pipeline.

## Current milestones

| M | Title | Status | Evidence boundary |
| --- | --- | --- | --- |
| M1 | IR and catalog | Complete | Presentation-neutral nodes and registry-derived grammar |
| M2 | Djot parser | Complete | `.djot` source parses to named cells with source locations |
| M3 | Short layouts and multiple choice | Complete | Canonical names and slot contracts, no aliases |
| M4 | Export dispatch | Complete | `.md` and `.djot` select the shared export path by suffix |
| M5 | Animation backend | Blocked | PowerPoint and reference timing XML are absent |
| M6 | Linter and corpus | Complete | Strict lint and one-time eight-deck corpus/reproducibility acceptance |
| M7 | Verification and close-out | In progress | Native acceptance passed; animation/compatibility close-out remains |

## Completed design and implementation

- The layout registry owns geometry, canonical short layout names, and legal slot names.
- Djot grammar is exact and whole-line based: `=== layout: <name>`, `@<slot>`, `<= appear`,
  `=> appear`, and `=> cascade appear`.
- Source is normalized into global title/subtitle blocks and named cells. Multiple H2 lines on a
  title slide form one subtitle region.
- One-line attributes precede and attach to the next element. A standalone component image is a
  complete image paragraph; mixed image paragraphs are source-located unsupported input.
- `$inline$` and `$$display$$` are intentional local math extensions after strict-Djot validation.
  Their editable native rendering remains future work.
- `multiple-choice` uses required `question` and `answer` slots. Its answer has implicit reveal
  intent and permits one or two short flat paragraphs; it does not yet have verified PowerPoint
  playback.
- `blue overlay` is a recognized, explicit deferral rather than a silent no-op.
- The explicit Djot native-layout E2E passed through editable PPTX, LibreOffice ODP, and PDF across
  the registry, including gallery images and distinct editable multiple-choice shapes/final state.
- The one-time all-eight legacy-corpus acceptance passed: 378 source slides, 336 visible slides, 42
  hidden slides, 167 reachable assets, 72 bounded source regions, 96 review slides, and 186 image
  occurrences. A second private regeneration was byte-identical across 183 generated files.
- One-time native acceptance passed: strict lint covered 8 decks, 336 visible slides, and 186 image
  occurrences; `build_slides.sh genetics`, all three native E2Es, and eight sequential matching
  PPTX/ODP/PDF exports passed. Text and direct images remained editable, and Lecture 02e retained its
  native table.

## Remaining gates

1. On a licensed, attended PowerPoint host, perform the two-deck experiment in
   [wp_a1_animation_fidelity.md](active_plans/reports/wp_a1_animation_fidelity.md).
2. If the observed Impress result preserves the required behavior, derive minimal timing templates
   from that PowerPoint evidence and verify first-advance playback. If it degrades or loses the
   behavior, record and select the documented slide-multiplication fallback.
3. Complete the remaining strict-Djot formatter/editor-rule suite selection before claiming full
   compatibility-suite coverage.

## Verification lanes

| Lane | Permanent status | What it proves |
| --- | --- | --- |
| Fast pytest | Permanent, offline | Parser, grammar, layout, suffix, and source diagnostics |
| Strict Jotdown and source lint | One-time/source acceptance | Raw-Djot syntax and project slide semantics |
| Native E2E | Passed explicit E2E | The real editable PPTX -> ODP -> PDF chain |
| Legacy corpus review | Passed one-time acceptance | Regenerated corpus, provenance, asset integrity, and reproducibility |
| Native all-format output | Passed one-time acceptance | Editable PPTX, ODP, and PDF artifacts for every regenerated deck |
| PowerPoint and Impress | Attended manual check | Repair behavior, first advance, and animation survival |

Do not treat a fast test, native lint, or render as a substitute for the attended timing checks.
