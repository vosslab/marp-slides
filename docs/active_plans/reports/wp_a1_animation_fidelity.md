# WP-A1 animation fidelity experiment

Date: 2026-09-06

Status: blocked before the experiment; no fidelity result is claimed.

## Required experiment

WP-A1 requires two minimal decks authored by the actual Microsoft PowerPoint
application:

| Required deck | Required behavior | Evidence required |
| --- | --- | --- |
| `appear-click-object.pptx` | One textbox appears on click. | Its PowerPoint-generated `<p:timing>` tree. |
| `appear-click-paragraphs.pptx` | One text shape builds paragraph by paragraph. | Its PowerPoint-generated `<p:timing>` tree. |

Each deck must then pass through the repository's LibreOffice bridge to ODP,
be opened and observed in Impress, and be converted from ODP to PDF. The
observation class must be `exact`, `survived`, `degraded`, or `lost`; the PDF
must be checked for final-state flattening.

## Current evidence

Microsoft PowerPoint is unavailable on this host. The standard path
`/Applications/Microsoft PowerPoint.app` does not exist, and a bounded search
of `/Applications` and `/Users/vosslab/Applications` found no PowerPoint app.
LibreOffice 26.2.5.2 is installed, and the existing bridge in
[`marp_lib/libreoffice.py`](../../../marp_lib/libreoffice.py) can convert
presentation files to ODP and PDF.

The host command evidence and bridge preflight constraint are recorded in
[`devel/animation_reference/ENVIRONMENT.md`](../../../devel/animation_reference/ENVIRONMENT.md).

## Result

No timing tree was captured. No ODP animation-survival classification or PDF
final-state result can be made. Generating substitute PPTX files from
python-pptx or LibreOffice would not meet the plan's requirement that
PowerPoint be the timing-XML and playback oracle, so no substitute artifact was
created.

This leaves M5's fidelity gate unresolved. The animation backend must not use
WP-A1 as positive evidence, and the slide-multiplication fallback cannot yet be
adopted as an evidence-based decision because its trigger is an observed
failure or degradation in Impress, not missing PowerPoint.

## Exact next run

On a host with licensed Microsoft PowerPoint and attended GUI access:

1. Hand-create and save the two named PPTX decks in PowerPoint using the stated
   click-appear behaviors.
2. Unzip each PPTX and save its `ppt/slides/slide*.xml` `<p:timing>` subtree in
   `devel/animation_reference/` with the corresponding source deck.
3. Use [`marp_lib.libreoffice.convert_file()`](../../../marp_lib/libreoffice.py)
   to convert each PPTX to ODP, then open each ODP in Impress and record the
   observed survival class.
4. Convert each ODP to PDF through the same bridge and inspect whether it shows
   the final reveal state.

The LibreOffice bridge preflight invokes `ps`; this host's sandbox denied that
call, so the conversion commands require normal unsandboxed approval even after
PowerPoint is available.
