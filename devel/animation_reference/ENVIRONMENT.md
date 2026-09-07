# WP-A1 environment evidence

Recorded 2026-09-06 on the macOS build host.

## Presentation applications

The following host checks were run on 2026-09-06:

```text
$ test ! -e '/Applications/Microsoft PowerPoint.app'; printf 'powerpoint_path_exit=%s\n' "$?"
powerpoint_path_exit=0
$ find /Applications /Users/vosslab/Applications -maxdepth 1 -type d -iname '*powerpoint*.app' -print; printf 'powerpoint_search_exit=%s\n' "$?"
powerpoint_search_exit=0
$ '/Applications/LibreOffice.app/Contents/MacOS/soffice' --version; printf 'soffice_version_exit=%s\n' "$?"
LibreOffice 26.2.5.2 cd7284b4cbbfeb507e630c1aac019f4157393acb
soffice_version_exit=0
```

PowerPoint is therefore absent from the standard application path and the
bounded application search; LibreOffice is installed at
`/Applications/LibreOffice.app`.

## Bridge availability

[`marp_lib/libreoffice.py`](../../marp_lib/libreoffice.py) provides the required
conversion bridge through `convert_file(input_path, output_dir, output_format)`.
It invokes the installed
`soffice` binary in headless mode and supports both `odp` and `pdf` output.

The bridge's preflight calls `ps -axo command=` to require LibreOffice to be
closed. This host's sandbox denied that command:

```text
$ ps -axo command=; printf 'ps_exit=%s\n' "$?"
/opt/homebrew/bin/bash: line 4: /bin/ps: Operation not permitted
ps_exit=126
```

Therefore, a conversion run needs normal unsandboxed command approval. No
conversion was attempted because the required PowerPoint-authored input decks
could not be made.

## Consequence for WP-A1

The two required source decks have not been fabricated with python-pptx or
LibreOffice. Doing so would not establish the PowerPoint timing-tree oracle
required by the plan. Consequently, no timing XML, ODP, or PDF artifact exists
yet for this experiment.
