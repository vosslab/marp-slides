# Pptx2marp review

- Local snapshot: `OTHER_REPOS/pptx2marp`
- Upstream: [pptx2marp](https://github.com/HNRobert/pptx2marp)
- Local version: 0.0.2
- Content type: Small Python PPTX-to-Marp converter
- License found: MIT
- Recommendation: Comparison baseline only

## What it contains

Pptx2marp uses `python-pptx` to extract text, images, and simple tables, then writes Markdown. The
package separates a converter, image extractor, slide processor, text formatter, utilities, and a
small CLI. No automated tests were found in the snapshot.

## Reuse assessment

- Ideas: Its table formatting and Markdown escaping can be compared with local behavior.
- Code and functions: MIT allows reuse with notice, but the implementation has no notes,
  visibility, geometry classification, archive validation, or image-size safety. Direct writes and
  simple shape-order traversal make it weaker than the current importer.
- Themes and assets: It has no reusable theme.
- Fit: The local ODP normalization and structured importer already cover a harder source format
  with stronger contracts and tests.

## Decision

Do not adopt code or dependencies from this project. Retain it only as a compact comparison when
reviewing importer features or error handling.

[Return to the inventory](../RELATED_PROJECTS.md).
