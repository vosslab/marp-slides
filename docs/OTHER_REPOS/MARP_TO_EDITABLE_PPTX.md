# Marp to editable PPTX review

- Local snapshot: `OTHER_REPOS/marp-to-editable-pptx`
- Upstream: [marp-to-editable-pptx](https://github.com/KatsuYuzu/marp-to-editable-pptx)
- Local version: 1.3.0
- Content type: VS Code extension with a native PPTX conversion engine
- License found: MIT
- Recommendation: Strong future bakeoff candidate

## What it contains

The project renders Marp to HTML, inspects computed layout through Puppeteer, converts the DOM into
typed slide data, and writes native objects with PptxGenJS. Its `src/native-pptx` area is the most
relevant part. Notable boundaries include `extractSlides`, `generateNativePptx`, `buildPptx`,
`placeElement`, text association, adjacency grouping, and the `SlideData` model.

It includes structural tests and visual-comparison tooling. The native route handles text, images,
lists, tables, code, split backgrounds, presenter notes, and fallbacks for unsupported visuals.

## Reuse assessment

- Ideas: A typed intermediate model, computed-geometry capture, native-object placement, and paired
  visual and structural acceptance are excellent prior art for editable output.
- Code and functions: MIT permits reuse with notice, but this is a large TypeScript, Puppeteer, and
  PptxGenJS engine. It conflicts with the Python-only toolchain and adds many special cases.
- Workflow: The VS Code extension is unnecessary; even the separable engine targets PPTX, not ODP.
- Fidelity: Raster fallbacks mean that native output is not uniformly editable.

## Decision

Do not integrate it now. If native editability becomes an approved requirement, run a bounded
genetics-deck bakeoff and borrow its intermediate-model and acceptance concepts before choosing an
implementation. Keep the normal workflow editor-independent.

[Return to the inventory](../RELATED_PROJECTS.md).
