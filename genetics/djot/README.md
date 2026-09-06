# Experimental extended-Djot genetics decks

This folder is a source-level exploration of the future extended-Djot slide language. It does not
replace the current Marp source or create a second production pipeline. Each deck was imported from
the authoritative ODP with `tools/odp_to_djot.py`, which normalizes through a temporary PPTX only
to recover text, images, reading order, and source-hidden slide state.

The generated source assumes the proposed layout catalog and uses the current authoring forms:
`=== layout: <name>`, `@body`, `@left`, `@right`, `@gallery`, standard Djot headings and lists, and
the reserved `![alt](path)` image form. It deliberately omits presenter notes; it does not infer
semantic animations or visual styling from a legacy file. Short DNA sequences use inline verbatim;
the documented `&prime;` source reference projects to U+2032 PRIME in the future native pipeline.

| Deck | Visible slides | Hidden source slides excluded | Distinct extracted images |
| --- | ---: | ---: | ---: |
| `lect01a-course_intro.djot` | 31 | 9 | 18 |
| `lect01b-genetic_disorders.djot` | 23 | 0 | 6 |
| `lect02a-2025_announcements.djot` | 43 | 32 | 15 |
| `lect02b-genes_dogma.djot` | 49 | 0 | 22 |
| `lect02c-genome_sizes.djot` | 59 | 0 | 32 |
| `lect02d-dna_structure_overview.djot` | 43 | 0 | 19 |
| `lect02e-restriction_enzymes.djot` | 62 | 0 | 18 |
| `lect02f-dna_electrophoresis.djot` | 26 | 1 | 20 |
| **Total** | **336** | **42** | **150** |

`assets/<deck>/import_report.json` retains the import inventory, including each visible source-slide
number, selected layout, omitted-note count, and extraction-review reason. Image placement count can
exceed the distinct-asset count because a figure may recur across teaching steps.

## Validation boundary

Run the fast local structural check with:

```bash
source source_me.sh && python3 tools/djot_slide_lint.py genetics/djot
```

It verifies slide declarations, documented required slots, animation-directive shape, and local
image references without rendering a slide. Jotdown 0.10.0 is the pinned native parser and has
passed all eight sources through the native-first check:

```bash
source source_me.sh && python3 tools/djot_slide_lint.py \
  --require-native --native-executable "$(command -v jotdown)" genetics/djot
```

Jotdown is a parser, not a substitute for a formatter, editor rule, or standalone linter. The
remaining compatibility-suite lanes still need explicit decisions before this corpus can claim to
pass every applicable Djot tool. See the
[language exploration record](../../docs/active_plans/decisions/djot_slide_extension_exploration.md)
for that governing requirement and the upstream Djot and Jotdown sources.
