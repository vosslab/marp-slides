# Marp2pptx review

- Local snapshot: `OTHER_REPOS/marp2pptx`
- Upstream: [marp2pptx](https://github.com/Fjeldmann/marp2pptx)
- Local version: 0.1.5
- Content type: Python postprocessor for editable Marp PPTX output
- License found: MIT with bundled notices
- Recommendation: Test individual hypotheses only

## What it contains

Marp2pptx invokes Marp's editable PPTX route and uses `python-pptx` to alter the result. Functions
parse rendered HTML, calculate background regions, normalize font names, merge multiline text
boxes, remove redundant white rectangles, process native images, and translate styled divisions.

## Reuse assessment

- Ideas: Font normalization, background-image crop calculations, and removal of provably redundant
  shapes could each become a small experiment against a failing fixture.
- Code and functions: The package invokes the latest npm Marp dynamically and depends on Node,
  LibreOffice, BeautifulSoup, Pydantic, and network-capable libraries. Its broad transformations and
  error style do not fit the local deterministic pipeline.
- Themes: It provides no theme improvement needed here.
- Baseline risk: Its input is Marp editable PPTX, which locally lost all notes and broke two-pane
  geometry. Postprocessing does not remove that upstream limitation.

## Decision

Do not adopt the package. Never use blanket textbox widening as a general fix. Study one function
only when a current deck supplies a reproducible defect and the result can be tested structurally
and visually.

[Return to the inventory](../RELATED_PROJECTS.md).
